#!/bin/bash
# Railway start script for MCP server

# Print current directory for debugging
echo "Current directory: $(pwd)"
echo "Contents of current directory:"
ls -la

# Check if the MCP server exists
if [ -f "ambivo_mcp_server/server.py" ]; then
    echo "Found MCP server, starting..."
    python -m ambivo_mcp_server --host 0.0.0.0 --port ${PORT:-8080}
else
    echo "ERROR: Cannot find ambivo_mcp_server/server.py"
    echo "Looking for Python files:"
    find . -name "*.py" -type f | head -20
    exit 1
fi