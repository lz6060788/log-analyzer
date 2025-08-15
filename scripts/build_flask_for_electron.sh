#!/bin/bash

echo "正在构建Flask应用..."

cd "$(dirname "$0")/.."

# 检查是否安装了PyInstaller
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "正在安装PyInstaller..."
    pip install pyinstaller
    if [ $? -ne 0 ]; then
        echo "PyInstaller安装失败，请手动安装"
        exit 1
    fi
fi

# 创建updates目录
mkdir -p "static/updates"

echo "开始构建Flask应用..."
pyinstaller app/build_flask.spec --distpath static/updates --workpath client/build/flask-work

if [ $? -ne 0 ]; then
    echo "Flask应用构建失败"
    exit 1
fi

# 更新版本信息
echo "更新版本信息..."
python -c "
import json, os, hashlib
from datetime import datetime

try:
    version_file = 'static/updates/flask-version.json'
    exe_file = 'static/updates/flask_app.exe'
    root_version_file = 'VERSION'
    
    # 从根目录VERSION文件读取版本号
    version = '1.0.0'
    if os.path.exists(root_version_file):
        with open(root_version_file, 'r', encoding='utf-8') as f:
            version = f.read().strip()
        print(f'从VERSION文件读取到版本号: {version}')
    else:
        print(f'警告: VERSION文件不存在，使用默认版本号: {version}')
    
    # 检查可执行文件是否存在
    if not os.path.exists(exe_file):
        print(f'错误: Flask应用文件不存在: {exe_file}')
        exit(1)
    
    # 构建版本信息
    version_info = {
        'version': version,
        'file_size': os.path.getsize(exe_file),
        'build_date': datetime.now().strftime('%Y-%m-%d'),
        'checksum': hashlib.md5(open(exe_file, 'rb').read()).hexdigest()
    }
    
    # 写入版本文件
    with open(version_file, 'w', encoding='utf-8') as f:
        json.dump(version_info, f, indent=2, ensure_ascii=False)
    
    print(f'版本信息更新完成，版本号: {version}')
    print(f'文件大小: {version_info[\"file_size\"]} 字节')
    print(f'构建日期: {version_info[\"build_date\"]}')
    print(f'MD5校验和: {version_info[\"checksum\"]}')
    
except Exception as e:
    print(f'错误: 更新版本信息失败: {e}')
    exit(1)
"

echo "Flask应用构建成功！"
echo "输出目录: static/updates"
echo "版本文件: static/updates/flask-version.json"
