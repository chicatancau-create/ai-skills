---
name: windows-gui-control
description: 这台 Windows 上「操控电脑 / 操作 GUI / 截图看界面 / 点按钮 / 发快捷键 / 打开某软件里的文件」的唯一标准做法。**允许在前台操作，但不许抢用户的前台**：动手前先用 `useridle.py` 判用户是否正在用电脑——用户在操作就先停、先让路；用户没在用时可以正常激活窗口、点击、发快捷键。用户只要让你操控软件界面、看某个窗口里的内容、或在 Adobe XD 等桌面软件里做操作时，先加载本 skill 再动手。
---

# 本机 GUI 操控：唯一标准做法（能动前台，但不抢前台）

## 这是被动技能：什么时候自动生效

**任何**「要去看某个窗口长什么样」「要点某个软件里的按钮」「要用快捷键让它打开文件」「要证明某个界面状态」的任务，都必须走本 skill，不要临时另写一套。
`~/.dsh/AGENTS.md` 已把这条写进常驻规则，用户不需要每次提醒。

## 铁律 0：让路，不是禁止（用户 2026-11-11 的两次澄清）

用户原话：

> 「不要再去抢我的前台了，搞得我很难受！」
> 「我不是不让你操作前台，我是不让你抢我的前台」
> 「只要我在前台进行操作的时候，你就默认先停一下，先暂停」

**允许**在前台操作（激活目标窗口、点击、发快捷键）；**禁止**把用户正在用的窗口挤下去、把焦点从他手里夺走。

### 动手前必须先判「用户是不是在用电脑」

```bash
python "C:\Users\Admin\.dsh\tools\gui-control\useridle.py"
#   idle    : 122.78s (threshold 5.0s)
#   foregrnd: 787174  '用AI控制XD制作文件 — DeepSeekRuntime'
#   verdict : USER_IDLE -> free to operate in the foreground
```

| verdict | 含义 | 该怎么做 |
|---|---|---|
| `USER_ACTIVE` | 最近 5 秒内有键鼠输入，前台是用户的窗口 | **先停**：等、或先问一句「现在可以动一下界面吗」。不许抢 |
| `USER_IDLE` | 用户没在操作 | **直接做**：激活目标窗口、点击、发键都行，不必逐次申请 |

`useridle.py --json` 给机器读，`--threshold N` 调灵敏度（聊天类场景 10–15 秒更稳）。

### 绝对禁止的「抢」（与用户是否授权无关）

| 禁止 | 为什么 |
|---|---|
| 用户正在用的窗口被挤到后面 / 焦点被夺走 | 这就是用户说的「抢」，最招人烦 |
| `SetWindowPos(HWND_TOPMOST)` 盖住他的窗口 | XAML 应用还清不掉，一盖就赖着 |
| 最小化用户的窗口腾地方 | 打断他；只有他同意时才短暂用并立刻恢复 |

### 允许且推荐的（完全不碰焦点）

- `pwcap.py` 的 `PrintWindow` 抓图——**能抓到被完全遮挡的窗口内容**，是 UWP 界面唯一可靠取证方式
- 枚举窗口、读标题/类名/矩形/样式
- 直接读写文件（`.xd`、`.docx`、配置、日志……）——**能文件级解决就绝不碰界面**
- 启动程序（用户没在用时启动，别顺手把它顶到前台）

### 真的动鼠标键盘时，仍必须

1. 每次点击前用 `WindowFromPoint` + `GetAncestor(GA_ROOT)` 确认该像素**真的属于目标窗口**（防点歪打到用户窗口里，曾误关他的 HBuilderX / 浏览器标签页）；
2. 抢不到前台就**中止并记录 NOFOCUS**，绝不盲点；
3. 中途发现用户开始操作了 → **立刻让出**，不要硬顶。
4. 做完把界面恢复到他原来的样子（他同意最小化过的窗口要还回去）。

## 能力分层（从上往下选，能用上层就不用下层）

| 层 | 手段 | 是否动前台 |
|---|---|---|
| T0 | 直接改文件 / 读文件（zip、docx、json、注册表、日志） | 否 |
| T1 | `PrintWindow` 截图 + 窗口枚举取证 | 否 |
| T2 | 启动/关闭进程、等待窗口出现 | 否 |
| T3 | 激活窗口 + 键鼠注入（`SendKeys`、`mouse_event`） | **是**——用户 `USER_IDLE` 时可直接用；`USER_ACTIVE` 时先停 |

## 工具（本机已装，别重写）

