@echo off
REM 单独恢复原壁纸（不停止正在运行的进程；如果壁纸进程还在跑，过一会儿又会被换回地图）
python "%~dp0restore_wallpaper.py"
pause
