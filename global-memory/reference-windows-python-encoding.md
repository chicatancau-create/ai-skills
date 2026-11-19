---
name: reference-windows-python-encoding
description: 本机 Windows 的 Python/Java/curl 控制台编码与路径坑：python3 是 rc=49 坏存根、stdout 默认 GBK、比对 UTF-8 必须 -X utf8、bash 风格路径不认、heredoc 压反斜杠、Git Bash 的 curl -d 会把中文 JSON 转码成 400。
metadata:
  type: reference
---

本机（Windows 10 28000 + Git Bash）实测，2026-09-28：

- `python` = `D:\PyCharm\Python\python.exe` → **3.14.2**；`python3` 解析到 `WindowsApps\python3.exe` 的 AppInstaller 存根，
  **零输出、退出码 49**。任何脚本一律用 `python`。
- **Python 的 stdout 默认按 GBK 编码**（实测 `sys.stderr.encoding=gbk`、`locale` preferred `cp936`）。
  同一段印中文的脚本做 A/B：`python x.py` 被按 UTF-8 读取得到 `"ż\ufffd\ufffd\ufffd\ufffd = 2550"`（首字符变 `ż` + 四个替换符），
  `python -X utf8 x.py` 才得到 `"偶数和 = 2550"`。**只要把 stdout 与 UTF-8 文本逐字比对（写门禁、写回归、写 expectedOutput），就必须带 `-X utf8`**，
  否则程序没错、判据却必然报差行。
- `javac` / `java` 的中文诊断在这台 Git Bash 里同样是 GBK 乱码（原始字节 `b4 ed ce f3` = GBK「错误」）；
  要读原文用 `javac -J-Dstderr.encoding=UTF-8 …` / `java -Dstderr.encoding=UTF-8 …`。取到的原始字节可留档当证据，别说「没报错」。
- gcc（MinGW 15.2.0）报错里的中文路径名也是 GBK 字节（`d6 d0 ce c4 c4 bf c2 bc`），按 Latin-1 直读会显示成 `ÖÐÎÄÄ¿Â¼`。
- 写 markdown/JSON 仍**不要用 PowerShell**（BOM/CRLF/GBK 会坏字节），见 [[feedback-windows-config-json-encoding]]；用 Write/Edit 工具或 Python 的 utf-8。
- `grep` 遇 GBK 文件会截断，要 `-a`；见 [[reference-powershell-through-bash-and-recyclebin]]。

## heredoc 里写 Windows 路径的坑（2026-10-08 反复踩）

即使用 `<<'PY'`（单引号定界，关掉变量/命令替换），**我自己在正文里写的双反斜杠仍会被压成单个**，
于是 python 侧出现三类静默破坏：

- `'D:\\npm-global'` → 落到 python 变成 `'D:\npm-global'` → `\n` 被解释成换行，
  写出的 `.cmd` 里 `set "PATH=D:` 换行 `pm-global;..."`，脚本语法没报错但整行报废。
- `r'C:\'` → **原始字符串不能以反斜杠结尾** → `SyntaxError: unterminated string literal`
  （这就是让 Gemini CLI 扫描脚本静默秒死的真因，提权跑时 stdout 没接走，报错看不见）。
- 文档字符串里写 `C:\Users` → `\U` 触发 `unicodeescape` 解码错。

**做法**：路径一律用 `os.path.join` / `os.environ[...]` / `chr(92)` 拼，**不要在 heredoc 里手写反斜杠串**；
含中文的 `.ps1` 用 `encoding='utf-8-sig'` 写（PowerShell 5.1 无 BOM 会按 GBK 解析整段失败），
纯 ASCII 脚本才用 `encoding='ascii'`；写文件走 `.new` + `os.replace`（见
[[feedback-destructive-file-ops]] 第 7 条）。

**同一类坑还有“写 JS 字符串里的 `\n`”**（2026-11-09 连吃两回合）：用 Python heredoc 做替换、
生成 `JSON.stringify(...) + '\\n'` 这一行时，反斜杠被压成真换行，Node 直接报
`SyntaxError: Invalid or unexpected token`；改成 `String.fromCharCode(10)` 或用**按行重写**整段尾部才通过。
⇒ 生成含转义序列的 JS/JSON 时，优先用 Write 工具直写，或按行拼接；不要用 Python 字符串替换去插 `\n`。
同时替换失败时不要只改一处：残留的 `} finally {` 会让语法错继续指向同一行，要整段重写而不是局部补。