机器级（任何项目都能用）：`C:\Users\Admin\.dsh\tools\gui-control\`
XD 专用：`C:\Users\Admin\.dsh\tools\xd\`（`xd-open.ps1` 打开文件、`xd-accept.py` 预览窗点测；`.xd` 的格式与生成见 `xd-authoring` skill）
Python：`C:\Users\Admin\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe`（含 Pillow；跑前设 `PYTHONIOENCODING=utf-8`）

| 工具 | 用途 |
|---|---|
| `winlist.py` | 列全部可见顶层窗口：hwnd / pid / class / rect / title。**排查"窗口在哪"第一步** |
| `pwcap.py <hwnd> [out.png] [maxw]` | **PrintWindow 后台抓图**（PW_RENDERFULLCONTENT）。被遮挡也能抓，是 UWP 内容唯一可靠截图法；`out` 默认落临时目录。也可当模块用：`from pwcap import capture; img = capture(hwnd)`（已加 `__main__` 保护，可安全 import） |
| `useridle.py [--json] [--threshold N]` | **动手前第一步**：判用户是不是正在用电脑。输出 idle 秒数 / 前台窗口 / `USER_ACTIVE` 或 `USER_IDLE`；也可 `from useridle import user_is_active; user_is_active(5.0)` |
| `maxcap.py <hwnd> <out.png>` | 先恢复+最大化再 PrintWindow（会短暂动窗口，`USER_ACTIVE` 时别用） |
| `crop.py <src> <out> "x0,y0,x1,y1" <scale>` | PIL 裁剪放大，看细节用 |
| `tapcalc.py <png> <ax> <ay> ...` | 从截图反推「画板坐标 → 屏幕坐标」的比例与原点 |
| `docmin.py min\|restore` | 最小化/恢复文档窗口（会短暂动窗口；`USER_ACTIVE` 时先问，用完恢复） |
| `shot.ps1` | 全屏截图（1500 宽，屏幕坐标 = 截图坐标 × 2048/宽） |
| `pvact.ps1` / `focus.ps1` / `key.ps1` / `click.ps1` / `maximize.ps1` / `cleanlaunch.ps1` | **T3 键鼠与激活**：`USER_IDLE` 可直接用；`USER_ACTIVE` 先停 |

## 已验证的硬事实（省得再踩）

1. **DPI 虚拟化**：不声明 DPI 感知时 `GetWindowRect` 给逻辑坐标、`PrintWindow` 给物理像素，两套单位混用 → 点击全偏。所有脚本开头必须 `SetProcessDPIAware()`。
2. **`ImageGrab` / `BitBlt` 抓不到 UWP（XAML）合成内容**，得到纯灰空图或黑图；`PrintWindow(hdc, PW_RENDERFULLCONTENT=2)` 可以。
3. **窗口可能不属于应用进程**：XD 等 UWP 应用的窗口挂在 `ApplicationFrameHost` 上，按 `Get-Process <app>` 的 pid 过滤窗口会漏掉。用 `winlist.py` 按标题找。
4. **`GetForegroundWindow()` 可能返回 0**（不是锁屏）。判断"前台是不是目标"不能用它单独下结论，用 `WindowFromPoint` 命中测试。
5. **Windows 会拒绝 `SetForegroundWindow`**，而且 XAML 应用对 `SetWindowPos(HWND_TOPMOST)` 不敏感、`HWND_NOTOPMOST` 清不干净 → 一旦置顶就很难消掉，所以**别随手置顶**。
6. **`PostMessage` 发快捷键对 XAML 应用无效**，`SendKeys` 只发给真正的前台窗口。
7. **窗口状态在两次调用之间会变**（被最小化到 `-32000,-32000`、丢掉焦点、对话框自动关闭）→ 「激活→等对话框→填路径→回车」必须挤在**同一个进程**里连续完成，拆成多次调用必失败。
8. **`GetWindowTextW` 不写 `CharSet=CharSet.Unicode` 会得到首字节乱码标题**；自绘标题栏的窗口，`GetWindowText` 返回的常常不是用户看到的那串文字。
9. **PowerShell 5.1 读无 BOM 的 .ps1 会按 GBK 解码**：脚本里的中文匹配串（如 `'*打开*'`）变成 `鎵撳紑`，永远匹配不到 → 表现为"点了没反应"。含非 ASCII 的 .ps1 **必须 UTF-8 带 BOM + CRLF**。这是本机第一大坑，已在 `~/.dsh/AGENTS.md` 记录。
10. **`pwsh` 是 Windows PowerShell 5.1**：命令里出现 `$`、配对反斜杠、长 here-string 一律落成文件再跑，不要内联。
11. 变量名不能叫 `$home` / `$x`（与参数 `$X` 大小写不敏感撞车）等，PowerShell 只读变量赋值会直接报错。
12. **PrintWindow 抓的是窗口自身内容（含被遮挡部分）**，但鼠标事件发给屏幕最顶层窗口 → 只要动鼠标，就必须先确认像素归属。
13. 已实测：前台窗口是 A 时，`pwcap` 抓被挡住的窗口 B 拿到的是 B 的真实画面（2026-11-11 验证，零焦点变化）。**所以"看一眼"这件事根本不需要抢前台。**

## 标准工作流

1. `winlist.py` 找目标窗口的 hwnd（按标题子串，注意 4 和 8）。
2. `pwcap.py <hwnd> shot.png` 取样，`read_image` 看内容 —— **这一步已经能看到界面，不需要动前台**。
3. 能通过改文件/读文件达成目的，就到此为止（T0）。
4. 必须点击/发键时：先 `useridle.py` 判一次。
   - `USER_IDLE` → 直接进 T3 干活（激活→点击→发键），不必逐次申请；每次点击前做命中判定。
   - `USER_ACTIVE` → **先停**，等它变 idle，或一句话问用户「现在可以动一下界面吗」。
5. 每次自动化之后用 `pwcap.py` 复判结果；**不要用全屏 ImageGrab 判"有没有变化"**，它会给出假的"没变"。
6. 干完把界面恢复原样（最小化过的恢复、动过的窗口还回原位）。

## Adobe XD 专项（本机已装 XD 58.0.12.9，UWP 版）

- 启动：`Start-Process 'explorer.exe' -ArgumentList 'shell:AppsFolder\Adobe.XD_pc75e8sa7ep4e!App'`（约 30s 出 Home）
- 打开文档的可靠路径（**需要动前台，属 T3**）：XD 里先有一个打开的文档 → `^o` → 对话框（标题「打开」、类 `#32770`）→ 点「文件名(N)」输入框 → `^a` → 粘贴完整路径 → `{ENTER}`。完整实现见 `C:\Users\Admin\.dsh\tools\xd\xd-open.ps1`（重启 XD + 打开 + 等文档窗口，含 DPI 感知与激活重试）。
- `.xd` 的容器格式、生成与改交互**不要在本 skill 里现学**：加载 `xd-authoring` skill（格式规范 `C:\Users\Admin\.dsh\tools\xd\SCHEMA.md`、生成器 `xdgen.py`、加交互 `xdpatch.py`、校验器两个）。一句话：`.xd` 是 zip，交互在 `interactions/interactions.json`，画板注册表在 `resources/graphics/graphicContent.agc` 的 `artboards`（键是 `artboard.ref`，**不是**目录名里的 guid）。
- 预览窗是 `ApplicationFrameWindow`（标题也是 "Adobe XD"，按标题取会抓错，必须用 hwnd）；被最大化的文档窗压住时点击全落到文档窗 → 要么最小化文档窗，要么**干脆别点，改用 PrintWindow 取证**。
- 画板标定（预览窗）：窗口 1px 黑边 + 40px 浅灰标题栏，画板从 `y=41` 开始；`x0=9, y0=41, k≈1.2489`（375×667 逻辑 px → 468×833 物理 px）。
- 真实存在的 `.xd` 样例可以直接改：`xdpatch.py --spec` 只替换 `interactions/interactions.json` 就能给课件加交互，其余 38 个成员字节不动（详见 `xd-authoring` skill）。

## 反模式（踩过，别再犯）

- **为了截图**去激活窗口、置顶、最大化 → 没必要：`pwcap.py` 被遮挡也能抓到。
- 用户 `USER_ACTIVE` 时还硬去激活窗口/发键 → 这就是用户说的「抢」。
- 置顶（`HWND_TOPMOST`）盖住用户的窗口 → XAML 应用还清不干净，一盖就赖着。
- 用 `SendKeys` 打通一切 → 用户在用电脑时会打到他的窗口里。
- 拆成多次 PowerShell 调用做「激活→找对话框→填路径」→ 窗口状态在中间就变了。
- 拿 `ImageGrab` 判断点击是否生效 → 得到假阴性。
- 在没 BOM 的 .ps1 里写中文窗口名做匹配 → 永远匹配不上。
- 「读不到权限」就写成「不存在」→ 判不了就说判不了。
