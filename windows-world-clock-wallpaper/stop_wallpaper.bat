@echo off
REM Stop the World Clock Map Wallpaper process and restore your previous
REM desktop wallpaper. ASCII-only on purpose - see note in
REM install_autostart.bat.
setlocal

set "PID_FILE=%~dp0state\wallpaper.pid"

if exist "%PID_FILE%" (
  set /p WCW_PID=<"%PID_FILE%"
  taskkill /F /PID %WCW_PID% >nul 2>nul
  del /f /q "%PID_FILE%" >nul 2>nul
  echo Stopped World Clock Map Wallpaper (PID %WCW_PID%).
) else (
  echo No running World Clock Map Wallpaper found (no pid file).
)

python "%~dp0restore_wallpaper.py"
pause
