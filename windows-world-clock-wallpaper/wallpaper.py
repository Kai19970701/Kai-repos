# -*- coding: utf-8 -*-
"""
Windows 动态壁纸 - 世界地图时钟
==================================
把当前脚本渲染的画面「嵌入」到 Windows 桌面图标层的下面（经典 WorkerW 技巧），
从而直接替换系统桌面背景，桌面图标/文件仍然显示在最上层、可以正常点击。

画面是一整张暗色世界地图，几个关键城市在地图上对应的地理位置显示一个
发光点 + 当前本地时间（小字号，不遮挡地图整体观感）。

用法：
    python wallpaper.py          # 前台运行（可看到控制台日志，Ctrl+C 退出）
    pythonw wallpaper.py         # 后台静默运行（无控制台窗口）

依赖：
    pip install -r requirements.txt

仅支持 Windows。若不在 Windows 上运行，会自动降级为「普通窗口」模式，
方便在开发阶段预览效果（不会嵌入桌面）。
"""

import json
import os
import sys
import platform
import tkinter as tk
from datetime import datetime

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - Python < 3.9 不支持
    print("需要 Python 3.9 及以上版本（内置 zoneinfo）。")
    sys.exit(1)

from config import (
    CITIES, THEME, TICK_MS,
    MAP_LAT_MIN, MAP_LAT_MAX, MAP_LON_MIN, MAP_LON_MAX,
)

IS_WINDOWS = platform.system() == "Windows"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LAND_DATA_PATH = os.path.join(SCRIPT_DIR, "assets", "world_land.json")


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def lerp_color(c1, c2, t):
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


def attach_to_desktop(hwnd):
    """把窗口句柄 hwnd 挂到 Progman 下的 WorkerW 上，使其成为桌面壁纸本身。

    这是社区里广泛使用的技巧：Explorer 为了兼容旧版 Active Desktop，在收到
    一个未公开文档的消息（0x052C）后会创建一个 WorkerW 承载壁纸内容，桌面
    图标层（SHELLDLL_DefView）仍然叠加在其上，因此文件图标始终可见、可点击。
    找不到合适的 WorkerW 时返回 False（调用方应保持普通窗口，不做嵌入）。
    """
    import win32con
    import win32gui

    progman = win32gui.FindWindow("Progman", None)
    if not progman:
        return False

    # 部分系统需要连续发两次才能可靠创建 WorkerW
    win32gui.SendMessageTimeout(progman, 0x052C, 0, 0, win32con.SMTO_NORMAL, 1000)
    win32gui.SendMessageTimeout(progman, 0x052C, 0, 0, win32con.SMTO_NORMAL, 1000)

    workerw = 0

    def enum_windows_cb(hwnd_top, _):
        nonlocal workerw
        p = win32gui.FindWindowEx(hwnd_top, 0, "SHELLDLL_DefView", None)
        if p:
            workerw = win32gui.FindWindowEx(0, hwnd_top, "WorkerW", None)
        return True

    win32gui.EnumWindows(enum_windows_cb, None)

    if not workerw:
        return False

    win32gui.SetParent(hwnd, workerw)
    return True


