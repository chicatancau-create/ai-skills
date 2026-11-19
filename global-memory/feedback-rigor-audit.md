---
name: feedback-rigor-audit
description: "不要出现任何形式的纰漏" — audit your own prior output, verify counts by script against disk, repair inbound links after renames, report honest metrics, and ask before irreversible restructuring
metadata:
  type: feedback
---

The user's standing quality bar is zero sloppiness, including sloppiness I introduced in earlier turns of the same session. What they rewarded:

- **Self-audit previous claims.** Several of my own statements turned out wrong (Oracle 23ai, Docker 28.x, MySQL 8.0 as mainstream, a fabricated HarmonyOS "网络" topic inferred from episode titles, "流水线已停止" while the ASR process still ran). Re-check my own recent assertions against official sources / disk before treating them as settled.
- **Measure, don't estimate.** Counts (volumes, source cards, transcript files, banner coverage) were always resolved by a script over the filesystem, and stale prose numbers were then fixed everywhere they appeared — including root README, 总纲, 长期计划, and the registry READMEs. Durable lesson: prefer "counting from tool output" over hand-written totals.
- **After any rename, grep inbound links.** Renaming a section heading broke an anchor link from a compat entry; `check_vault.py` caught it. Same for section-number references written in prose in other files.
- **Report honest deltas.** A "精简" that cut 16% of bytes but only 2% of lines was reported that way rather than as a big win; I also had to correct a line-count figure I had written into a history file before measuring.
- **Ask before destructive/ambiguous restructuring.** When "这个总文件" was ambiguous and the edit meant deleting sections, using AskUserQuestion to pick target + structural template was accepted without pushback. The vault is not under Git, and backups (copied to `outputs/备份/` with a non-`.md` extension so validators skip them) are the only rollback.
- **Watch self-inflicted bulk edits.** A regex "escape the pipes" pass double-escaped 22 already-escaped lines. Any scripted bulk transform needs a post-check, not just a success count.
- **Grade evidence by depth, not just presence.** A subagent produced 74/74 review rows with a "recommend `reviewed`" column, and 33 looked approvable — measuring the notes showed only 5 carried per-考点 content-coverage evidence while 28 proved only that the file and heading exist on disk. Before handing any batch recommendation over, classify the evidence (existence vs coverage) and say so; "not found" is itself a valid evidence item that should downgrade the recommendation, not be smoothed over.
- **Hunt stale numbers in my own prose.** Two engineering docs carried claims that no longer matched reality: a checklist header said the cross-origin restore was "verified" when the execution record for the same milestone said browser proof was still missing, and a record quoted "58 files / 748 tests" measured while other agents' unfinished files were in the tree. Correct the claim, and mark the old figure as voided rather than silently rewriting it.
- **Prove my own bug reports before trusting them.** A "snapshots directory vanished" scare turned out to be my own `head -4` truncating the listing. Re-check the measurement command before writing an incident up.
- **A changed error message is not a fixed error.** After stripping a UTF-8 BOM that had been breaking an app's config, the same log line kept firing with a *different* cause (Go wanted `map[string]string`, the file had a plain string). I had reported it as resolved. Rule: re-grep the error to **zero occurrences** after the restart, and say which class of error disappeared vs which merely changed text.
- **Never quote a single benchmark number as a baseline.** I wrote "42 tok/s" into a handover doc from one hot-state run; the same config later measured 4.3 / 15 / 29 tok/s because the laptop's GPU power budget swings (nvidia-smi `clocks_throttle_reasons` = SW Power Cap, 50→114W). Fixed by running an **A/B under identical conditions** (original vs modified file: 15.4 @73W vs 29.4 @106W) which also proved my rewrite hadn't slowed anything. Record the mechanism, not one figure.
- **Disclosing my own regressions gets rewarded, not penalized.** In one session I volunteered: a backup routine whose filenames collided so three config backups overwrote each other; a 7th reference location missed during a rename (an app's router config still had the old model name, silently breaking that endpoint); and the bad baseline number above. The user's response was to ask me to go fix the underlying error ("既然你已经发现了它是错误的，那你能把它修复一下吗"). So: list the self-found mistakes plainly at the end of a delivery.
- **Distrust GUI gauges; read the counter behind them.** Two app panels told the user "GPU 0% / VRAM 0%" while the model was demonstrably in显存 — the panel's own data source returned nothing (`--`). Verified instead via `Get-Counter '\GPU Process Memory(*)\Local Usage'`, per-process command lines, and nvidia-smi. When a user screenshots a dashboard that contradicts me, check whether the dashboard is broken before concluding I was wrong. See [[reference-computer-use-blocked]].
- **A measuring tool needs self-checks, not just green output.** While producing the §5.4 visual evidence (2026-09-21) I shipped four rounds of "0 errors, all cells measured" that were wrong in ways the numbers themselves could not reveal: a CLS baseline sampled after the event it was meant to isolate (so every cell read 0), layout-shift entries summed without excluding `hadRecentInput` (so a login page's real CLS of 0 reported as 0.51), a contrast parser that dropped the alpha channel (41 fake failures), and screenshots taken after the harness's own clicks had navigated away — three "login" PNGs were byte-identical to the "path" PNGs, five "profile" PNGs identical to "path". Fixes that the user endorsed as the standard: hash the artifacts and flag duplicates, parse-check injected code before running it, and have the in-page probe verify five known colour values every time so a broken parser fails the cell instead of emitting 1.0 everywhere. **Also: a partial re-run wiped the full matrix's screenshots while leaving its report intact — never let a debug run destroy a completed run's evidence.** See [[project-m6-visual-evidence]].
- **Geometry and computed style are not behaviour — prove interaction targets by clicking them.** Two separate cases on 2026-09-22: (a) my overflow probe blamed decorative spans whose rects exceeded the viewport, but their ancestor had `overflow:hidden`, so they contributed nothing to `scrollWidth` — the real culprit was a `::before { inset: -10% -6% }` found only by hiding subtrees and watching the number drop; (b) a subagent "proved" a 44px hit area by clicking 8px outside a checkbox and seeing it toggle — but that point was inside the wrapping `<label>`, and `elementFromPoint` at the genuinely-pseudo-only point returned `MAIN.content-wrap`, so the pseudo did nothing: **`::before` never generates a hit box for replaced form controls** (only after `appearance: none`). Rule now baked into `tools/visual/probes.mjs`: never credit a pseudo-element box for INPUT/SELECT/TEXTAREA with `appearance !== none`, and verify any claimed hit area with `elementFromPoint` + a trusted click, in both directions. Related: `getBoundingClientRect()` is viewport-relative, so clicking it back without scrolling first = clicking air (this bit me a second time; when `scrollIntoView` is unreliable under `Emulation.setDeviceMetricsOverride`, raise the viewport instead).
- **Re-run a subagent's verification, don't read it.** The same agent's report was accurate on 12 of 13 items and wrong on the one where its control experiment was confounded. Treat "I verified X" as a hypothesis with a named command, then run that command.
- **Fixing an overstatement is where I introduce the next error.** Same day, while correcting M3's header claim "键盘走查已证" (genuinely overstated), I wrote the inverse — "Tab 遍历与焦点环可见至今未测" — which was *also* false: M3 §5 and M4's keyboard table both recorded a real Tab press with `:focus-visible` outline 1.6px + 5px glow. A doc-audit subagent caught it minutes later. Rule: before replacing a wrong claim, look up what the replacement asserts and find its own evidence; state the precise scope ("单点已证、整页未测") rather than a stronger inverse.
- **Every "0 errors" must name whose errors it counted.** My "20 格 0 报错" only meant the取证 script threw nothing — page `console.error`, uncaught exceptions and resource 4xx/5xx had never been captured (`grep consoleAPICalled` → 0 hits). After wiring capture, the same run reported 6 resource 4xx and 0 JS exceptions. So: declare the observation surface of any clean-bill claim, and when the user asks 查一下有哪些错误, expect a separate category for errors in **my own tooling and prose**, not just the product's.
- **`git ls-files` 的八进制转义路径会把存在性判断全判错.** I reported「297 个跟踪文件里 295 个从磁盘消失」并据此报警数据丢失 —— 真实数字是 9。原因是把 git 默认的带引号转义输出（`"\345\272\224\270端/..."`）直接喂给 `os.path.exists()`。规则：**拿 git 的路径输出与磁盘比对，一律 `-z`（或 `core.quotepath=off`）**；报警「文件消失」前先用一种以上方法复核。
- **搜丢失文件要搜归档内部，别只看文件名.** 我断言 `pipe-transport.mjs`「真的丢了」，因为只 glob 了磁盘；它其实在 `备份区/.../electron-runtime-source.zip` 里。宣布不可恢复之前，先列 zip 的 namelist。
- **grep 命中数不是性能证据.** 我用「667 处文件 IO」「15 个文件 include windows.h」推断「秒级界面假死」，被项目里另一会话的工程文档明确拒绝沿用（「不沿用未核实统计」），它是对的 —— 后者还指出那 15 个 include 含 main 与测试，不是 15 个缺陷。计数 ≠ 延迟；要么实测，要么写「未证实」。
- **并发写入的树：快照必须带时间戳，断言前重测.** 同一会话内我的现状数字一小时内就过期两次（native 7,204 → 8,643 行；main.cpp 948 → 1,378；`pnpm test` 21 → 4 用例；「GDI 手绘」实为系统控件）。打印快照时刻，并在任何结论前重跑测量。
- **先分清「故障」与「有意的路线切换」再报警.** 「UI 全白」我第一反应是坏了/被删，实际是另一个会话把 Electron 壳换成原生程序并归档了旧源码。读方案文档确认意图，比急着定性为事故更有用。
- **An audit request is answered by re-running, not by reciting.** For "总结一下项目情况…是否严格按照工程文件在做" I re-executed every gate (typecheck / lint / test / coverage / build / content-check, the three vault python tools, the DATA-18 aggregate, launcher status/doctor/verify-entry) instead of quoting prior records, then listed the milestone criteria genuinely **not** met (M3 keyboard walkthrough partial; M6 CI never executed on GitHub — repo has no remote — and `install --frozen-lockfile` never run; M6 recovery covers file layer only; two pages never visually inspected; the evidence-writeback chain has never produced real data). Delegating a docs-vs-tool-output cross-check in parallel surfaced 8 real drift items, two of them in edits I had made minutes earlier — worth repeating after any large evidence-writing round.

- **「已通过/可启动/已交付」必须挂本轮自产的证据，否则写「未验证」.** 2026-10-05 用户把我这条自我要求正式采纳为项目规则（「加上这条规则」）：任何完成类表述要同时满足 ① 指向 `evidence/` 下的具体文件或可复现命令 ② 是**本轮自己跑出来的**（不引用旧轮次或推断） ③ 口径一致（同产物、同负载、同机器）。并明确三组不等式：「生成了部署目录」≠「可独立启动」、「编译链接通过」≠「功能可用」、「CTest 通过」≠「已验收」。写不了的结论就写「未测」，**不许换成含糊说法绕过**。
- **既有测试可能恰好把 bug 绕开，甚至把 bug 固化成期望.** 修「已成功写入却被改写成已取消」这个缺陷时，覆盖它的既有测试之所以是绿的，是因为它的 work 自己在取消时返回 failure —— 恰好不走那条路径；而另一条 `!requestClose()` 断言则把「关闭时拒绝」写成了期望。规则：修缺陷时先问「现有哪个用例会红」，没有就**补一个会红的**；若为了让新语义通过而改测试，必须显式声明改了哪条断言、为什么，别静默改。
- **改测试以匹配新行为 = 必须申报的事件**，不算「测试通过了」的加分项。
- **代理报出的严重缺陷要逐行自验再转述.** 同一轮里子代理给的三个缺陷，我逐行读到源码才敢写进结论；它对「关闭只取消队列不取消在飞任务」的定位（要另登记在飞令牌才拿得到）是我自己看代码才发现的修正。见 [[feedback-verify-subagent-file-claims]]。

- **用标题当 Edit 锚点时，别把标题本身吞掉.** 2026-11-07 在施工验证报告插入 7.28 时，`old_string` 用了下一节的标题 `### 7.15 ...`，替换后新文本没有把该标题写回，导致 7.15 整节失去标题。**同日插入 7.34 时又复发一次**，同样吞掉了 7.15。catalog 的链接检查仍然全绿（没有断链），只有回读章节顺序才发现。规则：插入新章节时以标题为锚，替换文本必须原样保留该标题；提交前 `grep -n '^### 7\.'` 检查章节号连续性，或直接读插入点前后 10 行。

- **`echo "$(cmd)"` 是退出码黑洞.** 2026-11-07 Java/MySQL 冒烟脚本里 `echo "task: $(curl -fsS …)"` 中的 curl 收到 400，
  `set -euo pipefail` 没有中止脚本：命令替换在 `echo` 的参数位置失败不会触发 `set -e`，摘要仍写出了 `JAVA-MYSQL PASS`。
  规则：要判生死的命令先 `out=$(cmd)` 再 `echo "$out"`；汇总 PASS 只能在所有分段成功且逐段检查后生成；
  看到空变量/空响应先怀疑被吞掉的退出码，而不是接口返回空。
- **总览表与明细行会漂移，验收前必须逐表对账.** 2026-11-07 批次 4 总览仍写“1/7、项目 02–05 未开始”，
  批次 5/7 写“未开始”，而明细行已有提交、测试与证据；独立对抗复核第一轮就抓到。规则：改批次状态时
  总览与明细同一提交改完，验收前用 grep 抽查“未开始/进行中”与详细行是否矛盾。
- **manifest 的 `commit` 是生成时 HEAD，不是“与代码同提交”的证明.** `manifest.mjs verify` 只校验证据文件
  SHA-256；project05/frameworks 的 manifest 曾指向另一个项目的提交，仍显示 `manifest OK`。规则：manifest
  在代码提交后生成；报告里只写“manifest 哈希校验通过”，不要把 commit 字段当成代码关联证据。
- **自动从文档抽样本/计数必须先设结束边界与长度断言.** 解析 JD-12 时只找下一个 `###`，把后续整章分析吞进
  单条 requirements，导致 SQL/Docker/K8s 频次虚高。规则：解析器遇到 `##` 也停止，并断言单条最大长度、
  总数与空值数，再渲染统计。

- **同一静态场景截两次，不是两份独立证据.** 2026-11-08 托盘取证：我对同一条未变化的任务栏截了
  `strip` 和 `strip2` 两次，各得 10 个强调色像素，脚本把两者相加凑到阈值并输出 `ok=true`。
  这是重复计数，不是复现。规则：独立证据必须来自**不同状态/不同来源**（例如「任务栏未展开」与
  「溢出面板已展开」），同一画面多次采样只能取一次；阈值不达标就报失败，再查是工具错还是产品错。
- **取证工具里的硬编码期望值也要先验来源.** 同一轮我把旧 tkinter 的强调色 `#34D399` 当成唯一真值，
  屏幕上另一个 `#00D76B` 的绿图标被误读成「我们的图标变淡」；正确的第一步是回源码/旧实现确认
  当前应是什么颜色、图标应在哪个区域，再判缺失。**修工具里的坐标系/期望值可以，放宽判据不行。**

- **全绿门禁之后，独立审查仍能抓出真缺陷.** 2026-11-08 cc-hud：数据/host 审查 8 条中 7 条成立
  （导出未按字段名脱敏、Herdsman 把 request_id 当会话、cc-haha 跨日成本摊销、范围外 sid、revision 回退、
  多 SELECT 无读快照、host 初始化竞态/托盘线程），前端审查 6 条全部成立（设置回包竞态、bootstrap 永久加载、
  卡片五态、场景桩、电源确认超时、E2E 吞断言）。规则：绿门禁只证明"已测的点"，收口前另起只读审查并逐条回源码核对。
- **探针失败先分清"没点到"与"点不动".** 合成 SendInput 点 WebView2 圆点未恢复窗口：`WindowFromPoint` 落在
  `Chrome_WidgetWin_1` 子窗，说明 `cursor_on_dot` 判据本身无效；`evaluate_js` 证 `window.pywebview.api` 已注入、
  托盘消息链路正常。结论写"合成点击未命中"，不写"圆点点击坏了"。

- **文档→证据要独立对账，绿门禁不覆盖报告正文.** 2026-11-08 cc-hud 让只读审计代理交叉核对交付索引/验证报告/README
  与 artifacts，6 处漂移全部成立：pytest 写 49 实为 60、`FINAL13-*.json` 指向一个没有 JSON 的目录、"托盘全项 true"
  而两个信息项是 false、"cchud/ 未改"实际改了 `sysw.py`、评分写 8/9 却并列两项失败、卡片检查写 18 实为 17。
  规则：收口前跑一次 docs-vs-evidence 审计；计数用 `--collect-only`，每个证据路径做存在性校验，
  评分口径必须与列出的失败项一致，"全项通过"要排除 informational。

- **证据文件改了就先提交，再生成 manifest.** 2026-11-08 给 K8s Deployment 补 `resources` 后直接生成 manifest，
  但忘记提交 YAML；manifest 记下工作区哈希，独立复核在现树跑 `verify` 立刻报 `HASH MISMATCH`。
  规则：evidence/源码/YAML 的修改先 commit，再 `manifest make`，最后再跑一次 `verify`；manifest 的 `commit`
  字段只是生成时 HEAD，不证明“同提交”。
- **多轮 VM/故障证据要标明哪一轮成功，别把命令统一记成 exit 0.** K8s 前几轮镜像拉取/网络失败、后续 run9/run10
  成功；manifest 若只写一条 `qemu …|0`，会被读成所有轮次都通过。规则：成功与失败分别保留，manifest 只列
  真正成功的那轮并注明轮次；README 明确“失败输出保留、不冒充通过”。

- **收口表会自己漂移：同一项同时出现在“已关闭”和“剩余”.** 2026-11-08 的审计表里 Testcontainers 同时被列为已关闭和剩余，
  E01 工具链剩余项还留着“—”。规则：每次新增关闭项后重读整张表，去重、删掉已完成项；不要只往“已关闭”里追加。
- **CI run id 是易腐数字.** 文档里连续几轮写着旧 run id；每次最终提交后重新取
  `gh run list --limit 1` 并全局替换，别让“最近全绿”指向旧提交。

- **移动工具/改路径后，门禁脚本自身会先过期.** 2026-11-08 把 `catalog_tool.py` 从 `_采集暂存/` 移到 `tools/` 后，
  `verify_all.mjs` 与 `verify_archive.sh` 里的硬编码旧路径立刻让 source-only 失败；重签 E02 manifest 才恢复 28/28。
  规则：移动/改名后立刻重跑所有门禁，先全局 grep 旧路径；证据文件变了要重新 `manifest make` 再 `verify`。
- **纯行尾差异不要当用户改动提交.** 同一轮 `04-资源与评估` 有 15 个文件整文件 diff，`git diff -w` 后只剩 1 行语义改动；
  其余是其他会话写出的 CRLF。规则：提交前先 `git diff -w --stat` / `--ignore-cr-at-eol`，纯行尾先 restore，别把 CRLF 写进历史。

- **验收要跑“门禁脚本本身”，不是只跑 `npm test`.** 2026-11-09 P03/P04 的 `npm test` 全绿，但 `scripts/run_project.sh` 仍失败：前者带 `--test-concurrency=1`，一键脚本里直接 `node --test tests/*.test.js` 少了并发度，多文件并行 TRUNCATE 同一 schema 互踩（死锁/登录 401）。另一次是重构删掉了 `enqueue` 导出，单测不引用它所以全绿，`alert_check.mjs` 作为调用方直接 SyntaxError。规则：代码或导出变了就重跑**完整 evidence runner**；runner 与 npm script 的测试参数必须同口径；evidence 脚本也是重构的调用方，要一起修。
- **工具扫描失败要写“尝试失败”，不能写成“已扫描/通过”.** 2026-11-09 E11：ZAP 2.17.0 能启动，但 `-quickurl` 跑 420s 超时、无报告。README 与 evidence 明确写“尝试失败、无报告”，验收项保持未闭合；只有手工 PoC 就只写手工 PoC。规则：任何扫描器的“通过”必须指向本轮生成的报告文件，否则按未执行处理。

- **「逐项核对」类断言必须同时断言核对到的条数，否则「零失败」可能只是「零执行」.** 2026-11-10 的刷机预检脚本里，
  「与固件自带 md5sum.xml 交叉核对」这一节因为正则没匹配上真实格式（`<digest hash="md5" name="x.img">md5</digest>`），
  9 个文件全部走 `[SKIP]` 分支，却仍然计入 PASS —— 汇总报出 **44/44 全绿**，实际那一节一项都没验。
  修法：给这类循环加**硬闸**（「至少核对到 8 条，否则 FAIL」），并把 SKIP 数单独打印。
  推广规则：**只要汇总里可能包含「跳过」，就必须把「执行了多少条」也写进汇总**；`[SKIP]` 不计入通过。

- **判「新增违规」前先对基线做差集，搬迁≠新造.** 2026-11-11 我把 QML 29 处写死颜色定性为「违反『新增写死颜色视为不合格』」，对比基线提交后发现：出现次数 95→29、23 个不同值**全部**来自拆分前的单文件、真新增 0 —— 是净改善+搬迁，只能按「既有待收口」处理。同轮网页端「新增 5 处颜色」里 4 处其实是在 tokens.css **定义新令牌**（正是规则要求的做法），真违规只有 1 处。规则：引用「新增/既有」类条款时，先 `git show <base>:<file>` 取值集合做差集，再定性。
- **`xargs wc -l | tail -1` 在文件多时只给最后一批的合计.** 2026-10-11 我用它报 DeepTutor 各目录行数，全部偏小（xargs 分批调用 wc，tail 只取末批）。正确做法：`find -exec cat {} + | wc -l` 或 Python 逐文件累加。任何「总量」数字先问测量命令会不会分批/截断。
- **grep 的形式变体会造成假阴/假阳，报缺陷前先换写法复核.** 同轮三次误报：`aspect-ratio` 0 命中（实际是 CSS-in-JS 的 `aspectRatio` 且有测试断言）；`^!工作区` 0 命中（实际白名单带前导 `/`）；把 `ShellDialog.qml`/`ShellPopup.qml` 组件**自身 id** 当成「无 open 调用的死组件」。另一次把「facade 引用数=0」当成模块半接线，实际是经服务层正确接线。规则：静态检索的 0 命中先换 camelCase/kebab、前导斜杠、别名、间接引用再下结论；「没被 X 引用」不等于「没被使用」。
- **文档里的 `文件:行号` 引用可以机器全量校验，是一类独立审查面.** 2026-11-11 对四份工程文档抽全部 `path.ext:NN[-MM]` 引用，按 basename 解析到磁盘并断言行数上限：41 条里 1 条失效（引到 1390 行而文件只有 1382 行，且起止两端都漂）。这类漂移绿门禁永远抓不到，收口前值得跑一次；修正时还要核对该引用**声称覆盖的内容**是否真在那个范围（任务含「日历+角标」时只给 dialog 范围会丢一半指针）。
- **检测器类修复的验收是「负对照」，不是「跑一遍没报警」.** 2026-11-12 给「QML 警告采集只覆盖创建期」写处置建议时定的 gate：临时在仅窄窗触发的分支故意引用一个未声明令牌 → 跑 ≤1200 宽真实窗口 → 断言该警告**被采集到** → 移除故意缺陷 → 断言 0。没有这一步，「warnings 0」证明不了采集器有效；那个未声明令牌正是靠「1440×900 截图照不到窄窗分支 + 创建期采集漏运行期警告」双重盲区藏住的。推广：任何新增的检测/采集/告警能力，验收必须含一次「故意让它报」的对照。
- **在飞树上跑出的绿门禁只是快照结论.** 2026-11-12 复跑 Qt 11/11 + Web 1296 全绿时，执行方 15 分钟前还在改三个 QML 文件、15 个文件未提交。报告必须写明「绿只证明此刻源码可编译可过测，不证明在飞改动已完成/已验收」，并附脏文件数与最近写入时间。
- **视觉类收口用「等值令牌」手法保证零副作用.** 处置写死颜色时定的做法：新令牌取值**等于**现字面量，再替换引用 ⇒ 纯改名、可证明零视觉差，同状态截图配对自然通过；「收口」与「改色」必须分成两个决策/两次提交。不要为过检查挑一个颜色相近的现有令牌。

**Why:** they asked twice for "仔细检查，不要出现任何形式的纰漏" and the vault's whole design is auditability.

**How to apply:** for content-quality work here, budget a verification pass (tools + spot reads) after the edits, list the concrete problems found and fixed, and never present a cleanup as complete without the check output.

Related: [[feedback-vault-engineering-rules]], [[project-vault-work-environment]]
