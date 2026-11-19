---
name: reference-windows-display-topology-probe
description: 只读判断本机能否造第二块屏：EnumDisplayDevices/EnumDisplaySettings 的判据、幻影输出与 MuMu 虚拟显示适配器没有模式、手搓 QueryDisplayConfig 结构体易假报 0 paths
metadata:
  type: reference
---

2026-11-08 cc-hud 多屏验收时实测（Windows 10.0.28000、单屏 2560×1600）：

- `EnumDisplayDevicesW(None, i, ...)` 会列出**未挂载输出**和虚拟显示适配器，`StateFlags=0` 不代表可用：
  本机列出 NVIDIA `DISPLAY22–24`、AMD `DISPLAY5–9`、**MuMu Virtual Display Adapter `DISPLAY10–19`**。
- 能否挂载看两条：`EnumDisplaySettingsW(dev, ENUM_CURRENT_SETTINGS=0xFFFFFFFF)` 和 registry mode `0`。
  本机**只有 `\\.\DISPLAY21` 两者都 True**（2560×1600、Generic PnP Monitor）；其余全 False，子显示器枚举也 False。
  装了 MuMu 的虚拟显示适配器 ≠ 能扩展桌面；没有模式就无法 `ChangeDisplaySettings` 挂载，别在无硬件机器上硬造第二屏。
- 手搓 `QueryDisplayConfig(QDC_ALL_PATHS=2)` 的 PATH/SOURCE/TARGET 结构体容易因对齐/字段错误返回 **0 paths 且不报错**；
  优先用 `EnumDisplayDevices`/`EnumDisplaySettings`，或项目里已验证的 `monitors()`。
- 系统 DPI 档位同理：只读确认当前缩放（本机 125%）；改档要动用户显示设置。
  `--force-device-scale-factor=1|1.5` 只能证明 WebView 渲染，报告里必须与"系统级 DPI"分开写。

- **`ChangeDisplaySettingsEx(dev, 1920×1080@60, CDS_TEST)` 可做"有无可挂输出"的只读试配**：本机对
  `DISPLAY22/23/24`（NVIDIA）、`DISPLAY5–7`（AMD）、`DISPLAY10/11`（MuMu）全部返回 **-1（DISP_CHANGE_FAILED）**，
  与"无模式"一致；`Get-PnpDevice -Class Monitor` 只有内屏 `OK`，外接 ACER S271HL 是 **Unknown（未接入）**。
  → 单屏机器无法用软件造第二屏，多显示器门禁只能换硬件；不要用虚拟/模拟数据把该项标通过。
  注意设备名要用原始字符串 `r"\\.\DISPLAY22"`，普通字符串会把 `\\` 吃成 `\.\` 并返回 `BADPARAM(-5)` 误判。

- **启动 MuMu Player 主程序也补不出第二块屏（2026-11-08 实测）**：`D:\Program Files\Netease\MuMu\nx_main\MuMuNxMain.exe`
  起来后 `GetSystemMetrics(SM_CMONITORS)` 仍是 1，DISPLAY10/11 仍未挂载；它只拉起 `MuMuNxService`/Updater，不启动 VMM 实例。
  试完把 MuMuNxMain 与 MuMuNxService 结束掉即可恢复原状（`MuMuRemoteService` 是原本就在跑的）。
  **不要再尝试**“靠虚拟显示凑双屏”，也不要为此装第三方 IDD 或开 RDP 会话（侵入且会锁控制台）。

- **MuMuManager CLI 也补不出屏（2026-11-08 实测）**：`D:\Program Files\Netease\MuMu\nx_main\MuMuManager.exe`
  `info -v all` 可只读列出实例（本机 index 0，`is_process_started=false`），但 `control -v 0 launch` 返回
  `{"errcode":-503,"errmsg":"mainnx connect failed"}`（主程序未连接时必失败），实例不启动、显示数仍为 1。
  即使先起 `MuMuNxMain.exe`，虚拟显示适配器也不挂载；`MuMuNxService` 是随主程序拉起的进程（不是注册服务，`sc stop` 报 1060），
  直接结束该进程即可恢复原状。**结论：不要再用模拟器凑双屏门禁。**

Related: [[reference-windows-window-capture-pixelcheck]], [[reference-pywebview-host-traps]]
