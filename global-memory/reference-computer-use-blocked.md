---
name: computer-use-blocked
description: computer-use 能力边界（2026-10-09 更新）：终端与 Electron 桌面窗口可驱动（截图有效），但 Electron 的 UIA 只有空区域节点读不到正文；Chrome 触发 browser_url_policy 终止整轮；browser-use 是应用内浏览器不是用户的 Chrome，user-browser-use 会中途下线；Windows Terminal 的 UIA 无文本缓冲区。
metadata:
  type: reference
---

# computer-use：终端能动，浏览器是硬墙

**旧结论已作废**：本文件曾记「computer-use 在 auto 模式被权限分类器全量拦掉」（2026-09-20 的观察）。
2026-10-08 实测**不再成立** —— 对普通桌面应用（Windows Terminal）以下调用全部成功：
`list_windows`、`get_window_state(include_screenshot=true)`、`press_key(key="Return", window={app,id})`，
键盘事件真的进了 TUI（一个 CLI 的 onboarding 界面被我从「选配色」推进到「连账号」页）。

**但浏览器是硬边界**：一旦对 Chrome 窗口调 `get_window_state`，返回
`error.code = browser_url_policy`、`reason = insufficient_url_confidence`、
`policy = url_verification_required`，并且消息明说 **“Computer Use has been stopped for this turn”**
—— 不是这一条调用失败，是**整轮 GUI 控制被终止**，重试也不会放行。所以：
- 需要「在网页里选账号 / 点允许」这类步骤，**只能用户自己做**，别去试。
- 只要任务里可能碰到浏览器，先把终端侧的事做完，再单独把浏览器那一步交给用户，避免半轮作废。

**调用细节（省得再试错）**：
- `get_window_state` / `press_key` 的必填参数是 **`window: {app, id}`**（`app` 用 `process:<exe全路径>` 原样抄，
  `id` 原样抄 `list_windows` 的值）；传 `windowId` 会直接 schema 报错。
- `press_key` 用 X11 键名（`Return`、`Tab`、`Control_L+a`），加 `post_action_state=true` +
  `post_action_include_screenshot=true` 才能一次拿到动作后的画面。
- **Windows Terminal 的 UIA 树只有结构没有文本**（节点是「终端/滚动条/选项卡」，读不到屏幕上的命令行文字）
  → 判断终端内容必须 `include_screenshot=true` 看图，别指望 `include_text`。
- 窗口 `bounds` 里 `x=-7,y=-7` 是最大化窗口；`x=-25600` 表示被最小化。

**仍然有效的老替代手段**（不碰界面就能证明 GUI 应用在干什么）：进程命令行
（`Get-CimInstance Win32_Process`）、性能计数器（`\GPU Process Memory(*)\Local Usage`、`\GPU Engine(*)\Utilization Percentage`）、
`nvidia-smi --query-gpu=clocks_throttle_reasons.active`（0x400 = SW Power Cap）、应用自己的日志/状态文件、
`EnumWindows`+`GetWindowText`+`DwmGetWindowAttribute(14)` 枚举（含 cloaked）、UIA `ControlType=TabItem` 读标签标题、
`strings -n 3 app.exe` 读内嵌前端/Go 字符串表看判断逻辑。
⚠ 枚举结果必须肉眼校验形状再下结论（2026-09-22 我用 `StringBuilder(GetWindowTextLength+2)` 把标题截成 1 字符，
拿坏数据断言「系统里没有这些窗口」，结论正好反）；⚠ 应用自带监控面板会说谎（面板显示 GPU 0%，实测显存 7.7 GB、利用率 97%）。

**Electron 桌面应用：能驱动，但只能看图**（2026-10-09 实测 Gemini 桌面版
`C:\Users\Admin\AppData\Local\Google\Gemini\app-<ver>\Gemini.exe`）：`list_apps` 能列到它、
`get_window_state(include_screenshot=true)` 出图正常，**不触发** `browser_url_policy`（那条只管 Chrome 窗口）。
但 `include_text=true` 拿到的 UIA 树只有 15 个空「区域」节点 + 最小化/最大化/关闭三个按钮，
**网页正文一个字都读不到** ⇒ 判断它显示什么只能靠截图，坐标点击也全靠图上的位置。

**两个浏览器通道的区分（2026-10-09 踩过）**：
- `browser-use`（Qoder 自带的那套）连的是**应用内浏览器**，`list_pages` 只有 `about:blank`，
  **看不到也控制不了用户自己的 Chrome 标签页**。别拿它当「用户浏览器的遥控器」。
- `user-browser-use`（Browser Connector）才是连用户 Chrome 的，但它**会在会话中途整个下线**
  （某次 system-reminder 直接把它从可用列表里移除）。所以依赖它的取证要当场做完，别规划成多步流程。

**`run_steps` 往 Windows Terminal 打字时，用户会移动窗口**：一次批量输入里窗口 bounds 从
`(223,202)` 变成 `(302,333)`，结果发出去的按键落到了别处，屏幕上留下 `/l` 这种半截内容。
⇒ 给用户演示 TUI 时，每步都重新 `list_windows` 拿 id 并带截图复核，不要连着批量发按键。

**给用户的操作指令怎么写**：他明说「我不会英文，不会操作」，所以要么我自己用 computer-use 做掉，
要么把动作降级成「哪个窗口标题、哪一行、按什么键」并附一条他点完能自查的命令；
涉及浏览器的部分单独拎出来问，别混在长段说明里。
**但交给用户照敲的命令，我自己必须先跑过一遍**（2026-10-09 我把没实测过的 `/login` 和一个漏了 `-` 的
`ag.cmd` 写成步骤给他，两次都白跑，见 [[feedback-no-unverified-cause-claims]]）。

相关：[[feedback-rigor-audit]]、[[feedback-plain-language-first]]、[[feedback-capability-boundaries]]、
[[reference-inapp-browser-verification]]、[[reference-windows-window-capture-pixelcheck]]、[[user-role]]
