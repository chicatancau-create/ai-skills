---
name: reference-obsidian-wiki-link-table-pipe
description: Obsidian 表格里 wiki 链接的别名竖线必须写成 \| ，否则表格列数错乱；校验脚本数竖线要用 chr(92) 判转义，别在 Bash heredoc 里手写反斜杠正则
metadata:
  type: reference
---

在 Obsidian 库里给 Markdown 表格内嵌 `[[目标|别名]]` 时：

- **别名分隔符必须转义成 `\|`**。未转义时那根竖线会被当成表格列分隔符，Obsidian 渲出的表会多切一列。
  2026-11-04 在 `E:\OBsidian\全栈工程师学习计划` 的「项目路线表」（6 行）和「24 个月节奏表」（1 行）里就是历史遗留的未转义写法，脚本列数校验才暴露出来。
- 表格外（正文、列表）的 `[[A|B]]` 不用转义，别全局替换。

## 校验脚本的写法（本机实测踩过三次）

- **不要用 `re.split(r'(?<!\\)\|', ...)`**：在 Bash `<<'PY'` heredoc 里反斜杠会被压掉，落到 Python 变成
  `(?<!\)\|` → `re.PatternError: missing ), unterminated subpattern`。同理 `x != '\\'` 会变成 `'\'` →
  `SyntaxError: unterminated string literal`。
- 可行做法：
  - 数竖线：`sum(1 for n, ch in enumerate(line) if ch == '|' and (n == 0 or line[n-1] != chr(92)))`；
  - 取链接目标：`m.group(1).split('|', 1)[0].split('#', 1)[0].strip().rstrip(chr(92))`（先 split 再剥尾部反斜杠，不要玩 lookbehind）。
- 这条与 [[reference-windows-python-encoding]] 的「heredoc 里别手写反斜杠串」同源，一律用 `chr(92)` 或路径拼接。

## 其它 Obsidian 校验点

非空文件、代码围栏成对、内部链接可达（相对路径 + 库根两种解析）、表格列数一致、逐周计划的周次序列完整。
文件数/行数/链接数必须自己用脚本量 —— 见 [[feedback-subagent-write-reliability]]。
