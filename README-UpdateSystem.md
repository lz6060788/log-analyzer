# Log Analyzer 更新系统

本系统实现了完整的客户端自动更新功能，包括Electron客户端、Flask应用打包和自动升级机制。

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web部署       │    │  Electron客户端  │    │   更新服务器     │
│   (Docker)      │    │  (内置Flask)     │    │   (Flask API)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   更新包生成     │    │   自动检查更新   │    │   版本管理      │
│   (构建时)      │    │   (定期检查)     │    │   (哈希验证)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 主要功能

### 1. Electron客户端
- 内置Flask应用，无需外部Python环境
- 自动启动Flask后端服务
- 集成自动更新检查
- 支持跨平台（Windows/macOS/Linux）

### 2. 更新包生成
- **手动生成**：通过命令行工具生成更新包
- **自动生成**：Docker构建时自动生成更新包
- **版本控制**：基于代码哈希和Git提交的智能版本管理
- **增量更新**：支持不同类型的更新包（full/docker/client）

### 3. 自动升级
- 定期检查更新
- 下载并安装更新包
- 重启应用完成升级
- 支持回滚机制

## 文件结构

```
log-analyzer/
├── app/
│   ├── api/updates/routes.py          # 更新API路由
│   └── utils/update_package_generator.py  # 更新包生成器
├── client/                             # Electron客户端
│   ├── main.js                        # 主进程
│   ├── preload.js                     # 预加载脚本
│   └── package.json                   # 客户端配置
├── scripts/                           # 构建脚本
│   ├── build_python_app.py           # Python应用打包
│   ├── build_docker.sh               # Docker构建(Linux/Mac)
│   ├── build_docker.bat              # Docker构建(Windows)
│   ├── build_client.sh               # 客户端构建(Linux/Mac)
│   ├── build_client.bat              # 客户端构建(Windows)
│   └── manage_updates.py             # 更新包管理工具
├── static/updates/                    # 更新包存储目录
└── VERSION                           # 版本文件
```

## 使用方法

### 1. 构建客户端

#### Linux/macOS
```bash
chmod +x scripts/build_client.sh
./scripts/build_client.sh
```

#### Windows
```cmd
scripts\build_client.bat
```

### 2. 构建Docker镜像（包含更新包生成）

#### Linux/macOS
```bash
chmod +x scripts/build_docker.sh
./scripts/build_docker.sh
```

#### Windows
```cmd
scripts\build_docker.bat
```

### 3. 手动管理更新包

```bash
# 生成更新包
python scripts/manage_updates.py generate --type client --include-client

# 查看可用更新包
python scripts/manage_updates.py list

# 查看系统状态
python scripts/manage_updates.py status

# 清理旧版本
python scripts/manage_updates.py clean
```

### 4. 启动客户端

```bash
cd client
npm start
```

## API接口

### 更新检查
```http
POST /api/updates/check
Content-Type: application/json

{
  "version": "1.0.0",
  "code_hash": "abc123..."
}
```

### 获取最新版本
```http
GET /api/updates/latest
```

### 下载更新包
```http
GET /api/updates/download/{version}
```

### 生成更新包
```http
POST /api/updates/generate
Content-Type: application/json

{
  "package_type": "client",
  "include_frontend": true,
  "include_backend": true,
  "include_client": true
}
```

## 配置说明

### 版本控制
- 使用`VERSION`文件管理版本号
- 支持语义化版本（如：1.0.0）
- 自动生成时间戳版本（如：2025.01.27.1430）

### 更新包类型
- **full**: 完整应用包
- **docker**: Docker部署包
- **client**: 客户端更新包

### 环境要求
- Python 3.8+
- Node.js 16+
- Git
- Docker (可选)

## 部署流程

### 1. 开发环境
```bash
# 安装依赖
pip install -r requirements.txt
cd frontend && npm install

# 启动开发服务器
python app/app.py
cd frontend && npm run dev
```

### 2. 生产环境
```bash
# 构建并部署
./scripts/build_docker.sh
docker run -p 5000:5000 log-analyzer:latest
```

### 3. 客户端分发
```bash
# 构建客户端
./scripts/build_client.sh

# 分发client/dist/目录下的安装包
```

## 故障排除

### 常见问题

1. **GitPython导入错误**
   ```bash
   pip install GitPython==3.1.40
   ```

2. **PyInstaller构建失败**
   ```bash
   pip install pyinstaller
   python scripts/build_python_app.py
   ```

3. **Electron构建失败**
   ```bash
   cd client
   npm install
   npm run build
   ```

4. **更新包生成失败**
   - 检查`static/updates/`目录权限
   - 确保有足够的磁盘空间
   - 验证Git仓库状态

### 日志查看
- Flask应用日志：控制台输出
- Electron日志：开发者工具控制台
- 更新日志：`static/updates/`目录

## 安全考虑

1. **代码哈希验证**：防止无效更新
2. **版本控制**：避免重复升级
3. **HTTPS支持**：生产环境建议使用HTTPS
4. **权限控制**：更新包生成需要适当权限

## 扩展功能

### 1. 增量更新
- 支持差异更新包
- 减少下载大小
- 提高更新速度

### 2. 回滚机制
- 保存历史版本
- 支持版本回退
- 错误恢复

### 3. 多环境支持
- 开发/测试/生产环境
- 环境特定配置
- 条件更新

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT License
