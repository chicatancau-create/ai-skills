---
name: visual-tool-add-section
description: 给 workspace/tools/visual 取证跑器新增或修改一个取证段(section)／注入探针模板(probe)时的一致性登记与验证流程。当要加改 §5.4 补测段、probes.mjs 里的模板，或遇到「--only=xxx 退出码 0 却零张图」「--selftest 疑似写盘盖图」「模板字符串反引号打断语法」「toolChangedDuringRun 报警」时使用。覆盖 SECTIONS、needMain、主实例派发行、TEMPLATES 四处登记与静默失败陷阱。不用于换构建后的重测与批次账（那是 codeweave-visual-rebuild-rerun）。
---

# 取证跑器加段／加探针的登记流程

## Overview

`workspace/tools/visual/` 是两个 runner（`visual-check.mjs` 满矩阵 + `visual-states.mjs` 补测段）共用一份模板模块（`probes.mjs`）的取证工具。加一个段或一个模板不是改一处，而是把同一个名字登记到 3—4 处；**漏登记不会报错，只会静默少跑一段并交出退出码 0**。本 Skill 就是那三道闸：登记清单、改完必跑、静默陷阱对照。

## 何时用 / 何时不用

用：新增取证段、新增或改注入页模板、把判据接进 `sectionJudge`、`--only` 跑出来 0 张图要查原因。

不用：只是跑批次读报告、换了构建要重测与记批次账 → 走 `codeweave-visual-rebuild-rerun`（它管「重跑哪一批」，本 Skill 管「改工具代码本身」）；也不用于改 `app/` 生产代码与 M6 文档。

## 硬约束（违反过的每一条都对应一次真实损失）

1. **批次跑期间绝不编辑 `tools/visual/`。** 收尾会比对工具指纹写 `report.toolChangedDuringRun`。**注意它只是标志位**：退出码只由 `report.errors.length` 决定，所以这条不会让进程失败，只往 stdout 打一句「不能当同一批用，要重跑」。看退出码的 agent 会漏掉——**必须读报告字段**。
2. **`--selftest` 只能是「看语法、不碰浏览器、不写盘」。** `visual-states.mjs` 曾根本没有 `--selftest` 分支，于是 `node visual-states.mjs --selftest` 被当成「不带参数的完整跑」：十段全跑、把共享 `shots/` 里上一批的 76 张同名 PNG 逐张盖掉，报告数字还在、图换成了另一版构建的。新增 runner 时先确认这个分支存在并且早于任何写盘返回。
3. **绝不清空 `shots/`。** 满矩阵与补测住同一个目录（`paths.mjs` 的 `OUT`，默认在仓库外的 `CodeWeave-recovery/tmp-m6-visual`，`VC_OUT` 可整体改指）。只 `mkdirSync(..., {recursive:true})`，不 `rmSync`。部分跑尤其不许清。
4. **模板字符串里不能出现反引号。** 模板是「字符串里的 JS」，一个反引号就提前终结外层字符串、直接打断 `probes.mjs` 的语法（在 `BOOTSTRAP` 里踩过）。注释里要引用代码就用单引号或中文引号。
5. **模板里的正则字面量双转义。** 源码里要写两个反斜杠，单反斜杠会被外层模板字符串吃掉。且 `--selftest` 只挡得住**整段解析失败**——正则字面量要等首次求值才编译，所以 `LAYOUT_PROBE` 内另有 `colorProbe` 五值自检每次探测当场验。改判据级代码时配一个当场自检，别只靠本地解析。
6. **端口 4274 / 9779 只此一对**（`VC_PORT`/`VC_CDP` 可换）。4173 是用户自己在跑的实例、9333 是 Qoder 内置浏览器调试端口，两个都不碰。启动前 `assertFree()`，收尾复核已释放。
7. **可能并行就用 `VC_DATA_TAG`。** 给浏览器 profile 与三个隔离数据目录加后缀；共用 profile／dataDir 时后起的那个会把前一个的目录删掉，两边量到的都不是自己种的东西。
8. **对 `runtime/data` 只读。** 发布包只拷出来当种子写进隔离目录，不写不删源。账户只用从没注册过的合成账户。

## 登记清单

### A. 新增注入探针模板（`probes.mjs`）

