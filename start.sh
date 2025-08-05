#!/bin/bash

# Log Analyzer 启动脚本

echo "=== Log Analyzer 启动脚本 ==="

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "错误: Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 检查Docker是否运行
if ! docker info &> /dev/null; then
    echo "错误: Docker 服务未运行，请启动 Docker 服务"
    exit 1
fi

echo "Docker 环境检查通过"

# 选择运行模式
echo ""
echo "请选择运行模式:"
echo "1) 开发模式 (推荐用于开发和测试)"
echo "2) 生产模式 (推荐用于生产环境)"
echo "3) 停止所有容器"
echo "4) 清理所有数据"

read -p "请输入选择 (1-4): " choice

case $choice in
    1)
        echo "启动开发模式..."
        docker-compose up --build
        ;;
    2)
        echo "启动生产模式..."
        docker-compose -f docker-compose.prod.yaml up --build -d
        echo "应用已启动，访问地址: http://localhost:5000"
        echo "查看日志: docker-compose -f docker-compose.prod.yaml logs -f"
        ;;
    3)
        echo "停止所有容器..."
        docker-compose down
        docker-compose -f docker-compose.prod.yaml down
        echo "所有容器已停止"
        ;;
    4)
        echo "清理所有数据..."
        docker-compose down -v
        docker-compose -f docker-compose.prod.yaml down -v
        docker system prune -f
        echo "所有数据已清理"
        ;;
    *)
        echo "无效选择，退出"
        exit 1
        ;;
esac 