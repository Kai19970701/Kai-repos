# -*- coding: utf-8 -*-
"""把桌面壁纸恢复成运行本工具之前的样子（读取 state/original_wallpaper.json）。"""

import ctypes
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(SCRIPT_DIR, "state")
ORIGINAL_STATE_PATH = os.path.join(STATE_DIR, "original_wallpaper.json")

SPI_SETDESKWALLPAPER = 20
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02
DESKTOP_REG_KEY = r"Control Panel\Desktop"


def main():
    if not os.path.exists(ORIGINAL_STATE_PATH):
        print("没有找到原壁纸备份记录，无法自动恢复。")
        print("请手动在「设置 -> 个性化 -> 背景」里重新选择壁纸。")
        return

    with open(ORIGINAL_STATE_PATH, "r", encoding="utf-8") as fh:
        state = json.load(fh)

    import winreg

    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, DESKTOP_REG_KEY, 0, winreg.KEY_SET_VALUE
    ) as key:
        winreg.SetValueEx(key, "WallpaperStyle", 0, winreg.REG_SZ, str(state.get("style", "10")))
        winreg.SetValueEx(key, "TileWallpaper", 0, winreg.REG_SZ, str(state.get("tile", "0")))

    wallpaper_path = state.get("wallpaper", "")
    ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER, 0, wallpaper_path, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    )
    print(f"已恢复原壁纸：{wallpaper_path or '(空 / 纯色背景)'}")


if __name__ == "__main__":
    main()
