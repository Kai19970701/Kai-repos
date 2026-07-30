# -*- coding: utf-8 -*-
"""
城市与外观配置。
- 修改 CITIES 列表即可增删/调整显示的城市（tz 必须是 IANA 时区名）。
- 修改 THEME 调整颜色（暗色主题）。
"""

CITIES = [
    {"city": "北京", "en": "Beijing", "country": "中国", "tz": "Asia/Shanghai", "flag": "🇨🇳"},
    {"city": "东京", "en": "Tokyo", "country": "日本", "tz": "Asia/Tokyo", "flag": "🇯🇵"},
    {"city": "迪拜", "en": "Dubai", "country": "阿联酋", "tz": "Asia/Dubai", "flag": "🇦🇪"},
    {"city": "莫斯科", "en": "Moscow", "country": "俄罗斯", "tz": "Europe/Moscow", "flag": "🇷🇺"},
    {"city": "伦敦", "en": "London", "country": "英国", "tz": "Europe/London", "flag": "🇬🇧"},
    {"city": "巴黎", "en": "Paris", "country": "法国", "tz": "Europe/Paris", "flag": "🇫🇷"},
    {"city": "纽约", "en": "New York", "country": "美国", "tz": "America/New_York", "flag": "🇺🇸"},
    {"city": "洛杉矶", "en": "Los Angeles", "country": "美国", "tz": "America/Los_Angeles", "flag": "🇺🇸"},
    {"city": "悉尼", "en": "Sydney", "country": "澳大利亚", "tz": "Australia/Sydney", "flag": "🇦🇺"},
]

# 中文星期缩写，index 0 = 周一 (与 datetime.weekday() 对齐)
WEEKDAYS_CN = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

THEME = {
    # 背景渐变（从上到下）
    "bg_top": "#05070d",
    "bg_bottom": "#10162a",
    # 卡片
    "card_bg": "#131a2b",
    "card_border": "#232a44",
    "card_border_hover": "#2f3a5c",
    # 文字
    "time_color": "#e5edff",
    "accent_color": "#7dd3fc",
    "city_color": "#f1f5f9",
    "sub_color": "#8b93a7",
    "header_color": "#5b6478",
    # 状态点：白天 / 夜晚
    "day_dot": "#fbbf24",
    "night_dot": "#818cf8",
    # 字体（Windows 上建议使用等宽/无衬线字体，需系统已安装）
    "font_time": ("Consolas", 40, "bold"),
    "font_city": ("Microsoft YaHei UI", 17, "bold"),
    "font_sub": ("Microsoft YaHei UI", 11),
    "font_header": ("Microsoft YaHei UI", 13),
}

# 刷新间隔（毫秒）
TICK_MS = 1000
