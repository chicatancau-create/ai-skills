---
name: reference-windows-permission-denied-as-missing
description: 本机非提权 shell 读 C:\ProgramData 等目录时，"访问被拒"会伪装成"文件不存在"；任何"不存在"结论必须提权复核后才可行动。
metadata:
  type: reference
---

**规则：在本机（以及任何 Windows 机器）用非提权通道判"文件/目录不存在"，一律先提权复核再行动。**

Qoder Bash 派生的进程令牌是**非提权**的。对 `C:\ProgramData\<第三方>`、`C:\Program Files`、
别的用户目录这类位置：

- `Test-Path` / `os.path.exists` → 访问被拒时返回 **False**（与"真的没有"同一个返回值）
- `os.walk` → 静默吞掉 `PermissionError`，**递归数出 0 个文件**，看起来像空目录
- `Get-ChildItem -ErrorAction SilentlyContinue` → 直接什么都不打印

**Why**：2026-11-03 我就踩实了。我看到 `C:\ProgramData\clash-verge-service` "递归 0 文件"、
服务 exe 的 `Test-Path=False`，判 `clash_verge_service` 是"文件被删、进程残留"的僵尸，
于是跑了 Verge 自带的 uninstall+install 重装服务。**提权后同一批路径**：exe 有 3,379,200 B，
logs/runtime/users 全套都在，服务一直 `Running/Auto` 正常——从头到尾没坏。
而 Clash Verge 的**内核就跑在这个服务里**（`verge.yaml` 的 `clash_core` + 日志 `[Service] service core stopped`），
我这一拆导致 7897 停听、`ProxyEnable` 被清 0，**断网约 5 分钟**，只能靠提权重启 Verge 才恢复。

**How to apply**：
- 判存在性时把三种结果分开报：**存在 / 不存在 / 读不了**。`os.walk` 要显式捕获 `PermissionError`；
  PowerShell 判存在用 `Test-Path` 之外再补一次 `Get-Acl` 或提权复查。
- **动服务、驱动、安全软件之前**，先确认"应用的核心是不是由它承载"：读应用自己的配置与日志、
  比对端口监听者 PID 与服务 PID。凡"看起来坏了"的东西，先做**只读的提权复核**再决定是否重装。
- 顺带一条同源陷阱：`Stop-Process` 杀以管理员运行的进程会**静默失败**——必须回读 PID 确认，
  别把"执行过了"当成"杀掉了"。
- **同一只狼第二次来（2026-11-03）**：我派出的研究代理用非提权 python 报 `clash_verge_service` 的
  `C:\ProgramData\clash-verge-service` 是"0 项空目录、exe 不存在"的死服务，我照抄进了结论。
  提权 `Get-ChildItem` 同一目录 = **7 项**、exe 在、服务 `Running/Auto`。⇒ **代理/脚本给的"不存在/空目录"
  只能当线索**；写进"可删清单"之前，必须自己用提权读数复核一遍，尤其涉及服务与 ProgramData 时。
- 相关：[[reference-qoder-bash-spawn-token-limits]]（同一令牌限制的 GUI 侧表现）、
  [[feedback-destructive-file-ops]]、[[reference-windows-network-path-diagnosis]]。
