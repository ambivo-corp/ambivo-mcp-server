#!/usr/bin/env python3
"""
Tests for security components
"""

import pytest
import time
from unittest.mock import Mock, patch
try:
    from security import RateLimiter, InputValidator, TokenValidator
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from security import RateLimiter, InputValidator, TokenValidator


class TestRateLimiter:
    """Test rate limiting functionality"""
    
    def test_rate_limiter_init(self):
        """Test rate limiter initialization"""
        limiter = RateLimiter(max_requests=10, window_seconds=60)
        assert limiter.max_requests == 10
        assert limiter.window_seconds == 60
        assert len(limiter.clients) == 0
    
    def test_rate_limiter_allows_requests_within_limit(self):
        """Test that requests within limit are allowed"""
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        client_id = "test_client"
        
        # Should allow first 5 requests
        for i in range(5):
            assert limiter.is_allowed(client_id) == True
    
    def test_rate_limiter_blocks_requests_over_limit(self):
        """Test that requests over limit are blocked"""
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        client_id = "test_client"
        
        # Allow first 3 requests
        for i in range(3):
            assert limiter.is_allowed(client_id) == True
        
        # Block 4th request
        assert limiter.is_allowed(client_id) == False
    
    def test_rate_limiter_window_reset(self):
        """Test that rate limit resets after window"""
        limiter = RateLimiter(max_requests=2, window_seconds=1)
        client_id = "test_client"
        
        # Use up limit
        assert limiter.is_allowed(client_id) == True
        assert limiter.is_allowed(client_id) == True
        assert limiter.is_allowed(client_id) == False
        
        # Wait for window to pass
        time.sleep(1.1)
        
        # Should allow requests again
        assert limiter.is_allowed(client_id) == True
    
    def test_rate_limiter_stats(self):
        """Test rate limiter statistics"""
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        client_id = "test_client"
        
        # Make some requests
        limiter.is_allowed(client_id)
        limiter.is_allowed(client_id)
        
        stats = limiter.get_client_stats(client_id)
        assert stats["requests"] == 2
        assert stats["remaining"] == 3
        assert stats["window_seconds"] == 60


