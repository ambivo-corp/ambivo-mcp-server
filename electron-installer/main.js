const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');
const os = require('os');

let mainWindow;
let detectedPythonCommand = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 600,
    height: 700,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    },
    icon: path.join(__dirname, 'assets', 'icon.png'),
    resizable: false
  });

  mainWindow.loadFile('index.html');
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Get Claude config path
function getClaudeConfigPath() {
  if (process.platform === 'darwin') {
    return path.join(os.homedir(), 'Library', 'Application Support', 'Claude', 'claude_desktop_config.json');
  } else if (process.platform === 'win32') {
    return path.join(process.env.APPDATA, 'Claude', 'claude_desktop_config.json');
  }
}

// Check if Python is installed and version
ipcMain.handle('check-python', async () => {
  return new Promise((resolve) => {
    let debugInfo = [];
    
    // First, let's gather diagnostic information
    const diagnosticCommands = [];
    
    if (process.platform === 'darwin') {
      diagnosticCommands.push(
        'which python3',
        'which python',
        'ls /usr/bin/python*',
        'ls /usr/local/bin/python*',
        'ls /opt/homebrew/bin/python*',
        'ls /Library/Frameworks/Python.framework/Versions/*/bin/python*'
      );
    } else if (process.platform === 'win32') {
      diagnosticCommands.push(
        'where python',
        'where python3',
        'py -0'
      );
    }
    
    // Run diagnostics first
    let diagnosticCount = 0;
    const runDiagnostics = () => {
      if (diagnosticCount >= diagnosticCommands.length) {
        // Now try actual Python commands
        tryPythonCommands();
        return;
      }
      
      const diagCmd = diagnosticCommands[diagnosticCount];
      diagnosticCount++;
      
      exec(diagCmd, { timeout: 2000 }, (error, stdout, stderr) => {
        if (!error && stdout.trim()) {
          debugInfo.push(`${diagCmd}: ${stdout.trim()}`);
        }
        runDiagnostics();
      });
    };
    
    const tryPythonCommands = () => {
      const pythonCommands = [];
      
      if (process.platform === 'win32') {
        pythonCommands.push(
          'python',
          'python3',
          'py -3',
          'py -3.12',
          'py -3.11',
          '"C:\\Program Files\\Python312\\python.exe"',
          '"C:\\Program Files\\Python311\\python.exe"',
          '"C:\\Users\\%USERNAME%\\AppData\\Local\\Programs\\Python\\Python312\\python.exe"',
          '"C:\\Users\\%USERNAME%\\AppData\\Local\\Programs\\Python\\Python311\\python.exe"'
        );
      } else if (process.platform === 'darwin') {
        // Prioritize newer Python versions first
        pythonCommands.push(
          '/Library/Frameworks/Python.framework/Versions/3.12/bin/python3',
          '/opt/homebrew/bin/python3.12',
          '/usr/local/bin/python3.12',
          '/Library/Frameworks/Python.framework/Versions/3.11/bin/python3',
          '/opt/homebrew/bin/python3.11',
          '/usr/local/bin/python3.11',
          '/Library/Frameworks/Python.framework/Versions/Current/bin/python3',
          '/opt/homebrew/bin/python3',
          '/usr/local/bin/python3',
          '/usr/bin/python3',
          'python3',
          'python'
        );
        
        // Add any python3 executables found in diagnostics
        debugInfo.forEach(info => {
          if (info.includes('python3') && info.includes('/')) {
            const paths = info.split(':')[1]?.trim().split('\n') || [];
            paths.forEach(path => {
              if (path.trim() && !pythonCommands.includes(path.trim())) {
                pythonCommands.push(path.trim());
              }
            });
          }
        });
      } else {
        pythonCommands.push('python3', 'python');
      }
      
      const timeout = setTimeout(() => {
        resolve({ 
          installed: false, 
          version: null, 
          error: 'timeout checking all Python locations',
          debugInfo: debugInfo
        });
      }, 15000); // 15 second timeout
      
      let attemptIndex = 0;
      
      function tryNextCommand() {
        if (attemptIndex >= pythonCommands.length) {
          clearTimeout(timeout);
          resolve({ 
            installed: false, 
            version: null, 
            error: 'no valid Python found in any location',
            debugInfo: debugInfo,
            triedCommands: pythonCommands
          });
          return;
        }
        
        const cmd = pythonCommands[attemptIndex];
        attemptIndex++;
        
        exec(`${cmd} --version`, { timeout: 3000 }, (error, stdout, stderr) => {
          if (error) {
            debugInfo.push(`FAILED: ${cmd} (${error.message})`);
            tryNextCommand();
          } else {
            const versionMatch = stdout.match(/Python (\d+)\.(\d+)\.(\d+)/);
            if (versionMatch) {
              const major = parseInt(versionMatch[1]);
              const minor = parseInt(versionMatch[2]);
              detectedPythonCommand = cmd;
              clearTimeout(timeout);
              debugInfo.push(`SUCCESS: ${cmd} -> ${stdout.trim()}`);
              resolve({ 
                installed: true, 
                version: `${major}.${minor}`,
                versionString: stdout.trim(),
                isValid: major === 3 && minor >= 11,
                command: cmd,
                debugInfo: debugInfo
              });
            } else {
              debugInfo.push(`INVALID VERSION: ${cmd} -> ${stdout.trim()}`);
              tryNextCommand();
            }
          }
        });
      }
      
      tryNextCommand();
    };
    
    runDiagnostics();
  });
});

