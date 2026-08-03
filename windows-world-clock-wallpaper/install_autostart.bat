@echo off
REM 将「世界时钟地图壁纸」添加到开机自启动
REM 做法：把 pythonw.exe 的绝对路径解析出来，直接写进一个放在「启动」文件夹里的
REM       .vbs 脚本，登录时由 wscript.exe 静默执行——不依赖开机那一刻 PATH 是否
REM       已经生效（这正是之前版本自启动没反应的根本原因），也不经过容易出错的
REM       PowerShell 嵌套引号。
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "AUTOSTART_VBS=%STARTUP_DIR%\WorldClockWallpaper.vbs"
set "WALLPAPER_SCRIPT=%SCRIPT_DIR%wallpaper.py"

set "PYTHONW_PATH="
for /f "delims=" %%P in ('where pythonw 2^>nul') do (
    if not defined PYTHONW_PATH set "PYTHONW_PATH=%%P"
)

if not defined PYTHONW_PATH (
    for /f "delims=" %%P in ('where python 2^>nul') do (
        if not defined PYTHONW_PATH if exist "%%~dpPpythonw.exe" set "PYTHONW_PATH=%%~dpPpythonw.exe"
    )
)

if not defined PYTHONW_PATH (
    echo [错误] 没有找到 pythonw.exe / python.exe。
    echo 请确认已安装 Python，且安装时勾选了 "Add python.exe to PATH"，
    echo 然后重新打开一个新的命令行窗口再运行本脚本（新窗口才会读到最新的 PATH）。
    pause
    exit /b 1
)

echo 找到 Python 解释器：!PYTHONW_PATH!

if not exist "%STARTUP_DIR%" mkdir "%STARTUP_DIR%"

echo Set objShell = CreateObject("WScript.Shell") > "%AUTOSTART_VBS%"
echo objShell.Run """!PYTHONW_PATH!"" ""%WALLPAPER_SCRIPT%""", 0, False >> "%AUTOSTART_VBS%"

if exist "%AUTOSTART_VBS%" (
    echo.
    echo 已在开机启动文件夹创建：
    echo   %AUTOSTART_VBS%
    echo 实际会静默运行：
    echo   !PYTHONW_PATH! "%WALLPAPER_SCRIPT%"
    echo.
    echo 注意：Windows 的「启动」文件夹里的项目只在你【登录】时触发一次——
    echo 必须完整注销后重新登录、或重启电脑才能测试效果；
    echo 单纯锁屏/解锁、或从睡眠中唤醒，都不会重新触发它。
    echo.
    echo 如需取消自启动，请运行 uninstall_autostart.bat
    echo.
) else (
    echo [错误] 写入启动脚本失败，请检查该目录是否有写入权限：
    echo   %STARTUP_DIR%
)
pause
