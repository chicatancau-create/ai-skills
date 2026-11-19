---
name: reference-pywebview-host-traps
description: pywebview 6.2.1 + WebView2 宿主硬坑：http_server 在 start、js_api 公开属性会被序列化致注入静默失败、WinForms 饿死 Python 线程、125% DPI 右侧被裁、分层窗口取图、file:// 缓存旧 bundle、loaded 时序、托盘要隐藏顶层工具窗+uID=1 且必须 GUI 线程 BeginInvoke 创建（pre-start 主线程会让 WM_TRAY 失效）、次窗口 js_api/easy_drag/合成点击判据
metadata:
  type: reference
---

2026-11-07 把 cc-hud 从 tkinter 重构为 React + pywebview 6.2.1 + WebView2（Python 3.14.2、运行时 156/157、125%）时实测：

1. **`http_server` 是 `webview.start(...)` 的参数**，`create_window()` 没有这个关键字（传了直接 `TypeError`）。
   生产：`webview.start(..., http_server=False, private_mode=False, storage_path=...)` + `file:///.../index.html`。
2. **`window.events.loaded` 回调不带参数**（写 `def on_loaded(self)`），但本组合下会**偶发不触发**。
   必须加幂等兜底：`_after_start` 起线程轮询 `window.native.Handle.ToInt64()`，拿到 HWND 再初始化；
   `loaded` 与轮询共用一把锁 + `_initialized` 标志。
3. **js_api 对象的公开属性会被当 API 序列化**：Bridge 上有 `window_port`（指向 Host）时，pywebview 去读
   `window_port.window.native.browser.webview.ZoomFactor` → `CoreWebView2Controller ... only be accessed from the
   UI thread`，注入线程失败；前端拿不到 `window.pywebview.api`，**静默回落桩数据**（页面看起来有数）。
   修法：内部依赖全部下划线私有，js_api 只暴露方法；前端轮询等 API，`file://` 超时报错，不许用假数据兜底。
4. **WinForms 循环起来 1~2 秒后 Python 后台线程被饿死**（1s 心跳只打两行就停）。所以托盘事件在
   `Tray._wnd`（GUI 线程）同步处理，不用 queue+轮询线程；周期刷新由前端 `setInterval` 调桥接
   （桥接走 .NET 线程，GIL 可用）。
5. **125% DPI 下右侧 1/5 被裁**：pywebview 按物理像素建窗、WebView2 又按系统缩放渲染。修法
   `document.documentElement.style.zoom = String(1/(devicePixelRatio||1))`，切视图时按目标尺寸重设窗口。
   另：PrintWindow 出的是 CSS 尺寸位图，125% 下只覆盖左 80%，看着像布局溢出，实际 DOM 的
   `scrollWidth == clientWidth` —— 先量 `innerWidth/dpr` 再改 CSS。
6. **分层窗口取图**：`WS_EX_LAYERED` + alpha 的窗口做屏幕 BitBlt 会把后面的桌面一起拍进来；取证前临时
   `SetLayeredWindowAttributes(alpha=255)`，PrintWindow 抓完再恢复。
7. **`file://` 会缓存旧 bundle**：改完前端仍看到旧界面时，用全新的 `storage_path`（每次验证一个临时 profile）
   再起，别先怀疑 CSS。
8. **镂空必须在同一层属性里同时给 COLORKEY 和 ALPHA**：`SetLayeredWindowAttributes(..., LWA_COLORKEY|LWA_ALPHA)`
   后，任何一次只带 `LWA_ALPHA` 的 `set_alpha` 都会把 `flags` 从 3 改回 2，颜色键立即失效（`colorkey` 值还在，
   但读回来 `flags=2`）。取证判据：`flags & 1`、`alpha`、`colorkey`（本机 BG `#0b0e14` → COLORREF `0x140E0B`），
   再数窗口矩形内等于底色的像素（实测 **0/379555**）；截图前不能把 alpha 置 1。
