#!/bin/bash
# Build script for Ambivo Claude Installer

echo "🏗️  Building Ambivo for Claude installer..."

# Install dependencies
npm install

# Create assets directory
mkdir -p assets

# Create a simple icon (you should replace with your actual logo)
echo "📦 Note: Add your logo as assets/icon.png (512x512px)"
echo "📦 Note: Add your logo as assets/icon.icns (for Mac)"
echo "📦 Note: Add your logo as assets/icon.ico (for Windows)"

# Build for all platforms
npm run build

echo "✅ Build complete! Check the 'dist' folder for installers:"
echo "  - Mac: Ambivo for Claude.dmg"
echo "  - Windows: Ambivo for Claude Setup.exe"