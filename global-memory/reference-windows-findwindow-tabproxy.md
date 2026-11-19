---
name: windows-findwindow-tabproxy
description: FindWindow/窗口标题判断程序是否在跑会在 Win11 假阳性——命中的是 explorer 的 Windows.Internal.Shell.TabProxyWindow；改用程序自己的命名互斥体
metadata:
  type: reference
---

**别用 `FindWindowW(None, "<应用标题>")` 或 `Get-Process | ? MainWindowTitle -eq ...` 判断程序是否在运行**：Win11 上即使应用已退出，explorer.exe 仍持有同名任务栏/Alt-Tab 代理窗（类名 `Windows.Internal.Shell.TabProxyWindow`），FindWindow 会返回非 0。2026-11-08 实测 cc-hud 已停，`FindWindow(None,"cc-hud")` 仍命中 owner=explorer 的代理窗，导致验收脚本误报 `hud_running`。

**判据/做法**
- 查程序自己的命名互斥体：`OpenMutexW(SYNCHRONIZE=0x00100000, False, r"Local\<name>")`，句柄非空=在跑，`CloseHandle` 收尾；程序侧用 `CreateMutexW` 建同名互斥体做单实例。
- 需要拿窗口时再按 owner PID 选：`EnumWindows` + `GetWindowThreadProcessId`（设 argtypes）比对 runtime pid，别按标题。
- 同理 `FindWindow` 也适合做"是否已开窗"的反例教训——标题不是身份，pid/互斥体才是。

**How to apply:** 写"验收前先检测/要求退出常驻实例"的脚本、做单实例闸门、判断 GUI 是否起来时。相关：[[reference-windows-window-capture-pixelcheck]]、[[reference-windows-tray-icon-registration]]。