class TestInputValidator:
    """Test input validation functionality"""
    
    def test_validator_init(self):
        """Test validator initialization"""
        validator = InputValidator(max_query_length=500, max_payload_size=1024)
        assert validator.max_query_length == 500
        assert validator.max_payload_size == 1024
    
    def test_validate_query_success(self):
        """Test successful query validation"""
        validator = InputValidator()
        
        # Should not raise exception
        validator.validate_query("Show me all leads")
        validator.validate_query("Find contacts with gmail addresses")
    
    def test_validate_query_empty(self):
        """Test validation of empty query"""
        validator = InputValidator()
        
        with pytest.raises(ValueError, match="Query cannot be empty"):
            validator.validate_query("")
        
        with pytest.raises(ValueError, match="Query cannot be empty"):
            validator.validate_query("   ")
    
    def test_validate_query_too_long(self):
        """Test validation of overly long query"""
        validator = InputValidator(max_query_length=10)
        
        with pytest.raises(ValueError, match="Query too long"):
            validator.validate_query("This query is definitely longer than 10 characters")
    
    def test_validate_query_dangerous_content(self):
        """Test validation blocks dangerous content"""
        validator = InputValidator()
        
        dangerous_queries = [
            "Show me ${dangerous.code}",
            "<script>alert('xss')</script>",
            "javascript:alert(1)",
            "eval(malicious_code)",
            "import os; os.system('rm -rf /')"
        ]
        
        for query in dangerous_queries:
            with pytest.raises(ValueError, match="dangerous content"):
                validator.validate_query(query)
    
    def test_validate_entity_type_success(self):
        """Test successful entity type validation"""
        validator = InputValidator()
        allowed_types = ["lead", "contact", "opportunity"]
        
        validator.validate_entity_type("lead", allowed_types)
        validator.validate_entity_type("contact", allowed_types)
    
    def test_validate_entity_type_invalid(self):
        """Test validation of invalid entity type"""
        validator = InputValidator()
        allowed_types = ["lead", "contact"]
        
        with pytest.raises(ValueError, match="Invalid entity type"):
            validator.validate_entity_type("invalid_type", allowed_types)
        
        with pytest.raises(ValueError, match="invalid characters"):
            validator.validate_entity_type("lead-type", allowed_types)
    
    def test_validate_filters_success(self):
        """Test successful filter validation"""
        validator = InputValidator()
        
        valid_filters = [
            {"status": "active"},
            {"created_date": {"$gte": "2024-01-01"}},
            {"$and": [{"status": "active"}, {"type": "lead"}]}
        ]
        
        for filters in valid_filters:
            validator.validate_filters(filters)
    
    def test_validate_filters_dangerous(self):
        """Test validation blocks dangerous filters"""
        validator = InputValidator()
        
        dangerous_filters = [
            {"$where": "this.status == 'active'"},
            {"name": {"$regex": ".*", "$options": "i", "$where": "1==1"}}
        ]
        
        for filters in dangerous_filters:
            with pytest.raises(ValueError, match="dangerous MongoDB operators"):
                validator.validate_filters(filters)
    
    def test_validate_fields_success(self):
        """Test successful field validation"""
        validator = InputValidator()
        
        validator.validate_fields(["name", "email", "phone"])
        validator.validate_fields(["created_date", "user.name"])
    
    def test_validate_fields_invalid(self):
        """Test validation of invalid fields"""
        validator = InputValidator()
        
        with pytest.raises(ValueError, match="Field names must be strings"):
            validator.validate_fields([123, "name"])
        
        with pytest.raises(ValueError, match="Invalid field name"):
            validator.validate_fields(["field-name"])
    
    def test_validate_sort_success(self):
        """Test successful sort validation"""
        validator = InputValidator()
        
        validator.validate_sort({"created_date": -1})
        validator.validate_sort({"name": 1, "email": -1})
    
    def test_validate_sort_invalid_direction(self):
        """Test validation of invalid sort direction"""
        validator = InputValidator()
        
        with pytest.raises(ValueError, match="Sort direction must be"):
            validator.validate_sort({"name": 2})
    
    def test_validate_pagination_success(self):
        """Test successful pagination validation"""
        validator = InputValidator()
        
        validator.validate_pagination(50, 0)
        validator.validate_pagination(100, 50)
    
    def test_validate_pagination_invalid(self):
        """Test validation of invalid pagination"""
        validator = InputValidator()
        
        with pytest.raises(ValueError, match="Limit must be a positive integer"):
            validator.validate_pagination(0, 0)
        
        with pytest.raises(ValueError, match="Limit too large"):
            validator.validate_pagination(2000, 0)
        
        with pytest.raises(ValueError, match="Skip must be a non-negative integer"):
            validator.validate_pagination(50, -1)


class TestTokenValidator:
    """Test token validation functionality"""
    
    def test_validator_init(self):
        """Test token validator initialization"""
        validator = TokenValidator(cache_ttl=300)
        assert validator.cache_ttl == 300
        assert len(validator.token_cache) == 0
    
    def test_get_client_id_from_token(self):
        """Test client ID generation from token"""
        validator = TokenValidator()
        
        token1 = "test_token_1"
        token2 = "test_token_2"
        
        id1 = validator.get_client_id_from_token(token1)
        id2 = validator.get_client_id_from_token(token2)
        
        # Should be consistent
        assert validator.get_client_id_from_token(token1) == id1
        
        # Should be different for different tokens
        assert id1 != id2
        
        # Should be reasonable length
        assert len(id1) == 16
    
    def test_validate_token_format_success(self):
        """Test successful token format validation"""
        validator = TokenValidator()
        
        # Valid JWT format
        valid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        
        validator.validate_token_format(valid_token)
    
    def test_validate_token_format_invalid(self):
        """Test validation of invalid token formats"""
        validator = TokenValidator()
        
        invalid_tokens = [
            "",
            "short",
            "not.a.jwt",
            "too.many.parts.here.invalid",
            "invalid@characters.in.token"
        ]
        
        for token in invalid_tokens:
            with pytest.raises(ValueError):
                validator.validate_token_format(token)
    
    def test_token_caching(self):
        """Test token caching functionality"""
        validator = TokenValidator(cache_ttl=1)
        token = "test.token.here"
        
        # Initially not cached
        assert not validator.is_token_cached(token)
        
        # Cache it
        validator.cache_token(token)
        assert validator.is_token_cached(token)
        
        # Wait for expiry
        time.sleep(1.1)
        assert not validator.is_token_cached(token)