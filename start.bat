@echo off
chcp 65001 >nul
echo === Log Analyzer 启动脚本 ===

REM 检查Docker是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Docker 未安装，请先安装 Docker
    pause
    exit /b 1
)

REM 检查Docker Compose是否安装
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Docker Compose 未安装，请先安装 Docker Compose
    pause
    exit /b 1
)

REM 检查Docker是否运行
docker info >nul 2>&1
if errorlevel 1 (
    echo 错误: Docker 服务未运行，请启动 Docker 服务
    pause
    exit /b 1
)

echo Docker 环境检查通过

echo.
echo 请选择运行模式:
echo 1) 开发模式 (推荐用于开发和测试)
echo 2) 生产模式 (推荐用于生产环境)
echo 3) 停止所有容器
echo 4) 清理所有数据

set /p choice=请输入选择 (1-4): 

if "%choice%"=="1" (
    echo 启动开发模式...
    docker-compose up --build
) else if "%choice%"=="2" (
    echo 启动生产模式...
    docker-compose -f docker-compose.prod.yaml up --build -d
    echo 应用已启动，访问地址: http://localhost:5000
    echo 查看日志: docker-compose -f docker-compose.prod.yaml logs -f
) else if "%choice%"=="3" (
    echo 停止所有容器...
    docker-compose down
    docker-compose -f docker-compose.prod.yaml down
    echo 所有容器已停止
) else if "%choice%"=="4" (
    echo 清理所有数据...
    docker-compose down -v
    docker-compose -f docker-compose.prod.yaml down -v
    docker system prune -f
    echo 所有数据已清理
) else (
    echo 无效选择，退出
    pause
    exit /b 1
)

pause 