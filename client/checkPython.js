const { exec, execFile } = require('child_process')
const path = require('path')
const { existsSync, readFileSync } = require('fs')
const { app } = require('electron')

// 存储检查状态
let checkStatus = {
  hasPython: false,
  pythonVersion: '',
  dependencies: {
    installed: [],
    missing: [],
    installing: [],
    failed: []
  },
  overallStatus: 'initializing', // initializing, checking, installing, ready, error
  error: null
};

// 发送状态更新到前端
function sendStatusUpdate(window) {
  if (window && window.webContents) {
    window.webContents.send('python-check-status', { ...checkStatus });
  }
}

// 检查Python环境
async function checkPythonEnvironment(window) {
  checkStatus.overallStatus = 'checking';
  sendStatusUpdate(window);

  try {
    // 检查Python是否安装
    const pythonPath = await findPythonExecutable();
    if (!pythonPath) {
      throw new Error('未找到Python环境，请先安装Python');
    }
    
    checkStatus.hasPython = true;
    sendStatusUpdate(window);

    // 检查Python版本
    const versionOutput = await executePythonCommand(pythonPath, ['--version']);
    checkStatus.pythonVersion = parsePythonVersion(versionOutput.stderr || versionOutput.stdout);
    sendStatusUpdate(window);

    // 检查requirements.txt是否存在
    const requirementsPath = app.isPackaged ? path.join(process.resourcesPath, 'requirements.txt') : path.join('..', 'requirements.txt');
    if (!existsSync(requirementsPath)) {
      throw new Error('未找到requirements.txt文件');
    }

    // 读取依赖列表
    const requirementsContent = await readFileSync(requirementsPath, 'utf8');
    const dependencies = requirementsContent
      .split('\n')
      .map(line => line.trim())
      .filter(line => line && !line.startsWith('#'));

    // 检查每个依赖是否已安装
    await checkDependencies(pythonPath, dependencies, window);

    // 如果有缺失的依赖，进行安装
    if (checkStatus.dependencies.missing.length > 0) {
      checkStatus.overallStatus = 'installing';
      sendStatusUpdate(window);
      
      await installMissingDependencies(pythonPath, window);
    }

    checkStatus.overallStatus = 'ready';
    sendStatusUpdate(window);
    return true;

  } catch (error) {
    checkStatus.overallStatus = 'error';
    checkStatus.error = error.message;
    sendStatusUpdate(window);
    console.error('Python环境检查失败:', error);
    return false;
  }
}

// 查找Python可执行文件路径
function findPythonExecutable() {
  return new Promise((resolve) => {
    // 先尝试python3
    exec('python3 --version', (error) => {
      if (!error) {
        return resolve('python3');
      }
      
      // 再尝试python
      exec('python --version', (error) => {
        if (!error) {
          return resolve('python');
        }
        
        // Windows系统尝试py
        if (process.platform === 'win32') {
          exec('py --version', (error) => {
            if (!error) {
              return resolve('py');
            }
            resolve(null);
          });
        } else {
          resolve(null);
        }
      });
    });
  });
}

// 执行Python命令
function executePythonCommand(pythonPath, args) {
  return new Promise((resolve, reject) => {
    execFile(pythonPath, args, (error, stdout, stderr) => {
      if (error) {
        reject(error);
      } else {
        resolve({ stdout, stderr });
      }
    });
  });
}

// 解析Python版本
function parsePythonVersion(versionOutput) {
  const match = versionOutput.match(/Python (\d+\.\d+\.\d+)/);
  return match ? match[1] : '未知版本';
}

// 检查依赖是否已安装
async function checkDependencies(pythonPath, dependencies, window) {
  try {
    // 执行pip list命令获取已安装包信息（格式：包名==版本号）
    const pipListOutput = await executePythonCommand(
      pythonPath,
      ['-m', 'pip', 'list', '--format=freeze']
    );
    
    // 解析输出为Map（包名 -> 版本号），忽略大小写
    const installedPackages = new Map();
    pipListOutput.stdout.split('\r\n').forEach(line => {
      const trimmedLine = line.trim();
      if (!trimmedLine) return;
      
      // 分离包名和版本号（处理带版本范围的情况）
      const [pkgName, pkgVersion] = trimmedLine.split(/[=<>~]/, 2);
      if (pkgName) {
        installedPackages.set(pkgName.toLowerCase(), pkgVersion || true);
      }
    });

    // 检查每个依赖是否已安装
    for (const dep of dependencies) {
      // 提取依赖名（忽略版本号部分）
      const depName = dep.split(/[=<>~]/)[0].trim().toLowerCase();
      
      if (installedPackages.has(depName)) {
        checkStatus.dependencies.installed.push(dep);
      } else {
        checkStatus.dependencies.missing.push(dep);
      }
      
      sendStatusUpdate(window);
      await new Promise(resolve => setTimeout(resolve, 100));
    }
  } catch (error) {
    console.error('检查依赖失败:', error);
    // 处理命令执行失败的情况（如pip不可用）
    dependencies.forEach(dep => checkStatus.dependencies.missing.push(dep));
    sendStatusUpdate(window);
  }
}

// 安装缺失的依赖
async function installMissingDependencies(pythonPath, window) {
  const requirementsPath = app.isPackaged ? path.join(process.resourcesPath, 'requirements.txt') : path.join('..', 'requirements.txt');
  
  return new Promise((resolve, reject) => {
    // 使用pip安装依赖
    const installProcess = execFile(
      pythonPath, 
      ['-m', 'pip', 'install', '-i', 'https://mirrors.aliyun.com/pypi/simple/', '-r', requirementsPath],
      (error) => {
        if (error) {
          reject(new Error(`依赖安装失败: ${error.message}`));
        } else {
          resolve();
        }
      }
    );

    // 捕获安装输出，更新进度
    installProcess.stdout.on('data', (data) => {
      console.log('安装输出:', data);
      // 可以在这里解析安装进度并更新状态
      sendStatusUpdate(window);
    });

    installProcess.stderr.on('data', (data) => {
      console.error('安装错误:', data);
      // 处理安装错误
    });
  });
}

module.exports = {
  checkStatus,
  sendStatusUpdate,
  checkPythonEnvironment,
  findPythonExecutable,
  executePythonCommand,
  parsePythonVersion,
  checkDependencies,
  installMissingDependencies
}
