#!/usr/bin/env python3
"""
Security utilities for Ambivo MCP Server
"""

import hashlib
import json
import logging
import re
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger("ambivo-mcp.security")


@dataclass
class RateLimitEntry:
    """Rate limit tracking entry"""

    requests: deque = field(default_factory=deque)
    window_start: float = field(default_factory=time.time)


class RateLimiter:
    """Simple in-memory rate limiter"""

    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.clients: Dict[str, RateLimitEntry] = {}

    def is_allowed(self, client_id: str) -> bool:
        """Check if client is within rate limits"""
        current_time = time.time()

        if client_id not in self.clients:
            self.clients[client_id] = RateLimitEntry()

        entry = self.clients[client_id]

        # Clean old requests outside the window
        cutoff_time = current_time - self.window_seconds
        while entry.requests and entry.requests[0] < cutoff_time:
            entry.requests.popleft()

        # Check rate limit
        if len(entry.requests) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            return False

        # Add current request
        entry.requests.append(current_time)
        return True

    def get_client_stats(self, client_id: str) -> Dict[str, Any]:
        """Get rate limit statistics for a client"""
        if client_id not in self.clients:
            return {"requests": 0, "remaining": self.max_requests}

        entry = self.clients[client_id]
        current_requests = len(entry.requests)
        remaining = max(0, self.max_requests - current_requests)

        return {
            "requests": current_requests,
            "remaining": remaining,
            "window_seconds": self.window_seconds,
            "reset_time": (
                entry.requests[0] + self.window_seconds
                if entry.requests
                else time.time()
            ),
        }


class InputValidator:
    """Input validation utilities"""

    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        r"\$\{.*\}",  # Template injection
        r"<script.*?>.*?</script>",  # XSS
        r"javascript:",  # JavaScript protocol
        r"data:.*?base64",  # Data URLs
        r"eval\s*\(",  # Code evaluation
        r"exec\s*\(",  # Code execution
        r"import\s+os",  # OS imports
        r"__import__",  # Dynamic imports
        r"subprocess",  # Subprocess calls
    ]

    # MongoDB injection patterns
    MONGODB_PATTERNS = [
        r"\$where",
        r"\$regex.*?\$options",
        r"mapReduce",
        r"function\s*\(",
    ]

    def __init__(self, max_query_length: int = 1000, max_payload_size: int = 1048576):
        self.max_query_length = max_query_length
        self.max_payload_size = max_payload_size
        self.dangerous_regex = re.compile(
            "|".join(self.DANGEROUS_PATTERNS), re.IGNORECASE
        )
        self.mongodb_regex = re.compile("|".join(self.MONGODB_PATTERNS), re.IGNORECASE)

    def validate_query(self, query: str) -> None:
        """Validate natural language query"""
        if not isinstance(query, str):
            raise ValueError("Query must be a string")

        if len(query) > self.max_query_length:
            raise ValueError(f"Query too long. Maximum length: {self.max_query_length}")

        if len(query.strip()) == 0:
            raise ValueError("Query cannot be empty")

        # Check for dangerous patterns
        if self.dangerous_regex.search(query):
            raise ValueError("Query contains potentially dangerous content")

        logger.debug(f"Query validation passed for: {query[:50]}...")

    def validate_entity_type(self, entity_type: str, allowed_types: List[str]) -> None:
        """Validate entity type"""
        if not isinstance(entity_type, str):
            raise ValueError("Entity type must be a string")

        if entity_type not in allowed_types:
            raise ValueError(
                f"Invalid entity type. Allowed: {', '.join(allowed_types)}"
            )

        # Additional validation
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", entity_type):
            raise ValueError("Entity type contains invalid characters")

    def validate_filters(self, filters: Dict[str, Any]) -> None:
        """Validate MongoDB-style filters"""
        if not isinstance(filters, dict):
            raise ValueError("Filters must be a dictionary")

        filters_str = json.dumps(filters)

        # Check payload size
        if len(filters_str.encode("utf-8")) > self.max_payload_size:
            raise ValueError(
                f"Filters too large. Maximum size: {self.max_payload_size} bytes"
            )

        # Check for dangerous MongoDB patterns
        if self.mongodb_regex.search(filters_str):
            raise ValueError("Filters contain potentially dangerous MongoDB operators")

        # Recursively validate filter values
        self._validate_filter_values(filters)

    def _validate_filter_values(self, obj: Any, depth: int = 0) -> None:
        """Recursively validate filter values"""
        if depth > 10:  # Prevent deep recursion
            raise ValueError("Filter structure too deeply nested")

        if isinstance(obj, dict):
            for key, value in obj.items():
                if not isinstance(key, str):
                    raise ValueError("Filter keys must be strings")

                # Check for dangerous operators
                if key.startswith("$") and key not in {
                    "$eq",
                    "$ne",
                    "$gt",
                    "$gte",
                    "$lt",
                    "$lte",
                    "$in",
                    "$nin",
                    "$exists",
                    "$type",
                    "$mod",
                    "$regex",
                    "$options",
                    "$size",
                    "$and",
                    "$or",
                    "$not",
                    "$nor",
                }:
                    raise ValueError(f"Dangerous MongoDB operator: {key}")

                self._validate_filter_values(value, depth + 1)

        elif isinstance(obj, list):
            for item in obj:
                self._validate_filter_values(item, depth + 1)

        elif isinstance(obj, str):
            if len(obj) > 1000:  # Arbitrary limit for string values
                raise ValueError("Filter string value too long")

    def validate_fields(self, fields: List[str]) -> None:
        """Validate field selection"""
        if not isinstance(fields, list):
            raise ValueError("Fields must be a list")

        if len(fields) > 100:  # Reasonable limit
            raise ValueError("Too many fields requested")

        for field in fields:
            if not isinstance(field, str):
                raise ValueError("Field names must be strings")

            if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_.]*$", field):
                raise ValueError(f"Invalid field name: {field}")

    def validate_sort(self, sort: Dict[str, int]) -> None:
        """Validate sort criteria"""
        if not isinstance(sort, dict):
            raise ValueError("Sort must be a dictionary")

        if len(sort) > 10:  # Reasonable limit
            raise ValueError("Too many sort fields")

        for field, direction in sort.items():
            if not isinstance(field, str):
                raise ValueError("Sort field names must be strings")

            if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_.]*$", field):
                raise ValueError(f"Invalid sort field name: {field}")

            if direction not in [-1, 1]:
                raise ValueError(
                    "Sort direction must be 1 (ascending) or -1 (descending)"
                )

    def validate_pagination(self, limit: int, skip: int) -> None:
        """Validate pagination parameters"""
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("Limit must be a positive integer")

        if limit > 1000:
            raise ValueError("Limit too large. Maximum: 1000")

        if not isinstance(skip, int) or skip < 0:
            raise ValueError("Skip must be a non-negative integer")

        if skip > 100000:  # Reasonable limit to prevent performance issues
            raise ValueError("Skip value too large")


