const { app, BrowserWindow, ipcMain, dialog } = require('electron');
// const { autoUpdater } = require('electron-updater');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const axios = require('axios');
// const crypto = require('crypto');

let mainWindow;
let flaskProcess;
let updateServer = 'http://127.0.0.1:5000'; // 默认更新服务器

// Flask应用管理
class FlaskAppManager {
  constructor() {
    // 使用Electron打包后的resources/flask目录
    this.flaskAppDir = path.join(process.resourcesPath, 'flask');
    this.currentVersionFile = path.join(this.flaskAppDir, 'flask-version.json');
  }

  // 检查Flask应用是否存在
  async checkFlaskAppExists() {
    const flaskExe = path.join(this.flaskAppDir, 'flask_app.exe');
    return fs.existsSync(flaskExe);
  }

  // 获取当前Flask应用版本
  async getCurrentVersion() {
    try {
      if (fs.existsSync(this.currentVersionFile)) {
        const versionInfo = JSON.parse(fs.readFileSync(this.currentVersionFile, 'utf8'));
        return versionInfo.version;
      }
    } catch (error) {
      console.error('Failed to read current version:', error);
    }
    return null;
  }

  // 获取可用版本信息
  async getAvailableVersion() {
    try {
      // 通过接口获取最新版本信息
      const response = await axios.get(`${updateServer}/updates/flask/version`);
      if (response.status === 200) {
        return response.data;
      }
    } catch (error) {
      console.error('Failed to get available version from API:', error);
    }
    return null;
  }

  // 下载Flask应用
  async downloadFlaskApp() {
    try {
      // 确保目录存在
      if (!fs.existsSync(this.flaskAppDir)) {
        fs.mkdirSync(this.flaskAppDir, { recursive: true });
      }

      // 通过接口获取最新版本信息
      const versionInfo = await this.getAvailableVersion();
      if (!versionInfo) {
        throw new Error('Failed to get version information');
      }

      // 通过接口下载Flask应用
      const response = await axios.get(`${updateServer}/updates/flask/download`, {
        responseType: 'stream'
      });

      if (response.status !== 200) {
        throw new Error(`Download failed with status: ${response.status}`);
      }

      // 下载到临时文件
      const tempExePath = path.join(app.getPath('temp'), 'flask_app_temp.exe');
      const writer = fs.createWriteStream(tempExePath);
      
      response.data.pipe(writer);
      
      await new Promise((resolve, reject) => {
        writer.on('finish', resolve);
        writer.on('error', reject);
      });

      // 在更新之前先停止Flask进程
      if (flaskProcess && !flaskProcess.killed) {
        console.log('Stopping Flask process for update...');
        flaskProcess.kill('SIGTERM');
        
        // 等待进程完全停止
        await new Promise((resolve) => {
          if (flaskProcess) {
            flaskProcess.on('exit', resolve);
            // 如果5秒后进程仍未退出，强制终止
            setTimeout(() => {
              if (flaskProcess && !flaskProcess.killed) {
                flaskProcess.kill('SIGKILL');
              }
              resolve();
            }, 5000);
          } else {
            resolve();
          }
        });
      }

      // 使用更安全的文件替换方法
      const targetExe = path.join(this.flaskAppDir, 'flask_app.exe');
      const backupExe = path.join(this.flaskAppDir, 'flask_app_backup.exe');
      
      try {
        // 如果目标文件存在，先创建备份
        if (fs.existsSync(targetExe)) {
          // 删除旧的备份文件（如果存在）
          if (fs.existsSync(backupExe)) {
            fs.unlinkSync(backupExe);
          }
          // 重命名当前文件为备份
          fs.renameSync(targetExe, backupExe);
        }
        
        // 复制新文件到目标位置
        fs.copyFileSync(tempExePath, targetExe);
        
        // 删除备份文件
        if (fs.existsSync(backupExe)) {
          fs.unlinkSync(backupExe);
        }
        
        console.log('✅ Flask app updated successfully');
      } catch (error) {
        // 如果更新失败，尝试恢复备份
        console.error('Update failed, attempting to restore backup...', error);
        if (fs.existsSync(backupExe)) {
          if (fs.existsSync(targetExe)) {
            fs.unlinkSync(targetExe);
          }
          fs.renameSync(backupExe, targetExe);
        }
        throw error;
      }
      
      // 清理临时文件
      fs.unlinkSync(tempExePath);

      // 创建或更新本地版本文件
      const localVersionInfo = {
        version: versionInfo.version,
        download_time: new Date().toISOString(),
        source: 'api'
      };
      
      fs.writeFileSync(this.currentVersionFile, JSON.stringify(localVersionInfo, null, 2));
      
      // 如果Flask应用之前正在运行，则重新启动它
      if (flaskProcess && flaskProcess.killed === false) {
        console.log('Restarting Flask app after update...');
        await this.restartFlaskApp();
      }
      
      return true;
    } catch (error) {
      console.error('Failed to download Flask app:', error);
      return false;
    }
  }