**压完不等于报错——最坏的一支是「静默写进文件变成不可见控制字符」（2026-11-15 实测两次）。**
`\\2026` 被压成 `\2026` 后，Python 按**八进制**消费 `\202` → **U+0082**、`\01` → U+0001、`\02` → U+0002；
`\node_modules` 里的 `\n` 直接把一行劈成两行。全程**不报任何错、文件仍能 UTF-8 解码、Read 显示完全正常**，
只有 `repr()` 或按码点正则 `[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]` 才现形（放行 `\t\n\r`）。
另一支：`printf`/`echo -e` 里 `\e` → **ESC U+001B**（手册 README 第 91 行就躺着一个，原文本意是 `\encryption.data`）。

三个反直觉点：① **替换用的"正确字符串"同样会被吃**——我第一次修复就是把损坏原样写回去还多加了 U+0001；
② **校验语句本身也会被吃**——`for c in "\u0080-\u009f"` 实际只遍历几个字面字符（含 `-`），
对干净文件报出「残留 218」，假阳性与假阴性同源；
③ 所以改文件必须三件套齐了才落盘：**改前备份 → 匹配数断言 → 写盘后按码点复检**。
正解仍是 `chr(92)`/`chr(10)` 拼，或干脆走 Write/Edit 工具（字面写入、不经解释层）。
正文与完整证据见手册 `03-通用/03-调试与验证/踩坑-Bash内联传参吞PowerShell变量与反斜杠.md` 的 2026-11-15 追加节。

