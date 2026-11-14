---
name: xd-authoring
description: 生成或修改 Adobe XD 文件（.xd）的本机唯一标准做法。用户让你「做一个 XD 文件 / 课件 .xd / 交互原型 / 给这个 xd 加点击跳转 / 改画板布局 / 复刻某个 xd 的交互」时，先加载本 skill，直接用这里的生成器与校验器，不要从零试错、不要手写 ZIP。内含 .xd 容器格式规范（SCHEMA.md）、从零生成的 xdgen.py、给任意已有 .xd 加交互的 xdpatch.py、四个结构校验器（validate / validate_proto / geom_check / inter_probe），以及真机打开与自动点测流程（xd-open.ps1 / tpl_check.py / xd_watch_run.py，均受「不抢用户前台」约束）。
---

# 本机生成 / 修改 .xd 文件：唯一标准做法

## 这套东西是什么（先认清 .xd 的真相）

`.xd` **不是二进制格式，是一个 ZIP 包**。本项目已把它完整逆向量化，结论在
`C:\Users\Admin\.dsh\tools\xd\SCHEMA.md`（675 行，每条都带真实样本证据，5 个样本
8.8MB/2.9MB/88KB/1.7MB/740KB 全量比对过）。

因此：**生成 .xd = 写对 ZIP 里的 JSON；绝不要试图用 GUI 一个像素一个像素画。**
XD 软件只在最后「验收入眼」这一步才需要打开。

## 工具清单（全部在 `C:\Users\Admin\.dsh\tools\xd\`）

| 文件 | 干什么 | 关键用法 |
|---|---|---|
| `xdgen.py` | **从零生成** .xd（含分组、交互、预览图） | `python xdgen.py 设计.json -o out.xd` |
| `xdpatch.py` | 给**任意已有** .xd 加/改交互（其余成员字节不动） | `python xdpatch.py --index a.xd` 看结构；`--spec s.json -o b.xd` 写交互 |
| `validate.py` | 包结构校验（对照真实样本） | `python validate.py a.xd --compare "某样本.xd"` |
| `validate_proto.py` | 交互校验（key 是否命中真实节点/画板） | `python validate_proto.py a.xd` |
| `geom_check.py` | **几何独立审计**：按真实文件规则逐节点累加父链，检查顶层/组内坐标写法与画板范围 | `python geom_check.py a.xd [--verbose]` |
| `inter_probe.py` | **交互可用性探针**：按「手点会怎样」验命中框几何、同板两个 tap 目标是否重叠、从 home 出发能否走到每个画板、`time` 是否有正 delay、symbol 实例内是否被挂了交互 | `python inter_probe.py a.xd [--json]`（有 FAIL 退出 1） |
| `probe_selftest.py` | 探针自测（6 个故意坏/好的样本，防探针被改坏后悄悄全绿） | `python probe_selftest.py` → 期望 `6 cases, 0 unexpected` |
| `tpl_check.py` | 通用原型点测器（任意文档 + 一份步骤 JSON），在预览窗里按画板局部坐标点并截图 | `python tpl_check.py <标题片段> steps.json` |
| `wait_and_check.py` | **等用户空闲再整套跑**（文档没开就先用 `xd-open.ps1` 打开，再跑 `tpl_check.py`）；等不到就 `exit 3` 不动界面 | `python wait_and_check.py <doc.xd> <标题片段> steps.json --streak 2 --max-min 60` |
| `xd_watch_run.py` | 同上但多一层：连续 N 次 IDLE 才动作，日志落 `%TEMP%\xd_watch.log`（更啰嗦，日常用 `wait_and_check.py` 就够） | `python xd_watch_run.py <doc.xd> <标题片段> steps.json` |
| `specs\课件模板点测.json` | `tpl_check.py` 用的步骤样例（6 步：跳转/返回/tab/time 自动跳） | 照抄改 `ax/ay` |
| `SCHEMA.md` | 格式规范（写生成器/排错时查这里） | 直接读 |
| `examples\课件模板.json` | 3 画板课件设计描述样例（顶栏+卡片+底栏+6 条交互） | 复制改内容 |
| `specs\交互式原型.json` | 11 条交互的 spec 样例（真实交付物同款） | 复制改目标 |
| `xd-open.ps1` | 重启 XD 并打开指定 .xd（文件对话框自动化） | `-Path "E:\x.xd"` |
| `xd-accept.py` | 在 XD 预览窗里按坐标点测交互并截图 | 见文末「真机验证」 |

Python 用：`C:\Users\Admin\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe`
跑前设 `$env:PYTHONIOENCODING='utf-8'`（否则中文被吞成 `??`）。

