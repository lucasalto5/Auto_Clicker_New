const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let overlayWindow;
let backendProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1000, // Aumentado para não cortar o menu (presets novos ocupam espaço)
    height: 120,
    frame: false,
    transparent: true,
    resizable: false,
    alwaysOnTop: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true // Necessário em algumas versões do Electron para IPC
    },
    backgroundColor: '#00000000',
    icon: path.join(__dirname, 'icon.ico')
  });

  // Position at the top center
  mainWindow.center();
  const bounds = mainWindow.getBounds();
  mainWindow.setBounds({ x: bounds.x, y: 10 }); // 10px from top

  mainWindow.loadFile('index.html');

  // Create overlay window for points
  createOverlayWindow();

  // Start persistent Python backend
  startPythonBackend();

  // Window Controls
  ipcMain.on('window-min', () => mainWindow.minimize());
  ipcMain.on('window-close', () => {
    if (backendProcess) backendProcess.kill();
    app.quit();
  });

  // Settings
  ipcMain.on('set-always-on-top', (event, value) => {
    mainWindow.setAlwaysOnTop(value, 'screen-saver'); // 'screen-saver' é mais agressivo para ficar no topo
  });

  // Resize window to keep top position fixed
  ipcMain.on('resize-window', (event, { width, height }) => {
    const bounds = mainWindow.getBounds();
    mainWindow.setBounds({
      x: bounds.x,
      y: bounds.y, // Mantém a posição Y no monitor
      width: width,
      height: height + 50 // Adiciona uma margem de segurança
    }, true);
  });

  ipcMain.on('update-overlay-points', (event, points) => {
    console.log("Main received points for overlay:", points.length);
    if (overlayWindow && !overlayWindow.isDestroyed()) {
      overlayWindow.webContents.send('update-points', points);
    } else {
      console.log("Overlay window not ready, recreating...");
      createOverlayWindow();
      // Wait for it to load before sending
      overlayWindow.webContents.once('did-finish-load', () => {
        overlayWindow.webContents.send('update-points', points);
      });
    }
  });

  ipcMain.on('remove-point-index', (event, index) => {
    if (mainWindow) {
      mainWindow.webContents.send('point-removed-from-overlay', index);
    }
  });
}

function createOverlayWindow() {
  overlayWindow = new BrowserWindow({
    width: 1920, // Should cover full screen
    height: 1080,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    skipTaskbar: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
    pointerEvents: 'none'
  });
  
  overlayWindow.setIgnoreMouseEvents(true, { forward: true });
  overlayWindow.maximize();
  overlayWindow.loadFile('overlay.html');

  ipcMain.on('set-overlay-ignore-mouse', (event, ignore) => {
    if (overlayWindow) {
      overlayWindow.setIgnoreMouseEvents(ignore, { forward: true });
    }
  });
}

function startPythonBackend() {
    if (backendProcess) backendProcess.kill();

    const isPackaged = app.isPackaged;

    if (isPackaged) {
        // No build final, o backend.exe está na pasta resources
        const backendPath = path.join(process.resourcesPath, 'backend.exe');
        console.log('Production: Running backend from', backendPath);
        backendProcess = spawn(backendPath, [], { stdio: ['pipe', 'pipe', 'pipe'] });
    } else {
        console.log('Development: Running backend from python script');
        backendProcess = spawn('python', ['-u', path.join(__dirname, 'backend.py')], { stdio: ['pipe', 'pipe', 'pipe'] });
    }

    // Handle stdout from Python (our JSON messages)
    backendProcess.stdout.on('data', (data) => {
        const lines = data.toString().split('\n');
        for (const line of lines) {
            if (line.trim()) {
                try {
                    const message = JSON.parse(line);
                    if (mainWindow && !mainWindow.isDestroyed()) {
                        mainWindow.webContents.send('python-message', message);
                    }
                } catch (e) {
                    console.log('Non-JSON output from backend:', line);
                }
            }
        }
    });

    backendProcess.stderr.on('data', (data) => {
        console.error('Backend Error:', data.toString());
        if (mainWindow && !mainWindow.isDestroyed()) {
            mainWindow.webContents.send('python-error', data.toString());
        }
    });

    backendProcess.on('close', (code) => {
        console.log(`Backend process exited with code ${code}`);
    });
}

// IPC communication
ipcMain.on('update-config', (event, config) => {
    if (backendProcess && backendProcess.stdin) {
        backendProcess.stdin.write(JSON.stringify({ type: 'update_config', value: config }) + '\n');
    }
});

ipcMain.on('start-clicking', () => {
    if (backendProcess && backendProcess.stdin) {
        backendProcess.stdin.write(JSON.stringify({ type: 'start' }) + '\n');
    }
});

ipcMain.on('stop-clicking', () => {
    if (backendProcess && backendProcess.stdin) {
        backendProcess.stdin.write(JSON.stringify({ type: 'stop' }) + '\n');
    }
});

ipcMain.on('request-position-pick', (event, mode = 'single') => {
    if (backendProcess && backendProcess.stdin) {
        backendProcess.stdin.write(JSON.stringify({ type: 'pick_position', value: mode }) + '\n');
    }
});

ipcMain.on('stop-position-pick', (event) => {
    if (backendProcess && backendProcess.stdin) {
        backendProcess.stdin.write(JSON.stringify({ type: 'stop_pick_position' }) + '\n');
    }
});

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    if (backendProcess) backendProcess.kill();
    app.quit();
  }
});
