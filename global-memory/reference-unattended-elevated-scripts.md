---
name: reference-unattended-elevated-scripts
description: 本机无人值守提权 PowerShell 的四个静默失败族（Stop-Service 确认提示卡死、报错只进看不见的控制台=日志缺行、Get-Acl 拼字符串假绿、提权进程杀不掉）与已验证可靠的生成/启动通路。
metadata:
  type: reference
---

2026-11-04 修 Clash Verge 服务模式时一轮内全踩到。适用于任何 `Start-Process -Verb RunAs` 起的、
没人看控制台 PowerShell 脚本（本机 `-Verb RunAs` 静默提权可用，见 [[reference-office-c2r-cleanup]]）。

**1. `Stop-Service` 会在没人看的窗口里等确认，整条脚本永久卡死**

`Stop-Service` 的 `ConfirmImpact='High'` 且默认 `$ConfirmPreference='High'` ⇒ 它会打「继续进行吗? Y/N」；
`-Force` **只压依赖服务提示，不压确认提示**。提权子进程的窗口我看不到，于是表现为
「进程活着、零输出、不报错、不超时」。实测白等 8 分钟。

- 解法（按稳妥度）：`& sc.exe stop <名>`（原生工具，根本不提示）> `Stop-Service -Confirm:$false` >
  脚本内设 `$ConfirmPreference='None'`（会连别的确认一起关，慎用）。
- 定位手法（排除法，不需要看见窗口）：看**已完成步骤的产物** + **未发生的外部事实**。
  那次是「备份文件已生成、服务仍 Running 且 PID 未变、无卸载器进程、SCM 事件日志近 15 分钟零条停止事件」
  ⇒ 卡点被夹在这两步之间，正好是 `Stop-Service` 那一行。
- 停止后用**轮询代替固定 Sleep**：`for ($i=1..12) { Start-Sleep 2; if (状态到位) {break} }`，
  每轮结果写进日志（`sc.exe stop` 那次第 1 轮就 Stopped，反证第一次不是服务起不来）。

**2. 报错只落在看不见的提权控制台 ⇒ 症状是「日志缺行」，不是报错**

`$ErrorActionPreference='Continue'` 时，异常文本只写进那个提权控制台。
`Get-FileHash` 在服务刚起、文件被占用时抛异常，那一行 `Say` 整条没落盘，
日志从「验证」标题直接跳到最终状态 —— **差点把「没打印」当成「没问题」**。

- 提权 worker 里每个可能失败的调用都要 `2>&1` 并进日志；或设 `Stop` 并在外层 `try/catch` 把异常文本落盘。
- **按脚本的步骤数核对日志行数**：缺行＝那一步没成功。
- 第一版「跑完再 `WriteAllText`」是错的：卡住时日志文件压根不存在。必须**逐行 `AppendAllText`**。
- 启动器**不要 `-Wait`**（`-Wait` 会把卡死变成我的 bash 超时，什么也看不见）；
  让它后台跑，我这边轮询日志文件。

**3. 比较类断言两侧都取到空值时，`-eq $true` 是假绿**

`(Get-Acl).Access | ForEach-Object { $_.IdentityReference + ':' + $_.AccessControlType }` 拼出来是**空串**，
于是「ACL 一致=True」毫无意义。改用 `icacls <文件>` 打印原文才拿到
`SYSTEM:(I)(F)` / `Administrators:(I)(F)` 两行真实数据。
⇒ **凡是"一致/相等"断言，必须两侧原文各打印一遍**；两侧皆空（或 `NA`/`$null`）时的 True 不计入证据。
（`C:\ProgramData` 下的 ACL 要提权读，非提权 `icacls` 回「拒绝访问」而不是空，
见 [[reference-windows-permission-denied-as-missing]]。）

**4. 提权进程在提权外面杀不掉**

非提权侧 `Stop-Process` 对管理员进程静默失败（[[reference-windows-permission-denied-as-missing]]），
且 `Win32_Process.CommandLine` 会被读成空 —— 所以「提权脚本卡住」只能靠**日志文件是否还在长**判断。
收掉它的可靠写法：在新的提权脚本里按命令行精确匹配自杀，
`Where-Object { $_.ProcessId -ne $PID -and $_.CommandLine -like '*<脚本名>.ps1*' }` + `taskkill /F /PID`，
匹配串要在脚本改名时同步改，否则误杀或漏杀。

**5. `-Verb RunAs` 不能与 `-RedirectStandardOutput` 同用**

`Start-Process -Verb RunAs -RedirectStandardOutput x.log` 直接抛
`AmbiguousParameterSet`（RunAs 属 ShellExecute 参数集，重定向属 CreateProcess 参数集）。
2026-11-10 装 MTK WinUSB 驱动时踩到。**解法：不重定向，让子脚本自己写日志**
（worker 内 `"... " | Out-File $log -Append -Encoding utf8`），父进程只 `Start-Process -Verb RunAs -Wait -WindowStyle Hidden`。
`-Wait` 在这里可用（脚本很短、且自己落盘），长任务仍按第 2 条改成不 `-Wait` 轮询日志。

**6. 驱动安装器会被 CWD 里的残留目录卡住**

libwdi 的 `wdi-simple.exe` 连跑两次时，第一次留下的 `usb_driver\` 目录会让第二次报
`libwdi:error [check_dir] Unable to create directory 'usb_driver' (already exists)` + `Access denied`，
退出码 `-3`（之前还有一次 `-11`）。**删掉该目录后立刻 `exit=0`、`Installing driver(s)... Success`**。
⇒ 驱动安装器返回非 0 时先看它有没有在工作目录留下中间目录，别急着判"Windows 拦签名"。

**已验证可靠的生成通路（避开 bash 吃转义，见 [[reference-windows-python-encoding]]）**

1. 用 Write 工具建一个 ASCII-only 的 `.py` 生成器，里面用 `r"""…"""` 写 PowerShell 正文；
2. 生成器把 worker `.ps1` 以 `encoding='utf-8-sig', newline='\r\n'` 写进 `%TEMP%`（含中文必须有 BOM，
   PS 5.1 无 BOM 会按 GBK 解析整段失败并报「表达式缺少右括号」这类误导性错），
   把 launcher `.ps1` 以 `encoding='ascii'` 写（launcher 里只放 `%TEMP%` 的 ASCII 路径，
   中文路径留在 worker 里，靠 BOM 保命）；
3. launcher 内容 `Start-Process powershell -Verb RunAs -Wait -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File',('"'+$w+'"')`，
   结果一律写进 `%TEMP%` 的产物文件，我再用 `python -X utf8` 读回。
4. 直接 `powershell -Command "…$var…"` 会被 bash 吃掉 `$`，`python -c "…"` 里的反斜杠会被压 —— 都不可靠。

相关：[[reference-powershell-through-bash-and-recyclebin]]、[[reference-clash-verge-service-mode]]、
[[reference-dsh-desktop-internals]]、[[feedback-destructive-file-ops]]
