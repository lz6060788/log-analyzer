@echo off
setlocal enabledelayedexpansion

chcp 65001

echo 正在构建Flask应用压缩包...

cd /d "%~dp0.."

REM 创建updates目录
if not exist "static\updates" mkdir "static\updates"

echo 开始构建Flask应用压缩包...

REM 获取时间戳
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "datetime=%%a"
set TIMESTAMP=%datetime:~0,14%

REM 创建临时目录用于打包
if not exist "temp_build" mkdir "temp_build"
if exist "temp_build\app" rmdir /s /q "temp_build\app"
if exist "temp_build\static" rmdir /s /q "temp_build\static"

REM 复制app目录到临时目录
echo 复制app目录...
xcopy /e /i /q "app" "temp_build\app"

REM 复制static目录（排除updates目录）
echo 复制static目录...
xcopy /e /i /q "static" "temp_build\static"
REM 删除临时目录中的updates文件夹
if exist "temp_build\static\updates" rmdir /s /q "temp_build\static\updates"

REM 创建压缩包 - 使用PowerShell的Compress-Archive命令
echo 正在创建压缩包...
set ZIP_FILE=flask_app.zip
set ZIP_PATH=static\updates\!ZIP_FILE!

REM 使用PowerShell的Compress-Archive命令（Windows 10+自带）
powershell -command "Compress-Archive -Path 'temp_build\*' -DestinationPath '%ZIP_PATH%' -Force"

if not exist "%ZIP_PATH%" (
    echo 压缩包创建失败
    goto :cleanup_and_exit
)

REM 获取文件大小
for %%F in ("%ZIP_PATH%") do set FILE_SIZE=%%~zF

REM 获取当前日期时间
for /f "tokens=1-3 delims=/ " %%a in ("%date%") do (
    set YEAR=%%c
    set MONTH=%%a
    set DAY=%%b
)
for /f "tokens=1-3 delims=:." %%a in ("%time%") do (
    set HOUR=%%a
    set MINUTE=%%b
    set SECOND=%%c
)
set BUILD_DATE=%YEAR%-%MONTH%-%DAY% %HOUR%:%MINUTE%:%SECOND%

REM 计算MD5校验和
echo 计算MD5校验和...
set MD5_CHECKSUM=
for /f "skip=1 delims=" %%i in ('certutil -hashfile "%ZIP_PATH%" MD5') do (
    if not defined MD5_CHECKSUM set MD5_CHECKSUM=%%i
)
set MD5_CHECKSUM=%MD5_CHECKSUM: =%

REM 读取版本号
set VERSION=1.0.2
if exist "VERSION" (
    set /p VERSION=<VERSION
    set VERSION=%VERSION: =%
)

REM 创建版本信息JSON文件
echo 更新版本信息...
(
echo {
echo   "version": "%VERSION%",
echo   "file_name": "%ZIP_FILE%",
echo   "file_size": %FILE_SIZE%,
echo   "build_date": "%BUILD_DATE%",
echo   "checksum": "%MD5_CHECKSUM%"
echo }
) > static\updates\flask-version.json

:cleanup
REM 清理临时目录
if exist "temp_build" rmdir /s /q "temp_build"

echo Flask应用压缩包构建成功！
echo 输出目录: static\updates
echo 压缩包: %ZIP_FILE%
echo 文件大小: %FILE_SIZE% 字节
echo MD5校验和: %MD5_CHECKSUM%
echo 版本文件: static\updates\flask-version.json
echo.
echo 包含的目录:
echo   - app目录
echo   - static目录（排除updates子目录）
pause
exit /b 0

:cleanup_and_exit
if exist "temp_build" rmdir /s /q "temp_build"
echo 构建失败！
pause
exit /b 1