- [ ] `export const MY_PROBE = \`(() => { ... })()\`` —— 模板本体。
- [ ] 文件末尾 `Object.assign(TEMPLATES, { ..., MY_PROBE })` —— **漏了这一条，`--selftest` 的解析检查就覆盖不到它**，等于这段模板从没被人验过语法。登记表上方那句注释就是这条规矩。
- [ ] 用到它的 runner 里补 `import { MY_PROBE } from './probes.mjs'`。**`--selftest` 查不出漏 import**：它只遍历 `TEMPLATES`，漏 import 只在真跑时以 `undefined` 内插进字符串的形式暴露。
- [ ] 若是**按参数生成的工厂**（如 `panelProbe(sel)`）：登记表里放一份真生成出来的样本（`PANEL_PROBE_SAMPLE: panelProbe('[role=dialog]')`），否则工厂产物永远进不了解析检查。
- [ ] 共享片段（如 `HIT_BOX_SRC`）不必单独登记——插值发生在模块求值时，登记后的宿主字符串已含其全文，解析检查覆盖得到。前提是它真的被插进了某个已登记模板。
- [ ] 若模板只住在某个 runner 本地：加进该 runner `selfTest()` 里那个 `local` 对象（`visual-check.mjs` 就是这么管它私有的 `maskPageBehindDialog` / `unmaskPage` / `dialogState` 的）。两个 runner 共用 `TEMPLATES`，所以 `probes.mjs` 登记一次两边都覆盖。

### B. 新增取证段（`visual-states.mjs`）

四处必须同时改，少一处就是静默不跑：

- [ ] **① `const SECTIONS = [...]`** —— 段名进总名单。
- [ ] **② `const needMain = sections.some((s) => [...].includes(s))`** —— 这一段要用「种了现役发布包」的主实例，就把段名加进那个**独立字面量名单**（它与 ① 是两个列表，不会因为同名而自动同步）。
- [ ] **③ `if (sections.includes('mysec')) await runSection('mysec', sectionMySec, ctx)`** —— `if (needMain)` 块内的派发行。
- [ ] **④ `async function sectionMySec(ctx, report)`** —— 段本体，末尾调 `sectionJudge`。

段若不需要主实例（`empty` 要不种包的实例、`longtext` 要合成包实例、`writeback` 要工程外资料库副本），走的是它们各自另起的实例块，② ③ 换到对应块里改。新第五类实例就照那一块的形状加一段串行块。

**改完必查这一条**：只漏 ② 或 ③，收尾的 `sectionsSkipped` 闸门会抓到并报 error。**只漏 ①，什么都抓不到**——见陷阱表第 1 行。

## 改完必跑（顺序不能换，cwd = 工程根 `workspace/`）

```bash
# 0) 拿到证据目录（别写死盘符，从代码反推）
OUT=$(node -e "import('./tools/visual/paths.mjs').then(m=>console.log(m.OUT))")
BEFORE=$(ls "$OUT/shots" | wc -l)

# 1) 语法：改了哪个文件就 check 哪个
node --check tools/visual/probes.mjs
node --check tools/visual/visual-states.mjs

# 2) 两个 runner 的自检都要跑（共用 TEMPLATES，一处登记两边覆盖）
node tools/visual/visual-states.mjs --selftest
node tools/visual/visual-check.mjs --selftest

# 3) 自检必须零写盘：图数不得变
echo "shots: $BEFORE -> $(ls "$OUT/shots" | wc -l)"

# 4) 先看计划再看行为
node tools/visual/visual-states.mjs --plan
node tools/visual/visual-states.mjs --only=<新段名>
```

自检要看的输出：`解析失败 0 段`、`共 N 段` 的 N 等于 `TEMPLATES` 条目数（比上一批多 1，就是你刚登记进去的那段）、以及「自检不启动浏览器、不注册账户、不写任何文件」这句。**图数变了就说明自检在写盘，这是 bug，先修它再往下。**

`--plan` 是验 ① 有没有漏的唯一手段：它打印的就是 `chosen()` 的结果。

真跑之后读报告四字段，别看退出码：

