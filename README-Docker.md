# Log Analyzer - Docker 部署指南

这是一个基于Flask的日志分析应用，支持客户端日志和操作日志的分析处理。

## 系统要求

- Docker
- Docker Compose

## 快速开始

### 方法一：使用启动脚本（推荐）

#### Linux/macOS:
```bash
chmod +x start.sh
./start.sh
```

#### Windows:
```cmd
start.bat
```

### 方法二：手动启动

#### 1. 构建并启动应用

```bash
# 构建并启动容器
docker-compose up --build

# 后台运行
docker-compose up -d --build
```

### 2. 访问应用

应用启动后，可以通过以下地址访问：
- 主页：http://localhost:5000
- 客户端日志：http://localhost:5000/log/client
- 操作日志：http://localhost:5000/log/operation

### 3. 停止应用

```bash
# 停止并移除容器
docker-compose down

# 同时移除卷（会清除session数据）
docker-compose down -v
```

## 项目结构

```
log-analyzer/
├── app/                    # Python Flask应用
│   ├── api/               # API路由
│   ├── entity/            # 业务逻辑处理器
│   ├── utils/             # 工具函数
│   └── app.py            # 主应用文件
├── templates/             # HTML模板
├── static/               # 静态文件
├── requirements.txt       # Python依赖
├── Dockerfile            # Docker镜像构建文件
├── docker-compose.yaml   # Docker Compose配置
└── .dockerignore         # Docker忽略文件
```

## 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| FLASK_APP | app/app.py | Flask应用入口 |
| FLASK_ENV | development | Flask环境模式 |
| PYTHONPATH | /app | Python路径 |

## 数据持久化

- Flask session数据存储在Docker卷中，容器重启后数据不会丢失
- 应用代码通过卷挂载，修改代码后重启容器即可生效

## 开发模式

在开发模式下，代码修改会自动生效：

```bash
# 开发模式启动
docker-compose up --build

# 查看日志
docker-compose logs -f

# 进入容器调试
docker-compose exec log-analyzer-app bash
```

## 生产部署

### 开发环境
```bash
# 使用开发配置启动
docker-compose up --build
```

### 生产环境
```bash
# 使用生产配置启动
docker-compose -f docker-compose.prod.yaml up --build -d
```

生产环境配置特点：
- 使用Gunicorn作为WSGI服务器，支持多进程
- 内存限制和预留配置
- 非root用户运行，提高安全性
- 不挂载源代码目录，提高性能
- 自动重启策略

## 环境测试

运行测试脚本验证Docker环境配置：

```bash
# 在容器内运行测试
docker-compose exec log-analyzer-app python test-docker.py

# 或在本地运行测试
python test-docker.py
```

## 故障排除

### 1. 端口冲突
如果5000端口被占用，可以修改 `docker-compose.yaml` 中的端口映射：
```yaml
ports:
  - "8080:5000"  # 使用8080端口
```

### 2. 权限问题
在Linux系统上可能需要调整文件权限：
```bash
sudo chown -R $USER:$USER .
```

### 3. 内存不足
如果遇到内存不足问题，可以增加Docker的内存限制或优化pandas的内存使用。

### 4. 依赖问题
如果遇到依赖问题，可以重新构建镜像：
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### 5. 日志查看
查看应用日志：
```bash
# 开发模式
docker-compose logs -f

# 生产模式
docker-compose -f docker-compose.prod.yaml logs -f
```

## 技术栈

- **后端**: Python 3.11 + Flask 2.3.3
- **数据处理**: Pandas 2.1.4 + NumPy 1.24.3
- **会话管理**: Flask-Session 0.8.0
- **容器化**: Docker + Docker Compose 