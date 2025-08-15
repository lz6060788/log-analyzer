const { app, BrowserWindow, ipcMain, dialog, session } = require('electron');
const { globalShortcut } = require('electron')
// const { autoUpdater } = require('electron-updater');
const path = require('path');
const {
  FlaskAppManager,
  waitForFlaskApp,
} = require('./flaskManager')
const {
  checkStatus,
  checkPythonEnvironment,
} = require('./checkPython')

let mainWindow;

// 创建Flask应用管理器实例
const flaskManager = new FlaskAppManager();


// 创建主窗口
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
    },
    icon: path.join(__dirname, 'assets', 'icon.png')
  });

  // 加载前端页面
  mainWindow.loadFile('init.html');

  // 启动时检查Python环境
  checkPythonEnvironment(mainWindow).then(async (success) => {
    if (!success) {
      // 如果检查失败，5秒后退出应用
      setTimeout(() => {
        app.quit();
      }, 5000);
    } else {
      // 启动Flask应用
      try {
        if (await flaskManager.startFlaskApp()) {
          console.log('Flask app starting...');
        } else {
          console.log('Failed to start Flask app');
          dialog.showErrorBox('Error', 'Failed to start Flask application. Please check the console for details.');
        }
      } catch (error) {
        console.error('Error starting Flask app:', error);
        dialog.showErrorBox('Error', `Failed to start Flask application: ${error.message}`);
      }
      // 等待Flask应用启动后加载页面
      waitForFlaskApp().then((success) => {
        if (success) {
          // 加载Flask应用页面
          mainWindow.loadURL('http://127.0.0.1:5000/');
          if (!app.isPackaged) {
            mainWindow.webContents.toggleDevTools()
          }
          console.log('Loaded Flask app successfully');
        } else {
          // 如果Flask启动失败，显示错误页面
          mainWindow.loadFile(path.join(__dirname, 'error.html'));
          dialog.showErrorBox('Error', 'Failed to start Flask application. Please check the console for details.');
        }
      });
    }
  }).catch((e) => {
    dialog.showErrorBox('Error', e);
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// 应用准备就绪
app.whenReady().then(async () => {
  // 注册控制台快捷键
  globalShortcut.register('CommandOrControl+Shift+I', () => {
    const win = BrowserWindow.getFocusedWindow()
    if (win) win.webContents.toggleDevTools()
  })
  
  createWindow();

});

// 应用事件处理
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

app.on('quit', (event) => {
  // 关闭Flask进程
  if (FlaskAppManager.flaskProcess) {
    FlaskAppManager.flaskProcess.kill('SIGTERM');
  }
});

// 处理开发模式下的中断信号 (如 Ctrl+C)
process.on('SIGINT', () => {
  app.quit();
});

process.on('SIGTERM', () => {
  app.quit();
});

// 处理前端请求状态更新
ipcMain.on('request-python-status', (event) => {
  event.reply('python-check-status', { ...checkStatus });
});
