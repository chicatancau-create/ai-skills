---
name: reference-windows-batch-entry-encoding
description: Windows .cmd/.bat 的十四个坑：UTF-8 正文会劈行(中文可用但必须 GBK+CRLF)、LF-only 吞字符、"%~dp0" 尾反斜杠、echo. 被同名空文件咬、bash 把 nul 改成 /dev/null、中文别当参数穿 bat、timeout /t 在非交互 stdin 报错、无参数分支静默、net session 判管理员依赖 LanmanServer 会致提权死循环(改用 fltmc)、choice /D 默认档落在 errorlevel 最大档、无权限读到的判据别写成否定结论、call :label a=b 会被当变量赋值吃掉致参数前移(实参加引号)、Git Bash 会把 schtasks 的 /Create 当路径改写
metadata:
  type: reference
---

写或改 `.cmd` / `.bat` 双击入口时：**行尾必须 CRLF，正文只能是 ASCII 或 GBK 二者之一**，
并且**别把 `%~dp0` 原样塞进带引号的参数**。

**中文能不能写进 .bat**：能 —— 2026-10-05 实测一份 435 行、满屏中文提示的 GBK `.bat`
在提权和非提权下都零报错、控制台正常显示。禁止的是**UTF-8 中文**（坑 1）。所以写中文的
正确姿势是：先按 UTF-8 起草，再用 python `.encode('gbk')` 转码写入（strict 编码会当场
顶出任何 GBK 装不下的字符，等于自带校验），并在文件头 `rem` 里写明"编码 ANSI/GBK，
别用 UTF-8 保存"。转码后 `%%TEMP%%`、`%%{http_code}` 这类要留双百分号的行都要复看。

