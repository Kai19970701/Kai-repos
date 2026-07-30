@echo off
REM 将「世界时钟壁纸」添加到开机自启动（在 Windows 启动文件夹里创建快捷方式）
setlocal

set "SCRIPT_DIR=%~dp0"
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "VBS_PATH=%SCRIPT_DIR%run_wallpaper.vbs"

powershell -NoProfile -Command ^
  "$s=(New-Object -COM WScript.Shell).CreateShortcut('%STARTUP_DIR%\WorldClockWallpaper.lnk'); $s.TargetPath='%VBS_PATH%'; $s.WorkingDirectory='%SCRIPT_DIR%'; $s.Save()"

echo.
echo 已添加开机自启动快捷方式：
echo   %STARTUP_DIR%\WorldClockWallpaper.lnk
echo 重启电脑或重新登录后将自动运行。
echo 如需取消，请运行 uninstall_autostart.bat
echo.
pause
