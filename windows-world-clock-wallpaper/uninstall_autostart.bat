@echo off
REM 取消「世界时钟壁纸」的开机自启动
setlocal

set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
del /f /q "%STARTUP_DIR%\WorldClockWallpaper.vbs" 2>nul
del /f /q "%STARTUP_DIR%\WorldClockWallpaper.lnk" 2>nul

echo 已移除开机自启动项（如果存在的话）。
pause
