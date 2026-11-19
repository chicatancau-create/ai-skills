---
name: reference-windows-dir-locked-by-process-cwd
description: Windows 上目录改名/删除报 Permission denied 时，占用者往往不在命令行里——是某个进程把该目录当成了当前工作目录；用读 PEB CurrentDirectory 的方法找，别只 grep CommandLine，也别忽略自己的 shell
metadata:
  type: reference
---

2026-11-09 实测：`git mv project02-frameworks projects/...` 连续报
`fatal: renaming 'project02-frameworks' failed: Permission denied`，而按命令行 grep
（`CommandLine -like '*project02-frameworks*'`）一个进程都找不到；目录里的文件逐个改名却全部成功。

**根因一类是"目录句柄被当成 cwd"，不是文件被占用。** 三种来源都遇到过：
1. **我自己的 shell 还在里面**（Bash 工具的 cwd 跨调用保持）——`cd` 出来就好；
2. 三天前跑 `scripts/run_project.sh` 留下的 **bash + node**（父进程早退了，孙进程还活着）；
3. 从同一目录起的 **`vite preview` 服务**（端口 4183/4184），esbuild 子进程锁着 `node_modules`。

**判据（按这个顺序，30 秒定性）**
- 先看自己：`pwd` / 确认上一条命令没 `cd` 进目标目录。
- 再按 cwd 找：读每个候选进程的 PEB → `ProcessParameters`（x64 偏移 `+0x20`）→
  `CurrentDirectory.DosPath`（`UNICODE_STRING` 在 `+0x38`，Buffer 指针在 `+0x40`），
  过滤路径里含目标目录的进程。纯 ctypes 几十行可跑，**比 grep CommandLine 准**。
- 用 `explorer`/IDE 打开着该目录也可能持有句柄；杀之前先看 `CreationDate` 和命令行，确认是旧会话残留。

**收尾**
- `taskkill /PID <pid> /T /F` 连子进程一起收；杀完用 `Get-NetTCPConnection -LocalPort <端口>` 和再次读 cwd 复验。
- 删除目录还报 `WinError 5`（不是"被占用"而是只读/长路径）要换思路：
  见 [[feedback-destructive-file-ops]] 的 chmod / `\\?\` / robocopy 三条。

Related: [[feedback-destructive-file-ops]], [[reference-windows-permission-denied-as-missing]], [[reference-qoder-taskstop-orphan-process]]