## 两条路线，先选对

**A. 用户给了底稿（老师发的初始文件 .xd）→ 用 xdpatch.py 加交互。**
这是最稳的路线：底稿的美术、符号、重复网格都是真的，只把 `interactions/interactions.json`
换掉，其余 38 个成员字节不动（已实测：39 成员顺序一致、mimetype 仍首条目 STORED、
zip 时间戳/压缩方式/属性全保留、`testzip()=None`）。
**前提**：热区必须是真实节点；symbol 实例（`meta.ux.symbolId`）不能给其内部子层挂交互。

**B. 没有底稿，要从零造 → 用 xdgen.py。**
写一份设计描述 JSON（见下），生成 3 画板课件只要 26KB JSON。
限制：只支持 `rect / ellipse / text / image / group`，**不造 symbol、不支持渐变/复合路径**；
输出不可字节复现（每次新 guid），不要求复现就不用管。

## 设计描述 JSON（xdgen.py）

```json
{
  "name": "课件名",
  "home": "首页",
  "artboards": [
    {"name": "首页", "width": 375, "height": 667, "x": 0, "y": 0, "background": "#FFFFFF",
     "elements": [
       {"type": "group", "name": "底栏", "x": 0, "y": 618, "children": [
          {"type": "group", "name": "tab1", "x": 31, "y": 8, "children": [
             {"type": "rect", "name": "icon", "x": 0, "y": 0, "w": 24, "h": 24, "fill": "#1B6EF3", "radius": 6},
             {"type": "text", "name": "label", "x": -8, "y": 30, "text": "首页", "size": 11, "color": "#333333", "w": 40, "h": 16, "align": "center"}
          ]}
       ]}
     ]}
  ],
  "interactions": [
    {"board": "首页", "target": "tab3", "to": "列表"},
    {"board": "列表", "target": "顶栏", "action": "previous"},
    {"board": "首页", "target": "@artboard", "trigger": "time", "delay": 5, "to": "列表"}
  ]
}
```

要点：
- 元素类型：`rect`（`w/h/radius/fill/stroke`）、`ellipse`（或 `circle:true`）、
  `text`（`text/size/color/font/letterSpacing/lineHeight/w/h/align`，w+h 都有 = 自动换行区）、
  `image`（`src` 本地路径，会被 Pillow 重编码成 PNG 内嵌）、`group`（`children` 必填非空，可嵌套）。
- **坐标一律写「相对直属父容器」的**：画板顶层写画板内局部坐标（如 `x:16, y:104`），
  组内子元素写组内相对坐标（如 tab 里 `x:50` 就是组内 50，不要再加组的 x）。
  生成器负责把它转成 XD 的写法：**顶层 = 画板原点 + 局部（并写 `meta.ux.localTransform`）；
  组内后代 = 保持相对父组、且不写 `localTransform`**。别自己手改 AGC，也别把组内后代
  写成绝对坐标——XD 渲染时会再叠一次父组偏移，画面直接错位（2026-11-11 真机踩过）。
- `interactions[].target` 按**元素 name** 在该画板内递归查找，`"@artboard"` = 挂画板本身；
  找不到或重名会直接报错并列候选（**绝不猜**，所以命名要唯一）。
- 可覆盖 `transition`(dissolve/slide-left…)、`duration`、`easing`、`preserveScrollPosition`、`voiceLocale`；
  `tap` 缺省 `dissolve/0.3/ease-out`，`time` 触发缺省 `duration=1,easing=ease-in` 且必须给 `delay`（秒）。

## 交互 spec JSON（xdpatch.py）

```json
{"source": "E:\\XD\\交互式原型初始文件.xd",
 "output": "E:\\XD\\out\\demo.xd",
 "home": "首页",
 "links": [
   {"artboard": "首页", "node": "重复网格 1", "destination": "文章详情页"},
   {"artboard": "首页", "node": "75a5427a", "destination": "快捷键"},
   {"artboard": "素材列表", "node": "97437a9c", "action": "previous"}
 ]}
```

- `node` 三级解析：`@artboard` → 十六进制 id 前缀（≥8 位）→ name 精确；多命中报错列候选。
  **重名节点（如多个 `icon`）只能用 id 前缀**——先用 `--index` 看清楚。
- 只替换 `interactions/interactions.json`，其余成员字节不动；`--dry-run` 不落盘；
  失败 `FAIL: ...` + 退出码 2 且不留半成品。

## 交付前必须过的四道校验

