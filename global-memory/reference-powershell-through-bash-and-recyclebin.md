---
name: reference-powershell-through-bash-and-recyclebin
description: Gotchas running PowerShell from this Git-Bash shell ($_ gets mangled) and enumerating/purging Windows Recycle Bin entries per-item instead of emptying it.
metadata:
  type: reference
---

Running PowerShell from the Bash tool on this machine:

- `$_` inside a double-quoted `-Command "..."` string gets eaten by bash (emitted as `\extglob`), producing PowerShell parse errors. For anything with `$_`, `Where-Object`, or loops: write a `.ps1` with the Write tool (ASCII-only, no BOM) and run `powershell -NoProfile -ExecutionPolicy Bypass -File <path>`. Delete the script afterward.
- **ASCII-only 的具体症状（2026-10-08 复现）**：heredoc 写出的 `.ps1` 里带中文注释/字符串，PowerShell 5 按 ANSI/GBK 读文件 → `ParserError: 字符串缺少终止符 / 语句块中缺少"}"`，**整脚本一条语句都没执行**。同一份逻辑改成纯 ASCII 提示文字后立刻跑通。也别用 bash `printf '%s\n' '...'` 拼 `.ps1`：嵌套引号会让 bash 自己先报 `unexpected EOF` —— 用 Write 工具落文件。
- **中文 `.ps1` 的正解是加 BOM，不是改成 ASCII**（2026-10-15 实测）：用 python `open(p,"w",encoding="utf-8-sig",newline="\r\n")` 落文件，PowerShell 5.1 就能正常解析中文注释和字符串，`[Console]::OutputEncoding=[Text.Encoding]::UTF8` 后输出也不乱码。之前记的「改成纯 ASCII 才跑通」只是绕开了问题。
- **PowerShell 的 `>` / `Out-File` 默认写 UTF-16LE**，下游工具会把它当**二进制**：`"x" > a.txt` 之后 `git diff --stat` 变成 `Bin 12 -> 22 bytes`、`0 insertions`，文本对比演示全废。要 UTF-8 无 BOM 就用 `[IO.File]::WriteAllText($p,$t,(New-Object Text.UTF8Encoding($false)))`，或退一步 `| Out-File -Encoding ascii`。
- The console prints Chinese as mojibake. `[Console]::OutputEncoding=[Text.Encoding]::UTF8` at the top of the script fixes it.
- **`$ErrorActionPreference="Stop"` + 原生命令 `2>&1`** 会把 git 写到 stderr 的正常提示变成 ErrorRecord 抛 `NativeCommandError`，脚本在最后一行崩掉（前面全跑完了）。跑 git 的脚本用 `"Continue"`，靠 `git status` 而不是靠 stderr 判断状态。
- A PowerShell parse error means nothing executed — re-running after a syntax failure is safe, but always confirm the failed run really was a no-op before assuming.
- **`Get-CimInstance -Filter` 里再嵌单引号会被 bash 打坏**（2026-11-08）：`-Command '... -Filter "Name=''pythonw.exe''" ...'` 穿过 Git Bash 后变成
  `-Filter "Name=pythonw.exe"` → `无效查询 / HRESULT 0x80041017`。带 `Where-Object` / 嵌套引号的逻辑改用 `.ps1` 文件执行。
- **按 `CommandLine` 正则杀进程会命中“正在执行这条命令的 shell 自己”**（2026-11-08）：`Where-Object { $_.CommandLine -match "cc-hud\.pyw" }`
  会匹配 bash/powershell 的命令行文本，`Stop-Process` 把调用者一起杀掉（退出码 4294967295 / -1），后半条命令全不执行。
  先按 `Name` 收窄（`$_ .Name -eq 'pythonw.exe'`），或把过滤逻辑放进 `.ps1`。

Recycle Bin (`Shell.Application` → `NameSpace(10)`) detail-column indices on this zh-CN box: **1 = 原位置 (original path), 2 = 删除日期, 3 = 大小**. Column 0 is the name. `$_.Size` returns **0 for folders** — read the size string from column 3 instead.

