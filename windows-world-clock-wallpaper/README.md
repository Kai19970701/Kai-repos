# 世界时钟动态壁纸（Windows）

一个纯 Python 实现的 Windows 动态壁纸：**直接替换你的桌面背景**（不是打开一个
新窗口/新桌面），桌面上的文件图标仍然正常显示在最上层、可以照常点击。
背景是一整张暗色世界地图，几个关键国家/城市在地图上对应的地理位置显示一个
发光点 + 当前本地时间，字号不大，不会喧宾夺主。

默认展示 9 个城市：北京、东京、迪拜、莫斯科、伦敦、巴黎、纽约、洛杉矶、悉尼。
每个光点旁边是一个小标签：城市名 + 当前本地时间（时:分:秒），发光点颜色会随
昼夜切换（白天琥珀色、夜间靛蓝色）。

## 效果原理

**替换桌面背景（不是新建窗口/新桌面）**：Windows 桌面（Progman）在收到一个
内部消息（`0x052C`）后会创建一个名为 `WorkerW` 的隐藏窗口用来承载壁纸内容——
这是社区里公认的「嵌入桌面」技巧。本项目用 `pywin32` 把一个无边框的 Tkinter
窗口 `SetParent` 到这个 `WorkerW` 上，而桌面图标层（`SHELLDLL_DefView`）仍然
叠加在其上方，所以效果就是：**你的桌面背景变成了这张世界地图，文件图标照常
显示在图上、可以正常双击打开**——和系统自带壁纸的层级关系完全一样，只是内容
是动态刷新的。

**地图渲染**：世界地图用 [Natural Earth](https://www.naturalearthdata.com/)
1:110m 公共领域（Public Domain）数据渲染，随仓库一起打包在
`assets/world_land.json` 里（已简化/精简坐标点，纯离线数据，运行时不需要联网）。
城市用经纬度通过等距圆柱投影换算成屏幕坐标，光点位置就是该城市的真实地理位置。

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

- `pywin32`：用于查找 `WorkerW` 并 `SetParent`
- `tzdata`：为 `zoneinfo` 提供 IANA 时区数据（Windows 必需，否则会报
  `ZoneInfoNotFoundError`）

## 运行

前台运行（能看到控制台输出/报错，方便调试，`Ctrl+C` 退出）：

```powershell
python wallpaper.py
```

后台静默运行（无控制台窗口，双击 `run_wallpaper.vbs` 或用下面命令）：

```powershell
wscript run_wallpaper.vbs
```

运行后你的桌面背景会立刻变成世界地图；如果控制台/日志里打印了「未能找到
WorkerW」的警告，说明当前 Windows 版本的嵌入没有成功，脚本会退化成一个普通
的置底窗口（这种情况下桌面图标可能被遮挡，请反馈日志里的具体报错）。

在非 Windows 系统上直接运行 `wallpaper.py` 会自动降级为「普通窗口」预览模式
（不会嵌入桌面），方便开发时先看效果再拿去 Windows 上跑。

## 开机自启动

双击（或以管理员/普通用户身份运行均可）：

```powershell
install_autostart.bat
```

会在「启动」文件夹里创建一个指向 `run_wallpaper.vbs` 的快捷方式，下次登录
时自动静默运行、直接替换桌面背景。取消自启动：

```powershell
uninstall_autostart.bat
```

## 停止壁纸 / 恢复原来的桌面背景

因为窗口被嵌入了桌面、也没有任务栏图标，直接关闭稍显麻烦，提供了脚本：

```powershell
stop_wallpaper.bat
```

它会按窗口标题精确找到进程并结束，不会误杀其它 Python 程序。结束后桌面会
露出 Windows 原本设置的壁纸（本工具不会修改、也不会删除你原来的壁纸设置）。

## 自定义

- **增删/替换城市**：编辑 `config.py` 里的 `CITIES` 列表：
  - `tz` 必须是合法的 IANA 时区名（例如 `Asia/Shanghai`、`Europe/Berlin`）
  - `lat` / `lon` 是城市的地理坐标，决定光点在地图上的位置
  - `label_dx` / `label_dy` / `anchor` 用来微调文字标签相对光点的偏移方向，
    避免相邻城市（比如伦敦和巴黎）文字互相遮挡
- **配色 / 字体 / 时间字号**：编辑 `config.py` 里的 `THEME` 字典
  （`font_time` 控制时间文字大小，默认较小；`font_city` 控制城市名字号）。
- **地图裁剪范围**：`config.py` 里的 `MAP_LAT_MIN` / `MAP_LAT_MAX` 控制地图
  显示的纬度范围（默认裁掉了大部分南极冰盖，让有人居住的陆地占满屏幕）。
- **刷新频率**：`config.py` 里的 `TICK_MS`（默认 1000ms，即每秒刷新一次）。

## 已知限制

- 目前按「主显示器」分辨率渲染，多显示器环境下只会覆盖主屏。
- 世界地图采用等距圆柱投影并拉伸铺满屏幕（不是等比例的精确地图投影），
  纯粹为了在任意宽高比的显示器上都能铺满背景，越靠近两极的国家形状失真
  越明显，这是装饰性壁纸的常见取舍。
- 如果 Windows 资源管理器（`explorer.exe`）崩溃重启，`WorkerW` 会被重建，
  已运行的壁纸窗口可能需要重新运行脚本才能再次嵌入。
- 首次运行如果时钟显示 `ZoneInfoNotFoundError`，说明没装 `tzdata`，执行
  `pip install tzdata` 即可。

## 数据来源

`assets/world_land.json` 精简自 [Natural Earth](https://www.naturalearthdata.com/)
1:110m Cultural Vector 数据集（Public Domain，使用无需授权、也无需署名）。
