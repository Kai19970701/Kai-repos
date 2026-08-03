@echo off
REM Add World Clock Map Wallpaper to Windows startup.
REM Resolves the absolute path to pythonw.exe and writes it directly into a
REM .vbs script placed in the Startup folder (runs silently via wscript.exe
REM at logon). This avoids depending on PATH being ready at logon time, and
REM avoids fragile nested PowerShell quoting.
REM
REM NOTE: This file intentionally uses plain ASCII text only. Windows batch
REM files are parsed using the console's active code page (often GBK/936 on
REM Simplified Chinese Windows), and UTF-8 non-ASCII text can get misread
REM and corrupt command parsing. Keep this file ASCII-only.
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
    echo [ERROR] Could not find pythonw.exe / python.exe.
    echo Make sure Python is installed and "Add python.exe to PATH" was
    echo checked during installation, then open a NEW command prompt
    echo window (so it picks up the updated PATH) and run this again.
    pause
    exit /b 1
)

echo Found Python interpreter: !PYTHONW_PATH!

if not exist "%STARTUP_DIR%" mkdir "%STARTUP_DIR%"

echo Set objShell = CreateObject("WScript.Shell") > "%AUTOSTART_VBS%"
echo objShell.Run """!PYTHONW_PATH!"" ""%WALLPAPER_SCRIPT%""", 0, False >> "%AUTOSTART_VBS%"

if exist "%AUTOSTART_VBS%" (
    echo.
    echo Created startup script:
    echo   %AUTOSTART_VBS%
    echo It will silently run:
    echo   !PYTHONW_PATH! "%WALLPAPER_SCRIPT%"
    echo.
    echo NOTE: Windows only runs Startup-folder items when you SIGN IN.
    echo You must fully sign out and back in (or restart) to test this -
    echo locking/unlocking the screen or waking from sleep will NOT
    echo trigger it again.
    echo.
    echo To remove autostart later, run uninstall_autostart.bat
    echo.
) else (
    echo [ERROR] Failed to write the startup script. Check write access to:
    echo   %STARTUP_DIR%
)
pause