**坑 1 — UTF-8 非 ASCII 正文**：cmd.exe 按当前 ANSI 代码页（本机 936/GBK）逐字节解析批处理，
UTF-8 中文尾字节常凑出 `0x26 &`、`0x7c |`、`0x22 "`，一行从中间劈开；更常见的是最后一个中文字节的
尾字节**吃掉紧跟其后的 `\`**，路径直接变成 `缃戦〉绔痋dist`。典型报错对不上源码内容：

```
'?'rem' 不是内部或外部命令
'HER" (' 不是内部或外部命令
```

注意 `%~dp0` 展开出的中文是运行期从系统拿的，**永远是对的**；错的只有文件里手打的那些字面量。

**坑 2 — LF-only 换行**：cmd 按 CRLF 假设重定位读文件，LF-only 会逐行错位并**吞掉行首若干字符**，
于是 `set` 变成 `'se'`/`'t'`、整条赋值行报废、`if not exist (...)` 守卫也不执行。后果不是「报个错」而是
**变量全空还继续往下跑**：例如 `electron "%APP_ROOT%"` 拿到空参数，就打印 Electron usage 并弹出
Electron 原生欢迎窗，看着像「装坏了」。看到 `'o'` / `'se'` / `'t'` / `'"VAR="'` 这种**残句式**
「不是内部或外部命令」，先查换行和编码，别查逻辑。

**坑 3 — 尾反斜杠转义引号**（与前两条独立，改完编码仍会中招）：`%~dp0` 结尾自带 `\`，
`call prog "%APP_ROOT%"` 展开成 `"G:\dir\"`，`\"` 是转义引号，程序收到的参数变成 `G:\dir"`，
Electron 报 `Cannot find module 'G:\dir"'` / `Unable to find Electron app at ...`。
修法：另存一个去掉尾分隔符的变量再传，`set "APP_DIR=%APP_ROOT:~0,-1%"`。

**坑 4 — `echo.` 被当前目录里的同名空文件咬掉**（2026-10-05 实测，最难猜的一条）：
本机 `C:\Windows\System32\echo` 是一个 **0 字节文件**（2026-09-12 23:42 起存在）。`echo.` 这个词
带点，cmd 会先拿当前目录里的文件去匹配，匹配到 `echo` 就当程序执行 → 报
`'echo.' 不是内部或外部命令`。**只在提权时发作**：自提权脚本的 `cmd /c` 子进程默认停在 System32。
同一份脚本非提权跑就一条不错，极易误判成"GBK 多字节 + goto 偏移漂移"（我照这个猜想做最小用例
复现了三轮，全部不复现，最后靠 `@echo on` 让 cmd 自己吐出 `C:\Windows\System32>echo.` 才定案）。
修法两条一起用：开头的 `echo.` 全换成 `echo(`（不带点，走内部命令），并且
`setlocal` 后立刻 `cd /d "%~dp0" >nul 2>&1`。

**坑 5 — Git Bash 会把命令行里的 `nul` 改写成 `/dev/null`**：`python -c "... >nul 2>&1 ..."`
写进 `.bat` 的那一行会变成 `>/dev/null`。绕法：把字面量拆开（`'>n'+'ul'`），或先落成 `.py` 文件再跑；
同理 `"`+'\r\n'.join(...)` 里的 `\r\n` 被 `.split()[0]` 取反会静默变成空串，插入行必须回读确认。

**坑 6 — 中文路径别当参数穿过 .bat**：`verify.cmd <中文路径>` 里 `%~1` 展开的是**已经过 OEM 代码页转手**的字符串，`应用端` 会变成乱码，下游工具报「No such file or directory」，极易误判成被调用方的 bug。同类：`cmd /c 'call "C:\Program Files (x86)\x\vcvars64.bat" >nul && set'` 会被 cmd 的引号剥离规则打回原形（实测只解析出 1 个环境变量）。两条的解法都是：**让 .bat 完全 ASCII、不携带任何非 ASCII 文本或参数**，需要中文路径时由 Python 以 Unicode argv 直接调目标程序；要抓 vcvars 环境就单独写一份 ASCII bat 执行 `call vcvars64.bat >nul && set > env.txt`，再用 **gbk** 解码读那个文件。

**坑 7 — `timeout /t N` 在非交互 stdin 下直接报错**（2026-10-09 实测）：脚本被
`powershell Start-Process wt.exe -ArgumentList 'cmd','/k','D:\agy\switch.cmd'` 这类方式拉起来时，
`timeout /t 2 >nul` 输出 `timeout: invalid time interval '/t'` + `Try 'timeout --help' for more information.`
（注意那句 help 是 **coreutils 的 timeout**，说明这条命令根本没走 cmd 内建的 timeout）。
它不中断脚本，但那行报错会明晃晃留在用户看得见的窗口里。可靠写法是带退路：
`timeout /t 2 >nul 2>&1 || ping -n 3 127.0.0.1 >nul`。

**坑 8 — 壳子的「无参数」分支要自己补**：`ag.cmd <account> [args...]` 这种写法在 `%~1` 为空时
只会打 usage 然后 `exit /b`，用户漏掉占位符（例如该写 `-` 的位置）就表现为「敲了啥也没发生」。
正确做法：空参数分支也要正常执行目标程序，并在文件里用 `rem` 注明 `%*` 不受 `shift` 影响、
`shift` 之后必须显式传 `%1 %2 ... %9`。

**坑 9 — 自我提权脚本别用 `net session` 判管理员**（2026-10-12 实测）：`net session` 依赖 LanmanServer 服务，
非管理员下 rc=2、管理员下靠服务活着；一旦该服务被停，管理员也会被误判成非管理员，配上「非管理员就 `-Verb RunAs`
重开自己」就是**无限 UAC 循环**。改用 `fltmc`（非管理员 rc=1，只依赖过滤管理器）。本机 LanmanServer 现为 Running，
所以这条是预防、不是已发生故障 —— 写进记录时要这么说。再加一道护栏：提权重开前先 `set "X_FROM_ELEVATION=1"`，
子进程继承环境变量，第二次仍判非管理员就直接报「提权被拒」退出，不死循环。

**坑 10 — `choice` 的 `/D` 默认档落在「errorlevel 最大档」，分支必须从大往小判**（2026-10-12 实测）：
`choice /C YN /T 30 /D N` → errorlevel **2**；`choice /C 12N /T 30 /D N` → errorlevel **3**。
`if errorlevel N` 是「≥N」不是「=N」，所以取消分支要写成最先的那条（`if errorlevel 3 goto :cancelled` 在前，
`if errorlevel 2 ...` 在后）。凡是「默认=不动作」的脚本，先单独跑一份只 echo `%errorlevel%` 的 choice 探针，
再决定 /C 的字符顺序 —— 排错一次就是把真重启命令放进了默认路径。

**坑 11 — 无权限时读不到的判据，不能写成否定结论**：`bcdedit /enum {fwbootmgr}`（UEFI 判据）非管理员返回「拒绝访问」，
照 `if errorlevel 1 → 本机不是 UEFI` 写就把「判不了」报成了「不是」。体检/只读模式必须分三态输出：
有权限且是 / 有权限且不是 / 无权限所以判不了。取真值靠提权后跑（`Start-Process -Verb RunAs` + 把输出重定向到 TEMP 文件再读，
本机可用且无弹窗阻碍）。

**坑 12 — `call :label a=b` 被 cmd 当成变量赋值吃掉，参数整体前移且零报错**（2026-11-06 实测）：
`call :dns_srv %%A %%B %%C ...` 里 `%%A` 展开成 `ip=192.168.55.131` 时，cmd 把这段当成「给变量 ip 赋值」，
从参数表里剥掉，于是子过程收到的是 `%1`=ip、`%2`=192.168.55.131、`%3`=if、`%4`=19 …——**整体前移一位**，
`%~1` 拿到的是键名不是键值。表现是输出串成 `网卡.168.55.131  应答 pms` 这种**没有报错的乱码**，
排查者极易去怀疑解析逻辑本身。解法只有一条：**实参一律加引号** `call :sub "%%A" "%%B"`，
子过程继续用 `%~1` 取。写「把结构化输出喂给 bat 子过程」的代码时，先单独跑一个只 echo `%1..%6` 的最小用例。

**坑 13 — 从 Python 直接 `subprocess.run(["npm", ...])` 会 `FileNotFoundError: [WinError 2]`**（2026-11-08 实测）：
本机 `npm`/`npx` 是 `.cmd` 垫片，`CreateProcess` 只认可执行映像，不执行批处理；在 Git Bash 里手动敲能跑，
所以很容易误判成路径或 venv 问题。修法：非 `.exe` 的命令统一前置 `["cmd", "/c", *argv]`，
或 `shutil.which()` 找到 `.cmd` 后再包一层。写「一键跑门禁」的脚本时，逐条门禁都要覆盖这条。

**坑 14 — Git Bash 会把 `schtasks /Create` 的 `/Create` 当路径改写**（2026-11-08 实测）：
在 bash 里直接 `schtasks /Create ...`，MSYS 把 `/Create` 转成 `C:/Users/.../git/Create`，
报「无效参数/选项 - 'C:/.../Create'」；`/Run`、`/Delete`、`/F` 同理。修法：`export MSYS_NO_PATHCONV=1`
后再调 schtasks（或走 `cmd //c`）。这与 `tasklist //FI`、`taskkill //F //PID` 是同一类 MSYS 路径转换问题。
计划任务做交互式探针时用 `/SC ONCE /ST 23:59 /IT /RL LIMITED`，跑完立刻 `/Delete /F`；
判断任务是否真的启动要看 `Get-CimInstance Win32_Process` 里目标进程的 CommandLine 与 SessionId，
`schtasks /Run` 的「成功」只表示尝试启动。

**坑 15 — Git Bash 里 `cmd /c` 的 `/c` 也会被 MSYS 当路径改写**（2026-11-08 实测）：`cmd /c npm test`
在 Git Bash 里只打印 cmd 横幅和提示符，命令没执行；要写 **`cmd //c npm test`**（与 `schtasks /Create`、
`tasklist //FI` 同类）。Python 脚本里拼 `["cmd","/c",...]` 不受影响，只有 shell 里手敲会中招。

**How to apply**：用 `python`（不是 python3，本机是坏存根）二进制写入；纯 ASCII 入口用
`body.replace('\n','\r\n').encode('ascii')`，中文入口用 `.encode('gbk')`——两者都会在
非法字符上直接抛异常，等于自带校验。改完必跑三个静态审计（都是这次真抓到 bug 的）：
① 正则收集所有 `goto :X` / `call :X` 的目标，与 `:X` 定义求差集 → 漏写标签会**当场中断整个脚本**；
② 扫 `!\w+%,` 这种"延迟展开少了个 `!`"的打字错；③ python 数 `CRLF` / `LF-only` / 非法字节。
再动态验证：**提权跑一遍**（不跑提权就看不见坑 4），并加一个只读模式（本机 `check` 参数）
做零副作用复验；动态验证顺序 ① 变量非空 ② 只读模式 ③ 真改动。
仓库根加 `.gitattributes`：`*.cmd text eol=crlf`（`core.autocrlf=true` 下 LF 文件在
`git status` 里是**干净的**，所以这个 bug 能无声穿过提交，必须显式钉住）。
中文提示可以留在脚本里（按上面 GBK 规矩），但面向用户的长说明仍放 README。

**取原生错误框文字**（Electron/Win32 的 `#32770` 框 `WM_GETTEXT` 取不到正文）：
先 `ctypes.windll.user32.SetProcessDPIAware()`（否则 125% 缩放下 `GetWindowRect` 与截图坐标系错位，
只会拍到一条黑边），再 `EnumWindows` 拿 rect → `PIL.ImageGrab.grab(bbox=...)` → Read 那张 PNG 直接读字。
`ELECTRON_ENABLE_LOGGING=1` 对主进程未捕获异常**没用**，控制台仍然空的。

本机状态(2026-10-05 更新)：那个 System32 里 0 字节的 [echo] 文件已按用户授权删除；删后原失败用例（cwd=System32 加 echo.）复跑立刻恢复正常，因果闭环。同一次事故还留下 6 个 0 字节碎片文件躺在 System32：[18]、[Canvas]]、[或更高版本：]、[提供，必须先安装]、[未检测到]、[本应用的登录]，全部落在 2026-09-12 23:42:18-23:42:42 这 24 秒内。判垃圾的依据：links=1 且无数字签名，而合法 System32 文件是 links=2 + owner=NT SERVICE\TrustedInstaller —— 即某次在 System32 里跑的提权脚本把中文文本和重定向符拆错了。**这 6 个未删，等用户点头。**另记一条 bash 侧的坑：在 python -c 的双引号字符串里写反引号，会被 bash 当命令替换执行（这次就把写进记忆的一段啃空了）；带反引号/特殊字符的文本一律落成 .py 文件再跑，heredoc 用单引号定界符（<<'PY'）彻底关掉替换。

**坑 16 — `core.autocrlf=true` 会把 `.sh` 检出成 CRLF，bash/Docker 直接跑不起来**（2026-11-09 实测）：
仓库开了 autocrlf 时，`.gitattributes` 若只钉了 `*.cmd text eol=crlf`，**shell 脚本在没有对应 `eol=lf`
的情况下新克隆会得到 CRLF**（行尾的 `\r` 会进 shebang 和每条命令）。修法：在 `.gitattributes` 里对
`*.sh  *.mjs  *.js  *.ts  *.tsx  *.yml  *.yaml  *.conf  Dockerfile` 全部显式 `text eol=lf`，
Windows 入口（`*.cmd *.bat *.ps1`）保持 `eol=crlf`。判现状用 `git ls-files --eol <file>` 看 `i/lf w/lf`。

Related: [[feedback-windows-config-json-encoding]], [[reference-windows-python-encoding]], [[reference-computer-use-blocked]]
