#!/bin/bash
# Ambivo MCP Server Installer for macOS

echo "🚀 Installing Ambivo MCP Server for Claude Desktop..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python from python.org"
    exit 1
fi

# Install the package
echo "📦 Installing ambivo-mcp-server..."
python3 -m pip install --user ambivo-mcp-server

# Create Claude config directory if it doesn't exist
mkdir -p "$HOME/Library/Application Support/Claude"

# Check if config file exists
CONFIG_FILE="$HOME/Library/Application Support/Claude/claude_desktop_config.json"

if [ -f "$CONFIG_FILE" ]; then
    echo "⚠️  Claude config file already exists. Please add the following to your mcpServers section:"
else
    echo "✏️  Creating Claude configuration..."
    cat > "$CONFIG_FILE" << EOF
{
  "mcpServers": {
    "ambivo": {
      "command": "python3",
      "args": ["-m", "ambivo-mcp-server"],
      "env": {
        "AMBIVO_AUTH_TOKEN": "REPLACE_WITH_YOUR_TOKEN"
      }
    }
  }
}
EOF
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "📝 Next steps:"
echo "1. Open $CONFIG_FILE"
echo "2. Replace 'REPLACE_WITH_YOUR_TOKEN' with your Ambivo JWT token"
echo "3. Restart Claude Desktop"
echo ""
echo "🎉 Then try: 'Show me leads created this week' in Claude!"