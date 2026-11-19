---
name: feedback-no-resident-process
description: 桌面/工具类交付默认不留常驻进程、不装开机自启；要常驻或自启必须先问，用户宁可自己手动点快捷方式
metadata:
  type: feedback
---

给这台机器做桌面小工具/HUD/后台助手类交付时，**默认不注册开机自启、不常驻进程、不加 watchdog 轮询**。生命周期只保留"随目标应用一起退出"这一条；重新打开目标应用后要用户自己点快捷方式启动。

**Why**：2026-11-03 cc-hud 那次，用户原本有"开机判定一回 + CC Switch 退出则跟着退出"的跟随机制，实测发现"重开 CC Switch 不跟随启动"后，用户明确否掉了两个候选方案（改成隐藏等待 / 加常驻 watchdog），原话是「**不要留一个进程霸占空间，只留一个，那就是随着 CC switch 的关闭而关闭**」。他要的是桌面上零残留，而不是自动化便利。

**How to apply**：
- 想做自启/常驻（Startup 快捷方式、计划任务、服务、轮询探针）→ 先摆明代价再问，别默默装。
- 撤自启项用**可回滚**方式：送回收站（Shell `InvokeVerb('delete')`）+ 另存字节相同备份，并报告原位置与大小。
- 撤 Shell 项时**按解析出的目标匹配，不按文件名**：`Namespace(...).Items()` 的 `.Name` 会被 Explorer 去掉 `.lnk` 扩展，且中文文件名在 Python 目录列举里可能是乱码 —— 用 `WScript.Shell.CreateShortcut($it.Path)` 解出 TargetPath+Arguments 再比。
- 判据（verify 类门禁）要跟着翻成"名单里为 0"，并在注释里写明是用户点名的决定，否则以后会被当成漏装而"修回去"。

Related: [[feedback-delivery-shortcut-and-location]], [[reference-qoder-bash-spawn-token-limits]], [[feedback-destructive-file-ops]]
