# -*- coding: utf-8 -*-
"""
把「世界时钟地图壁纸」加入开机自启动。

优先尝试用 Windows 任务计划程序（Task Scheduler）创建一个「登录时触发」的
任务——出问题时能用 `schtasks /Query ... /V` 查到具体原因，比"启动"文件夹
方式更容易排查。但创建计划任务通常需要管理员权限（即便任务本身只在你自己
登录、以标准权限运行也一样），非管理员终端下会报"拒绝访问"。所以如果
schtasks 创建失败，会自动退回到不需要管理员权限的经典"启动"文件夹方式
（写一个 .vbs 到 Startup 目录）。

之前用纯 .bat 实现这整套逻辑（找 pythonw.exe 路径、拼 schtasks/vbs 内容）
反复踩到 cmd.exe 解析上的坑（嵌套引号、控制台代码页……），所以改成在这里用
Python 写：找解释器路径用 shutil.which，调用 schtasks 用
subprocess.run(参数列表) 而不是拼一整条命令行字符串，生成 .vbs 内容也用
Python 自带的字符串处理做引号转义，不再依赖手工拼接的批处理文本。
"""

import os
import shutil
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WALLPAPER_SCRIPT = os.path.join(SCRIPT_DIR, "wallpaper.py")
TASK_NAME = "WorldClockMapWallpaper"


def find_pythonw():
    # 优先用"当前正在运行这个脚本的解释器"所在目录里的 pythonw.exe，
    # 这样能保证和当前 python/pip 用的是同一个环境。
    candidate = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    if os.path.isfile(candidate):
        return candidate
    found = shutil.which("pythonw")
    if found:
        return found
    return None


def startup_dir():
    return os.path.join(
        os.environ.get("APPDATA", ""),
        "Microsoft", "Windows", "Start Menu", "Programs", "Startup",
    )


def startup_vbs_path():
    return os.path.join(startup_dir(), "WorldClockWallpaper.vbs")


def cleanup_legacy_startup_entries():
    """清理旧版本留下的文件（旧的 .lnk 方式，或者本次要重新生成的 .vbs），
    避免重复/过期内容干扰。"""
    for name in ("WorldClockWallpaper.vbs", "WorldClockWallpaper.lnk"):
        path = os.path.join(startup_dir(), name)
        if os.path.exists(path):
            os.remove(path)


def vbs_string_literal(text):
    """把任意字符串转成合法的 VBScript 字符串字面量（正确处理内部引号）。"""
    return '"' + text.replace('"', '""') + '"'


def try_create_scheduled_task(pythonw_path):
    subprocess.run(
        ["schtasks", "/Delete", "/TN", TASK_NAME, "/F"],
        capture_output=True, text=True,
    )  # 忽略结果：任务不存在也没关系

    tr_value = f'"{pythonw_path}" "{WALLPAPER_SCRIPT}"'
    result = subprocess.run(
        [
            "schtasks", "/Create",
            "/TN", TASK_NAME,
            "/SC", "ONLOGON",
            "/RL", "LIMITED",
            "/F",
            "/TR", tr_value,
        ],
        capture_output=True, text=True,
    )
    return result


def create_startup_folder_entry(pythonw_path):
    """不需要管理员权限的退路：往「启动」文件夹写一个 .vbs，登录时静默运行。"""
    os.makedirs(startup_dir(), exist_ok=True)
    run_arg_value = f'"{pythonw_path}" "{WALLPAPER_SCRIPT}"'
    vbs_content = (
        'Set objShell = CreateObject("WScript.Shell")\n'
        f"objShell.Run {vbs_string_literal(run_arg_value)}, 0, False\n"
    )
    # 不显式指定 encoding：VBScript 在没有 BOM 时按系统 ANSI 代码页读取 .vbs
    # 文件，用平台默认编码写入正好一致；反正路径通常是纯 ASCII，编码选择在
    # 绝大多数情况下不影响结果。
    with open(startup_vbs_path(), "w", errors="replace") as fh:
        fh.write(vbs_content)


def main():
    if os.name != "nt":
        print("[提示] 本脚本只能在 Windows 上设置开机自启动。")
        return 1

    pythonw_path = find_pythonw()
    if not pythonw_path:
        print("[错误] 没有找到 pythonw.exe / python.exe。")
        print('请确认已安装 Python，且安装时勾选了 "Add python.exe to PATH"，')
        print("然后重新打开一个新的命令行窗口再运行本脚本。")
        return 1

    print(f"找到 Python 解释器：{pythonw_path}")

    cleanup_legacy_startup_entries()

    result = try_create_scheduled_task(pythonw_path)
    if result.stdout.strip():
        print(result.stdout.strip())

    if result.returncode == 0:
        print()
        print(f'已通过任务计划程序创建 "{TASK_NAME}"（触发条件：登录时）。')
        print("实际会静默运行：")
        print(f'  {pythonw_path} "{WALLPAPER_SCRIPT}"')
        print()
        print("下次登录之后，可以用下面这条命令检查它有没有真的跑起来：")
        print(f'  schtasks /Query /TN "{TASK_NAME}" /V /FO LIST')
        print('重点看 "Last Run Time" 和 "Last Result"（0 表示成功）。')
    else:
        print()
        print("[提示] 任务计划程序创建失败（常见原因：需要管理员权限），错误信息：")
        print("  " + (result.stderr.strip() or "(无详细信息)"))
        print("改用不需要管理员权限的「启动」文件夹方式……")
        try:
            create_startup_folder_entry(pythonw_path)
        except OSError as exc:
            print(f"[错误] 写入启动脚本失败：{exc!r}")
            return 1
        print(f"已创建：{startup_vbs_path()}")
        print("实际会静默运行：")
        print(f'  {pythonw_path} "{WALLPAPER_SCRIPT}"')

    print()
    print("注意：这只会在你下一次【登录】时生效——需要完整注销后重新登录，")
    print("或者重启电脑才能测试效果；单纯锁屏/解锁、或从睡眠中唤醒都不会")
    print("重新触发它。可以先手动双击一下上面提到的文件/用任务计划程序里的")
    print("\"运行\"，确认命令本身没问题，不用等重启。")
    print()
    print("如需取消自启动，请运行 uninstall_autostart.bat")
    return 0


if __name__ == "__main__":
    sys.exit(main())