  // 检查Flask应用更新
  async checkForUpdates() {
    try {
      const currentVersion = await this.getCurrentVersion();
      const availableVersion = await this.getAvailableVersion();
      
      if (!availableVersion) {
        console.log('No version information available');
        return false;
      }
      
      if (!currentVersion || currentVersion !== availableVersion.version) {
        console.log(`🆕 Flask update available: ${availableVersion.version}`);
        return availableVersion;
      }
      
      console.log('Flask app is up to date');
      return false;
    } catch (error) {
      console.error('Failed to check for updates:', error);
      return false;
    }
  }

  // 启动Flask应用
  async startFlaskApp() {
    try {
      // 检查Flask应用是否存在
      if (!(await this.checkFlaskAppExists())) {
        console.log('Flask app not found, downloading...');
        if (!(await this.downloadFlaskApp())) {
          throw new Error('Failed to download Flask app');
        }
      }

      // 检查更新
      const update = await this.checkForUpdates();
      if (update) {
        console.log('Updating Flask app...');
        if (!(await this.downloadFlaskApp())) {
          throw new Error('Failed to update Flask app');
        }
      }

      // 启动Flask应用
      const flaskExe = path.join(this.flaskAppDir, 'flask_app.exe');
      if (!fs.existsSync(flaskExe)) {
        throw new Error('Flask executable not found');
      }

      console.log('Starting Flask app...');
      flaskProcess = spawn(flaskExe, [], {
        cwd: this.flaskAppDir,
        stdio: 'pipe',
        env: { ...process.env, FLASK_ENV: 'production' }
      });

      flaskProcess.stdout.on('data', (data) => {
        console.log('Flask:', data.toString());
      });

      flaskProcess.stderr.on('data', (data) => {
        console.error('Flask:', data.toString());
      });

      flaskProcess.on('close', (code) => {
        console.log('Flask process exited with code:', code);
      });

      return true;
    } catch (error) {
      console.error('Failed to start Flask app:', error);
      return false;
    }
  }

  // 重启Flask应用
  async restartFlaskApp() {
    try {
      console.log('Restarting Flask app...');
      
      // 停止当前进程
      if (flaskProcess && !flaskProcess.killed) {
        flaskProcess.kill('SIGTERM');
        
        // 等待进程完全停止
        await new Promise((resolve) => {
          if (flaskProcess) {
            flaskProcess.on('exit', resolve);
            // 如果5秒后进程仍未退出，强制终止
            setTimeout(() => {
              if (flaskProcess && !flaskProcess.killed) {
                flaskProcess.kill('SIGKILL');
              }
              resolve();
            }, 5000);
          } else {
            resolve();
          }
        });
      }

      // 等待一段时间确保端口释放
      await new Promise(resolve => setTimeout(resolve, 2000));

      // 重新启动Flask应用
      return await this.startFlaskApp();
    } catch (error) {
      console.error('Failed to restart Flask app:', error);
      return false;
    }
  }
}

// 创建Flask应用管理器实例
const flaskManager = new FlaskAppManager();


// 检查Flask应用是否启动成功
function waitForFlaskApp() {
  return new Promise((resolve) => {
    let attempts = 0;
    const maxAttempts = 30; // 最多等待30秒
    
    const checkFlask = () => {
      attempts++;
      
      // 尝试连接Flask应用
      axios.get('http://127.0.0.1:5000/readiness', { timeout: 1000 })
        .then(() => {
          console.log('Flask app is ready!');
          resolve(true);
        })
        .catch(() => {
          if (attempts < maxAttempts) {
            console.log(`Waiting for Flask app... (${attempts}/${maxAttempts})`);
            setTimeout(checkFlask, 1000);
          } else {
            console.error('Flask app failed to start within timeout');
            resolve(false);
          }
        });
    };

    checkFlask();
  });
}

// 创建主窗口
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, 'assets', 'icon.png')
  });

  // 等待Flask应用启动后加载页面
  waitForFlaskApp().then((success) => {
    if (success) {
      // 加载Flask应用页面
      mainWindow.loadURL('http://127.0.0.1:5000');
      console.log('Loaded Flask app successfully');
    } else {
      // 如果Flask启动失败，显示错误页面
      mainWindow.loadFile(path.join(__dirname, 'error.html'));
      dialog.showErrorBox('Error', 'Failed to start Flask application. Please check the console for details.');
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// 应用准备就绪
app.whenReady().then(async () => {
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

app.on('before-quit', () => {
  // 关闭Flask进程
  if (flaskProcess) {
    flaskProcess.kill();
  }
});

