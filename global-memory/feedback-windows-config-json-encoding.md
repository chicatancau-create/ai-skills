---
name: windows-config-json-encoding
description: On this Windows machine, never write app config JSON/YAML with PowerShell redirects — BOM and GBK silently break Go/other parsers; write with Python encode('utf-8') instead.
metadata:
  type: feedback
---

在这台 Windows 机器上修改第三方应用的配置文件（JSON/YAML）时，**不要用 PowerShell 的
`Set-Content` / `Out-File` / `>` 重定向写文件**。改用 Python 显式
`open(p,'wb').write(json.dumps(d, ensure_ascii=False).encode('utf-8'))`，
或用编辑器另存为「UTF-8 无 BOM」。改完要验证首字节不是 `EF BB BF`。

**Why**：2026-09-20 排查本地模型部署时发现的真实故障链。上一轮工作用 PowerShell 改过
牧羊人(Herdsman) 的两个配置文件，写成了带 UTF-8 BOM 的文件。Go 的 `encoding/json`
不接受 BOM，于是该应用每次启动都报 `invalid character 'ï' looking for beginning of value`，
表现为「本地模型注册表读不出来 → 出现幽灵重复条目」「开机自动恢复模型一直不生效」
——这些现象看起来像应用 bug，实际是配置文件编码被工具改坏了，白找了很久。

**How to apply**：任何在这台机器上「改配置文件/写清单文件」的任务都适用，不限于某个项目。
排障时也先怀疑这一点：如果应用日志里出现 `ï`、`锟斤拷`、乱码或直接报 JSON 解析错误，
第一件事就是查目标文件的 BOM 与字节编码，而不是去猜应用逻辑。写文件时同样别把中文
写成 GBK —— 内容要 UTF-8，控制台显示乱码只是终端代码页问题，不要因此去改文件编码。

同族的另一个坑：**`.cmd` / `.bat` 批处理文件里不要写中文**。cmd.exe 用 OEM 代码页
（本机是 GBK/936）读批处理，用 UTF-8 存中文会让脚本解析直接坏掉——现象是双击后
什么都没跑起来、也不报明确错误。批处理一律保持纯 ASCII，中文说明放到 .py/.md 里。
（2026-09-21 实测踩过一次：桌面快捷方式指向的 .cmd 因为 `title` 里有中文而完全没启动。）

**`.ps1` 也一样**：Write 工具产出的是 UTF-8 无 BOM，而本机 `powershell.exe` 是 5.1，
无 BOM 就按 GBK 解码 → 中文字符串/注释的字节会吞掉引号，报一堆
`字符串缺少终止符`、`表达式中缺少 ')'` 之类的解析错（2026-09-22 实测）。
⇒ 脚本正文一律**纯 ASCII**，要中文输出就 `Out-File -Encoding utf8` 到文件再用 Read 看；
终端直接打印中文必然乱码（控制台代码页问题，不是脚本错）。

两个补充坑（同一天踩到）：
1. **BOM 只是第一层**。去掉 BOM 后同一个日志行会换个原因继续报（那次是 Go 结构体要
   `map[string]string`，文件里是普通字符串）。修完必须把该错误 grep 到 0 次才算完。
2. **用 bash heredoc / `python -c` 传含反斜杠或中文的文本会被 shell 改写**（`\M` 被吃、
   `\\` 变 `\`、`\b` 变成退格符写进文档）。写这类文件要用 Write 工具，或在脚本里用
   `chr(92)` 拼反斜杠、用 `\uXXXX` 转义中文，写完用 `ast`/重新读回校验字节。
3. **想用中文标签/中文正则的 .ps1，给文件前置 UTF-8 BOM 就能正常工作**（2026-09-28 实测：
   `python -c` 往文件头写 `EF BB BF` → 同一个脚本从 `PARSE ERROR` 变 `PARSE OK`）。
   纯 ASCII 是默认选择；报告类脚本想让输出直接带中文小标题时，用「加 BOM」这条更省事。
   注意 Write/Edit 工具每次重写都会去掉 BOM，**改完要重新补一次**。

相关：[[feedback-rigor-audit]]、[[feedback-vault-engineering-rules]]
