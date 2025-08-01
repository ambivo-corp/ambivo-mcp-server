#!/bin/bash
# Railway start script for test app

# Print current directory for debugging
echo "Current directory: $(pwd)"
echo "Contents of current directory:"
ls -la

# Check if the test app exists
if [ -f "ambivo_gpt_actions/test_app.py" ]; then
    echo "Found test_app.py, starting server..."
    python ambivo_gpt_actions/test_app.py --host 0.0.0.0 --port ${PORT:-8080}
else
    echo "ERROR: Cannot find ambivo_gpt_actions/test_app.py"
    echo "Looking for Python files:"
    find . -name "*.py" -type f | head -20
    exit 1
fi