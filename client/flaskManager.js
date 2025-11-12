
const { spawn } = require('child_process');
const fs = require('fs');
const axios = require('axios');
const extract = require('extract-zip');
const path = require('path')


let updateServer = 'http://log-analyzer-web.myhexin.com'; // 默认更新服务器

// Flask应用管理
class FlaskAppManager {
  static flaskProcess = null;
  constructor() {
    // 使用Electron打包后的resources/flask目录
    this.flaskAppDir = path.join(process.resourcesPath, 'flask_app', 'app');
    this.currentVersionFile = path.join(path.join(process.resourcesPath, 'flask_app'), 'flask-version.json');
  }

  // 检查Flask应用是否存在
  async checkFlaskAppExists() {
    const flaskApp = path.join(this.flaskAppDir, 'app.py');
    return fs.existsSync(flaskApp);
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

      // 在更新之前先停止Flask进程
      if (FlaskAppManager.flaskProcess && !FlaskAppManager.flaskProcess.killed) {
        console.log('Stopping Flask process for update...');
        FlaskAppManager.flaskProcess.kill('SIGTERM');
        
        // 等待进程完全停止
        await new Promise((resolve) => {
          if (FlaskAppManager.flaskProcess) {
            FlaskAppManager.flaskProcess.on('exit', resolve);
            // 如果5秒后进程仍未退出，强制终止
            setTimeout(() => {
              if (FlaskAppManager.flaskProcess && !FlaskAppManager.flaskProcess.killed) {
                FlaskAppManager.flaskProcess.kill('SIGKILL');
              }
              resolve();
            }, 5000);
          } else {
            resolve();
          }
        });
      }
      
      // 通过接口获取最新版本信息
      const versionInfo = await this.getAvailableVersion();
      if (!versionInfo) {
        throw new Error('Failed to get version information');
      }
      // 通过接口下载Flask应用压缩包
      const response = await axios.get(`${updateServer}/updates/flask/download`, {
        responseType: 'stream',
        timeout: 300000 // 5分钟超时
      });

      if (response.status !== 200) {
        throw new Error(`Download failed with status: ${response.status}`);
      }

      // 获取文件总大小（用于进度显示）
      const totalSize = parseInt(response.headers['content-length'], 10);
      let downloadedSize = 0;

      // 下载到临时zip文件
      const tempZipPath = path.join(process.resourcesPath, `flask_app_temp_${Date.now()}.zip`);
      console.log('tempZipPath: ', tempZipPath)
      const writer = fs.createWriteStream(tempZipPath);

      // 添加进度监听
      response.data.on('data', (chunk) => {
        downloadedSize += chunk.length;
        if (totalSize) {
          const progress = (downloadedSize / totalSize) * 100;
          console.log('downloading... ', progress);
        }
      });

      await new Promise((resolve, reject) => {
        response.data.pipe(writer);
        writer.on('finish', resolve);
        writer.on('error', reject);
      });

      // 创建解压目录
      const extractDir = path.join(process.resourcesPath, 'flask_app');
      if (fs.existsSync(extractDir)) {
        // 清空现有目录
        fs.rmSync(extractDir, { recursive: true, force: true });
      }
      fs.mkdirSync(extractDir, { recursive: true });

      // 解压zip文件
      console.log('extracting... ', 0);
      
      await extract(tempZipPath, { 
        dir: extractDir,
        onEntry: (entry, zipfile) => {
          const progress = (zipfile.entriesRead / zipfile.entryCount) * 100;
          console.log('extracting... ', progress);
        }
      });

      console.log('extracting... ', 100);

      // 清理临时zip文件
      fs.unlinkSync(tempZipPath);

      // 验证解压后的文件结构
      const appDir = path.join(extractDir, 'app');
      const staticDir = path.join(extractDir, 'static');

      if (!fs.existsSync(appDir) || !fs.existsSync(staticDir)) {
        throw new Error('解压后的文件结构不正确');
      }

      console.log('Flask应用下载并解压完成');
      console.log('应用目录:', extractDir);

      // 创建或更新本地版本文件
      const localVersionInfo = {
        version: versionInfo.version,
        download_time: new Date().toISOString(),
        source: 'api'
      };
      
      fs.writeFileSync(this.currentVersionFile, JSON.stringify(localVersionInfo, null, 2));
      
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
      console.error('Failed to check for updates:', error.message);
      return false;
    }
  }

  // 启动Flask应用
  async startFlaskApp() {
    try {
      await axios.get('http://127.0.0.1:5000/readiness', { timeout: 3000 })
      return
    } catch {
      console.log('Flask app is not started, starting...')
    }
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
      const flaskApp = path.join(this.flaskAppDir, 'app.py');
      console.log('flask app path: ', flaskApp)
      if (!fs.existsSync(flaskApp)) {
        throw new Error('Flask executable not found');
      }

      console.log('Starting Flask app...',);
      FlaskAppManager.flaskProcess = spawn('python', [flaskApp], {
        cwd: this.flaskAppDir,
        stdio: 'pipe',
        env: { ...process.env, FLASK_ENV: 'production' },
        detached: false
      });

      FlaskAppManager.flaskProcess.stdout.on('data', (data) => {
        console.log('Flask:', data.toString());
      });

      FlaskAppManager.flaskProcess.stderr.on('data', (data) => {
        console.error('Flask:', data.toString());
      });

      FlaskAppManager.flaskProcess.on('close', (code) => {
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
      if (FlaskAppManager.flaskProcess && !FlaskAppManager.flaskProcess.killed) {
        FlaskAppManager.flaskProcess.kill('SIGTERM');
        
        // 等待进程完全停止
        await new Promise((resolve) => {
          if (FlaskAppManager.flaskProcess) {
            FlaskAppManager.flaskProcess.on('exit', resolve);
            // 如果5秒后进程仍未退出，强制终止
            setTimeout(() => {
              if (FlaskAppManager.flaskProcess && !FlaskAppManager.flaskProcess.killed) {
                FlaskAppManager.flaskProcess.kill('SIGKILL');
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

// 检查Flask应用是否启动成功
function waitForFlaskApp() {
  return new Promise((resolve) => {
    let attempts = 0;
    const maxAttempts = 60; // 最多等待60次
    
    const checkFlask = () => {
      attempts++;
      
      // 尝试连接Flask应用
      axios.get('http://127.0.0.1:5000/readiness', { timeout: 3000 })
        .then(() => {
          console.log('Flask app is ready!');
          resolve(true);
        })
        .catch((e) => {
          if (attempts < maxAttempts) {
            console.log(`Waiting for Flask app... (${attempts}/${maxAttempts})`);
            setTimeout(checkFlask, 3000);
          } else {
            console.error('Flask app failed to start within timeout');
            resolve(false);
          }
        });
    };
    
    checkFlask();
  });
}

module.exports = {
  FlaskAppManager,
  waitForFlaskApp,
  updateServer
}
