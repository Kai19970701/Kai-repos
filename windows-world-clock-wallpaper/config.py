# -*- coding: utf-8 -*-
"""
城市与外观配置。
- 修改 CITIES 列表即可增删/调整显示的城市。
    - tz 必须是合法的 IANA 时区名
    - lat/lon 是城市的地理坐标（十进制度），用于在世界地图上定位光点
    - label_dx / label_dy 用于微调该城市文字标签相对于光点的偏移（像素），
      避免相邻城市（如伦敦/巴黎）的文字互相重叠
    - anchor 是标签文字的对齐方式（tkinter anchor："w" 靠左对齐、"e" 靠右对齐等）
- 修改 THEME 调整颜色（暗色地图主题）。
"""

CITIES = [
    {"city": "北京", "en": "Beijing", "tz": "Asia/Shanghai",
     "lat": 39.90, "lon": 116.40, "label_dx": 14, "label_dy": -4, "anchor": "w"},
    {"city": "东京", "en": "Tokyo", "tz": "Asia/Tokyo",
     "lat": 35.68, "lon": 139.69, "label_dx": 14, "label_dy": -4, "anchor": "w"},
    {"city": "迪拜", "en": "Dubai", "tz": "Asia/Dubai",
     "lat": 25.20, "lon": 55.27, "label_dx": 14, "label_dy": -4, "anchor": "w"},
    {"city": "莫斯科", "en": "Moscow", "tz": "Europe/Moscow",
     "lat": 55.75, "lon": 37.62, "label_dx": 14, "label_dy": -14, "anchor": "w"},
    {"city": "伦敦", "en": "London", "tz": "Europe/London",
     "lat": 51.51, "lon": -0.13, "label_dx": -14, "label_dy": -14, "anchor": "e"},
    {"city": "巴黎", "en": "Paris", "tz": "Europe/Paris",
     "lat": 48.85, "lon": 2.35, "label_dx": 14, "label_dy": 12, "anchor": "w"},
    {"city": "纽约", "en": "New York", "tz": "America/New_York",
     "lat": 40.71, "lon": -74.01, "label_dx": -14, "label_dy": -4, "anchor": "e"},
    {"city": "洛杉矶", "en": "Los Angeles", "tz": "America/Los_Angeles",
     "lat": 34.05, "lon": -118.24, "label_dx": -14, "label_dy": -4, "anchor": "e"},
    {"city": "悉尼", "en": "Sydney", "tz": "Australia/Sydney",
     "lat": -33.87, "lon": 151.21, "label_dx": 14, "label_dy": -4, "anchor": "w"},
]

# 中文星期缩写，index 0 = 周一 (与 datetime.weekday() 对齐)
WEEKDAYS_CN = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

# 地图可视纬度范围（裁掉大部分南极冰盖，让有人居住的陆地占满屏幕）
MAP_LAT_MIN = -58.0
MAP_LAT_MAX = 83.0
MAP_LON_MIN = -180.0
MAP_LON_MAX = 180.0

THEME = {
    # 背景渐变（海洋，从上到下）
    "bg_top": "#04060c",
    "bg_bottom": "#0b1224",
    # 经纬网格线
    "graticule": "#111a30",
    # 陆地
    "land_fill": "#121c33",
    "land_outline": "#233052",
    # 城市光点
    "dot_day": "#fbbf24",
    "dot_night": "#818cf8",
    "dot_glow": "#334155",
    # 标签文字
    "label_city": "#f1f5f9",
    "label_time": "#7dd3fc",
    "label_bg": "#0a0f1e",
    "label_border": "#28324c",
    # 顶角信息条
    "header_color": "#5b6478",
    # 字体（Windows 上建议使用系统自带字体）
    "font_city": ("Microsoft YaHei UI", 10, "bold"),
    "font_time": ("Consolas", 12, "bold"),
    "font_header": ("Microsoft YaHei UI", 11),
}

# 刷新间隔（毫秒）
TICK_MS = 1000
