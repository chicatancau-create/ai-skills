---
name: reference-windows-toast-notification-layers
description: 本机「通知/提示音不弹」的三层开关优先级与唯一判据(ETW Id=3150 PolicyReason)；组策略 NoToastApplicationNotification 由 2026-07-22 去广告批写入且可能被重写；WpnUserService 后缀会变(13dbd4→16fb81)只能通配
metadata:
  type: reference
---

Windows 11 28000 本机 2026-11-06 实测。用户报「Qoder 完成任务不弹提示」时，**别从应用设置入手**。

**优先级：组策略 > 用户级 > 全局 UI 开关。**
1. `HKCU\Software\Policies\Microsoft\Windows\CurrentVersion\PushNotifications\NoToastApplicationNotification`（本机 =1，拦截源；同键还有 `NoTileApplicationNotification=1`，我特意留着没动）
2. `HKCU\Software\Microsoft\Windows\CurrentVersion\PushNotifications\ToastEnabled`（本机曾 =0，现为 1）
3. `HKCU\Control Panel\...Notifications\Settings\NOC_GLOBAL_SETTING_TOASTS_ENABLED`（本机曾 =0，现为 1）

**只有第 1 层是根因。** 我第一版改第 3 层、回读 1、行为没变 ⇒ 假修复。
定性只认 ETW：`Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-PushNotification-Platform/Operational'}`
- `Id=3150 + PolicyReason [GlobalSettingDisabled]` = 被策略/总开关丢弃
- `Id=2416 收到 / 2418 提交 / 3153 delivered` = 应用确实在发、系统确实送达
（我曾据"子键列表里没有 Qoder"断言它从没注册通知，被 2416/2418 直接反驳。）

**How to apply:**
- HKCU 的 `Policies` 子键对普通用户**只读**（默认 DACL 只给 SYSTEM/Administrators 写），删除必须提权；见 [[reference-registry-surgery-windows-bash]]。
- `WpnUserService_<hash>` 是按需启动，`sc stop` 后**不会自己回来**，会让 `CreateToastNotifier` 抛「通知平台不可用」——那是自造故障；后缀还会变（同机同用户 13dbd4 → 16fb81），**任何脚本别写死服务名**，用 `Get-Service -Name 'WpnUserService_*'`。
- 这批策略出自 2026-07-22 15:27 一次"隐私/去广告"批处理（同时写了 `TurnOffWindowsCopilot`、`DisableWindowsSpotlight*`、WER `LoggingDisabled` 等 8 项，全部未动）；**写入者未查清**，若那工具周期重写，症状会原样复发且应用侧仍零报错。复测一行：看窗口内有没有 `Id=3150`。
- 下一个可能干扰源：`QuietHours\FullScreenProcess`（本机含 `PixPin.exe`）。
- 详细取证与本机产物见手册 `03-通用\03-调试与验证\踩坑-应用通知设置全开但Windows全局总开关为0导致一切静默.md`；流量层故障判法见 [[reference-windows-network-path-diagnosis]]。
