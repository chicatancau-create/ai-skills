---
name: reference-clash-verge-service-mode
description: Clash Verge 服务模式的本机机制与判据——内核由 clash_verge_service 托管，降级成 Sidecar 时端口照听；修法是「重装对齐二进制 + 手工放回 cores 内核」两步都要，且须按平时方式重启 GUI
metadata:
  type: reference
---

本机 Clash Verge Rev（`D:\Clash Verge`，2026-11-04 实测 2.5.10）的「服务模式」要点。
它是**服务托管内核**结构：正常运行时 `verge-mihomo.exe` 是 `clash_verge_service.exe` 的子进程，
不是 GUI 的子进程。

**判服务模式是否真的在工作（唯一硬判据）**

```
verge-mihomo 的 ParentProcessId == (Get-CimInstance Win32_Service -Filter "Name='clash_verge_service'").ProcessId
```

`7897 在监听`、`ProxyEnable=1`、`curl -x 127.0.0.1:7897 github 200`、服务 `Running/Auto`、
服务 IPC `GET /magic|/version|/installation 全 200` —— **这些在降级态里全都成立**，
所以都不能证明服务模式正常。辅助判据：`C:\ProgramData\clash-verge-service\users\<hash>\desired-state.json`
的 `core_should_be_running`（正常应为 `true`）；App 日志 `%APPDATA%\io.github.clash-verge-rev.clash-verge-rev\logs\latest.log`
出现 `Starting Sidecar with Service unavailable:` 即已降级（后面两种文案分别对应两种病）。

**两种病与对应修法（两步都要，顺序不能反）**

1. `registered service is unavailable or incompatible` ⇒ 注册的服务二进制与 App 版本不符。
   对比 `D:\Clash Verge\resources\clash-verge-service.exe` 与 `C:\ProgramData\clash-verge-service\bin\` 同名文件的
   **大小与 SHA256**（本机实测 3,418,624 vs 3,379,200 就是这个错配）。用 App **当前版**自带的
   `resources\clash-verge-service-install.exe` 重装。
2. `the selected approved core is missing or does not match; reinstall the service to repair it` ⇒
   服务 `cores\` 里没有 App 选定内核。**`clash-verge-service-uninstall.exe` 会连带删掉 `cores\*.exe`，
   而 App 不会自己补回去** —— 要手工把 `D:\Clash Verge\verge-mihomo.exe` 复制到
   `C:\ProgramData\clash-verge-service\cores\verge-mihomo.exe`（`Copy-Item` 保 mtime，原本那份就是这样的拷贝态）。
   **母本在 App 根目录**：`D:\Clash Verge\` 下同时有 `verge-mihomo.exe`(61,271,040) 与
   `verge-mihomo-alpha.exe`(61,300,224)，两份都能补；别断言「没有副本」前先按 文件名+尺寸+mtime 具名搜一遍。

改完**必须重启 GUI 才会重估**（老进程不重估），用开机那个计划任务最贴近常态：
`schtasks /Run /TN 'Clash Verge (Admin)'`（先 `taskkill /F /PID <GUI>`；GUI 是管理员进程，
非提权 `Stop-Process` 会静默失败）。整段中断约 45 秒。

**手工放回内核后判 ACL 用 `icacls`，别用 `Get-Acl` 拼字符串**（拼出来是空串，两侧都空时 `-eq` 回 True 是假绿）；
正常应为 `SYSTEM:(I)(F)` + `Administrators:(I)(F)`，继承自 `cores` 目录的 `(OI)(CI)(F)`。

**读 `C:\ProgramData\clash-verge-service` 必须提权**，否则 `Test-Path` 回 False、`Get-Item` 报「找不到路径」
（其实是拒绝访问）——这个伪装害我两次误判，详见手册
[[踩坑-无权限读ProgramData被当成文件不存在致误删服务拆掉内核]]。

提权无人值守脚本的两个本机陷阱与解法，见手册
[[踩坑-Stop-Service默认确认提示在隐藏提权控制台里把脚本卡死]] 与
[[踩坑-App自更新后手动重装服务会装旧二进制且卸载器删内核致静默降级Sidecar]]。

相关：[[reference-windows-autostart-process-audit]]、[[reference-windows-network-path-diagnosis]]、
[[reference-git-push-needs-local-proxy]]（7897 就是这个内核的 mixed-port）
