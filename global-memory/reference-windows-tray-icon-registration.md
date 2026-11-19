---
name: reference-windows-tray-icon-registration
description: Windows 托盘图标注册与取证判据：szTip WCHAR[128]、NIM_ADD=1≠可见、GetRect 要 32B 且 uID 一致；窗口不能 HWND_MESSAGE、uID 必须显式 1，可见性由 HKCU NotifyIconSettings 的 IsPromoted（按真实宿主 exe）决定；隐藏区图标调暗，像素判据用 HSV 色相而非 RGB；GetRect=0 不是注册证据；含溢出面板 UIA 与 runtime pid 归属
metadata:
  type: reference
---

在 Windows 上证明「托盘图标真的出现了」时，以下几条是 2026-11-08 实测钉死的。

## 结构体：szTip 必须是 WCHAR[128]

- `NOTIFYICONDATAW.szTip` 是 **128 个 WCHAR**（256 字节），不是 64。写成 64 时 x64 下
  `sizeof(struct)` = **856**，正确值 **984**；后面的 `dwState/dwInfoFlags/guidItem` 全部错位。
- 错位后 `Shell_NotifyIconW(NIM_ADD)` **照样返回 1**，所以「tray_added=true」只能证明调用被接受，
  不能证明图标或提示可用。**回归判据：`ctypes.sizeof(_NID) == 984` 且 `_NID.szTip.size == 256`**
  （ctypes 的 `.size` 报的是字节数）。
- 同理 `ICONINFO` 真布局是 `fIcon/xHotspot/yHotspot/hbmMask/hbmColor`（32 字节，x64）；
  写成 `fIcon/fMask/...`（24 字节）会让 `CreateIconIndirect` 返回 NULL，`hIcon=0` 时 NIM_ADD 仍成功，
  外壳摆一个透明空槽。`_hicon` 应在 NULL 时直接抛错，别留不可见的图标。

## Win11 溢出面板：UIA 能打开，但要按下面做

- 溢出按钮在 `Shell_TrayWnd` 的 UIA 树里：`ClassName=SystemTray.NormalButton`，
  AutomatioId 是 `SystemTrayIcon`，**Name 是「显示隐藏的图标」**（英文系统为 "Show hidden icons"）。
  按 AutomationId `ShowHiddenIcons` 找会失败，按 Name 正则可靠。
- **PowerShell 5.1 下 .ps1 必须存成 UTF-8 with BOM**，否则中文正则按 ANSI/GBK 读成乱码，
  脚本会报「no overflow button」——这是编码问题，不是按钮不存在。
- Invoke 后要等 **约 1.4 秒**（900ms 不够）再找面板。面板类是
  `TopLevelWindowForOverflowXamlIsland`（不是旧的 `NotifyIconOverflowWindow`），
  在 root children 里；面板尺寸约 293×193，可回读每一项的 Name 与 BoundingRectangle。
- `TrayNotifyWnd` 句柄为 0 属正常；`Shell_NotifyIconGetRect` 返回 `0x80004005` 只在 hWnd/uID 与注册时一致时才有判读意义（见 2026-11-08 更正）。
- 面板未展开时不要按 `TopLevelWindowForOverflowXamlIsland` 的矩形截图：窗口对象可能已存在，
  拍到的是背后的应用。判据必须是展开后的截图或展开后回读的 UIA 项。

## 判断「图标到底有没有出现」的分层法

1. 可见托盘：枚举 `Shell_TrayWnd` 下 `SystemTray*` 元素的 Name/Rect，逐个核对（别只数数量）。
2. 溢出面板：按上面的方法展开后回读 Name 列表。
3. 颜色断言要先回源码取真值；本机曾把别的应用的 `#00D76B` 绿图标误当目标色。
4. **股票图标对照**：同一进程同时注册 `LoadIconW(None, IDI_APPLICATION)` 和自绘 HICON，
   两者都是 `NIM_ADD=1`。若股票图标也不出现，就不是图标构造问题。
5. **计划任务对照**：用 `schtasks /IT` 以普通用户令牌启动同一探针（先确认 `python.exe` 进程
   的 SessionId 真的在跑），仍不出现 → 是 Shell/会话侧拒绝新托盘项，不是父进程令牌或应用装配。
6. 关窗时**按 PID 关闭，不要按标题 `FindWindow("cc-hud")`**：用户可能同时开着旧版实例，
   按标题会误关他的进程。用运行态 JSON 里记录的 pid，或 `GetWindowThreadProcessId` 核对归属再发 WM_CLOSE。

## 2026-11-08 追加（v4 / GUID / 行为验收）

