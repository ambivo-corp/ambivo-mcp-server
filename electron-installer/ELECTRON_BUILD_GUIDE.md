# Electron Build Guide for Ambivo MCP Server

## Prerequisites

1. **Node.js** (v16 or higher)
   - Download from: https://nodejs.org/

2. **Your Logo Files** in `assets/` folder:
   - `icon.png` - 512x512px PNG
   - `icon.icns` - macOS icon (convert from PNG)
   - `icon.ico` - Windows icon (convert from PNG)

## Build Instructions

### Step 1: Navigate to Electron Installer Directory
```bash
cd electron-installer
```

### Step 2: Install Dependencies
```bash
npm install
```

### Step 3: Build for All Platforms
```bash
# Build for both Mac and Windows
npm run build

# Or build for specific platforms:
npm run build-mac    # Mac only
npm run build-win    # Windows only
```

### Step 4: Find Your Installers
After building, your installers will be in the `dist/` folder:
```
dist/
├── Ambivo-for-Claude-Mac.dmg       # Mac installer (consistent name)
├── Ambivo-for-Claude-Windows.exe   # Windows installer (consistent name)
└── [other build artifacts]
```

## Complete Build Process from Scratch

```bash
# 1. Clone or navigate to your project
cd /path/to/ambivo-mcp-server

# 2. Go to electron installer directory
cd electron-installer

# 3. Add your logo files (if not already added)
# Put these in the assets/ folder:
# - icon.png (512x512)
# - icon.icns (for Mac)
# - icon.ico (for Windows)

# 4. Install dependencies
npm install

# 5. Build installers
npm run build

# 6. Your installers are ready in dist/ with consistent names
ls -la dist/Ambivo-for-Claude-*.dmg dist/Ambivo-for-Claude-*.exe
```

## Building for Different Architectures

### For Apple Silicon Macs (M1/M2/M3):
```bash
npm run build -- --mac --arm64
```

### For Intel Macs:
```bash
npm run build -- --mac --x64
```

### For Both Mac Architectures:
```bash
npm run build -- --mac --universal
```

### For Windows 64-bit:
```bash
npm run build -- --win --x64
```

## Customizing Your Build

### Change App Name or Version:
Edit `package.json`:
```json
{
  "name": "ambivo-claude-installer",
  "version": "1.0.1",  // Change version here
  "build": {
    "productName": "Ambivo for Claude",  // Change display name here
  }
}
```

### Change App ID:
Edit `package.json`:
```json
{
  "build": {
    "appId": "com.yourcompany.ambivo-claude",  // Change app ID here
  }
}
```

## Files to Upload to Your Website

After building, upload these files:

### Primary Downloads (Required):

1. **Mac Installer**: `Ambivo-for-Claude-Mac.dmg`
   - For Mac users (universal installer)
   - Ready to upload - no renaming needed!

2. **Windows Installer**: `Ambivo-for-Claude-Windows.exe`
   - For all Windows users
   - Ready to upload - no renaming needed!

### Optional Files (for auto-updates):

3. **Mac Blockmap**: `Ambivo-for-Claude-Mac.dmg.blockmap`
   - Enables delta updates (smaller update downloads)

4. **Windows Blockmap**: `Ambivo-for-Claude-Windows.exe.blockmap`
   - Enables delta updates for Windows

## Troubleshooting

### "npm: command not found"
- Install Node.js from https://nodejs.org/

### "Cannot find module 'electron-builder'"
```bash
npm install --save-dev electron-builder
```

### Build fails on Mac
- Make sure you have Xcode Command Line Tools:
```bash
xcode-select --install
```

### Build fails on Windows
- Run as Administrator
- Install Windows Build Tools:
```bash
npm install --global windows-build-tools
```

## Testing Your Installer

1. **Test Mac Installer**:
   - Double-click the .dmg file
   - Drag app to Applications
   - Run and test all steps

2. **Test Windows Installer**:
   - Double-click the .exe file
   - Follow installation wizard
   - Run and test all steps

## Publishing Updates

When you release a new version:

1. Update version in `package.json`
2. Rebuild: `npm run build`
3. Upload new installers to your website
4. Keep old versions available for compatibility

## Website Download Page Example:

```html
<div class="download-section">
  <h2>Download Ambivo for Claude</h2>
  
  <div class="download-buttons">
    <a href="/downloads/Ambivo-for-Claude-Mac.dmg" class="download-btn mac">
      <i class="fab fa-apple"></i>
      Download for Mac
      <span class="size">~95 MB</span>
    </a>
    
    <a href="/downloads/Ambivo-for-Claude-Windows.exe" class="download-btn windows">
      <i class="fab fa-windows"></i>
      Download for Windows
      <span class="size">~85 MB</span>
    </a>
  </div>
  
  <p class="requirements">
    Requires: Claude Desktop and Python 3.11+ (Recommended: Python 3.12)
  </p>
</div>
```

## Quick Reference Commands

```bash
# Navigate to installer
cd electron-installer

# Install dependencies
npm install

# Build all platforms
npm run build

# Build Mac only
npm run build-mac

# Build Windows only
npm run build-win

# Clean build artifacts
rm -rf dist/

# Test locally without building
npm start
```