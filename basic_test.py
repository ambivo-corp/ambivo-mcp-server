#!/usr/bin/env python3
"""
Basic test script that doesn't require MCP dependencies
Tests the core logic and structure of the server
"""

import json
import sys
import os


def test_basic_structure():
    """Test basic server structure without MCP dependencies"""
    print("Basic Structure Test for Ambivo MCP Server")
    print("=" * 50)
    
    # Test 1: File structure
    print("Test 1: File Structure")
    required_files = [
        "server.py",
        "requirements.txt", 
        "README.md",
        "__init__.py",
        "setup.py"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} exists")
        else:
            print(f"✗ {file} missing")
    print()
    
    # Test 2: Server.py structure (basic parsing)
    print("Test 2: Server.py Structure")
    try:
        with open("server.py", "r") as f:
            content = f.read()
            
        # Check for key components
        checks = [
            ("AmbivoAPIClient class", "class AmbivoAPIClient" in content),
            ("natural_query method", "async def natural_query" in content),
            ("Authentication handling", "Bearer" in content),
            ("Error handling", "try:" in content and "except" in content),
            ("JSON handling", "json.dumps" in content),
            ("HTTP client", "httpx" in content)
        ]
        
        for check_name, result in checks:
            print(f"{'✓' if result else '✗'} {check_name}")
        print()
        
    except Exception as e:
        print(f"✗ Could not parse server.py: {e}")
        print()
    
    # Test 3: Requirements file
    print("Test 3: Requirements")
    try:
        with open("requirements.txt", "r") as f:
            requirements = f.read().strip().split("\n")
        
        expected_deps = ["mcp", "httpx"]
        for dep in expected_deps:
            found = any(dep in req for req in requirements)
            print(f"{'✓' if found else '✗'} {dep} dependency")
        print()
        
    except Exception as e:
        print(f"✗ Could not read requirements.txt: {e}")
        print()
    
    # Test 4: Documentation
    print("Test 4: Documentation")
    try:
        with open("README.md", "r") as f:
            readme = f.read()
        
        doc_checks = [
            ("Installation instructions", "Installation" in readme),
            ("Usage examples", "Usage" in readme or "Example" in readme),
            ("Tool descriptions", "Tools" in readme),
            ("Authentication info", "auth" in readme.lower()),
            ("Error handling info", "error" in readme.lower())
        ]
        
        for check_name, result in doc_checks:
            print(f"{'✓' if result else '✗'} {check_name}")
        print()
        
    except Exception as e:
        print(f"✗ Could not read README.md: {e}")
        print()


def test_configuration():
    """Test configuration values"""
    print("Test 5: Configuration")
    
    # Expected configuration
    expected_config = {
        "base_url": "https://goferapi.ambivo.com",
        "timeout": 30.0,
        "endpoints": [
            "/entity/natural_query",
            "/entity/data"
        ]
    }
    
    try:
        with open("server.py", "r") as f:
            content = f.read()
        
        # Check configuration values
        if "https://goferapi.ambivo.com" in content:
            print("✓ Base URL configured correctly")
        else:
            print("✗ Base URL not found or incorrect")
            
        if "DEFAULT_TIMEOUT = 30" in content:
            print("✓ Timeout configured")
        else:
            print("⚠ Timeout may not be configured")
            
        if "/entity/natural_query" in content and "/entity/data" in content:
            print("✓ Both endpoints referenced")
        else:
            print("✗ Missing endpoint references")
        print()
        
    except Exception as e:
        print(f"✗ Could not verify configuration: {e}")
        print()


def print_next_steps():
    """Print next steps for deployment"""
    print("Next Steps for Deployment:")
    print("=" * 30)
    print()
    print("1. Install dependencies:")
    print("   pip install -r requirements.txt")
    print()
    print("2. Test the server (requires MCP dependencies):")
    print("   python test_server.py")
    print()
    print("3. Run the MCP server:")
    print("   python server.py")
    print()
    print("4. Configure Claude Code to use this MCP server:")
    print("   - Add server configuration to MCP settings")
    print("   - Test with real JWT tokens")
    print()
    print("5. Example MCP configuration:")
    config_example = {
        "mcpServers": {
            "ambivo-api": {
                "command": "python",
                "args": ["/path/to/mcp-server/server.py"],
                "env": {}
            }
        }
    }
    print(json.dumps(config_example, indent=2))
    print()


def test_tool_definitions():
    """Test tool definition structure"""
    print("Test 6: Tool Definitions")
    
    expected_tools = {
        "set_auth_token": {
            "required": ["token"],
            "purpose": "Authentication"
        },
        "natural_query": {
            "required": ["query"],
            "optional": ["response_format"],
            "purpose": "Natural language queries"
        },
    }
    
    try:
        with open("server.py", "r") as f:
            content = f.read()
        
        for tool_name, tool_info in expected_tools.items():
            if tool_name in content:
                print(f"✓ Tool '{tool_name}' defined")
            else:
                print(f"✗ Tool '{tool_name}' missing")
        print()
        
    except Exception as e:
        print(f"✗ Could not verify tool definitions: {e}")
        print()


def main():
    """Run all basic tests"""
    print("Ambivo MCP Server - Basic Test Suite")
    print("(No MCP dependencies required)")
    print("=" * 50)
    print()
    
    test_basic_structure()
    test_configuration()
    test_tool_definitions()
    print_next_steps()
    
    print("=" * 50)
    print("Basic tests completed!")
    print()
    print("The MCP server structure is ready.")
    print("Install dependencies and run full tests when ready.")


if __name__ == "__main__":
    main()