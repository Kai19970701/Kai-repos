@echo off
REM Restore your original wallpaper without stopping the running process
REM (if the wallpaper process is still running, it will switch back to the
REM map on its next refresh). ASCII-only on purpose - see note in
REM install_autostart.bat.
python "%~dp0restore_wallpaper.py"
pause
