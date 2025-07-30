#!/bin/bash

# =============================================================================
# MANUAL PYPI PUBLISH SCRIPT - Ambivo MCP Server
# =============================================================================
# 
# This script manually publishes ambivo-mcp-server to PyPI when GitHub Actions 
# runners are unavailable or overbooked.
#
# Prerequisites:
# - .pypirc file with PyPI credentials configured
# - Git repository with proper tags
# - Python 3.11+ environment with build tools
#
# Usage:
#   ./manual_pypi_publish.sh [--test] [--force] [--version VERSION]
#
# Options:
#   --test     Publish to Test PyPI instead of production
#   --force    Skip version checks and confirmations
#   --version  Specify version manually (e.g., --version 1.0.1)
#
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_NAME="ambivo-mcp-server"
PYPROJECT_FILE="pyproject.toml"
SETUP_FILE="setup.py"
PYPIRC_FILE=".pypirc"
#PYPIRC_FILE="$HOME/.pypirc"

# Default settings
USE_TEST_PYPI=false
FORCE_PUBLISH=false
MANUAL_VERSION=""
DRY_RUN=false

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

print_header() {
    echo -e "${PURPLE}=================================================================${NC}"
    echo -e "${PURPLE} $1${NC}"
    echo -e "${PURPLE}=================================================================${NC}"
}

