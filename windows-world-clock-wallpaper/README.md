# 世界时钟地图壁纸（Windows）

一个纯 Python 实现的 Windows 动态壁纸：把一整张暗色世界地图渲染成图片，
**通过 Windows 官方 API 直接设置成系统桌面壁纸**（等价于你在「设置 -> 个性化 ->
背景」里手动换一张图），并按 20 秒左右的间隔自动刷新。地图上几个关键国家/
城市对应的真实地理位置会显示一个发光点 + 当前本地时间，字号不大，不会
喧宾夺主。

**重要：这不是打开一个新窗口、也不是"嵌入桌面图标层"之类的技巧** ——
它就是把你的桌面壁纸文件换成了自动生成的地图图片，桌面图标 100% 显示在图片
最上层，可以正常查看和双击打开，因为图标本来就一直渲染在壁纸之上，这是
Windows 桌面本身的层级关系，不依赖任何未文档化的行为。

默认展示 9 个城市：北京、东京、迪拜、莫斯科、伦敦、巴黎、纽约、洛杉矶、悉尼。

## 效果原理

- **地图渲染**：用 [Natural Earth](https://www.naturalearthdata.com/) 1:110m
  公共领域（Public Domain）数据渲染陆地轮廓，随仓库一起打包在
  `assets/world_land.json` 里（已简化坐标点，纯离线数据，运行时不需要联网）。
  城市用经纬度通过等距圆柱投影换算成屏幕坐标，光点位置就是该城市的真实
  地理位置。渲染在 `renderer.py` 里，用 Pillow 画成一张 PNG 图片。
- **设为壁纸**：`wallpaper.py` 每隔 `REFRESH_SECONDS`（默认 20）秒调用一次
  `renderer.render()`，把图片存到 `state/generated_wallpaper.png`，再调用
  Windows 的 `SystemParametersInfoW(SPI_SETDESKWALLPAPER, ...)` 把这张图设成
  桌面壁纸，同时把壁纸样式设为「填充」（不平铺）。
- 因为壁纸文件本身是分钟级刷新（不是逐秒跳动的实时画面），时间只显示到
  分钟，避免出现"秒数卡住不动"的违和感。

## 环境要求

- Windows 10 / 11
- Python 3.9 及以上（自带 `zoneinfo`，但 **Windows 上没有系统自带的 IANA 时区
  数据库**，需要额外装 `tzdata` 包，见下）

## 安装

```powershell
cd windows-world-clock-wallpaper
pip install -r requirements.txt
```

`requirements.txt` 包含：

- `Pillow`：渲染地图 + 文字到图片
- `tzdata`：为 `zoneinfo` 提供 IANA 时区数据（Windows 必需，否则会报
  `ZoneInfoNotFoundError`）

不再需要 `pywin32`，也不涉及任何隐藏窗口，依赖比之前更少。

## 运行

前台运行（能看到控制台日志/报错，方便确认效果，`Ctrl+C` 停止并自动恢复
原壁纸）：

```powershell
python wallpaper.py
```

后台静默运行（无控制台窗口，双击 `run_wallpaper.vbs`）：

```powershell
wscript run_wallpaper.vbs
```

运行后你的桌面壁纸会在几秒内变成世界地图，且立刻就能看到桌面上的所有文件
图标——它们从始至终都在壁纸图片的最上层。

在非 Windows 系统上运行 `wallpaper.py`（比如先在 Mac/Linux 上试一下效果）
会自动降级：只在当前目录生成一张 `preview.png` 预览图，不会尝试设置系统
壁纸。

## 开机自启动

双击（或以管理员/普通用户身份运行均可）：

```powershell
install_autostart.bat
```

会在「启动」文件夹里创建一个指向 `run_wallpaper.vbs` 的快捷方式，下次登录
时自动静默运行。取消自启动：

```powershell
uninstall_autostart.bat
```

## 停止 / 恢复原来的壁纸

```powershell
stop_wallpaper.bat
```

会结束后台进程，并自动把桌面壁纸恢复成运行本工具之前的样子（首次运行时会
自动把你原来的壁纸路径和样式备份到 `state/original_wallpaper.json`）。
如果只想恢复壁纸、不停止进程（那样过 20 秒左右又会被换回地图），可以单独
运行 `restore_wallpaper.bat`。

## 自定义

- **增删/替换城市**：编辑 `config.py` 里的 `CITIES` 列表：
  - `tz` 必须是合法的 IANA 时区名（例如 `Asia/Shanghai`、`Europe/Berlin`）
  - `lat` / `lon` 是城市的地理坐标，决定光点在地图上的位置
  - `label_dx` / `label_dy` / `anchor` 用来微调文字标签相对光点的偏移方向，
    避免相邻城市（比如伦敦和巴黎）文字互相遮挡（按 1920x1080 画布设计）
- **配色 / 字号**：编辑 `config.py` 里的 `THEME` 字典
  （`font_time_size` / `font_city_size` 控制字号，默认较小）。
- **地图裁剪范围**：`config.py` 里的 `MAP_LAT_MIN` / `MAP_LAT_MAX` 控制地图
  显示的纬度范围（默认裁掉了大部分南极冰盖，让有人居住的陆地占满屏幕）。
- **刷新频率**：`config.py` 里的 `REFRESH_SECONDS`（默认 20 秒）。调得更短
  会更快反映分钟数变化，但也会增加磁盘写入和壁纸刷新时的轻微闪烁。

## 已知限制

- 按主显示器分辨率渲染，多显示器环境下默认只覆盖主屏（Windows 的「跨越」
  壁纸样式可以让同一张图铺满所有显示器，如果需要可以把 `apply_wallpaper`
  里的样式代码从 `"10"`（填充）改成 `"22"`（跨越）并自行验证效果）。
- 每次刷新壁纸时桌面会有一次非常短暂的重绘（Windows 本身刷新壁纸的正常
  行为），因此没有做到逐秒跳动，而是分钟级刷新。
- 如果 Windows 资源管理器重启，下一次 `SystemParametersInfoW` 调用会照常
  生效，不需要额外处理。
- 首次运行如果日志里出现 `ZoneInfoNotFoundError`，说明没装 `tzdata`，执行
  `pip install tzdata` 即可。
- 运行日志在 `state/wallpaper.log`，静默运行（pythonw）时看不到控制台输出，
  遇到问题可以先查这个文件。

## 数据来源

`assets/world_land.json` 精简自 [Natural Earth](https://www.naturalearthdata.com/)
1:110m Cultural Vector 数据集（Public Domain，使用无需授权、也无需署名）。