// Install the MCP server
ipcMain.handle('install-server', async () => {
  return new Promise((resolve, reject) => {
    // Use the Python command that was detected during the check
    let pythonCmd = detectedPythonCommand || (process.platform === 'win32' ? 'python' : 'python3');
    
    exec(`${pythonCmd} -m pip install ambivo-mcp-server`, (error, stdout, stderr) => {
      if (error) {
        reject(`Installation failed with ${pythonCmd}: ${error.message}`);
      } else {
        resolve('Installation successful');
      }
    });
  });
});

// Configure Claude
ipcMain.handle('configure-claude', async (event, token) => {
  try {
    const configPath = getClaudeConfigPath();
    const configDir = path.dirname(configPath);
    
    // Create directory if it doesn't exist
    if (!fs.existsSync(configDir)) {
      fs.mkdirSync(configDir, { recursive: true });
    }
    
    // Read existing config or create new one
    let config = {};
    if (fs.existsSync(configPath)) {
      try {
        config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      } catch (e) {
        // Invalid JSON, start fresh
        config = {};
      }
    }
    
    // Add our server configuration
    if (!config.mcpServers) {
      config.mcpServers = {};
    }
    
    config.mcpServers.ambivo = {
      command: detectedPythonCommand || (process.platform === 'win32' ? 'python' : 'python3'),
      args: ['-m', 'ambivo-mcp-server'],
      env: {
        AMBIVO_AUTH_TOKEN: token
      }
    };
    
    // Write the config
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
    
    return 'Configuration successful';
  } catch (error) {
    throw error.message;
  }
});

// Get app version
ipcMain.handle('get-version', async () => {
  const packageJson = require('./package.json');
  return packageJson.version;
});

// Restart the app
ipcMain.handle('restart-app', async () => {
  app.relaunch();
  app.exit();
});

// Open external links
ipcMain.handle('open-external', async (event, url) => {
  require('electron').shell.openExternal(url);
});

// Download and install Python
ipcMain.handle('install-python', async () => {
  return new Promise((resolve, reject) => {
    const platform = process.platform;
    let downloadUrl;
    
    if (platform === 'darwin') {
      // Mac - download universal installer for Python 3.12
      downloadUrl = 'https://www.python.org/ftp/python/3.12.7/python-3.12.7-macos11.pkg';
    } else if (platform === 'win32') {
      // Windows - download 64-bit installer for Python 3.12
      downloadUrl = 'https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe';
    } else {
      reject('Unsupported platform for auto-install');
      return;
    }
    
    // Open the download URL
    require('electron').shell.openExternal(downloadUrl);
    resolve(`Python 3.12 installer downloaded. Please run it, then click "Recheck Python" below.

IMPORTANT: After installing Python, you may need to restart this installer or your terminal for the new Python version to be detected.`);
  });
});