# -*- coding: utf-8 -*-
"""
Windows 动态壁纸 - 世界城市时钟
==================================
把当前脚本渲染的画面「嵌入」到 Windows 桌面图标层的下面（经典 WorkerW 技巧），
从而实现类似 Wallpaper Engine 的动态壁纸效果：实时显示全球几个关键城市的
本地日期和时间，暗色主题。

用法：
    python wallpaper.py          # 前台运行（可看到控制台日志，Ctrl+C 退出）
    pythonw wallpaper.py         # 后台静默运行（无控制台窗口）

依赖：
    pip install -r requirements.txt

仅支持 Windows。若不在 Windows 上运行，会自动降级为「普通窗口」模式，
方便在开发阶段预览效果（不会嵌入桌面）。
"""

import sys
import platform
import tkinter as tk
from datetime import datetime

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - Python < 3.9 不支持
    print("需要 Python 3.9 及以上版本（内置 zoneinfo）。")
    sys.exit(1)

from config import CITIES, WEEKDAYS_CN, THEME, TICK_MS

IS_WINDOWS = platform.system() == "Windows"


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
    """把窗口句柄 hwnd 挂到 Progman 下的 WorkerW 上，使其成为桌面壁纸的一部分。

    这是社区里广泛使用的技巧（Explorer 内部为了兼容旧版 Active Desktop 会
    在响应 0x052C 消息后创建一个 WorkerW 承载壁纸内容）。若系统实现有差异，
    函数会尽力寻找合适的 WorkerW，找不到则返回 False（调用方应保持普通窗口）。
    """
    import win32con
    import win32gui

    progman = win32gui.FindWindow("Progman", None)
    if not progman:
        return False

    # 让 Progman 生成 WorkerW（该消息未在官方文档中说明，但被广泛使用）
    win32gui.SendMessageTimeout(
        progman, 0x052C, 0, 0, win32con.SMTO_NORMAL, 1000
    )

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


class WorldClockWallpaper:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("World Clock Wallpaper")
        self.root.configure(bg=THEME["bg_top"])
        self.root.overrideredirect(True)  # 无边框
        self.root.attributes("-topmost", False)

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.width, self.height = screen_w, screen_h
        self.root.geometry(f"{screen_w}x{screen_h}+0+0")

        self.canvas = tk.Canvas(
            self.root, width=screen_w, height=screen_h, highlightthickness=0, bd=0
        )
        self.canvas.pack(fill="both", expand=True)

        self.city_items = []  # 每个城市对应的可变文本 item id
        self._draw_background()
        self._build_grid()

        self.root.after(50, self._embed_in_desktop)
        self._tick()

    # ---------- 背景 ----------
    def _draw_background(self):
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

        self.canvas.create_text(
            40,
            34,
            text="🌍  世界时钟 · WORLD CLOCK",
            font=THEME["font_header"],
            fill=THEME["header_color"],
            anchor="w",
        )
        self.utc_text = self.canvas.create_text(
            self.width - 40,
            34,
            text="",
            font=THEME["font_header"],
            fill=THEME["header_color"],
            anchor="e",
        )

    # ---------- 卡片网格 ----------
    def _rounded_rect(self, x1, y1, x2, y2, r=18, **kwargs):
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1,
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

    def _build_grid(self):
        n = len(CITIES)
        cols = 3
        rows = (n + cols - 1) // cols

        top_margin = 70
        bottom_margin = 30
        side_margin = 40
        gap = 22

        grid_w = self.width - 2 * side_margin
        grid_h = self.height - top_margin - bottom_margin

        card_w = (grid_w - gap * (cols - 1)) / cols
        card_h = (grid_h - gap * (rows - 1)) / rows

        for idx, city in enumerate(CITIES):
            col = idx % cols
            row = idx // cols
            x1 = side_margin + col * (card_w + gap)
            y1 = top_margin + row * (card_h + gap)
            x2 = x1 + card_w
            y2 = y1 + card_h

            self._rounded_rect(
                x1, y1, x2, y2, r=20,
                fill=THEME["card_bg"], outline=THEME["card_border"], width=1.5,
            )

            cx = x1 + card_w / 2

            dot = self.canvas.create_oval(
                x1 + 22, y1 + 22, x1 + 34, y1 + 34,
                fill=THEME["night_dot"], outline="",
            )

            self.canvas.create_text(
                x1 + 44, y1 + 28,
                text=f"{city['flag']}  {city['city']}  {city['en']}",
                font=THEME["font_city"], fill=THEME["city_color"], anchor="w",
            )

            time_item = self.canvas.create_text(
                cx, y1 + card_h * 0.55,
                text="--:--:--", font=THEME["font_time"],
                fill=THEME["time_color"], anchor="center",
            )

            date_item = self.canvas.create_text(
                cx, y2 - 26,
                text="", font=THEME["font_sub"],
                fill=THEME["sub_color"], anchor="center",
            )

            self.city_items.append(
                {"tz": ZoneInfo(city["tz"]), "time": time_item,
                 "date": date_item, "dot": dot}
            )

    # ---------- 每秒刷新 ----------
    def _tick(self):
        now_utc = datetime.now(ZoneInfo("UTC"))
        self.canvas.itemconfigure(
            self.utc_text, text=now_utc.strftime("UTC %H:%M:%S")
        )

        for item in self.city_items:
            local = now_utc.astimezone(item["tz"])
            time_str = local.strftime("%H:%M:%S")
            weekday = WEEKDAYS_CN[local.weekday()]
            date_str = local.strftime(f"%Y-%m-%d  {weekday}")

            self.canvas.itemconfigure(item["time"], text=time_str)
            self.canvas.itemconfigure(item["date"], text=date_str)

            is_day = 6 <= local.hour < 18
            self.canvas.itemconfigure(
                item["dot"],
                fill=THEME["day_dot"] if is_day else THEME["night_dot"],
            )

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
                print("[警告] 未能找到 WorkerW，改为置底的普通窗口显示。")
                self.root.lower()
        except Exception as exc:  # noqa: BLE001
            print(f"[警告] 嵌入桌面失败：{exc!r}，改为置底的普通窗口显示。")
            self.root.lower()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = WorldClockWallpaper()
    app.run()
