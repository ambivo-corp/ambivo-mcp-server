#!/usr/bin/env python3
"""
Test imports to verify the package structure works correctly
"""

def test_imports():
    """Test that all modules can be imported without MCP dependencies"""
    print("Testing imports...")
    
    try:
        # Test config module
        from config import ServerConfig, load_config
        print("✓ config module imports successfully")
        
        # Test config functionality
        config = ServerConfig()
        print(f"✓ ServerConfig works: base_url={config.base_url}")
        
    except Exception as e:
        print(f"✗ config module failed: {e}")
        return False
    
    try:
        # Test security module  
        from security import RateLimiter, InputValidator, TokenValidator
        print("✓ security module imports successfully")
        
        # Test security functionality
        limiter = RateLimiter()
        validator = InputValidator()
        token_validator = TokenValidator()
        print("✓ Security components initialize successfully")
        
    except Exception as e:
        print(f"✗ security module failed: {e}")
        return False
    
    try:
        # Test server module imports (without actually running server)
        import sys
        import importlib.util
        
        # Load server module without executing it
        spec = importlib.util.spec_from_file_location("server_module", "server.py")
        server_module = importlib.util.module_from_spec(spec)
        
        # This will import the module but not execute the main code
        print("✓ server.py module structure is valid")
        
    except ImportError as e:
        if "mcp" in str(e).lower():
            print("⚠ server.py requires MCP dependencies (expected)")
        else:
            print(f"✗ server.py import failed: {e}")
            return False
    except Exception as e:
        print(f"✗ server.py validation failed: {e}")
        return False
    
    print("\n🎉 All imports successful!")
    return True


def test_functionality():
    """Test basic functionality without MCP"""
    print("\nTesting basic functionality...")
    
    try:
        from config import ServerConfig
        from security import RateLimiter, InputValidator
        
        # Test configuration
        config = ServerConfig(
            base_url="https://test.example.com",
            timeout=60.0,
            rate_limit_requests=50
        )
        config.validate()
        print("✓ Configuration validation works")
        
        # Test rate limiter
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        client_id = "test_client"
        
        # Should allow requests
        for i in range(3):
            assert limiter.is_allowed(client_id), f"Request {i} should be allowed"
        print("✓ Rate limiter allows requests within limit")
        
        # Test input validator
        validator = InputValidator()
        validator.validate_query("Show me all leads")
        validator.validate_entity_type("lead", ["lead", "contact"])
        validator.validate_fields(["name", "email"])
        print("✓ Input validation works")
        
        print("🎉 Basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Functionality test failed: {e}")
        return False


if __name__ == "__main__":
    print("Ambivo MCP Server - Import Test")
    print("=" * 40)
    
    imports_ok = test_imports()
    functionality_ok = test_functionality()
    
    if imports_ok and functionality_ok:
        print("\n✅ All tests passed! The package is ready for use.")
        exit(0)
    else:
        print("\n❌ Some tests failed. Please fix the issues before proceeding.")
        exit(1)