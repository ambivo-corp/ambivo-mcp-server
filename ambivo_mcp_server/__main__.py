#!/usr/bin/env python3
"""
Entry point for running ambivo-mcp-server as a module.
Supports: python -m ambivo_mcp_server
"""

from .server import run_server as main

if __name__ == "__main__":
    main()