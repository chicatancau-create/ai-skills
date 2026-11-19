---
name: reference-windows-window-capture-pixelcheck
description: 在本机证明一个 Windows 桌面窗口「真的渲染出来了」的取图与判读方法：PrintWindow 在 user32、WebView2 窗口 PrintWindow 全黑须改屏幕 BitBlt、SetForegroundWindow 被前台锁挡、ctypes.wintypes 缺 c_long、DPI 错位、原生错误框取不到文字
metadata:
  type: reference
---

要回答「这个 GUI 到底画成什么样了」，别只看进程活着或窗口存在 —— 用像素证据。本机（2560×1600 @ 300 Hz、DPI 120、缩放 125%）实测要点：

## 取图

- **`PrintWindow` 在 `user32`，不在 `gdi32`**（`ctypes.windll.user32.PrintWindow`）。flag 用 `PW_RENDERFULLCONTENT = 2`。配合 `GetWindowDC → CreateCompatibleDC → CreateCompatibleBitmap → SelectObject → PrintWindow → GetDIBits`。
- **不要用「屏幕区域截图」代替 PrintWindow**：`SetForegroundWindow` 会被 Windows 的**前台锁**拦住（非前台进程调用无效），于是 `ImageGrab.grab(bbox=窗口矩形)` 拍到的是压在上面的别的窗口 —— 我有一次拍 Qt 窗口结果拍到满屏 B 站视频卡片。
- **`ctypes.wintypes` 没有 `DEVMODEW` / `BITMAPINFO` / `RGBQUAD`**，要自己下 `ctypes.Structure`。`GetDIBits` 在 `biClrUsed=0`、32 bpp 时直接传一个 `BITMAPINFOHEADER` 就够，不必凑完整 BITMAPINFO。
- **先 `SetProcessDPIAware()`**，否则 `GetWindowRect` 与截图坐标系不同源，125% 缩放下只会拍到一条黑边。
- 判读要落到可数的量：`PrintWindow` 返回值 + 窗口类名 + 像素采样计数（例如近黑像素数、目标色像素数），而不是「看着没问题」。

## WebView2 / DirectComposition 窗口：PrintWindow 会给你一张全黑图（2026-10-30 实测）

pywebview、Electron 这类走 WebView2 的窗口，内容用 DirectComposition 合成，**`PrintWindow(..., PW_RENDERFULLCONTENT)` 返回 0，取到的是纯黑位图**（判据：`getextrema()` 返回 `(0, 0)`，别只看"文件生成了"）。

- 唯一可行办法：`GetDC(None)` + `BitBlt(SRCCOPY)` 按窗口矩形从**屏幕 DC** 抠像素，配 `GetWindowRect` 的坐标。前提是该窗口可见且未被遮挡 —— 先 `SetForegroundWindow`，再读回 `GetForegroundWindow()` 确认它真的拿到了前台（拿不到也照样拍，只是可能被别的窗口压住）。
- 窗口类名会骗人：同一个 pywebview 应用，弹错误框时类名是 `#32770`（对话框），主窗口是 `WindowsForms10.Window.8.app.0.*`（WinForms 宿主）。**按标题匹配 + 按宽度过滤（>300px）** 比认类名稳。
- **同一个窗口，`GetWindowRect` 在调 `SetProcessDpiAwareness()` 前后返回的是两套坐标**（本机 125% 缩放实测
  820×560 逻辑 vs 1025×700 物理）。所以**枚举窗口和截图必须在同一次进程、同一 DPI 感知状态下做**，
  否则拿旧矩形去截新坐标系，会截出尺寸错乱（我截出过 352×1373）或整块偏移的图。
  判据：截图后立刻打印 `im.size` 与预期矩形对照，别只看"文件生成了"。
- **`ctypes.wintypes` 没有 `c_long` / `c_uint` / `c_ushort`**（只有 HWND/RECT/DWORD 那些），
  自下 `BITMAPINFOHEADER` 时必须用 `ctypes.c_long` / `ctypes.c_ushort`，写成 `wt.c_ushort` 直接 `AttributeError`。
- 拿到全黑图**不要报"应用渲染失败"** —— 那是取图方法错，应用可能完全正常。换 BitBlt 重拍再判。

## 认窗口

