# Ambivo MCP Server Installer for Windows
Write-Host "🚀 Installing Ambivo MCP Server for Claude Desktop..." -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed. Please install Python from python.org" -ForegroundColor Red
    exit 1
}

# Install the package
Write-Host "📦 Installing ambivo-mcp-server..." -ForegroundColor Yellow
python -m pip install --user ambivo-mcp-server

# Create Claude config directory if it doesn't exist
$claudeDir = "$env:APPDATA\Claude"
if (!(Test-Path $claudeDir)) {
    New-Item -ItemType Directory -Path $claudeDir | Out-Null
}

# Configure Claude
$configFile = "$claudeDir\claude_desktop_config.json"
$config = @{
    mcpServers = @{
        ambivo = @{
            command = "python"
            args = @("-m", "ambivo-mcp-server")
            env = @{
                AMBIVO_AUTH_TOKEN = "REPLACE_WITH_YOUR_TOKEN"
            }
        }
    }
} | ConvertTo-Json -Depth 4

if (Test-Path $configFile) {
    Write-Host "⚠️  Config file exists. Add this to your mcpServers:" -ForegroundColor Yellow
    Write-Host $config
} else {
    $config | Out-File -FilePath $configFile -Encoding UTF8
    Write-Host "✅ Configuration created!" -ForegroundColor Green
}

Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Cyan
Write-Host "1. Open $configFile"
Write-Host "2. Replace 'REPLACE_WITH_YOUR_TOKEN' with your Ambivo JWT token"
Write-Host "3. Restart Claude Desktop"
Write-Host ""
Write-Host "🎉 Then try: 'Show me leads created this week' in Claude!" -ForegroundColor Green