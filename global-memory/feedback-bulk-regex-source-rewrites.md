---
name: feedback-bulk-regex-source-rewrites
description: 脚本批量改写源码的硬规则：先整目录备份、替换必须断言且全成才写盘、循环正则会因 \s 吃掉自己插入的换行而死循环、拆粘连行用 tokenizer
metadata:
  type: feedback
---

用 Python 脚本跨多文件批量改源码（删属性链、拆粘连行、裁未用导入）时：

1. **先 `cp -r` 整个源码目录到 TEMP 再动手**；脚本里每处 `replace` 都写「找不到就 `raise SystemExit`」，并且**一个文件的全部替换都成功后才写盘**，否则会留下半改文件。
2. **`while re.search(p): s = re.sub(p, ...)` 会死循环**。2026-11-02 一条拆粘连行的命令就是这样挂到超时被杀：替换插进去的 `\n` 属于 `\s`，下一轮 `search` 照样命中而 `sub` 结果幂等。
   拆行改用逐字符 tokenizer：遇 `)` 后数空格 ≥4，且下一个字符是 `.` / `}` / 大写字母 / `$` 才断行；跑完自己数 `remaining joined lines` 必须为 0。
3. 删一整条链式调用要**按括号配平**扫描，不能用 `[^}]*` —— `stateStyles`/`showAlertDialog` 里有嵌套花括号，非贪婪会漏删或多吃代码。
4. 撤掉某个 API 之后必须**回头补语义与签名**，这类是编译期才暴露的连带伤：
   底色本来只有 `linearGradient`（撤完标题条/价格条变透明，要补 `backgroundColor`）；
   删确认弹窗后 `@Builder itemEnd` 的参数个数与调用点不一致（`Expected 2 arguments, but got 1`）；
   顺手写的 `itemEnd(index)` 丢了 `: number` 会撞 `arkts-no-any-unknown`。
5. 正则批量改完别只看「编译过」：导入块会被压成一行、注释会和新行为互相矛盾（我留过一条「日历弹窗待查」而下面已经接上了），要逐处目检注释与代码是否一致。

6. **全库替换「路径前缀」会连标识符一起改**（2026-11-09 实测，我造成的）：把 `project0X/` 批量改成
   `projects/project0X/` 时，同一条正则也命中了 CI 的 **job id**（`project01:` → `projects/project01:`），
   而 GitHub Actions 的 job id 只允许 `[A-Za-z_][A-Za-z0-9_-]*`，**斜杠会让整个 workflow 无法解析**。
   规则：改前缀只匹配「引用位置」（`working-directory`、`cache-dependency-path`、文档链接），
   或在替换后用解析器校验——YAML `safe_load` 后逐个 job id 过正则、再确认没有 `projects/projects` 连环前缀。

7. **`awk 'NR==FNR{next}{print}' file > .t && mv .t file` 会把文件写空**（2026-11-15 我造成的）：`NR==FNR` 只在**两个**输入文件时才有意义，单文件时它对每一行都成立，于是全部行被 `next` 跳过。
   当场把 `E:\本地AI使用手册\03-通用\03-调试与验证\README.md`（97 行 / 44144 字节 / 85 条链接）写成 0 字节，靠**动手前先建的备份**恢复回来了。
   规则：改用户的知识库/单文件配置一律用 `Edit` 工具做定点替换，不要 `awk`/`sed` 就地重定向；非用 shell 追加时只用 `>>`，不要「读一遍再重写」。
   改完必须核 `wc -l`、`wc -c` 与链接计数，并和备份比对确认**只增不减**。

相关：[[reference-windows-python-encoding]]（heredoc 会压反斜杠，脚本里路径用 `chr(92)`）、[[feedback-verify-subagent-file-claims]]、[[reference-harmony-hvigor-cli]]、[[feedback-local-ai-manual-protocol]]（写手册前先备份目标文件）
