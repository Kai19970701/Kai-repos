@echo off
REM Thin wrapper: all the actual logic lives in install_autostart.py
REM (finding pythonw.exe, calling schtasks) because doing it in plain batch
REM kept hitting cmd.exe parsing edge cases (nested quoting, code pages).
REM ASCII-only on purpose - see the longer note in this repo's README.
python "%~dp0install_autostart.py"
pause
