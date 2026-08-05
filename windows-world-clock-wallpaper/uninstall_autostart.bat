@echo off
REM Remove World Clock Map Wallpaper from Windows startup.
REM ASCII-only on purpose - see note in install_autostart.bat.
setlocal

set "TASK_NAME=WorldClockMapWallpaper"
schtasks /Delete /TN "%TASK_NAME%" /F >nul 2>nul

REM Also clean up leftovers from older versions of this installer that
REM used the classic Startup folder instead of Task Scheduler.
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
del /f /q "%STARTUP_DIR%\WorldClockWallpaper.vbs" 2>nul
del /f /q "%STARTUP_DIR%\WorldClockWallpaper.lnk" 2>nul

echo Removed the startup task/items (if they existed).
pause