- **`Shell_NotifyIconGetRect` 要的是 32 字节的 `NOTIFYICONIDENTIFIER`（cbSize/hWnd/uID/GUID），不是 NOTIFYICONDATAW**。
  传 NID 时 cbSize=984，恒返 **`0x80070057 (E_INVALIDARG)`**，会被误读成"图标不存在"。改对后若仍 `E_FAIL`，
  先核对 **uID**：GetRect 的 uID 必须与 NIM_ADD 时一致（2026-11-08 根因，见文末）。`NIM_SETVERSION(4)`、`NIF_GUID|NIF_SHOWTIP` 都不改变可见性。
- **GetRect 不能当"图标存在"的唯一判据**：本机任何新注册都不认；可见性要靠 UIA 清单 + 整条任务栏截图 + 股票图标对照。
- v4 回调语义变了：左键是 `NIN_SELECT(0x400)` / `NIN_KEYSELECT(0x401)`，右键是 `WM_CONTEXTMENU(0x7B)`；
  `TRAY_EVT` 映射表必须同时含 0x400/0x401/0x7B，否则 v4 下点击/菜单全哑。
- x64 字段偏移可用来最后排除结构问题：`hWnd=8, szTip=44, dwState=300, guidItem=956, hBalloonIcon=976, sizeof=984`。
- **行为可以独立于图标可见性验收**：`PostMessageW(tray_hwnd, 0x801, 0, 0x202)`（`WM_TRAY` + `WM_LBUTTONDOWN`）
  实测主窗隐藏、圆点出现、再次点击恢复。这条只证明消息泵与隐藏/恢复链路，不证明图标像素。
- 运行态 JSON 必须带 **pid**，而且这个 pid 是**宿主子进程**的 pid（`.venv` 的 `python.exe` 是启动器，`Popen.pid` ≠ runtime pid）。
  托盘/窗口探针按 runtime pid 判归属（`GetWindowThreadProcessId(hwnd) == runtime.pid`），关闭时 WM_CLOSE 后等该 pid 退出、
  再 `taskkill /PID` 兜底；`FindWindow("cc-hud")` 会命中用户旧实例，残留实例还会占住 runtime 让后续门禁卡在 `after_start`。
- ~~判定本机 Shell 会话不接受任何新托盘项~~（**2026-11-08 当天被推翻，见下节**）：股票图标/计划任务/可见顶层窗对照
  仍不显示，当时的结论下错了；不要把它当"环境不可修"的依据。

## 2026-11-08 更正：根因是 message-only 窗口 + `uID=0`

同一天继续排查，最小探针（隐藏顶层工具窗、uID=1、延迟 0.6s 再 GetRect）**一次成功**，随后定位到两个真实 bug：

1. **托盘窗口不能用 `HWND_MESSAGE`**。message-only 窗口收不到 `TaskbarCreated` 等广播，Win11 Shell 会静默丢弃图标：
   `NIM_ADD=1`、GetRect `E_FAIL`、溢出面板无条目。改为隐藏的**顶层工具窗**：
   `CreateWindowExW(WS_EX_TOOLWINDOW=0x80, class, title, 0, 0,0,0,0, parent=None, ...)`
   （不 `ShowWindow`，不进 Alt+Tab）。顶层窗在 `webview.start` 之前用主线程创建即可注册成功。
2. **`NOTIFYICONDATAW.uID` 必须显式赋值**。ctypes 零初始化 → uID=0；`NIM_ADD` 仍返回 1，但 GetRect 查 uID=1
   恒 `E_FAIL`，Shell 也不显示。设 `nid.uID = 1`，GetRect 的 `NOTIFYICONIDENTIFIER` 用**同一个值**。
   修后宿主 `tray_getrect_rc=0`、`tray_rect` 非零（实测 `[2038,1540,2078,1600]`），此前恒 E_FAIL。

**修后仍未过像素门禁（2026-11-08）**：
- Win11 把新图标放进**隐藏槽位**：GetRect 有 rect，但按 rect 截图像素为 0，溢出面板 UIA 11 项仍无 cc-hud，
  `HKCU\Control Panel\NotifyIconSettings` 下也没有 `.venv\pythonw.exe` 条目（旧 PyCharm pythonw 有条目且 `IsPromoted=0`）。
- 换成 `python.exe` 的独立探针同样只在隐藏区拿到 rect；可见性受「任务栏设置 → 其他系统托盘图标」的 per-exe 提升开关控制，
  没有受支持的 API 强制提升。判据仍是：**GetRect=0 ≠ 可见**。
- explorer 重启后图标丢失；已加 `RegisterWindowMessageW("TaskbarCreated")` 后重发 NIM_ADD，但本机未观测到恢复，
  重新启动宿主可恢复 `GetRect=0`。
