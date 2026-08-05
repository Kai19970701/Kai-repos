@echo off
REM Add World Clock Map Wallpaper to Windows startup using Task Scheduler
REM (a logon trigger), instead of the classic Startup folder. Task
REM Scheduler is more reliable and, importantly, lets you check *why*
REM something failed via "schtasks /Query /TN WorldClockMapWallpaper /V",
REM which shows Last Run Time / Last Result - the Startup folder gives no
REM such feedback at all when it silently fails.
REM
REM NOTE: This file intentionally uses plain ASCII text only. Windows batch
REM files are parsed using the console's active code page (often GBK/936 on
REM Simplified Chinese Windows), and UTF-8 non-ASCII text can get misread
REM and corrupt command parsing. Keep this file ASCII-only.
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "WALLPAPER_SCRIPT=%SCRIPT_DIR%wallpaper.py"
set "TASK_NAME=WorldClockMapWallpaper"

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
    echo [ERROR] Could not find pythonw.exe / python.exe.
    echo Make sure Python is installed and "Add python.exe to PATH" was
    echo checked during installation, then open a NEW command prompt
    echo window (so it picks up the updated PATH) and run this again.
    pause
    exit /b 1
)

echo Found Python interpreter: !PYTHONW_PATH!

REM Remove any leftover Startup-folder entry from an older version of this
REM installer, so there is only ever one autostart mechanism active.
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
del /f /q "%STARTUP_DIR%\WorldClockWallpaper.vbs" 2>nul
del /f /q "%STARTUP_DIR%\WorldClockWallpaper.lnk" 2>nul

schtasks /Create /TN "%TASK_NAME%" /SC ONLOGON /RL LIMITED /F ^
  /TR "\"!PYTHONW_PATH!\" \"%WALLPAPER_SCRIPT%\""

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] schtasks failed to create the task - see the error above.
    pause
    exit /b 1
)

echo.
echo Created scheduled task "%TASK_NAME%" ^(trigger: at log on^).
echo It will silently run:
echo   !PYTHONW_PATH! "%WALLPAPER_SCRIPT%"
echo.
echo NOTE: this only runs on your NEXT sign-in (log off + log back in, or
echo restart the PC). Locking/unlocking or waking from sleep will not
echo trigger it.
echo.
echo To check whether it actually ran after your next sign-in, run:
echo   schtasks /Query /TN "%TASK_NAME%" /V /FO LIST
echo and look at "Last Run Time" and "Last Result" (0 = success).
echo You can also check state\wallpaper.log for details.
echo.
echo To remove autostart later, run uninstall_autostart.bat
echo.
pause
