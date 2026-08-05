# -*- coding: utf-8 -*-
"""取消「世界时钟地图壁纸」的开机自启动（删除计划任务 + 清理旧版残留）。"""

import os
import subprocess
import sys

TASK_NAME = "WorldClockMapWallpaper"


def main():
    if os.name != "nt":
        print("[提示] 本脚本只能在 Windows 上取消开机自启动。")
        return 1

    result = subprocess.run(
        ["schtasks", "/Delete", "/TN", TASK_NAME, "/F"],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        print(f'已删除计划任务 "{TASK_NAME}"。')
    else:
        print(f'没有找到计划任务 "{TASK_NAME}"（可能本来就没装，或已经删除过）。')

    startup_dir = os.path.join(
        os.environ.get("APPDATA", ""),
        "Microsoft", "Windows", "Start Menu", "Programs", "Startup",
    )
    for name in ("WorldClockWallpaper.vbs", "WorldClockWallpaper.lnk"):
        path = os.path.join(startup_dir, name)
        if os.path.exists(path):
            os.remove(path)
            print(f"已清理旧版本残留：{path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
