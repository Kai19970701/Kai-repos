@echo off
REM 停止世界时钟地图壁纸进程，并把桌面壁纸恢复成之前的样子
setlocal

set "PID_FILE=%~dp0state\wallpaper.pid"

if exist "%PID_FILE%" (
  set /p WCW_PID=<"%PID_FILE%"
  taskkill /F /PID %WCW_PID% >nul 2>nul
  del /f /q "%PID_FILE%" >nul 2>nul
  echo 已停止世界时钟地图壁纸进程（PID %WCW_PID%）。
) else (
  echo 未找到正在运行的世界时钟地图壁纸（没有 pid 文件），可能本来就没在运行。
)

python "%~dp0restore_wallpaper.py"
pause