9. **不改系统缩放也能验 100%/150%**：`WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS=--force-device-scale-factor=1|1.5`
   实测拿到 `dpr=1` / `1.5`、`innerWidth=2184` / `1456`，配合 `zoom=1/dpr` 两种都无右侧裁切。这是 WebView 缩放，
   不是系统 DPI 档位，报告里要分开写。
10. **托盘图标取证的两个死路**：`GetRect` 对**隐藏/溢出**图标可能返回 `E_FAIL`；hWnd/uID 不一致时也会 E_FAIL
    （2026-11-08：uID 未赋值 0 是根因之一，见 [[reference-windows-tray-icon-registration]]）。
    任务栏**自动隐藏**时 UIA 在 `Shell_TrayWnd` 下找不到「显示隐藏的图标」按钮，屏幕裁剪只会截到别的窗口。
    `NIM_ADD` 成功 ≠ 图标可见（旧版 `hIcon=0` 也会假成功）；修对了 uID 后 GetRect=0 也仍可能只是隐藏槽位。
11. **未 DPI 感知时 `GetMonitorInfo` 返回虚拟化坐标**：2560 宽的工作区量成 2048，于是按右下角裁任务栏会裁错位置。
    任何按工作区裁图/定位的脚本，先 `SetProcessDpiAwarenessContext(-4)`，再用 `EnumDisplayMonitors` 的 `rcWork`。

12. **托盘窗口用隐藏的顶层工具窗，且 `nid.uID` 必须显式设**（2026-11-08）：不要用 `HWND_MESSAGE`——
    message-only 窗口收不到 `TaskbarCreated`，Win11 Shell 静默丢弃图标（`NIM_ADD=1`、GetRect `E_FAIL`）。
    `uID` 默认 0 也会导致 GetRect E_FAIL（查询用 1 时），必须 `nid.uID=1` 且 GetRect 用同值。
    **创建时机：仍用 GUI 线程 `BeginInvoke`**。实测把同一个托盘放在 `webview.start` 之前的主线程创建，
    注册没改善，反而 `WM_TRAY` 不再被派发（tray_click `hidden_after_click=false`），已回退。
    explorer 重启会丢图标，注册 `TaskbarCreated` 后重发 NIM_ADD（本机曾未观测到恢复，重开宿主可恢复）。
    **可见性还受 Win11 `NotifyIconSettings.IsPromoted`（按真实宿主 exe，不是 `.venv` 启动器）控制**，
    且 `GetRect=0` 不等于图标存在。详见 [[reference-windows-tray-icon-registration]]。
13. **js_api 会注入每个窗口**：次窗口可用 `evaluate_js("!!(window.pywebview && window.pywebview.api)")` 自检
    （实测圆点窗 `dot_api=true`）。frameless 窗口 `easy_drag=True` 会吞单击手势，圆的"点一下恢复"类控件要设 `False`。
14. **合成点击不能证明 WebView2 交互链路**：`SendInput` 到圆点中心时 `WindowFromPoint` 返回 WebView2 子窗
    `Chrome_WidgetWin_1`，`cursor_on_dot` 判据失效，DOM click 也没触发。验证接线用「evaluate_js 查 api + 页面内 click 计数」，
    行为链路用 PostMessage 直接打托盘窗口；把"合成点击未命中"写成结论，别写成"功能坏了"。
15. **`.venv` 的 python.exe 是启动器：真正的宿主是它拉起的子进程** —— `Popen.pid` ≠ runtime `pid`。
    验收按 runtime pid 判窗口归属（`GetWindowThreadProcessId(hwnd)==runtime.pid`），关闭发 WM_CLOSE 后等该 pid 退出、
    再 `taskkill /PID` 兜底；`FindWindow("cc-hud")` 会命中用户旧实例，残留实例还会让下一次启动卡在 `after_start`。
    用户入口脚本（本项目 `start-hud.bat`）实测同样 ready/tray=true。

相关：[[reference-windows-window-capture-pixelcheck]]、[[reference-inapp-browser-verification]]