`[Microsoft.VisualBasic.FileIO.FileSystem]::DeleteDirectory($path,'OnlyErrorDialogs','SendToRecycleBin')` can report success while silently leaving a leftover subtree behind — always `du -sh` the parent after a bulk delete.

**Sending items TO the Bin (verified 2026-09-27, 143 items, zero silent loss):** `$folder = $shell.NameSpace($parent); $folder.ParseName($leaf).InvokeVerb('delete')` works with **no confirmation dialog** on this box and does **not** hang. It is **asynchronous** — poll `Test-Path -LiteralPath` until false instead of trusting the call. Pre-flight the quota or a big delete becomes a permanent delete: resolve the volume GUID with `Get-CimInstance Win32_Volume -Filter "DriveLetter='E:''" | % DeviceID`, then read `HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\BitBucket\Volume\{guid}` → `MaxCapacity` (MB) and `NukeOnDelete` (must be 0; E: = 18329 MB). Post-check every item by matching **name + column-1 original path** against the manifest — that is what proves nothing got nuked.

**退出码归属：谁在链尾谁说了算。** `cmd | tail` 让 shell 报 **tail 的** rc 而不是命令的；真退出码用 `cmd > file 2>&1; echo $?`。同一个坑的后台任务版（2026-10-05 踩到两次）：**后台命令完成通知里的「exit code 0」是整条链最后一条命令的 rc** —— `aqt install ... > log; echo "[rc=$?]"; tail log` 里那个 0 来自 `tail`，而 aqt 其实失败了、目标目录压根没建。**验证产物文件存在，别信退出码。**

**同一管道族的另外两枪**：① 把 PowerShell 输出接 `grep` 会掐断后续流（`Binary file (standard input) matches`），因为中文/GBK 字节看着像二进制 —— 用 `grep -a`。② Node harness 反向中招（2026-09-29 验证）：node 的 stdout 被管道时是**块缓冲**，`node verify.js | grep ... | head -8` 会提前结束、整份报告丢失，看着像卡死其实啥也没产出。一律 `node x.js > out.log 2>&1` 再 grep 文件，或让脚本逐行 `fs.appendFileSync`。

**`subprocess` 调 cmd 的引号坑（2026-10-05）**：`subprocess.run(['cmd','/c', 'call "C:\Program Files (x86)\...\vcvars64.bat" && ...'])` 会被 `list2cmdline` 把内层 `"` 转义成 `\"`，**cmd 不认 `\"`**，报「不是内部或外部命令」。解法：把命令写成**纯 ASCII + CRLF 的 .bat 文件**再执行该文件（与 [[reference-windows-batch-entry-encoding]] 同一纪律）。

**别用 Bash 内联 Python（`python -c "..."` 或 heredoc）**：反引号会被 bash 当命令替换吃掉（写进文件的内容变成 `\` 残渣）、`r'G:\'` 这种尾反斜杠是 SyntaxError、`\\` 会被减半。规则：**多行/含反引号含路径的脚本一律先用 Write 工具落成 .py 再跑**，别内联。

Why the pre-check matters: emptying the Recycle Bin is irreversible, and on this machine it was holding ~26 historical deletions unrelated to whatever task triggered the cleanup, including files the user might still want (source spreadsheets, a bookmark export, a password CSV). Note the Bin can read back **0 items** even when a prior turn claimed files were in it — enumerate and report the mismatch instead of assuming either side.

**How to apply:** for any "clear the trash / finish the cleanup" request, first enumerate every entry with name + original path + size, then purge **only** the items this task created, matched by both name and original path. Report the untouched remainder instead of nuking it, and offer a separate explicit confirmation for a full empty. Moving items to the Bin does not free disk space — the bytes just relocate to `$RECYCLE.Bin`, so measure free-space delta only after a permanent purge, and state the number you measured rather than the number the Bin claims.