窗口类名能直接暴露技术栈，比标题可靠：`Chrome_WidgetWin_1` = Chromium/Electron；`#32770` = Win32 对话框（含 Electron 错误框）；`Qt683QWindowIcon` = Qt 6.8.3 原生窗口；`CodeWeaveNativeWindow` = 自研 Win32。用 `EnumWindows` + `GetWindowThreadProcessId` 按 PID 过滤，再 `IsWindowVisible`。

## 原生错误框的文字

- Electron/Win32 的 `#32770` 错误框，正文**取不到**：`GetWindowTextW` 和 `SendMessageW(WM_GETTEXT)` 递归遍历子控件只会拿到按钮文字（如「确定」）。
- `ELECTRON_ENABLE_LOGGING=1` 对**主进程未捕获异常无效**，控制台仍是空的。
- 唯一可靠办法：`SetProcessDPIAware()` 后按窗口矩形截图（能置顶时）或 `PrintWindow`，再把 PNG 交给视觉读取。注意 `dialog.showErrorBox(title, content)` 的框**标题固定是 "Error"**、正文第一行才是传入的 title —— 别把系统 Error 框误判成「Electron 自带的默认欢迎窗」。

## 无头浏览器（静态页快速取证）

`msedge --headless=new --disable-gpu --window-size=W,H --virtual-time-budget=8000 --screenshot=<png> <url>` 可用；配合本机临时 `python -m http.server` 式服务渲染已构建的 dist，能在不启动整个桌面应用的情况下验证 UI 资产是否完好。

## 判「在不在屏上 / 进程在不在跑」的两个假阴性（2026-10-18 差点据此误诊）

- **`GetSystemMetrics` 在未 DPI 感知的进程里返回的是缩放后的虚拟值**：本机 2560x1600 @125%，没调 `SetProcessDPIAware()` 时量到 **2048x1280**。于是用户存的呼出点 `x=2437` 看起来"跑到屏外"，我差点据此回答"东西被我放到屏幕外了"。任何"坐标是否出屏"的判断，**必须先 `SetProcessDPIAware()` 再量**，或直接用 `SystemParametersInfoW(SPI_GETWORKAREA)`（同样要先 DPI 感知）。
- **自己手写的 `CreateToolhelp32Snapshot`+`Process32FirstW` 枚举会漏报**：同一时刻它返回"一个都没有"，而 `tasklist //FO CSV //NH | grep` 明明列出 `cc-switch.exe` 和两个 `pythonw.exe`。别再拿自写快照当"进程不存在"的证据；用 `tasklist`（bash 里参数要写 `//FI`、`//FO`，单斜杠会被 MSYS 吃掉），或至少两法对照。
- 反过来也成立：**`tasklist` 空输出多半是命令本身没跑起来**（斜杠被吞），不是"没有进程"。先确认它能列出几百行再下结论。

## 2026-11-07 更正：WebView2 的 PrintWindow 并非恒黑；分层窗口 BitBlt 会带桌面

- 上文"WebView2 PrintWindow 返回 0 且全黑"不是普适结论。pywebview 6.2.1 + WebView2 156/157、125% 缩放下实测
  `PrintWindow(PW_RENDERFULLCONTENT)` 返回 1、`max_luma=236`（小卡与大面板都非黑）。
- 反过来，窗口带 `WS_EX_LAYERED`（整窗 alpha）时，屏幕 BitBlt 会把窗口**后面的桌面/别的应用**一起拍进来
  （截图里能看到底层文字），不能直接当 UI 证据。
- 可靠组合：先把 alpha 临时设为 1.0（`SetLayeredWindowAttributes`），PrintWindow 抓图，再恢复原 alpha。
- 125% 下 PrintWindow 位图是 **CSS 尺寸**（≈物理宽/1.25），画面右侧像被裁；判据用页面内 `innerWidth`、
  `devicePixelRatio`、`scrollWidth==clientWidth` 与逐元素 `getBoundingClientRect().right`，别从截图下"布局溢出"结论。
- **镂空窗口（LWA_COLORKEY）用屏幕 BitBlt 会看到桌面，这是功能生效而不是穿透 bug**：证明办法是量窗口矩形内
  等于键色的像素数（背景区应≈0），并读回 `flags=3`；注意抓图前不要再调只会带 `LWA_ALPHA` 的 set_alpha，
  它会把 flags 覆盖成 2。
- **未 DPI 感知时 `GetMonitorInfo` 的 `rcWork` 也是虚拟化的**（2560 屏量成 2048）：先 `SetProcessDpiAwarenessContext(-4)`
  再 `EnumDisplayMonitors`，否则按右下角裁任务栏/定位会裁到别的窗口（实测裁出过 Clash 窗口的一条边）。