**反斜杠被压掉的不止 heredoc —— 工具调用参数那一层也会（2026-10-19 连踩三次）。**
我在 Bash/Write 参数里写 `r'E:\nodejs'` 或 JS 里的 `'D:\\Work…'`，经 JSON 解码后 `\\`→`\`，
于是出现三类静默破坏：`cwd=r'E:\nodejs'` 变成含换行的路径 → `NotADirectoryError [WinError 267] 目录名称无效`
（看着像"目录被删了"，我因此差点误判用户删了仓库目录）；JS 里 `'\W'`→`W` → 拼出的 Windows 路径丢掉所有分隔符，
让一次"带环境变量"的测试整组作废、我差点据此得出错误结论；`'…\U…'` → `unicodeescape` SyntaxError。
⇒ **跨工具传 Windows 路径只有三条安全路**：正斜杠（`E:/nodejs`，Python/PowerShell 都吃）、
`os.path.join` / JS `path.join`、或运行时用 `chr(92)` 拼。**别在任何参数里手写反斜杠字面量**，
且凡是"路径不存在"的报错先 `os.path.isdir` 复核再下结论。

**还有一条同源错误**：同一轮里我反复把脚本文件名敲错（`claude-purge.ps1` vs 实际的 `purge.ps1`），
于是把「找不到文件」误判成「脚本没执行/静默失败」。凡是报错说路径不存在，**先用 `ls`/glob 拿真实文件名**
（`f=$(ls *purge*.py | head -1); python "$f"`）再继续，别凭记忆重敲。另外 `open(p,'w')` 会**先截断**再抛编码错，
失败一次就把原文件清空了 —— 改内容必须写临时文件 + `os.replace`。

## bash 风格路径在 Windows Python 里必然失败（2026-10-30 连踩两次）

Bash 工具里 `/d/foo`、`/g/AIrenwu`、`/tmp/x` 是 MSYS 视图，**Windows 版 python 完全不认**：
`open('/d/platform-tools.zip','rb')` → `FileNotFoundError`，看着像"下载没成功"，其实文件在 `D:\` 上好好的。
`ls -la` 和 `wc -c` 能读它是因为它走的是 bash 的路径转换。

⇒ 同一条命令链里混用 shell 与 python 时，**传给 python 的路径一律写 `D:/...`、`G:/...` 正斜杠形式**；
或者干脆用 stdin 把内容喂给 python（`curl ... | python -c "import sys; sys.stdin.read()"`），绕开落盘路径。
报"文件不存在"先分清是**哪一侧**在解释这个路径。

## `$(python -c ...)` 会带 `\r` 回来，把 shell 判断全骗掉（2026-11-01 实测）

Windows 版 python 的 stdout 是 **CRLF**，所以 `for p in $(python -c "…print 路径列表…")` 里除了最后一项，
每项都尾随一个 `\r`。于是 `[ -f "ets/$p.ets" ]` 对 6 个真实存在的文件报 MISSING、只有末尾那个报 OK，
看起来像「路由指向不存在的文件」，其实是我的循环参数被 `\r` 污染。
⇒ 别用 python 的 print 给 bash 喂列表；把清单直接写在 `for` 里，或加 `| tr -d '\r'`。
凡是「批量存在性检查只有一项通过」，先怀疑行尾而不是怀疑文件。

同源噪声：`grep -rhoE "(\$rawfile\()"` 这类带括号的模式写在 bash 双引号里会报 `Unmatched ( or \(`
（`$(` 被当作命令替换开头），白白吃掉一个回合。⇒ 结构化的代码检索直接用 Grep 工具，别拼 bash 里的 grep 正则。

## 容量与磁盘测量的两个坑

- `os.statvfs` **在 Windows 上不存在** → 用 `shutil.disk_usage('C:')` 或 PowerShell `New-Object IO.DriveInfo`。
- `os.path.join("C:", "pagefile.sys")` 生成的是 **驱动器相对路径 `C:pagefile.sys`**（不是 `C:\pagefile.sys`），
  `os.stat` 直接报 WinError 2「找不到文件」，我就据此差点宣布"C 盘的页面文件消失了"。
  ⇒ 盘符根下的文件必须写 `"C:\\\\pagefile.sys"` 或 `"C:/" + "pagefile.sys"` 或 `os.path.join("C:\\\\", f)`；
  凡是"重要系统文件突然不存在"的读数，先打印出实际用的路径串再下结论。
- 单位会骗人：`shutil` 返回字节，除以 `1e9` 是 **GB**，PowerShell `/1GB` 是 **GiB**（2^30），
  同一块盘两个数差 ~7%。报数前先写清单位，别把两者当矛盾去「查真相」。
- 逐目录 `os.walk` 求和会**重复计数硬链接/稀疏文件**（本机实测 `C:\` 各顶层目录之和比卷「已用」多约 13 GB，
  主因 `WinSxS` 与 `System32` 共享硬链接），所以目录求和 ≠ 实际占盘，别据此宣称藏了多少垃圾。

## `python -X utf8 -c "…"` 内联脚本经 bash 会烂（2026-11-04 一轮内连炸 4 次）

上面"压反斜杠"那条在 **bash 双引号里的 `python -c`** 上表现得更恶劣，因为 bash 会先做一层
`$`/反引号/反斜杠处理，报的还是**误导性的 Python 语法错**：

- 脚本里有反引号（markdown 内容、`` `verified` `` 之类）→ `unexpected EOF while looking for matching ``'`。
- 写 `r"D:\"` → **原始串不能以反斜杠结尾** → `SyntaxError: unterminated string literal`。
- 写 `\u540e\u53f0` 混 `\\` 时 → `(unicode error) 'unicodeescape' codec can't decode … truncated \UXXXXXXXX escape`。
- 写 `$var` 会被 bash 吃掉（PowerShell 侧同理，`$_`/`$p` 都会没）。

⇒ **只要脚本超过两三行、或含中文/反引号/正则/Windows 路径，就用 Write 工具建 `.py` 文件再跑**；
需要生成带 BOM+CRLF 的 `.ps1` 时，也用这个 `.py` 去生成（见 [[reference-unattended-elevated-scripts]] 的生成通路）。
提权侧还有一条：`Start-Process -Verb RunAs -ArgumentList '-Command','python -c …'` 经常**静默不产出**
（产物文件根本不出现），要提权跑东西就 `-File` 指一个生成好的 `.ps1`，别拼 `-Command`。

**bash 双引号里的反引号会真的被执行**（同日改文档时踩到）：`python -c "…改 `start-hud-next.bat` 字串…"`
会把命令名当命令跑，报 `command not found`，同时把这个词从字符串里**挖空**写进文件。
⇒ 任何含反引号/`$( )` 的正文（尤其是要写进 md 的 code 片段）只能用 Write/Edit 工具或 `<<'PY'` 落盘；
用 bash 内联 python 改文档后要回读那一行。

## Git Bash 的 `curl -d` 会把中文 JSON 转码（2026-11-07 实测）

在 Windows Git Bash 里把中文直接写进 `curl -d '{"name":"Java 迁移验证"}'`，Spring Boot 返回 **400**；
同一接口换成 ASCII 名字立刻成功。原因是参数经过本地代码页（GBK）转换，服务端按 UTF-8 解 JSON 失败。
这不是应用校验 bug，node/应用内测试直接构造 UTF-8 字符串也不受影响。

⇒ 冒烟脚本优先用 ASCII 字段；必须发中文 JSON 时，把 payload 写成 **UTF-8 文件**再用
`curl --data-binary @payload.json`，或把请求放进应用内测试。别把这类 400 误判成接口或校验逻辑错误。
