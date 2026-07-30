' 静默启动世界时钟壁纸（不弹出黑色控制台窗口）
' 双击本文件，或将其加入开机启动项即可。

Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

Set objShell = CreateObject("WScript.Shell")
objShell.Run "pythonw.exe """ & scriptDir & "\wallpaper.py""", 0, False
