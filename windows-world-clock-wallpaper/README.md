# 世界时钟动态壁纸（Windows）

一个纯 Python 实现的 Windows 动态壁纸：把画面「贴」在桌面图标下方，实时显示
全球几个关键国家/城市的本地日期和时间，暗色主题，无需 Wallpaper Engine 等
第三方壁纸软件。

默认展示 9 个城市（3×3 网格）：北京、东京、迪拜、莫斯科、伦敦、巴黎、
纽约、洛杉矶、悉尼。每张卡片包含：国旗 + 城市名、大号数字时钟（时:分:秒）、
日期与星期，以及一个昼/夜状态点（白天为琥珀色、夜间为靛蓝色）。

## 效果原理

Windows 桌面（Progman）在收到一个内部消息（`0x052C`）后会创建一个名为
`WorkerW` 的隐藏窗口用来承载壁纸内容——这是社区里公认的「嵌入桌面」技巧。
本项目用 `pywin32` 把一个无边框的 Tkinter 窗口 `SetParent` 到这个 `WorkerW`
上，从而让内容显示在桌面图标的下方、看起来就像壁纸本身在动。

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

在非 Windows 系统上直接运行 `wallpaper.py` 会自动降级为「普通窗口」预览模式
（不会嵌入桌面），方便开发时先看效果再拿去 Windows 上跑。

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

## 停止壁纸

因为窗口被嵌入了桌面、也没有任务栏图标，直接关闭稍显麻烦，提供了脚本：

```powershell
stop_wallpaper.bat
```

它会按窗口标题精确找到进程并结束，不会误杀其它 Python 程序。

## 自定义

- **增删/替换城市**：编辑 `config.py` 里的 `CITIES` 列表，`tz` 必须是合法的
  IANA 时区名（例如 `Asia/Shanghai`、`Europe/Berlin`）。城市数量不必是 9，
  网格会自动按 3 列排布计算行数。
- **配色 / 字体**：编辑 `config.py` 里的 `THEME` 字典。
- **刷新频率**：`config.py` 里的 `TICK_MS`（默认 1000ms，即每秒刷新一次）。

## 已知限制

- 目前按「主显示器」分辨率渲染，多显示器环境下只会覆盖主屏。
- 如果 Windows 资源管理器（`explorer.exe`）崩溃重启，`WorkerW` 会被重建，
  已运行的壁纸窗口可能需要重新运行脚本才能再次嵌入。
- 首次运行如果时钟显示 `ZoneInfoNotFoundError`，说明没装 `tzdata`，执行
  `pip install tzdata` 即可。
