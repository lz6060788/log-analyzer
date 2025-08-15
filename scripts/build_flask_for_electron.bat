@echo off
echo 正在构建Flask应用...

cd /d "%~dp0.."

REM 检查是否安装了PyInstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo 正在安装PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo PyInstaller安装失败，请手动安装
        pause
        exit /b 1
    )
)

REM 创建updates目录
if not exist "static\updates" mkdir "static\updates"

echo 开始构建Flask应用...
pyinstaller app/build_flask.spec --distpath static/updates --workpath client/build/flask-work

if errorlevel 1 (
    echo Flask应用构建失败
    pause
    exit /b 1
)

REM 更新版本信息
echo 更新版本信息...
python -c "import json, os, hashlib; from datetime import datetime; version_file = 'static/updates/flask-version.json'; exe_file = 'static/updates/flask_app.exe'; root_version_file = 'VERSION'; version = open(root_version_file, 'r', encoding='utf-8').read().strip() if os.path.exists(root_version_file) else '1.0.0'; version_info = {'version': version, 'file_size': os.path.getsize(exe_file) if os.path.exists(exe_file) else 0, 'build_date': datetime.now().strftime('%%Y-%%m-%%d'), 'checksum': hashlib.md5(open(exe_file, 'rb').read()).hexdigest() if os.path.exists(exe_file) else ''}; json.dump(version_info, open(version_file, 'w', encoding='utf-8'), indent=2, ensure_ascii=False); print('版本信息更新完成，版本号: ' + version)"

echo Flask应用构建成功！
echo 输出目录: static/updates
echo 版本文件: static/updates/flask-version.json
pause
