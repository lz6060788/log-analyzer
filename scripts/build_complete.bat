@echo off
echo ========================================
echo 开始构建完整的Log Analyzer应用
echo ========================================

cd /d "%~dp0.."

echo.
echo 步骤1: 构建Flask应用...
call scripts\build_flask_for_electron.bat
if errorlevel 1 (
    echo Flask应用构建失败，停止构建
    pause
    exit /b 1
)

echo.
echo 步骤2: 构建Electron应用...
cd client
npm run build:win
if errorlevel 1 (
    echo Electron应用构建失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 构建完成！
echo ========================================
echo Flask应用: static/updates/
echo Electron应用: client/dist/
echo.
echo 现在可以运行安装程序了！
pause