def load_land_patches():
    with open(LAND_DATA_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


class WorldMapWallpaper:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("World Map Clock Wallpaper")
        self.root.configure(bg=THEME["bg_top"])
        self.root.overrideredirect(True)  # 无边框

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.width, self.height = screen_w, screen_h
        self.root.geometry(f"{screen_w}x{screen_h}+0+0")

        self.canvas = tk.Canvas(
            self.root, width=screen_w, height=screen_h, highlightthickness=0, bd=0
        )
        self.canvas.pack(fill="both", expand=True)

        self.city_items = []  # 每个城市对应的可变文本/光点 item id

        self._draw_ocean_background()
        self._draw_graticule()
        self._draw_land()
        self._draw_header()
        self._build_cities()

        self.root.after(50, self._embed_in_desktop)
        self._tick()

    # ---------- 坐标投影：经纬度 -> 屏幕像素（等距圆柱投影，拉伸铺满全屏） ----------
    def project(self, lon, lat):
        x = (lon - MAP_LON_MIN) / (MAP_LON_MAX - MAP_LON_MIN) * self.width
        y = (MAP_LAT_MAX - lat) / (MAP_LAT_MAX - MAP_LAT_MIN) * self.height
        return x, y

    # ---------- 背景 ----------
    def _draw_ocean_background(self):
        bands = 60
        step = self.height / bands
        for i in range(bands):
            t = i / (bands - 1)
            color = lerp_color(THEME["bg_top"], THEME["bg_bottom"], t)
            y0 = int(i * step)
            y1 = int((i + 1) * step) + 1
            self.canvas.create_rectangle(
                0, y0, self.width, y1, fill=color, outline=color
            )

    def _draw_graticule(self):
        for lon in range(-180, 181, 30):
            x, _ = self.project(lon, 0)
            self.canvas.create_line(
                x, 0, x, self.height, fill=THEME["graticule"], width=1
            )
        for lat in range(-60, 90, 30):
            _, y = self.project(0, lat)
            self.canvas.create_line(
                0, y, self.width, y, fill=THEME["graticule"], width=1
            )

    def _draw_land(self):
        patches = load_land_patches()
        for ring in patches:
            pts = []
            for lon, lat in ring:
                x, y = self.project(lon, lat)
                pts.extend((x, y))
            if len(pts) >= 6:
                self.canvas.create_polygon(
                    pts, fill=THEME["land_fill"],
                    outline=THEME["land_outline"], width=1,
                    joinstyle="round",
                )

    def _draw_header(self):
        self.canvas.create_text(
            26, 22,
            text="🌍  世界时钟地图 · WORLD CLOCK MAP",
            font=THEME["font_header"], fill=THEME["header_color"], anchor="w",
        )
        self.utc_text = self.canvas.create_text(
            self.width - 26, 22,
            text="", font=THEME["font_header"],
            fill=THEME["header_color"], anchor="e",
        )

    # ---------- 城市光点 + 标签 ----------
    def _rounded_rect(self, x1, y1, x2, y2, r=8, **kwargs):
        return self.canvas.create_polygon(
            self._rect_points(x1, y1, x2, y2, r), smooth=True, **kwargs
        )

    def _build_cities(self):
        for city in CITIES:
            x, y = self.project(city["lon"], city["lat"])

            glow = self.canvas.create_oval(
                x - 8, y - 8, x + 8, y + 8,
                fill=THEME["dot_glow"], outline="",
            )
            dot = self.canvas.create_oval(
                x - 3.5, y - 3.5, x + 3.5, y + 3.5,
                fill=THEME["dot_night"], outline="",
            )

            anchor = city.get("anchor", "w")
            lx = x + city.get("label_dx", 12)
            ly = y + city.get("label_dy", -6)

            # 标签底板（先占位，尺寸在首次 tick 时根据文字宽度精确调整）
            chip = self._rounded_rect(
                lx, ly, lx + 1, ly + 1, r=6,
                fill=THEME["label_bg"], outline=THEME["label_border"], width=1,
            )

            name_item = self.canvas.create_text(
                0, 0, text=f"{city['city']} {city['en']}",
                font=THEME["font_city"], fill=THEME["label_city"], anchor="w",
            )
            time_item = self.canvas.create_text(
                0, 0, text="--:--:--",
                font=THEME["font_time"], fill=THEME["label_time"], anchor="w",
            )

            self.city_items.append({
                "tz": ZoneInfo(city["tz"]),
                "anchor": anchor, "lx": lx, "ly": ly,
                "chip": chip, "name": name_item, "time": time_item,
                "dot": dot, "glow": glow,
            })
            self._layout_label(self.city_items[-1], first=True)

    def _layout_label(self, item, first=False):
        pad_x, pad_y, line_gap = 10, 7, 3
        name_bbox = self.canvas.bbox(item["name"])
        time_bbox = self.canvas.bbox(item["time"])
        name_w = (name_bbox[2] - name_bbox[0]) if name_bbox else 60
        time_w = (time_bbox[2] - time_bbox[0]) if time_bbox else 60
        name_h = (name_bbox[3] - name_bbox[1]) if name_bbox else 14
        time_h = (time_bbox[3] - time_bbox[1]) if time_bbox else 16

        box_w = max(name_w, time_w) + pad_x * 2
        box_h = name_h + time_h + line_gap + pad_y * 2

        lx, ly = item["lx"], item["ly"]
        if item["anchor"] == "e":
            x1 = lx - box_w
        else:
            x1 = lx
        y1 = ly - box_h / 2
        x2, y2 = x1 + box_w, y1 + box_h

        self.canvas.coords(item["chip"], self._rect_points(x1, y1, x2, y2, r=6))
        text_x = x1 + pad_x
        self.canvas.coords(item["name"], text_x, y1 + pad_y + name_h / 2)
        self.canvas.coords(item["time"], text_x, y1 + pad_y + name_h + line_gap + time_h / 2)

    @staticmethod
    def _rect_points(x1, y1, x2, y2, r=6):
        return [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
        ]

    # ---------- 每秒刷新 ----------
    def _tick(self):
        now_utc = datetime.now(ZoneInfo("UTC"))
        self.canvas.itemconfigure(
            self.utc_text, text=now_utc.strftime("UTC %H:%M:%S")
        )

        for item in self.city_items:
            local = now_utc.astimezone(item["tz"])
            self.canvas.itemconfigure(item["time"], text=local.strftime("%H:%M:%S"))

            is_day = 6 <= local.hour < 18
            color = THEME["dot_day"] if is_day else THEME["dot_night"]
            self.canvas.itemconfigure(item["dot"], fill=color)

        self.root.after(TICK_MS, self._tick)

    # ---------- 嵌入桌面 ----------
    def _embed_in_desktop(self):
        if not IS_WINDOWS:
            print("[提示] 当前非 Windows 系统，以普通窗口预览效果（不会嵌入桌面）。")
            return
        try:
            hwnd = self.root.winfo_id()
            ok = attach_to_desktop(hwnd)
            if not ok:
                print("[警告] 未能找到 WorkerW，改为置底的普通窗口显示，桌面图标可能被遮挡。")
                self.root.lower()
        except Exception as exc:  # noqa: BLE001
            print(f"[警告] 嵌入桌面失败：{exc!r}，改为置底的普通窗口显示。")
            self.root.lower()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = WorldMapWallpaper()
    app.run()
