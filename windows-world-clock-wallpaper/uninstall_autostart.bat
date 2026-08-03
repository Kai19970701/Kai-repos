@echo off
REM Remove World Clock Map Wallpaper from Windows startup.
REM ASCII-only on purpose - see note in install_autostart.bat.
setlocal

set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
del /f /q "%STARTUP_DIR%\WorldClockWallpaper.vbs" 2>nul
del /f /q "%STARTUP_DIR%\WorldClockWallpaper.lnk" 2>nul

echo Removed the startup item (if it existed).
pause
