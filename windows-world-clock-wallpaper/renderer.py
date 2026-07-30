# -*- coding: utf-8 -*-
"""
把世界地图 + 城市时间渲染成一张位图（PIL Image）。

不涉及任何窗口/桌面 API —— 这一层只管「画出一张图」，方便离线测试
（甚至可以在非 Windows 系统上单独运行 render_preview()）。真正把图片设为
系统壁纸的逻辑在 wallpaper.py 里。
"""

import json
import os

from PIL import Image, ImageDraw, ImageFont

from config import CITIES, THEME, MAP_LAT_MIN, MAP_LAT_MAX, MAP_LON_MIN, MAP_LON_MAX

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LAND_DATA_PATH = os.path.join(SCRIPT_DIR, "assets", "world_land.json")

# 渲染时按此倍数放大再缩小，让线条/文字带抗锯齿（PIL 本身画多边形/线条不带抗锯齿）
SUPERSAMPLE = 2

WINDOWS_FONT_DIR = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
# 允许通过环境变量追加额外的字体搜索目录，方便在非 Windows 系统上开发/预览
_EXTRA_FONT_DIRS = [
    d for d in os.environ.get("WCW_EXTRA_FONT_DIRS", "").split(os.pathsep) if d
]
FONT_SEARCH_DIRS = [WINDOWS_FONT_DIR] + _EXTRA_FONT_DIRS

# 候选字体文件名，按优先级排列；Windows 10/11 默认都自带前两种
CJK_FONT_CANDIDATES = ["msyh.ttc", "msyhbd.ttc", "simhei.ttf", "simsun.ttc"]
MONO_FONT_CANDIDATES = ["consola.ttf", "consolab.ttf", "cour.ttf", "courbd.ttf"]

_font_cache = {}


def _find_font_file(candidates):
    for directory in FONT_SEARCH_DIRS:
        for name in candidates:
            path = os.path.join(directory, name)
            if os.path.isfile(path):
                return path
    return None


def load_font(kind, size):
    """kind: 'cjk' 或 'mono'。找不到系统字体时退回 PIL 默认字体（不支持中文）。"""
    key = (kind, size)
    if key in _font_cache:
        return _font_cache[key]

    candidates = CJK_FONT_CANDIDATES if kind == "cjk" else MONO_FONT_CANDIDATES
    path = _find_font_file(candidates)
    if path:
        font = ImageFont.truetype(path, size)
    else:
        font = ImageFont.load_default()
    _font_cache[key] = font
    return font


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def lerp_color(c1, c2, t):
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    return (
        int(r1 + (r2 - r1) * t),
        int(g1 + (g2 - g1) * t),
        int(b1 + (b2 - b1) * t),
    )