| 字段 | 含义 | 非预期值怎么办 |
|---|---|---|
| `sectionsSkipped` | 选了却没留产物的段 | 非空 → 回查 ②③ 登记 |
| `shotsOverwritten` | 这批盖掉的开工前同名图 | 非空且你没打算覆盖 → 上一批证据丢了，重跑并补记 |
| `toolChangedDuringRun` | 跑的过程中探针被改过 | true → 这批不能与上批并列，重跑 |
| `cleanup.portsReleased` | 收尾端口是否释放 | false → 有僵尸实例，先清再跑 |

## 判据写法（`sectionJudge`）

段尾用 `sectionJudge(name, checks)`，每条 check 是 `{ where, what, ok, value }`：

- `ok !== true` 即算失败——`undefined`／缺字段都是失败，别依赖「没写就是过」。
- 失败**先记数字再抛错**（错误信息自己写的是「数字已全部记进报告」），段抛错被 `runSection` 接住、`fatal` 挂在已有部分结果上，所以「跑到第几页坏了」留得下来。
- 判据只收方案里是**绝对值**的那几条（焦点可见、无横向溢出、命中区 ≥44、字号跟设置走）；标准行为与已判豁免的装饰档不算失败。
- 历史坑：`loading`/`views`/`tab` 曾**只记录不抛错**，`editorfont` 更把异常吞成 `verdict.pass=false` 后正常返回——于是「0 报错」不等于「判据通过」，回归安静地从表格里走过去。新段一律接 `sectionJudge`。

## 静默失败陷阱表

| 症状 | 真因 | 怎么发现 |
|---|---|---|
| `--only=<新段>` 退出码 0、零张图、报告干净 | **`SECTIONS` 漏登记**。`chosen()` 返回 `SECTIONS.filter(s => only.includes(s))`，名字不在总名单里就先落空；而 `sectionsSkipped` 闸门遍历的是 `sections`（已空），看不见 CLI 里那个名字 → 无人报错 | 看 `--plan` 的「将跑的补测段」列表里有没有它；`--plan` 里没有 = ① 漏了 |
| `--only=<已有段>` 退出码 0、零张图 | `needMain` 或派发行漏登记（②③），整段被跳过 | 报告 `sectionsSkipped` + error「选了却根本没跑的段」 |
| 自检跑完 `shots/` 换了一批图 | runner 缺 `--selftest` 分支，参数被当成完整跑 | 跑自检前后各数一次图数（上面第 0/3 步） |
| `probes.mjs` 一打开就语法错 | 模板字符串里写了反引号 | `node --check tools/visual/probes.mjs` |
| 本地自检全绿，真跑才 `Unexpected end of input` | 该模板没进 `TEMPLATES`，解析检查没覆盖到 | 比对 `共 N 段` 与登记表条目数 |
| 真跑才报 `undefined` 内插 | runner 的 `import` 漏了这个名字（自检查不出） | grep runner 的 import 行 |
| 整批对比度全报 1.0 | 颜色解析器坏了但不报错——Chrome 把实心色序列化回 `#rrggbb`，只认 `rgb()` 会把每个像素比算成 1 | 看 `LAYOUT_PROBE` 的 `colorProbe` 五值自检，非空即解析器坏 |
| 两 agent 同时跑，数字互相污染 | 共用 Edge profile／dataDir，后起的把前一个的目录删了 | 并行时给 `VC_DATA_TAG`，端口冲突用 `VC_PORT`/`VC_CDP` 让开 |

## 定位锚点（用 grep，别记行号）

行号会随编辑腐坏，按符号名定位：

```bash
grep -n "const SECTIONS\|needMain\|await runSection\|function sectionJudge\|sectionsSkipped" tools/visual/visual-states.mjs
grep -n "Object.assign(TEMPLATES\|export const" tools/visual/probes.mjs
grep -n "const local = {\|解析失败\|--selftest" tools/visual/visual-check.mjs tools/visual/visual-states.mjs
```

## 收尾

改动要与工程文件同口径：本工具的判据来自 §5.4 / §11.2 方案，`probes.mjs` 顶部那三条「写模板的规矩」与本 Skill 的硬约束同源。任一条改了判据，就要交给 `codeweave-visual-rebuild-rerun` 重跑矩阵并与旧批数字对一遍——数字口径不连续比拿不到数字更糟。
