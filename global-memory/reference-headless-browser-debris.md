---
name: headless-browser-debris
description: How to spot and clean leftover headless Chrome/Edge instances (CDP ports 9222/9333, %TEMP%\tmp.* profiles) that agent sessions leave running on this machine
metadata:
  type: reference
---

这台机器上会长期残留 **agent 会话自启的 headless 浏览器**：由 Qoder 的 bash 包装链
（`bash -c "...snapshot-bash-xxx.sh... eval '... msedge/chrome --headless=new ...'"`）
启动，会话结束后 bash 外壳自动退出、浏览器却继续挂着，占几百 MB 内存并在
`%TEMP%` 里留下 Chromium profile 目录。2026-09-22 一次清理发现两组（Edge CDP 9222
+ Chrome CDP 9333，共 22 个进程、约 360MB 工作集），Temp 里同类 profile 目录合计
**796.7 MB**，最早的来自 09-19。

**症状先认出来**：`--headless=new` 的 Chromium **每个 target 会生成一个独立的、被 DWM 遮蔽的顶层窗口**，所以 Windows 11 的 Alt+Tab 里会冒出一堆「只有 favicon + 页面标题、缩略图全白」的卡片，同一个页面重复好几次。这些不是用户的浏览标签，而是残留 headless 实例的窗口。判断步骤：① UIA 读真 Chrome 的 TabItem 列表（按 `ClassName -eq 'Chrome_WidgetWin_1'` 筛窗口，别按标题筛——标题会变）对比一下就知道那些卡片不属于它；② 再按上面三条锁定是哪个 headless 进程。

⚠ **杀掉进程后 Alt+Tab 的卡片不会立刻消失**。2026-09-22 实测：`taskkill /T /F` 干掉 headless 实例之后，那 12 张白卡片在 Alt+Tab 里**一模一样还在**，而同时 `EnumWindows`（含非可见 + `DwmGetWindowAttribute` cloak 位，237 个有标题窗口，其中 219 个非可见/遮蔽）里一个都搜不到这些标题 ⇒ 卡片是 **explorer 渲染的 Alt+Tab 缓存幽灵**，不是活窗口，不占内存、点了没反应。别把它当成「没杀干净」，也别据此再下结论说进程还在。清掉它只能重启 explorer（`Stop-Process -Name explorer -Force`，Windows 会自动拉起来，实测约 1 秒恢复；会闪一下任务栏和桌面，属于用户可见的中断动作，先问再做），或注销/重启。**2026-09-22 实测：重启 explorer 后幽灵卡片全部消失，用户确认 OK。** 重启前先 `New-Object -ComObject Shell.Application` 枚举 `.Windows()` 记下开着的文件夹路径，重启后按原路径 `Start-Process explorer.exe <path>` 开回来。

**判定是不是僵尸（三条都要满足，别只看一条）**：
1. 父链往上第一个还活着的进程已经 `GONE`（`Get-CimInstance Win32_Process -Filter "ProcessId=X"` 逐层查 `ParentProcessId`）。
2. CDP 端口**无人连接**：`Get-NetTCPConnection -RemotePort 9222` 为空。
3. 命令行里是 `--headless=new` + `--user-data-dir=...Temp\...`，即一次性临时 profile。

**清理**：`taskkill /PID <root> /T /F`（杀树）→ 外壳通常已自行退出 → 端口应变 FREE。
删 Temp profile 前先过滤：目录里存在 `Default\` 或 `Local State` 才认定是 Chromium
profile（否则可能是别的程序的 `tmp.*` 目录，实测有两个 0MB 的就因此被跳过），
并且路径不出现在任何存活进程的命令行里。

**别顺手杀掉的**：`127.0.0.1:4173`（CodeWeave 的 `app/server.mjs`，用户 Chrome 里
十几个标签指着它）、`127.0.0.1:5173`（vite dev）、以及父进程是 `Qoder.exe` 的
node/bash（当前会话自己的）。判断依据：今天启动 + 端口有人连 + 用户界面正看着它。

相关：[[reference-computer-use-blocked]]、[[reference-inapp-browser-verification]]、
[[feedback-windows-config-json-encoding]]
