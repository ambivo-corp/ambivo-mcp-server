"""
Ambivo MCP Server

A Model Context Protocol (MCP) server for Ambivo API endpoints.
Provides natural language query capabilities and direct entity data access.
"""

__version__ = "1.0.0"
__author__ = "Ambivo Development Team"
__email__ = "dev@ambivo.com"

from .server import run_server as main

__all__ = ["main"]