```powershell
$py='C:\Users\Admin\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe'
$env:PYTHONIOENCODING='utf-8'
& $py "C:\Users\Admin\.dsh\tools\xd\validate.py"       "E:\out.xd" --compare "E:\XD\自动播放轮播图初始文件（单图）.xd"
& $py "C:\Users\Admin\.dsh\tools\xd\validate_proto.py" "E:\out.xd"
& $py "C:\Users\Admin\.dsh\tools\xd\geom_check.py"     "E:\out.xd"
& $py "C:\Users\Admin\.dsh\tools\xd\inter_probe.py"    "E:\out.xd"
```
四条都要 `RESULT: PASS`。`validate.py` 常出现 `NOTE`（如 `artboard.ref differs from id`、
`missing=['resources/<uid>']`）——**NOTE 不是失败**，是「与对照样本的差异」，读一眼确认合理即可。
`geom_check.py` 的 `warn` 多数无害（XD 允许画板外画内容、旧版文件整档不写 `localTransform`），
**`FAIL` 才是问题**：它专门抓「组内后代被写成绝对坐标」和「组内后代带了 `localTransform`」。
`inter_probe.py` 回答的是另一类问题——**点得到吗**：命中框是否落在画板外（>24pt 记 FAIL）、
同一画板两个 tap 目标是否重叠（XD 按绘制顺序，先画的可能永不触发 → warn）、每个画板能否从
home 走到（不可达 FAIL）、`time` 触发是否给了正 delay（FAIL）、symbol 实例内是否被挂了交互（FAIL）。
`inter_probe.py` 的 `warn` 多为「命中框重叠但后绘制者在上」，真机确认可点即可接受。
只有 `FAIL` 行才是问题。

## 真机验证（XD 里打开、点一遍）

**先加载 `windows-gui-control` skill。`xd-open.ps1` 与 `tpl_check.py` 自己会先跑 `useridle.py`：
`USER_ACTIVE` 时 `xd-open.ps1` 直接 `exit 9`、`tpl_check.py` 直接 `exit 3`，都不碰界面。**
（要强行跑加 `-Force`，但那是「抢前台」，只在用户明确同意时用。）

1. 打开：`powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\Admin\.dsh\tools\xd\xd-open.ps1" -Path "E:\out.xd"`
   （kill XD → 启动 → 点「打开」→ 文件对话框里粘路径 → 回车；约 60–90 秒，日志会打 `LOADED hwnd=... title=[...]`，
   文档窗信息写到 `%TEMP%\xd_docwin.json`）
2. 看画板：`pwcap.py <hwnd>` 抓窗口图（**PrintWindow**，能抓被遮挡的窗口；`ImageGrab` 抓 UWP 得到纯灰空图，别用）。
3. 点测交互：优先用通用点测器 `tpl_check.py`（写一份步骤 JSON，画板局部坐标）：
   `python "C:\Users\Admin\.dsh\tools\xd\tpl_check.py" "文档标题片段" steps.json`，
   它自己恢复被最小化的文档窗 → 开预览 → 标定 → 最小化文档窗 → 逐点点+截图到 `accept_tpl\`。
   步骤 JSON 里加 `"none": true, "wait": 7.5` 就是「只等待不点击」，用来测 `time` 触发的自动跳转。
   它每次点击前都会重跑 `useridle.py`，用户一动就 `USER-BUSY abort` 停下让路。
   也可以改 `xd-accept.py` 里写死的 `STEPS` 后跑 `XD_DOC_TITLE='文档标题' python xd-accept.py now`。
   **关键**：文档窗最大化时会压住预览窗且 `HWND_NOTOPMOST` 清不掉，必须把文档窗
   `ShowWindow(doc,6)` 最小化，否则所有点击都打进文档窗，表现为「点了没反应」。
   **标定必须按内容矩形算，不能靠「中心列第一个暗行」**：预览窗结构是 1px 黑外框 +
   9px 黑边 + 浅灰标题栏 (245,245,245) + 画板，画板横向铺满内容宽度
   （实测 486x883 窗 → left=9 right=476 cw=468 → `k=1.248`、`y0=42`）。
   旧启发式遇到「顶部是白色」的设计（课件模板顶栏 `#FFFFFF`）会给出
   `x0=49 y0=185 k=1.033`，每次点击都偏 ~30px 却仍显示「点到了」——`xd-accept.py`
   的 `calibrate()` 现已改成内容矩形优先、暗行法仅作 fallback，返回值带 `mode`
   （`content` / `darkrow`），看到 `mode='darkrow'` 就要怀疑标定。

## 硬约束与已知坑（每条都踩过）