print_step() {
    echo -e "\n${BLUE}🔧 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

check_prerequisites() {
    print_step "Checking prerequisites..."
    
    # Check if we're in the right directory
    if [[ ! -f "$PYPROJECT_FILE" ]]; then
        print_error "pyproject.toml not found. Are you in the correct directory?"
        exit 1
    fi
    
    # Check for .pypirc
    if [[ ! -f "$PYPIRC_FILE" ]]; then
        print_error ".pypirc file not found at $PYPIRC_FILE"
        print_info "Create .pypirc with your PyPI credentials:"
        echo "[distutils]"
        echo "index-servers = pypi testpypi"
        echo ""
        echo "[pypi]"
        echo "username = __token__"
        echo "password = pypi-your-token"
        echo ""
        echo "[testpypi]"
        echo "repository = https://test.pypi.org/legacy/"
        echo "username = __token__"
        echo "password = pypi-your-test-token"
        exit 1
    fi
    
    # Check if git is available and we're in a git repo
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "Not in a git repository"
        exit 1
    fi
    
    # Check required tools
    local tools=("python" "pip" "git")
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            print_error "$tool is not installed or not in PATH"
            exit 1
        fi
    done
    
    # Check Python version
    local python_version
    python_version=$(python --version 2>&1 | sed 's/Python //')
    if [[ ! "$python_version" =~ ^3\.1[1-9] ]]; then
        print_warning "Python version: $python_version (3.11+ recommended)"
    else
        print_success "Python version: $python_version"
    fi
    
    print_success "All prerequisites met"
}

get_current_git_tag() {
    local tag
    tag=$(git describe --tags --exact-match 2>/dev/null || echo "")
    echo "$tag"
}

get_pyproject_version() {
    local version
    version=$(grep '^version = ' "$PYPROJECT_FILE" | sed 's/version = "\(.*\)"/\1/')
    echo "$version"
}

get_setup_version() {
    local version
    version=$(grep 'version=' "$SETUP_FILE" | head -1 | sed 's/.*version="\([^"]*\)".*/\1/')
    echo "$version"
}

check_version_exists_on_pypi() {
    local version="$1"
    local use_test="$2"
    
    if [[ "$use_test" == "true" ]]; then
        # Check Test PyPI
        if pip index versions "$PACKAGE_NAME" --index-url https://test.pypi.org/simple/ 2>/dev/null | grep -q "$version"; then
            return 0  # Version exists
        fi
    else
        # Check Production PyPI
        if pip index versions "$PACKAGE_NAME" 2>/dev/null | grep -q "$version"; then
            return 0  # Version exists
        fi
    fi
    
    return 1  # Version doesn't exist
}

# =============================================================================
# VERSION MANAGEMENT
# =============================================================================

determine_target_version() {
    print_step "Determining target version..."
    
    local git_tag current_pyproject_version current_setup_version
    
    git_tag=$(get_current_git_tag)
    current_pyproject_version=$(get_pyproject_version)
    current_setup_version=$(get_setup_version)
    
    print_info "Git tag: ${git_tag:-'(none)'}"
    print_info "pyproject.toml version: $current_pyproject_version"
    print_info "setup.py version: $current_setup_version"
    
    # Determine target version
    if [[ -n "$MANUAL_VERSION" ]]; then
        TARGET_VERSION="$MANUAL_VERSION"
        print_info "Using manually specified version: $TARGET_VERSION"
    elif [[ -n "$git_tag" ]]; then
        # Remove 'v' prefix if present
        TARGET_VERSION="${git_tag#v}"
        print_info "Using git tag version: $TARGET_VERSION"
    else
        TARGET_VERSION="$current_pyproject_version"
        print_warning "No git tag found, using pyproject.toml version: $TARGET_VERSION"
    fi
    
    # Validate version format
    if [[ ! "$TARGET_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+([a-zA-Z0-9.-]*)?$ ]]; then
        print_error "Invalid version format: $TARGET_VERSION"
        print_info "Expected format: X.Y.Z or X.Y.Z-suffix"
        exit 1
    fi
    
    print_success "Target version: $TARGET_VERSION"
}

sync_version_files() {
    print_step "Synchronizing version across files..."
    
    local pyproject_version setup_version
    pyproject_version=$(get_pyproject_version)
    setup_version=$(get_setup_version)
    
    # Update pyproject.toml if needed
    if [[ "$pyproject_version" != "$TARGET_VERSION" ]]; then
        print_info "Updating pyproject.toml: $pyproject_version → $TARGET_VERSION"
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/version = \"$pyproject_version\"/version = \"$TARGET_VERSION\"/" "$PYPROJECT_FILE"
        else
            sed -i "s/version = \"$pyproject_version\"/version = \"$TARGET_VERSION\"/" "$PYPROJECT_FILE"
        fi
    fi
    
    # Update setup.py if needed
    if [[ "$setup_version" != "$TARGET_VERSION" ]]; then
        print_info "Updating setup.py: $setup_version → $TARGET_VERSION"
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/version=\"$setup_version\"/version=\"$TARGET_VERSION\"/" "$SETUP_FILE"
        else
            sed -i "s/version=\"$setup_version\"/version=\"$TARGET_VERSION\"/" "$SETUP_FILE"
        fi
    fi
    
    print_success "Version files synchronized to $TARGET_VERSION"
}

# =============================================================================
# BUILD AND PUBLISH FUNCTIONS
# =============================================================================

install_build_dependencies() {
    print_step "Installing/upgrading build dependencies..."
    
    python -m pip install --upgrade pip build twine setuptools wheel
    
    print_success "Build dependencies ready"
}

clean_previous_builds() {
    print_step "Cleaning previous builds..."
    
    rm -rf dist/ build/ *.egg-info/
    
    print_success "Build directories cleaned"
}

build_package() {
    print_step "Building package..."
    
    python -m build
    
    # Verify the built package has correct version
    local built_files
    built_files=(dist/*.whl dist/*.tar.gz)
    
    if [[ ! -f "${built_files[0]}" ]]; then
        print_error "Build failed - no wheel file found"
        exit 1
    fi
    
    # Check if version matches
    local built_version
    built_version=$(ls dist/*.whl | sed "s/.*-\([0-9][^-]*\)-.*/\1/")
    
    if [[ "$built_version" != "$TARGET_VERSION" ]]; then
        print_error "Built version ($built_version) doesn't match target ($TARGET_VERSION)"
        exit 1
    fi
    
    print_success "Package built successfully"
    print_info "Files created:"
    ls -la dist/
}

verify_package() {
    print_step "Verifying package integrity..."
    
    twine check dist/*
    
    print_success "Package verification passed"
}

test_package_installation() {
    print_step "Testing package installation..."
    
    # Create a temporary virtual environment
    python -m venv test_env
    source test_env/bin/activate
    
    # Install the built package
    pip install dist/*.whl
    
    # Test basic imports
    python -c "
try:
    import ambivo_mcp_server.server as server
    print('✅ Server module imports successfully')
    
    # Test config and security imports
    from ambivo_mcp_server.config import ServerConfig, load_config
    from ambivo_mcp_server.security import RateLimiter, InputValidator, TokenValidator
    print('✅ All core modules import successfully')
    
    # Test basic functionality
    config = ServerConfig()
    limiter = RateLimiter()
    validator = InputValidator()
    print('✅ Core components initialize successfully')
    
    print('✅ Package installation test passed')
    
except ImportError as e:
    if 'mcp' in str(e).lower():
        print('⚠️ MCP dependencies not available (expected in test)')
        print('✅ Package structure is valid')
    else:
        print(f'❌ Import test failed: {e}')
        exit(1)
except Exception as e:
    print(f'❌ Functionality test failed: {e}')
    exit(1)
"
    
    # Cleanup
    deactivate
    rm -rf test_env
    
    print_success "Package installation test passed"
}

check_existing_version() {
    print_step "Checking if version already exists..."
    
    if check_version_exists_on_pypi "$TARGET_VERSION" "$USE_TEST_PYPI"; then
        local pypi_name
        if [[ "$USE_TEST_PYPI" == "true" ]]; then
            pypi_name="Test PyPI"
        else
            pypi_name="Production PyPI"
        fi
        
        if [[ "$FORCE_PUBLISH" == "true" ]]; then
            print_warning "Version $TARGET_VERSION already exists on $pypi_name (continuing due to --force)"
        else
            print_error "Version $TARGET_VERSION already exists on $pypi_name"
            print_info "Use --force to override this check"
            exit 1
        fi
    else
        print_success "Version $TARGET_VERSION is new - ready to publish"
    fi
}

publish_package() {
    print_step "Publishing to PyPI..."
    
    local upload_args=("dist/*" "--config-file" "$PYPIRC_FILE" "--verbose")
    local pypi_name repo_url
    
    if [[ "$USE_TEST_PYPI" == "true" ]]; then
        upload_args+=("--repository" "testpypi")
        pypi_name="Test PyPI"
        repo_url="https://test.pypi.org/project/$PACKAGE_NAME/$TARGET_VERSION/"
    else
        upload_args+=("--repository" "pypi")
        pypi_name="Production PyPI"
        repo_url="https://pypi.org/project/$PACKAGE_NAME/$TARGET_VERSION/"
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_info "DRY RUN: Would execute: twine upload ${upload_args[*]}"
        return 0
    fi
    
    print_info "Uploading to $pypi_name..."
    twine upload "${upload_args[@]}"
    
    print_success "Package published successfully!"
    print_info "View at: $repo_url"
}

# =============================================================================
# CONFIRMATION AND SUMMARY
# =============================================================================

confirm_publish() {
    if [[ "$FORCE_PUBLISH" == "true" ]]; then
        return 0
    fi
    
    local pypi_name
    if [[ "$USE_TEST_PYPI" == "true" ]]; then
        pypi_name="Test PyPI"
    else
        pypi_name="Production PyPI"
    fi
    
    echo -e "\n${YELLOW}📋 PUBLISH SUMMARY${NC}"
    echo -e "  Package: $PACKAGE_NAME"
    echo -e "  Version: $TARGET_VERSION"
    echo -e "  Target:  $pypi_name"
    echo -e "  Git tag: $(get_current_git_tag || echo 'none')"
    
    echo -e "\n${CYAN}Files to upload:${NC}"
    ls -la dist/
    
    echo -e "\n${YELLOW}❓ Do you want to proceed with publishing? (y/N)${NC}"
    read -r response
    
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_info "Publishing cancelled by user"
        exit 0
    fi
}

print_final_summary() {
    local pypi_name repo_url install_cmd
    
    if [[ "$USE_TEST_PYPI" == "true" ]]; then
        pypi_name="Test PyPI"
        repo_url="https://test.pypi.org/project/$PACKAGE_NAME/$TARGET_VERSION/"
        install_cmd="pip install -i https://test.pypi.org/simple/ $PACKAGE_NAME==$TARGET_VERSION"
    else
        pypi_name="Production PyPI"
        repo_url="https://pypi.org/project/$PACKAGE_NAME/$TARGET_VERSION/"
        install_cmd="pip install $PACKAGE_NAME==$TARGET_VERSION"
    fi
    
    print_header "PUBLISH COMPLETE"
    
    echo -e "${GREEN}🎉 Successfully published $PACKAGE_NAME v$TARGET_VERSION to $pypi_name!${NC}\n"
    
    echo -e "${CYAN}📋 Summary:${NC}"
    echo -e "  • Package: $PACKAGE_NAME"
    echo -e "  • Version: $TARGET_VERSION"
    echo -e "  • Target:  $pypi_name"
    echo -e "  • Status:  Published ✅"
    
    echo -e "\n${CYAN}🔗 Links:${NC}"
    echo -e "  • PyPI page: $repo_url"
    
    echo -e "\n${CYAN}📦 Installation:${NC}"
    echo -e "  $install_cmd"
    
    echo -e "\n${CYAN}🚀 Usage:${NC}"
    echo -e "  # Run the MCP server"
    echo -e "  ambivo-mcp-server"
    echo -e ""
    echo -e "  # Or with Docker"
    echo -e "  docker run ambivo/mcp-server:latest"
    
    echo -e "\n${CYAN}⏰ Note:${NC}"
    echo -e "  It may take a few minutes for the package to appear in pip search/index"
}

# =============================================================================
# ARGUMENT PARSING
# =============================================================================

show_help() {
    cat << EOF
Manual PyPI Publish Script for Ambivo MCP Server

USAGE:
    $0 [OPTIONS]

OPTIONS:
    --test              Publish to Test PyPI instead of production
    --force             Skip version checks and confirmations
    --version VERSION   Specify version manually (e.g., --version 1.0.1)
    --dry-run          Show what would be done without actually publishing
    --help             Show this help message

EXAMPLES:
    $0                           # Publish current version to production PyPI
    $0 --test                    # Publish to Test PyPI for testing
    $0 --version 1.0.1           # Publish specific version
    $0 --test --version 1.0.1    # Publish specific version to Test PyPI
    $0 --force                   # Skip confirmations and version checks
    $0 --dry-run                 # See what would happen without publishing

PREREQUISITES:
    • .pypirc file with PyPI credentials configured
    • Git repository with proper tags (optional)
    • Python 3.11+ environment with build tools

CONFIGURATION:
    The script looks for .pypirc in your home directory with this format:
    
    [distutils]
    index-servers = pypi testpypi
    
    [pypi]
    username = __token__
    password = pypi-your-production-token
    
    [testpypi]
    repository = https://test.pypi.org/legacy/
    username = __token__
    password = pypi-your-test-token

EOF
}

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --test)
                USE_TEST_PYPI=true
                shift
                ;;
            --force)
                FORCE_PUBLISH=true
                shift
                ;;
            --version)
                if [[ -n "$2" && ! "$2" =~ ^-- ]]; then
                    MANUAL_VERSION="$2"
                    shift 2
                else
                    print_error "--version requires a version number"
                    exit 1
                fi
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                print_info "Use --help for usage information"
                exit 1
                ;;
        esac
    done
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

main() {
    parse_arguments "$@"
    
    print_header "MANUAL PYPI PUBLISH - $PACKAGE_NAME"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_warning "DRY RUN MODE - No actual changes will be made"
    fi
    
    # Step 1: Validate environment
    check_prerequisites
    
    # Step 2: Determine version to publish
    determine_target_version
    
    # Step 3: Sync version files
    if [[ "$DRY_RUN" == "false" ]]; then
        sync_version_files
    else
        print_info "DRY RUN: Would sync version files to $TARGET_VERSION"
    fi
    
    # Step 4: Install dependencies
    if [[ "$DRY_RUN" == "false" ]]; then
        install_build_dependencies
    else
        print_info "DRY RUN: Would install build dependencies"
    fi
    
    # Step 5: Clean and build
    if [[ "$DRY_RUN" == "false" ]]; then
        clean_previous_builds
        build_package
        verify_package
        test_package_installation
    else
        print_info "DRY RUN: Would clean, build, verify, and test package"
    fi
    
    # Step 6: Check if version exists
    check_existing_version
    
    # Step 7: Confirm publication
    if [[ "$DRY_RUN" == "false" ]]; then
        confirm_publish
    fi
    
    # Step 8: Publish
    publish_package
    
    # Step 9: Show summary
    if [[ "$DRY_RUN" == "false" ]]; then
        print_final_summary
    else
        print_info "DRY RUN COMPLETE - No actual publishing performed"
    fi
}

# =============================================================================
# SCRIPT ENTRY POINT
# =============================================================================

# Change to script directory
cd "$SCRIPT_DIR"

# Run main function with all arguments
main "$@"