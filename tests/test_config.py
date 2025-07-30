#!/usr/bin/env python3
"""
Tests for configuration management
"""

import pytest
import os
import json
import tempfile
from unittest.mock import patch
try:
    from config import ServerConfig, load_config
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import ServerConfig, load_config


class TestServerConfig:
    """Test server configuration functionality"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = ServerConfig()
        
        assert config.base_url == "https://goferapi.ambivo.com"
        assert config.timeout == 30.0
        assert config.rate_limit_requests == 100
        assert config.log_level == "INFO"
        assert "lead" in config.allowed_entity_types
        assert "contact" in config.allowed_entity_types
    
    def test_from_env(self):
        """Test configuration from environment variables"""
        env_vars = {
            "AMBIVO_BASE_URL": "https://test.ambivo.com",
            "AMBIVO_TIMEOUT": "60.0",
            "AMBIVO_RATE_LIMIT_REQUESTS": "200",
            "AMBIVO_LOG_LEVEL": "DEBUG",
            "AMBIVO_SERVER_NAME": "test-server"
        }
        
        with patch.dict(os.environ, env_vars):
            config = ServerConfig.from_env()
            
            assert config.base_url == "https://test.ambivo.com"
            assert config.timeout == 60.0
            assert config.rate_limit_requests == 200
            assert config.log_level == "DEBUG"
            assert config.server_name == "test-server"
    
    def test_from_file(self):
        """Test configuration from JSON file"""
        config_data = {
            "base_url": "https://file.ambivo.com",
            "timeout": 45.0,
            "rate_limit_requests": 150,
            "log_level": "WARNING",
            "max_query_length": 2000
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name
        
        try:
            config = ServerConfig.from_file(config_path)
            
            assert config.base_url == "https://file.ambivo.com"
            assert config.timeout == 45.0
            assert config.rate_limit_requests == 150
            assert config.log_level == "WARNING"
            assert config.max_query_length == 2000
        finally:
            os.unlink(config_path)
    
    def test_from_file_not_found(self):
        """Test configuration from non-existent file"""
        with pytest.raises(FileNotFoundError):
            ServerConfig.from_file("/nonexistent/config.json")
    
    def test_validation_success(self):
        """Test successful configuration validation"""
        config = ServerConfig()
        config.validate()  # Should not raise
    
    def test_validation_invalid_timeout(self):
        """Test validation with invalid timeout"""
        config = ServerConfig(timeout=0)
        
        with pytest.raises(ValueError, match="Timeout must be positive"):
            config.validate()
    
    def test_validation_invalid_rate_limit(self):
        """Test validation with invalid rate limit"""
        config = ServerConfig(rate_limit_requests=0)
        
        with pytest.raises(ValueError, match="Rate limit requests must be positive"):
            config.validate()
    
    def test_validation_invalid_url(self):
        """Test validation with invalid base URL"""
        config = ServerConfig(base_url="not-a-url")
        
        with pytest.raises(ValueError, match="Base URL must start with"):
            config.validate()
    
    def test_setup_logging(self):
        """Test logging setup"""
        config = ServerConfig(log_level="DEBUG")
        logger = config.setup_logging()
        
        assert logger.name == "ambivo-mcp"
        assert logger.level == 10  # DEBUG level


class TestLoadConfig:
    """Test configuration loading function"""
    
    def test_load_config_from_env(self):
        """Test loading configuration from environment"""
        with patch.dict(os.environ, {"AMBIVO_TIMEOUT": "90.0"}):
            config = load_config()
            assert config.timeout == 90.0
    
    def test_load_config_from_file(self):
        """Test loading configuration from file"""
        config_data = {"timeout": 120.0, "log_level": "ERROR"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name
        
        try:
            config = load_config(config_path)
            assert config.timeout == 120.0
            assert config.log_level == "ERROR"
        finally:
            os.unlink(config_path)
    
    def test_load_config_file_not_found(self):
        """Test loading configuration when file doesn't exist"""
        # Should fall back to environment
        config = load_config("/nonexistent/config.json")
        assert config.base_url == "https://goferapi.ambivo.com"  # default