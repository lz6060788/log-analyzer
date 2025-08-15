const { contextBridge, ipcRenderer } = require('electron');

// 暴露安全的API到渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
  // 更新相关API
  checkForUpdates: () => ipcRenderer.invoke('check-for-updates'),
  getUpdateStatus: () => ipcRenderer.invoke('get-update-status'),
  setUpdateServer: (serverUrl) => ipcRenderer.invoke('set-update-server', serverUrl),
  
  // 应用信息
  getVersion: () => process.versions.electron,
  getAppVersion: () => process.env.npm_package_version || '1.0.0',
  
  // 系统信息
  getPlatform: () => process.platform,
  getArch: () => process.arch
});