| 约束 | 后果 |
|---|---|
| `mimetype` 必须是 ZIP **第一个**成员、`STORED` 不压缩、内容恰好 `application/vnd.adobe.sparkler.project+dcxucf` | XD 认不出文件/直接打不开 |
| `resources/graphics/graphicContent.agc` 的 `artboards` 必须写成**字典**（键=各画板 `ref`） | 写成 `{"href":…}` → 报 `Artboard with ref <guid> not found`，画布全白 |
| 组内后代的 `transform` 必须是**相对直属父组**的坐标，且**不写** `meta.ux.localTransform`；只有画板顶层节点写「画板原点+局部」并写 `localTransform` | 写成绝对坐标 → XD 再叠一次父组偏移，内容被推到 2 倍位置、底栏被挤出画板裁掉 |
| 定位文本（`frame.type=positioned`）的 `ty` 是**首行基线**，字形向上长（真实文件：10px 标签 `ty=40` 在 628.5 的组里 → 基线 668、字形 658..668） | 按「顶边」理解会把标签压到图标上，文字被图标盖住 |
| 底栏放「图标 + 文字」时：图标 20x20 @y=6，文字 10px 基线 @y=38（底栏高 49） | 图标 y=8..32 + 文字顶边 y=30 → 文字和图标重叠 |
| 每个节点 `id` 是全档唯一的 36 位小写 uuid | XD 丢节点或崩溃 |
| `text.paragraphs[].lines` 是「列表的列表」，`\n` 不属于任何段落 | 文字错位/丢行 |
| symbol 实例（`meta.ux.symbolId`）内部子层**不能**挂交互 | 只能给整个实例挂，否则点哪都跳同一条 |
| 本机 pwsh 是 5.1：`.ps1` 带中文必须 UTF-8 **带 BOM** + CRLF；命令里有 `$` 或反斜杠先落文件 | 中文模式串变乱码 → 「对话框永远不出现」这类假故障 |
| `ImageGrab`/全屏截图抓不到 XD 预览窗（UWP 合成） | 截图纯灰，误判成「点击无效」 |
| 预览窗标定：内容宽度/黑边/标题栏高度才是标定依据，别用「中心列第一个暗行」 | 顶部为白的设计会标出 `k=1.03`（真值 1.248），点击偏 ~30px 却报「成功」 |
| 自己点击也会重置 `GetLastInputInfo`（idle 归零） | 粗糙 busy gate 会把自己刚点的当成「用户回来了」，第一步就 abort；判据要加「前台是否我们的窗口 + 距上次点击 <8s」 |

## 现在的验证状态（诚实标注）

| 能力 | 状态 |
|---|---|
| 给已有 .xd 加交互，其余字节不动 | ✅ 实测：用 `specs\交互式原型.json` 复现了交付物 11 条交互，节点→目的地逐条一致，`validate_proto.py` 19 passed |
| 从零生成 3 画板课件（分组 + 6 条交互） | ✅ 结构四校验 PASS（`validate.py` 18/0/1 skipped、`validate_proto.py` 14 passed、`geom_check.py` 0 fails、`inter_probe.py` 0 fail／0 warn）、**真机打开渲染正确**（2026-11-11 23:17：3 画板、卡片 y=104/212/320、底栏完整在画板内、`←` 与三个 tab 图标/标签都正常）、**6 条交互全部在预览里点通 6/6**（见下一行） |
| 生成器的通用性（非内置模板） | ✅ 另起 414x736 两板设计、含换行段落/四角不同圆角/半透明椭圆/内嵌图片/两层嵌套组 → 四校验全 PASS |
| 从零生成文件的交互在预览里点通 | ✅ **2026-11-12 10:22 实跑 `tpl_check.py '示例-课件模板' specs\课件模板点测.json` → `done 6/6`**：card1→详情、详情顶栏→previous、tab3→列表、列表顶栏→previous、tab1→首页(自身不跳)、`time` 5s 自动→列表，六个签名/截图全部符合预期。证据 `E:\XD\证据\模板点测\`（6 张 PNG，`03` 与 `06` 字节相同、`02`/`04`/`05` 字节相同，状态稳定无残留）。 |
| 生成器复刻老师底稿的美术（符号/重复网格） | ❌ 不支持，需要底稿就直接走 xdpatch 路线，别重画 |

## 反模式

- ❌ 手写 ZIP / 自己拼 AGC（用 xdgen.py / xdpatch.py，格式坑太多）
- ❌ 为了看一眼界面去抢用户前台（先 `useridle.py`）
- ❌ 用 `ImageGrab` 判 XD 界面变化（抓不到，永远「没变化」）
- ❌ 校验只看「没报错」就交付（必须两条 `RESULT: PASS`；有 NOTE 要读懂）
- ❌ 把 `.xd` 当二进制改字节（它是 ZIP，改成员内容即可）
