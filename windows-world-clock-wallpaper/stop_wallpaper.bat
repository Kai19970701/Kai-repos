@echo off
REM 通过窗口标题定位并结束「世界时钟壁纸」进程（不会影响其它 Python 程序）
powershell -NoProfile -Command ^
  "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class W { [DllImport(\"user32.dll\")] public static extern IntPtr FindWindow(string c, string t); [DllImport(\"user32.dll\")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid); }'; $h=[W]::FindWindow($null,'World Clock Wallpaper'); if ($h -ne [IntPtr]::Zero) { $procId=0; [W]::GetWindowThreadProcessId($h, [ref]$procId); Stop-Process -Id $procId -Force; Write-Host '已停止世界时钟壁纸进程。' } else { Write-Host '未找到正在运行的世界时钟壁纸。' }"
pause
