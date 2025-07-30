#!/usr/bin/env python3
"""
Ambivo GPT Actions - ChatGPT Integration Module
Standalone GPT Actions for ChatGPT without requiring Tornado server
"""

from .server import GPTActionsServer
from .schema_generator import generate_openapi_schema
from .cli import main

__version__ = "1.0.0"
__all__ = ["GPTActionsServer", "generate_openapi_schema", "main"]