## 2026-11-08：任务栏/托盘像素取证的两个坐标系陷阱

- **托盘不能按「工作区底边」裁图**：`rcWork` 本来就不含任务栏，按它裁只会拍到任务栏上方的窗口
  （我截到过自家卡片的一角，还误以为是托盘）。要拍托盘就用**整屏坐标**：先 DPI 感知，再
  `GetSystemMetrics(0/1)` 取 2560×1600，裁 `(0, h-70, w, h)`。
- **Win11 托盘是 XAML 组合**：`TrayNotifyWnd` 句柄为 0、`Shell_NotifyIconGetRect` 返回
  `0x80004005` 属正常现象；溢出按钮实际能在 UIA 里找到（Name=「显示隐藏的图标」，
  Class=SystemTray.NormalButton），但 .ps1 必须存成 **UTF-8 with BOM**，且 Invoke 后要等约 1.4s，
  面板类名是 `TopLevelWindowForOverflowXamlIsland`。详见 [[reference-windows-tray-icon-registration]]。
  面板未展开时按该窗口矩形裁图会拍到背景应用（我拍到过 IDE 的文件列表），判据必须是展开后的证据。
- **颜色断言要先回源码取真值**：取证脚本里硬编码的强调色可能来自旧实现；这次 `#34D399`
  属于旧 tkinter 托盘，屏幕上另一个 `#00D76B` 绿图标是别的应用。严格容差 10 px、放宽到 60 才 225 px
  的差异说明「颜色不是同一个东西」，不是「图标变淡了」。
- **按标题取窗会拿到别人的窗口**：本机同时开着用户旧的 `cc-hud.pyw`，`FindWindowW(None,"cc-hud")`
  第一次命中的是它；`GetWindowThreadProcessId` 不声明 `argtypes=[HWND, POINTER(DWORD)]` 时 64 位句柄
  按 int 截断，归属判断全假。正确做法：`EnumWindows` 枚举**所有同标题**窗口，逐个取 owner PID，
  选与运行态 JSON 中 pid 一致的那个；`dot_window` 同理。取证脚本据此只操作本进程窗口，避免误关用户实例。
- **托盘取证器已按整屏条带修**：`tools/tray_pixel.py` 原来裁 `rcWork` 底边（不含任务栏），现改为
  `(sw-800, sh-64, sw, sh)` 并先 DPI 感知；收尾按 runtime pid，不再 `FindWindow` 关窗。

## 2026-11-08：`FindWindow("cc-hud")` 会命中 explorer 的任务栏代理窗

- 即使目标应用已退出，`FindWindowW(None,"cc-hud")` 仍可能返回一个**可见**窗口：类名
  `Windows.Internal.Shell.TabProxyWindow`、owner 是 `explorer.exe`（本机 PID 10644）——这是 Win11 任务栏的
  tab 代理窗，不是应用本体。用它做“应用是否在跑”的预检会**误报 running**。
- 正确判“应用是否在跑”：查应用自己的命名互斥体（`OpenMutexW(SYNCHRONIZE, False, "Local\\cc-hud-single")`），
  或枚举窗口后按 owner PID 过滤（`GetWindowThreadProcessId` 必须设 argtypes）；不要按标题存在性下结论。

## 2026-11-08：合成点击/剪裁前必须设 DPI 感知

- **`SetCursorPos`/`mouse_event` 在未 DPI 感知的进程里按逻辑坐标解释**：本机 125% 下点任务栏溢出箭头
  `(2017,1533)` 实际落到时钟附近，弹出的是日历而不是溢出面板。任何合成点击脚本先
  `SetProcessDpiAwarenessContext(-4)`（或 `shcore.SetProcessDpiAwareness(2)`）再发坐标。
- **托盘隐藏槽位**：`GetRect` 返回的 rect 可能落在任务栏空白处，按它截图 accent 像素为 0 是“图标被隐藏”，
  不等于“没注册”。可见性判据只能靠展开溢出面板后的 UIA/截图，或看 `NotifyIconSettings` 的提升项。

Related: [[reference-inapp-browser-verification]], [[reference-headless-browser-debris]], [[reference-computer-use-blocked]], [[reference-qt-qml-build-traps]], [[reference-pywebview-host-traps]]
