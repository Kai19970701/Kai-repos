# -*- coding: utf-8 -*-
"""
把「世界时钟地图壁纸」加入开机自启动（Windows 任务计划程序，登录时触发）。

之前用纯 .bat 实现这个逻辑（找 pythonw.exe 路径、拼 schtasks 命令）反复踩到
cmd.exe 解析上的坑（嵌套引号、代码页、括号转义……），所以改成在这里用 Python
写：找解释器路径用 shutil.which，调用 schtasks 用 subprocess.run(参数列表)
而不是拼一整条命令行字符串，Windows 会自动正确处理带空格路径的引号，不需要
手工转义。
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


def cleanup_legacy_startup_entries():
    """清理旧版本用「启动」文件夹方式留下的文件，避免同时存在两套自启动。"""
    startup_dir = os.path.join(
        os.environ.get("APPDATA", ""),
        "Microsoft", "Windows", "Start Menu", "Programs", "Startup",
    )
    for name in ("WorldClockWallpaper.vbs", "WorldClockWallpaper.lnk"):
        path = os.path.join(startup_dir, name)
        if os.path.exists(path):
            os.remove(path)
            print(f"已清理旧版本残留：{path}")


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

    # 先删除同名的旧任务（如果存在），避免重复运行报错；不存在也没关系，忽略结果。
    subprocess.run(
        ["schtasks", "/Delete", "/TN", TASK_NAME, "/F"],
        capture_output=True, text=True,
    )

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

    if result.stdout.strip():
        print(result.stdout.strip())

    if result.returncode != 0:
        print("[错误] schtasks 创建任务失败：")
        print(result.stderr.strip())
        return 1

    print()
    print(f'已创建计划任务 "{TASK_NAME}"（触发条件：登录时）。')
    print("实际会静默运行：")
    print(f'  {pythonw_path} "{WALLPAPER_SCRIPT}"')
    print()
    print("注意：这只会在你下一次【登录】时生效——需要完整注销后重新登录，")
    print("或者重启电脑才能测试效果；单纯锁屏/解锁、或从睡眠中唤醒都不会")
    print("重新触发它。")
    print()
    print("下次登录之后，可以用下面这条命令检查它有没有真的跑起来：")
    print(f'  schtasks /Query /TN "{TASK_NAME}" /V /FO LIST')
    print('重点看 "Last Run Time" 和 "Last Result"（0 表示成功）。')
    print()
    print("如需取消自启动，请运行 uninstall_autostart.bat")
    return 0


if __name__ == "__main__":
    sys.exit(main())
