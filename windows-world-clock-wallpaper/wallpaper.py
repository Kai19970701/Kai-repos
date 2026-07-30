# -*- coding: utf-8 -*-
"""
Windows 世界时钟地图壁纸
==================================
不使用任何隐藏窗口/桌面图标层技巧 —— 直接调用 Windows 官方的
「设置桌面壁纸」API（SystemParametersInfo）把渲染好的世界地图图片设成真正的
系统壁纸。这和你在设置里手动换一张壁纸完全等价，所以桌面图标 100% 显示在
最上层、可以正常点击，不存在「嵌入失败导致遮挡桌面」的问题。

代价：不是逐秒刷新的实时窗口，而是每隔 REFRESH_SECONDS 秒重新生成一张图片
并刷新一次壁纸（默认 20 秒），时间只显示到分钟。

用法：
    python wallpaper.py          # 前台运行，Ctrl+C 停止（会恢复原壁纸）
    pythonw wallpaper.py         # 后台静默运行（无控制台窗口）

依赖：
    pip install -r requirements.txt
"""

import ctypes
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    print("需要 Python 3.9 及以上版本（内置 zoneinfo）。")
    sys.exit(1)

from config import REFRESH_SECONDS
import renderer

IS_WINDOWS = platform.system() == "Windows"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(SCRIPT_DIR, "state")
GENERATED_PATH = os.path.join(STATE_DIR, "generated_wallpaper.png")
ORIGINAL_STATE_PATH = os.path.join(STATE_DIR, "original_wallpaper.json")
PID_PATH = os.path.join(STATE_DIR, "wallpaper.pid")
LOG_PATH = os.path.join(STATE_DIR, "wallpaper.log")

SPI_SETDESKWALLPAPER = 20
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02
DESKTOP_REG_KEY = r"Control Panel\Desktop"


def log(message):
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(line)
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass


def get_screen_size():
    user32 = ctypes.windll.user32
    try:
        user32.SetProcessDPIAware()
    except Exception:  # noqa: BLE001
        pass
    width = user32.GetSystemMetrics(0)
    height = user32.GetSystemMetrics(1)
    return width, height


def _read_desktop_registry():
    import winreg

    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, DESKTOP_REG_KEY) as key:
        def _get(name, default):
            try:
                value, _ = winreg.QueryValueEx(key, name)
                return value
            except FileNotFoundError:
                return default

        return {
            "wallpaper": _get("WallPaper", ""),
            "style": _get("WallpaperStyle", "10"),
            "tile": _get("TileWallpaper", "0"),
        }


def _write_desktop_registry(style, tile):
    import winreg

    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, DESKTOP_REG_KEY, 0, winreg.KEY_SET_VALUE
    ) as key:
        winreg.SetValueEx(key, "WallpaperStyle", 0, winreg.REG_SZ, str(style))
        winreg.SetValueEx(key, "TileWallpaper", 0, winreg.REG_SZ, str(tile))


def backup_original_wallpaper_once():
    """只在第一次运行时记录用户原本的壁纸设置，方便之后一键恢复。"""
    if os.path.exists(ORIGINAL_STATE_PATH):
        return
    os.makedirs(STATE_DIR, exist_ok=True)
    try:
        state = _read_desktop_registry()
    except Exception as exc:  # noqa: BLE001
        log(f"[警告] 读取原壁纸设置失败，跳过备份：{exc!r}")
        return
    with open(ORIGINAL_STATE_PATH, "w", encoding="utf-8") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=2)
    log(f"已备份原壁纸设置到 {ORIGINAL_STATE_PATH}")


def apply_wallpaper(image_path):
    _write_desktop_registry(style="10", tile="0")  # 10 = Fill，铺满不平铺
    ok = ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER, 0, image_path, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    )
    if not ok:
        raise OSError("SystemParametersInfoW(SPI_SETDESKWALLPAPER) 调用失败")


def write_pid_file():
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(PID_PATH, "w", encoding="utf-8") as fh:
        fh.write(str(os.getpid()))


def remove_pid_file():
    try:
        os.remove(PID_PATH)
    except OSError:
        pass


def render_and_apply(width, height):
    now_utc = datetime.now(ZoneInfo("UTC"))
    image = renderer.render(width, height, now_utc)
    os.makedirs(STATE_DIR, exist_ok=True)
    image.save(GENERATED_PATH)
    apply_wallpaper(GENERATED_PATH)


def run():
    log("=== 世界时钟地图壁纸启动 ===")

    if not IS_WINDOWS:
        preview_path = os.path.join(SCRIPT_DIR, "preview.png")
        renderer.render_preview(preview_path)
        log(f"[提示] 当前非 Windows 系统，无法设置系统壁纸，已生成预览图：{preview_path}")
        return

    backup_original_wallpaper_once()
    write_pid_file()

    width, height = get_screen_size()
    log(f"屏幕分辨率：{width}x{height}，每 {REFRESH_SECONDS} 秒刷新一次壁纸")

    try:
        while True:
            try:
                render_and_apply(width, height)
                log("壁纸已刷新")
            except Exception:  # noqa: BLE001
                log("[错误] 渲染或设置壁纸失败：\n" + traceback.format_exc())
            time.sleep(REFRESH_SECONDS)
    except KeyboardInterrupt:
        log("收到停止信号，退出。")
    finally:
        remove_pid_file()


if __name__ == "__main__":
    run()