- 结论口径：**注册链路已修好（E_FAIL→0），像素可见性未验证/被系统隐藏**；不要再说"Shell 完全拒绝"，
  也不要因 GetRect=0 就宣称托盘通过。

- **Shell 归属只读核对（2026-11-08 末）**：本机 `Shell_TrayWnd` 与 `TopLevelWindowForOverflowXamlIsland` 同属
  explorer PID 10644（Console/会话 1，可见）；另有一个 explorer 63132 但未持任务栏；`TrayNotifyWnd` 与
  `NotifyIconOverflowWindow` 均不存在（Win11 XAML 托盘）。这说明托盘确由当前 explorer 托管，与"进程在别的会话"无关。

## 2026-11-08 最终定位：可见性由 `NotifyIconSettings.IsPromoted` 控制，GetRect 不是判据

- **注册表条目按“真实宿主 exe”记，不按 `.venv` 启动器**。`.venv\Scripts\pythonw.exe` 只是启动器，子进程映像是基础解释器
  `D:\PyCharm\Python\pythonw.exe`；`HKCU\Control Panel\NotifyIconSettings\2591989311186454988`（该 exe，UID=0）
  存在但 `IsPromoted=0`（继承旧 tkinter 版的“隐藏”），所以新宿主注册正确也不显示。
  用 `Set-ItemProperty ... -Name IsPromoted -Value 1 -Type DWord` 提升后，**常驻实例** rect `[2038,1540,2078,1600]`
  实测 **36 个强调色像素**（`tray-final.png`），图标确实显示。之前“没有 `.venv` 条目 → Shell 拒绝”的结论作废。
- **`GetRect=0` 不是“已注册”的证据**：同一进程里股票图标、自绘图标、不同 uID 都返回同一 rect
  `[2038,1540,2078,1600]`，而该槽位 max_luma=255（是别的图标）。判可见性只能靠像素/UIA/注册表条目。
- **explorer 重启**：提升后重启 explorer，`TaskbarCreated` 重发 NIM_ADD 未观测到恢复；重开宿主恢复 `GetRect=0`。
- ~~短命实例与常驻实例不一致（未定位）~~（**2026-11-08 当日闭合，见下节**）：0 像素是**容差**导致的假失败，不是实例差异。

## 2026-11-08T03:0x 闭合：隐藏区图标被调暗 → 按色相判定；门禁通过

- **隐藏槽位里的图标会被系统整体调暗**（环色接近 `(0,96,60)`，不是原色 `(52,211,153)`）。
  用 RGB 距离 ±26/±60 判定会得到 0；改用 **HSV 色相 0.30<h<0.55、s>0.35、v>0.12** 后，
  同一张截图（常驻与短命实例）都数出 **282 个绿像素**，`tools/tray_pixel.py` 输出
  `accent_pixels=282..284, tray_added=true, shell_getrect=0, ok=true`。判据是"绿色环"，不是精确色值。
- **`tray_pixel` 起实例前先等单实例互斥体释放**（`OpenMutexW("Local\cc-hud-single")`，最多 20s），
  否则上一个取证实例还在退出时，新宿主会静默自杀、runtime 缺失，门禁报 `tray_added=null`。
  同时启动前删旧 `runtime.json`，GetRect 用 runtime 里的 `tray_uid`（不是硬编码 0）。
- **`RegisterWindowMessageW` 必须声明 `argtypes=[LPCWSTR]` / `restype=UINT`**：未声明时传 Python str 会抛
  `ctypes.ArgumentError`，托盘初始化被 `_start_tray` 吞掉 → `tray_added=false`，部分验收里宿主 1s 内退出
  （表现为整批 `no hwnd`）。补上后窗口取证恢复全绿。
- 取样要重试：Shell 布局图标有延迟，`tray_pixel` 最多 12 次 × 1.5s，任一帧 ≥20 绿像素即通过；
  单次取样会在忙时误判失败。
- 验收口径更新：**像素门禁可通过**；`IsPromoted=1` 仍是让图标进可见区的前提，`GetRect=0` 仍不能单独证明存在。
- 结论：`NIM_ADD=1`、`GetRect=0`、`pixel>0` 是三件事；可见性的真判据是 `IsPromoted=1` + 实拍/UIA。
- 注：顶层窗在 `webview.start` 前用主线程创建“能注册”，但会让 `WM_TRAY` 不再派发（见
  [[reference-pywebview-host-traps]]），实际仍用 GUI 线程 `BeginInvoke` 创建。

Related: [[reference-windows-window-capture-pixelcheck]], [[reference-pywebview-host-traps]], [[reference-windows-batch-entry-encoding]]