def load_land_patches():
    with open(LAND_DATA_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


class MapProjector:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def project(self, lon, lat):
        x = (lon - MAP_LON_MIN) / (MAP_LON_MAX - MAP_LON_MIN) * self.width
        y = (MAP_LAT_MAX - lat) / (MAP_LAT_MAX - MAP_LAT_MIN) * self.height
        return x, y


def _draw_ocean_background(draw, width, height):
    bands = 80
    step = height / bands
    for i in range(bands):
        t = i / (bands - 1)
        color = lerp_color(THEME["bg_top"], THEME["bg_bottom"], t)
        y0 = int(i * step)
        y1 = int((i + 1) * step) + 1
        draw.rectangle([0, y0, width, y1], fill=color)


def _draw_graticule(draw, proj):
    color = hex_to_rgb(THEME["graticule"])
    for lon in range(-180, 181, 30):
        x, _ = proj.project(lon, 0)
        draw.line([(x, 0), (x, proj.height)], fill=color, width=1)
    for lat in range(-60, 90, 30):
        _, y = proj.project(0, lat)
        draw.line([(0, y), (proj.width, y)], fill=color, width=1)


def _draw_land(draw, proj, land_patches):
    fill = hex_to_rgb(THEME["land_fill"])
    outline = hex_to_rgb(THEME["land_outline"])
    for ring in land_patches:
        pts = [proj.project(lon, lat) for lon, lat in ring]
        if len(pts) >= 3:
            draw.polygon(pts, fill=fill, outline=outline)


def _draw_header(draw, proj, header_font, header_color, now_utc):
    draw.text((26 * SUPERSAMPLE, 20 * SUPERSAMPLE),
              "世界时钟地图 · WORLD CLOCK MAP", font=header_font, fill=header_color)
    utc_str = now_utc.strftime("UTC %H:%M")
    bbox = draw.textbbox((0, 0), utc_str, font=header_font)
    text_w = bbox[2] - bbox[0]
    draw.text((proj.width - text_w - 26 * SUPERSAMPLE, 20 * SUPERSAMPLE),
              utc_str, font=header_font, fill=header_color)


def _draw_city(draw, proj, city, now_utc, city_font, time_font):
    from zoneinfo import ZoneInfo

    x, y = proj.project(city["lon"], city["lat"])
    local = now_utc.astimezone(ZoneInfo(city["tz"]))
    is_day = 6 <= local.hour < 18
    dot_color = hex_to_rgb(THEME["dot_day"] if is_day else THEME["dot_night"])
    glow_color = hex_to_rgb(THEME["dot_glow"])

    glow_r = 8 * SUPERSAMPLE
    dot_r = 3.5 * SUPERSAMPLE
    draw.ellipse([x - glow_r, y - glow_r, x + glow_r, y + glow_r], fill=glow_color)
    draw.ellipse([x - dot_r, y - dot_r, x + dot_r, y + dot_r], fill=dot_color)

    name_text = f"{city['city']} {city['en']}"
    time_text = local.strftime("%H:%M")

    name_bbox = draw.textbbox((0, 0), name_text, font=city_font)
    time_bbox = draw.textbbox((0, 0), time_text, font=time_font)
    name_w, name_h = name_bbox[2] - name_bbox[0], name_bbox[3] - name_bbox[1]
    time_w, time_h = time_bbox[2] - time_bbox[0], time_bbox[3] - time_bbox[1]

    pad_x, pad_y, line_gap = 10 * SUPERSAMPLE, 7 * SUPERSAMPLE, 3 * SUPERSAMPLE
    box_w = max(name_w, time_w) + pad_x * 2
    box_h = name_h + time_h + line_gap + pad_y * 2

    lx = x + city.get("label_dx", 12) * SUPERSAMPLE
    ly = y + city.get("label_dy", -6) * SUPERSAMPLE
    if city.get("anchor", "w") == "e":
        x1 = lx - box_w
    else:
        x1 = lx
    y1 = ly - box_h / 2
    x2, y2 = x1 + box_w, y1 + box_h

    draw.rounded_rectangle(
        [x1, y1, x2, y2], radius=6 * SUPERSAMPLE,
        fill=hex_to_rgb(THEME["label_bg"]) + (235,),
        outline=hex_to_rgb(THEME["label_border"]), width=1,
    )
    draw.text((x1 + pad_x, y1 + pad_y - name_bbox[1]), name_text,
              font=city_font, fill=hex_to_rgb(THEME["label_city"]))
    draw.text((x1 + pad_x, y1 + pad_y + name_h + line_gap - time_bbox[1]), time_text,
              font=time_font, fill=hex_to_rgb(THEME["label_time"]))


def render(width, height, now_utc):
    """渲染一帧世界地图时钟，返回一个尺寸为 (width, height) 的 RGB PIL.Image。"""
    render_w, render_h = width * SUPERSAMPLE, height * SUPERSAMPLE

    image = Image.new("RGBA", (render_w, render_h))
    draw = ImageDraw.Draw(image, "RGBA")
    proj = MapProjector(render_w, render_h)

    _draw_ocean_background(draw, render_w, render_h)
    _draw_graticule(draw, proj)
    _draw_land(draw, proj, load_land_patches())

    header_font = load_font("cjk", 13 * SUPERSAMPLE)
    _draw_header(draw, proj, header_font, hex_to_rgb(THEME["header_color"]), now_utc)

    city_font = load_font("cjk", THEME["font_city_size"] * SUPERSAMPLE)
    time_font = load_font("mono", THEME["font_time_size"] * SUPERSAMPLE)
    for city in CITIES:
        _draw_city(draw, proj, city, now_utc, city_font, time_font)

    if SUPERSAMPLE != 1:
        image = image.resize((width, height), Image.LANCZOS)

    return image.convert("RGB")


def render_preview(path, width=1920, height=1080):
    """开发/调试用：渲染当前时间的一帧并保存到 path（任意系统均可运行）。"""
    from datetime import datetime
    from zoneinfo import ZoneInfo

    img = render(width, height, datetime.now(ZoneInfo("UTC")))
    img.save(path)
    return path


if __name__ == "__main__":
    render_preview(os.path.join(SCRIPT_DIR, "preview.png"))
    print("已生成预览图：preview.png")
