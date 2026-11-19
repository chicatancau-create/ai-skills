---
name: registry-surgery-windows-bash
description: 在本机从 Git Bash + Python 做注册表体检与删除的正确姿势：裸 exe 名要走 App Paths、HKCU\Software\Classes 提权反而删不掉、bash 里 reg 路径引号会被吞、改 PATH 要保类型并复验。
metadata:
  type: reference
---

2026-11-03/11-05 在一轮"全盘清垃圾 + 注册表清理"里实测出来的四条。

**1. 判"某条注册表引用死了"必须先做正确的可执行文件解析**，否则产出的全是假阳性：
- 裸名（`WinRAR.exe`、`msiexec.exe`、`cmd.exe`）→ `shutil.which(name, path=PATH+System32+SysWOW64)`
  → 再查 `HKLM/HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\<name>` 默认值。
  本机 WinRAR 在 `D:\RAR`（不在 PATH），我据此把 FileExts 的 125 条"死引用"误判成可删垃圾。
- 含空格路径用**最长存在前缀回试**，别 `split()` 取第一段（会把 `D:\Internet Download Manager\IDMan.exe`
  截成 `D:\Internet`）。`"D:\Program Files\..."` 要先配对引号取值。
- `%1`/`%*` 是参数占位符、`@shell32.dll,-8506` 是资源引用、`\??\` 与 `\SystemRoot\` 要先展开
  （不展开会把 235 个 Windows 自带驱动全报成缺失）。
- 从脚本正文里抠路径时，正则必须 `(?<![A-Za-z0-9])[A-Ha-h]:[\\/]…`，否则 `https://` 的 `s:` 被当盘符。
  另外中文文档句子里的 `D:\Skills 按条目 junction 进各客户端…` 会被整句吃掉 → 只对**引号内**的字符串判存在性。

**2. 删除权限的三条实测**
- `HKLM` 服务键：`sc delete <name>` **非提权就能成功**（本机删 `HWiNFO_216`、`n` 都 rc=0）。
- `HKLM\SOFTWARE\Classes\…`：`reg delete` 走提权 cmd 可行；但提权 python 的 `winreg.DeleteKey` 报**拒绝访问**。
- **`HKCU\Software\Classes\<progid>` 是合并视图**：用**提权**进程删它会 `拒绝访问`（Hive 归属不是那个令牌），
  用普通权限的 `reg delete` 又因 bash 引号被吞而报"找不到键"。可用的是：写 `.ps1` 用
  `Remove-Item -LiteralPath 'HKCU:\Software\Classes\hideme' -Recurse -Force`，然后 `Test-Path` 复验。
- 结论：**判存在性用 python `winreg`，删除用 .ps1 的 PowerShell 提供程序，别在 bash 里拼 `reg delete "HK…"`**。

**3. 改 PATH 要保类型 + 复验**：读回 `winreg.QueryValueEx` 拿 `(value, type)`，type=2 是 `REG_EXPAND_SZ`，
写回必须 `reg add … /t REG_EXPAND_SZ /v Path /d "<新串>" /f`（用 `SetEnvironmentVariable` 会退化成 REG_SZ，
`%USERPROFILE%` 之类的引用会失效）。写完立刻枚举两侧 37→36 项逐条 `os.path.exists` 复验，
并确认在用的工具仍能解析（`where java` → `D:\JAVA\jdk\bin\java.exe`）。

**4. 动手前一定 `reg export` 单键备份**（几 KB，放 `%TEMP%\regbk\`），删除后 `winreg.OpenKey` 复验
"该消失的消失、该留下的留下"（本机重点留检项：`clash_verge_service` 必须还在、
AMD 的 20 个驱动服务必须还在、`mouclass/kbdclass/nvlddmkm` 必须 RUNNING）。
相关：[[reference-windows-autostart-process-audit]]、[[reference-windows-permission-denied-as-missing]]、
[[feedback-destructive-file-ops]]、[[reference-power-scheme-registry-clutter]]
