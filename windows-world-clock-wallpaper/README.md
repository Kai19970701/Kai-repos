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

这个 `.bat` 只是个两行的小外壳，实际逻辑在 `install_autostart.py` 里，分两步：

1. **优先尝试任务计划程序（Task Scheduler）**：创建一个「登录时触发」的任务
   `WorldClockMapWallpaper`，好处是出问题时能查到原因（见下）。但创建计划
   任务通常需要管理员权限——哪怕任务本身只在你自己登录、以标准权限运行也
   一样，普通终端下会报"拒绝访问"。
2. **失败就自动退回「启动」文件夹方式**：往
   `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup` 写一个
   `WorldClockWallpaper.vbs`，这个位置是你自己账户的个人文件夹，不需要
   管理员权限就能写。

脚本运行完会明确告诉你最终用的是哪一种方式。取消自启动（两种方式都会一起
清理）：

```powershell
uninstall_autostart.bat
```

（这部分逻辑之所以放在 Python 里而不是纯批处理脚本里，是因为反复踩到
`cmd.exe` 解析批处理文件时的各种坑——嵌套引号、控制台代码页等。用 Python
的 `subprocess` 传参数列表调用 schtasks，Windows 会自动处理好带空格路径的
引号；生成 .vbs 时的引号转义也用 Python 字符串处理完成，不再依赖手工拼接
的批处理文本。）

**测试自启动时请注意**：
- 不管走的是哪种方式，都只在你**登录**的那一刻生效一次，必须完整
  「注销后重新登录」或「重启电脑」才能验证效果——单纯锁屏/解锁、或从睡眠
  中唤醒都不会重新触发它，这是最容易误判"没生效"的地方。
- 如果最终用的是**任务计划程序**：下次登录之后运行
  `schtasks /Query /TN "WorldClockMapWallpaper" /V /FO LIST`，重点看
  `Last Run Time`（上次运行时间，应该接近你登录的时间）和 `Last Result`
  （上次运行结果，`0` 表示成功；非 0 说明启动失败，把这个数字告诉我）。也
  可以在「任务计划程序」图形界面（`taskschd.msc` -> 任务计划程序库）里
  找到这个任务，右键"运行"立即手动触发一次，不用等重启。
- 如果最终用的是**「启动」文件夹**：可以直接双击
  `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\WorldClockWallpaper.vbs`
  手动跑一次，看是否正常（正常的话桌面应该几秒内变成地图），不用等重启。
- 同时也去 `state\wallpaper.log` 里看有没有报错——如果这个文件在你上次
  登录之后完全没有新内容，说明启动项根本没被触发（比如被安全软件拦截）；
  如果有新内容但报错，那是 Python 脚本自身的问题，把报错内容发给我即可。
- 如果是先装好 Python 才第一次运行 `install_autostart.bat` 却仍提示找不到
  `pythonw.exe`，多半是当前命令行窗口的 PATH 还没刷新——重新打开一个新的
  命令行窗口再试。

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
