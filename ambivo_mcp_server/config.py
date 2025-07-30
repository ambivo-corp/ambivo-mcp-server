#!/usr/bin/env python3
"""
Configuration management for Ambivo MCP Server
"""

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class ServerConfig:
    """Server configuration settings"""

    # API Configuration
    base_url: str = "https://goferapi.ambivo.com"
    timeout: float = 30.0
    max_retries: int = 3

    # Security Configuration
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600  # 1 hour in seconds
    max_query_length: int = 1000
    max_payload_size: int = 1048576  # 1MB in bytes
    allowed_entity_types: list = field(
        default_factory=lambda: [
            "lead",
            "contact",
            "opportunity",
            "task",
            "campaign",
            "order",
            "product",
            "message",
            "user",
            "project",
        ]
    )

    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: Optional[str] = None

    # Server Configuration
    server_name: str = "ambivo-mcp-server"
    server_version: str = "1.0.0"

    # Token Configuration
    token_validation_enabled: bool = True
    token_cache_ttl: int = 14400  # 4 hours
    auth_token: Optional[str] = None  # Optional default auth token

    @classmethod
    def from_env(cls) -> "ServerConfig":
        """Create configuration from environment variables"""
        return cls(
            base_url=os.getenv("AMBIVO_BASE_URL", "https://goferapi.ambivo.com"),
            timeout=float(os.getenv("AMBIVO_TIMEOUT", cls.timeout)),
            max_retries=int(os.getenv("AMBIVO_MAX_RETRIES", cls.max_retries)),
            rate_limit_requests=int(
                os.getenv("AMBIVO_RATE_LIMIT_REQUESTS", cls.rate_limit_requests)
            ),
            rate_limit_window=int(
                os.getenv("AMBIVO_RATE_LIMIT_WINDOW", cls.rate_limit_window)
            ),
            max_query_length=int(
                os.getenv("AMBIVO_MAX_QUERY_LENGTH", cls.max_query_length)
            ),
            max_payload_size=int(
                os.getenv("AMBIVO_MAX_PAYLOAD_SIZE", cls.max_payload_size)
            ),
            log_level=os.getenv("AMBIVO_LOG_LEVEL", cls.log_level),
            log_file=os.getenv("AMBIVO_LOG_FILE"),
            server_name=os.getenv("AMBIVO_SERVER_NAME", cls.server_name),
            server_version=os.getenv("AMBIVO_SERVER_VERSION", cls.server_version),
            token_validation_enabled=os.getenv(
                "AMBIVO_TOKEN_VALIDATION", "true"
            ).lower()
            == "true",
            token_cache_ttl=int(
                os.getenv("AMBIVO_TOKEN_CACHE_TTL", cls.token_cache_ttl)
            ),
            auth_token=os.getenv("AMBIVO_AUTH_TOKEN"),
        )

    @classmethod
    def from_file(cls, config_path: str) -> "ServerConfig":
        """Create configuration from JSON file"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_file, "r") as f:
            config_data = json.load(f)

        return cls(**config_data)

    def setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        # Configure root logger
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format=self.log_format,
            filename=self.log_file,
        )

        # Create and configure MCP server logger
        logger = logging.getLogger("ambivo-mcp")
        logger.setLevel(getattr(logging, self.log_level.upper()))

        # Add console handler if logging to file
        if self.log_file:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter(self.log_format)
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

        return logger

    def validate(self) -> None:
        """Validate configuration settings"""
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")

        if self.max_retries < 0:
            raise ValueError("Max retries must be non-negative")

        if self.rate_limit_requests <= 0:
            raise ValueError("Rate limit requests must be positive")

        if self.rate_limit_window <= 0:
            raise ValueError("Rate limit window must be positive")

        if self.max_query_length <= 0:
            raise ValueError("Max query length must be positive")

        if self.max_payload_size <= 0:
            raise ValueError("Max payload size must be positive")

        if not self.base_url.startswith(("http://", "https://")):
            raise ValueError("Base URL must start with http:// or https://")


def load_config(config_path: Optional[str] = None) -> ServerConfig:
    """
    Load configuration from file or environment variables

    Args:
        config_path: Optional path to configuration file

    Returns:
        ServerConfig instance
    """
    if config_path and os.path.exists(config_path):
        config = ServerConfig.from_file(config_path)
    else:
        config = ServerConfig.from_env()

    config.validate()
    return config
