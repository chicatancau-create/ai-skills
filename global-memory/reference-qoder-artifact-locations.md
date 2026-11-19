---
name: qoder-artifact-locations
description: Where this Agent writes its own scripts/artifacts on this Windows box, which of them are app runtime files that must not be deleted, and why atime cannot prove a script is unused
metadata:
  type: reference
---

Measured 2026-10-03 on this machine (`C:\Users\Admin`), after clearing 113 items.

**Where the agent's own files land, in order of how often it writes there:**
- `%LOCALAPPDATA%\Temp\` — one-off scripts from Bash-tool turns (`*.mjs`, `*.ps1`, `*.py` with
  hand-picked names like `cw-peek.ps1`, `audit3.mjs`). Also `qoder-<hex>-cwd` markers.
- `C:\Users\Admin\.qoder\shell-snapshots\snapshot-bash-<ms>-<rand>.sh` — auto-generated per new shell,
  one per session start, never self-reclaimed (68 in 15 days). The live one appears in a running
  `bash.exe` command line.
- `C:\Users\Admin\.qoder\tmp\<workspace-slug>\` — per-session tool *outputs* (screenshots, captured
  stdout), not scripts. Slug = the workspace path with `\`→`-` and `C:\`→`C--`.
- `C:\Users\Admin\.qoder\{logs, projects, file-history, tmp, plugins}` — the real space bulk:
  logs 958 MB, projects 330 MB, plugins 85 MB, file-history 45 MB, tmp 18 MB (`.qoder` ≈ 1.5 GB).
- Skill/toolkit scripts are permanent and in use: `C:\Users\Admin\.qoder\skills` (junction) and
  `D:\QoderToolkit\` — see [[skill-placement-convention]], [[toolkit-is-tools-only]].
- Inside the workspace itself only when explicitly told to write there.

**Do not delete as "agent litter":** `%LOCALAPPDATA%\Temp\<uuid>.tmp`, `<uuid>.tmp.js|css|node|ico`
(24 MB + 115 MB). Sampling headers proved these are Qoder IDE runtime caches — rolldown/Electron bundle
chunks, extracted PE `.node` modules — and many were locked (unreadable) by the running app.

**How to judge "still in use" here:** NTFS last-access updates are disabled on this box
(`fsutil behavior query DisableLastAccess` → `1`), so `st_atime == st_mtime` for every file and atime
proves nothing. Use instead: (1) grep skills/plugins/toolkit + `schtasks` + `set` env for the filename,
(2) running `Win32_Process.CommandLine` for the path, (3) whether absolute paths inside the script still
exist — the `cw-*` scripts pointed at `E:\CodeWeave\workspace`, which was gone (project now under
`G:\CodeWeave`), so they were dead on arrival.

Recover dir convention for this kind of sweep: copy → verify sha256 per file → only then delete, into
`C:\Users\Admin\_recover\<task>-<date>\` (outside any project), per [[feedback-destructive-file-ops]],
[[feedback-backup-and-write-authorization]]. **但对本机「确认是死的」的垃圾，用户已明确改为不留副本**
（见 [[feedback-no-backup-for-junk-deletes]]），`_recover` 只留给不可重建的改动；11-15 实测 `D:\_recover`、
`C:\Users\Admin\_recover`、`E:\_recover` 都已不存在。

**TEMP 是易失层，不是存储（2026-11-11 实测代价）**：Windows 自行安装 KB5132059 并重启（14:37）之后，
`%LOCALAPPDATA%\Temp` 从 15.21 GiB → 0.08 GiB / 114 文件，六目录回收站同时清空——本会话存在 `Temp\regbk` 的
**19 份 `.reg` 回滚备份与 4 份取证日志一起没了**，别人会话放在 TEMP 的 6.35 GiB 取证快照也归零。
`StorageSense` 计划任务 `LastRunTime=1999-11-30 / LastTaskResult=267011` 证明**不是存储感知**干的。
⇒ 写脚本落点：一次性探针可以继续放 TEMP；但**任何「以后可能要回滚 / 可能要复验」的字节必须当场写出 TEMP**，
本机现行落点是 `G:\AIrenwu\01_任务归档\<任务>\02_证据日志\`（随仓库走）或 `D:\_recover`。
同理事件日志有容量上限：11-15 再查 `WindowsUpdateClient/Operational` 的 `Id=19` 已「找不到任何匹配的事件」
（日志本身仍有 1597 条），只能用 `Win32_QuickFixEngineering` 反证更新装过。
盘点工具：`G:\AIrenwu\脚本库\09_机器体检与垃圾扫描\agent_artifacts.py`（11-15 实测 TEMP 1.06 GiB/3743 f、
shell-snapshots 仅 23 个文件，与上面 10-03 的旧数字相比已换了一批）。

---

## 国内版补充（2026-11-19 并入）

> 来源：Qoder 国内版 `C:\Users\Admin\.qoder-cn\memory\reference-qoder-artifact-locations.md`（本地修改日期 2026-11-04），国际版没有的内容，逐字保留；只追加，不改写上文。

> **【2026-11-04 更正】** 本页描述的是「应用和我历史上确实写过哪里」，其中「一次性脚本放 `%LOCALAPPDATA%\Temp`」
> **已不再是可接受的做法** —— 用户当场否掉把我新建的采集暂存目录放 C 盘，要求数据（含中间产物）只落工作区或他指定的位置，
> 见 [[feedback-no-c-drive-scratch]]。新建的 `.py` / 下载包 / 解压暂存一律改放工作区 `<目录>\_采集暂存\` 并在用完后自删。
> 已经存在的应用运行时目录（下面列的 `.qoder\...`）不属于「我放的东西」，照旧不要动。
**列进程只能走 PowerShell（2026-11-04）：** `wmic` 在这台 Windows 28000 上已经没了（子进程直接 `FileNotFoundError`），
用 `powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"name='python.exe'\" | Select-Object ProcessId,CommandLine | Format-List"`。
**后台任务的 ID 会随上下文压缩失效：** 2026-11-04 一个 `run_in_background` 批次在会话 turn 边界之后
`TaskStop` 报 `No task found with ID`，但进程仍在跑并继续写盘。别当成「已经停了」，按上面 PowerShell 拿 PID +
核对 CommandLine（确认是自己起的那条命令，见 [[feedback-destructive-file-ops]]）再 `taskkill //PID <n> //F`，
然后立刻查它已写出的产物有没有被污染。
