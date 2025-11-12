const { contextBridge, ipcRenderer } = require('electron');

// 暴露安全的API到渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
  // 获取Python检查状态
  getPythonStatus: () => {
    return new Promise((resolve) => {
      // 发送请求
      ipcRenderer.send('request-python-status');
      // 等待响应
      ipcRenderer.once('python-check-status', (event, status) => {
        resolve(status);
      });
    });
  },
  // 监听状态更新
  onPythonStatusUpdate: (callback) => {
    ipcRenderer.on('python-check-status', (event, status) => {
      callback(status);
    });
  },
  // 应用信息
  getVersion: () => process.versions.electron,
  getAppVersion: () => process.env.npm_package_version || '1.0.0',
  
  // 系统信息
  getPlatform: () => process.platform,
  getArch: () => process.arch,

  isProxyActive: () => true
});
