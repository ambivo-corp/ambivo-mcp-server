# Easy Installation Guide for Ambivo MCP Server

## 🎯 For Non-Technical Users

### Option 1: One-Click Installer (Recommended)

#### macOS:
1. Download our installer: [install_mac.sh](installer/install_mac.sh)
2. Double-click the downloaded file
3. Follow the prompts
4. Enter your Ambivo JWT token when asked
5. Restart Claude Desktop

#### Windows:
1. Download our installer: [install_windows.ps1](installer/install_windows.ps1)
2. Right-click and select "Run with PowerShell"
3. Follow the prompts
4. Enter your Ambivo JWT token when asked
5. Restart Claude Desktop

### Option 2: Copy-Paste Installation

#### Step 1: Open Terminal (Mac) or Command Prompt (Windows)
- **Mac**: Press `Cmd+Space`, type "Terminal", press Enter
- **Windows**: Press `Win+R`, type "cmd", press Enter

#### Step 2: Copy and paste this command:
```bash
# For Mac:
python3 -m pip install ambivo-mcp-server

# For Windows:
python -m pip install ambivo-mcp-server
```

#### Step 3: Configure Claude Desktop
1. Find your Claude Desktop config file:
   - **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add this configuration (replace YOUR_TOKEN_HERE):

💡 **TIP**: You can use either `ambivo_mcp_server` (underscore) or `ambivo-mcp-server` (dash) - both work!
```json
{
  "mcpServers": {
    "ambivo": {
      "command": "python3",
      "args": ["-m", "ambivo_mcp_server"],
      "env": {
        "AMBIVO_AUTH_TOKEN": "YOUR_TOKEN_HERE"
      }
    }
  }
}
```

**Alternative configuration (also works):**
```json
{
  "mcpServers": {
    "ambivo": {
      "command": "python3",
      "args": ["-m", "ambivo-mcp-server"],
      "env": {
        "AMBIVO_AUTH_TOKEN": "YOUR_TOKEN_HERE"
      }
    }
  }
}
```

3. Save the file and restart Claude Desktop

## 🔑 Getting Your Ambivo JWT Token

1. Log into your Ambivo account
2. Go to https://account.ambivo.com/integrations
3. Generate or copy your JWT token
4. Keep it safe - it's like a password!

## 🎉 Testing Your Installation

In Claude Desktop, try these commands:
- "Show me all leads from this week"
- "Find contacts with gmail addresses"
- "List my top opportunities"

## ❓ Troubleshooting

### "Python not found" error
- Download Python from [python.org](https://python.org)
- During installation, check "Add Python to PATH"

### "pip not found" error
- Try: `python3 -m pip` instead of just `pip`
- Or: `py -m pip` on Windows

### "Server disconnected" or "Module not found" error
- **Check**: Make sure you have `python3` in your PATH
- **Check**: Verify the package is installed: `pip show ambivo-mcp-server`
- **Try**: Both `ambivo_mcp_server` and `ambivo-mcp-server` work as module names

### Claude doesn't recognize the commands
- Make sure you restarted Claude Desktop completely
- Check that your JWT token is correct
- Verify the config file is valid JSON

## 📞 Need Help?

- GitHub Issues: [github.com/ambivo-corp/ambivo-mcp-server/issues](https://github.com/ambivo-corp/ambivo-mcp-server/issues)
- Email: support@ambivo.com
- Documentation: [Full Technical Docs](README.md)