class TokenValidator:
    """JWT token validation utilities"""

    def __init__(self, cache_ttl: int = 300):
        self.cache_ttl = cache_ttl
        self.token_cache: Dict[str, Dict[str, Any]] = {}

    def get_client_id_from_token(self, token: str) -> str:
        """Extract client ID from token for rate limiting"""
        # Use hash of token as client ID for privacy
        return hashlib.sha256(token.encode()).hexdigest()[:16]

    def validate_token_format(self, token: str) -> None:
        """Basic JWT token format validation"""
        if not isinstance(token, str):
            raise ValueError("Token must be a string")

        if len(token) < 10:
            raise ValueError("Token too short")

        if len(token) > 2048:  # Reasonable JWT size limit
            raise ValueError("Token too long")

        # Basic JWT structure check (3 parts separated by dots)
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid JWT token format")

        # Check for dangerous characters
        if not re.match(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$", token):
            raise ValueError("Token contains invalid characters")

    def is_token_cached(self, token: str) -> bool:
        """Check if token is in cache and still valid"""
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        if token_hash in self.token_cache:
            cache_entry = self.token_cache[token_hash]
            if time.time() - cache_entry["timestamp"] < self.cache_ttl:
                return True
            else:
                # Remove expired entry
                del self.token_cache[token_hash]

        return False

    def cache_token(self, token: str) -> None:
        """Cache a validated token"""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        self.token_cache[token_hash] = {
            "timestamp": time.time(),
            "client_id": self.get_client_id_from_token(token),
        }

        # Clean old entries periodically
        self._cleanup_cache()

    def _cleanup_cache(self) -> None:
        """Remove expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key
            for key, value in self.token_cache.items()
            if current_time - value["timestamp"] > self.cache_ttl
        ]

        for key in expired_keys:
            del self.token_cache[key]
