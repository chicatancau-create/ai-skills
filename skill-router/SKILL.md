---
name: skill-router
description: 本机技能总路由，默认必开。Use at the START of EVERY task on this machine, before deciding which skill or capability to use. 这台笔记本上所有 Agent 默认只加载 skill-router 与 headroom 两个技能，其余技能一律不加载。本技能负责判定「这次任务到底需要哪一个/哪几个技能」，然后按需直接读取对应的 SKILL.md。任何任务——写代码、做文档、表格、PPT、PDF、网页、逆向、钉钉、看图、操控 GUI、查本机踩坑、省 token——都先走这里。Do not load other skills by name; route through this skill first.
---

# 技能总路由（skill-router）

## 这台机器的规矩

**默认只开两个技能：`skill-router`（本技能）+ `headroom`（省 token）。其余全部关闭。**

原因：本机装了 50 个技能，全量加载会让每次会话都背上几万 token 的技能说明书，
模型负担大、还容易选错。所以改成「一个总路由 + 按需取用」。

**因此：你在技能列表里看不到别的技能，这是正常的，不是坏了。**
不要去猜它们的名字然后当工具调用——它们没有被注册成工具。
它们只是磁盘上的说明书，**用文件读取工具打开就能用**。

## 三步协议（每次任务都走）

**第 1 步 · 判定。** 看下面的索引，判断这次任务需要哪一个或哪几个技能。
不需要就一个都不选，直接用通用能力做。**不要为了用而用。**

**第 2 步 · 取用。** 对选中的每个技能，用文件读取工具打开：

```
D:\Skills\<目录名>\SKILL.md
```

原 QoderToolkit 的 9 个技能已并入本库，同样在 `D:\Skills\<目录名>\SKILL.md`（`web-kimi` 因许可排除，仍在 `D:\QoderToolkit\web-kimi`）。
索引里给了准确路径的以索引为准（少数目录名与技能名不同）。

**第 3 步 · 执行。** 按读到的说明书做。需要它的子文件（scripts/、references/）
就继续读同一目录下的文件。**只读这次真正要用的，别顺手把整库读一遍。**

## 可选：让脚本帮你判

有 shell 的 Agent 可以直接问路由（纯标准库，任何 python 都行）：

```
python D:\Skills\skill-router\router.py match "把这次任务原话贴进来"
```

它按相关度打分，输出候选技能 + SKILL.md 绝对路径。低于 2 分的噪声已过滤。
其他子命令：`list`（紧凑索引）、`cat <name>`（直接打印说明书全文）、
`show <name>`（只给路径）、`status`（当前默认窗口）、`doctor`（体检）、
`sync`（库里加了新技能后重建索引）。

**没有 shell 也能用**——直接看下面的索引 + 读文件即可，脚本只是加速器。

## 运维总入口（headroom 省 token 链路）

链路是 **Agent → headroom:8787 → cc-switch:15721 → 上游**。headroom 压缩送进 LLM 的
工具输出/日志/JSON（发送省），cc-switch 负责供应商与模型路由。日常运维只用一个脚本：

```
python D:\Skills\skill-router\ops.py status    # 代理/接线/默认窗口/12个技能根，一眼看全
python D:\Skills\skill-router\ops.py verify    # 真实补全请求，两跳对比
python D:\Skills\skill-router\ops.py savings   # 真实省量账本 + Kompress 是否加载（唯一可信证据）
python D:\Skills\skill-router\ops.py guard     # 接线守护状态（--fix 立刻修）
python D:\Skills\skill-router\ops.py shield    # 技能库自愈盾（--snapshot 额外打 zip）
python D:\Skills\skill-router\ops.py restart   # 重启 headroom
python D:\Skills\skill-router\ops.py wire      # 重新接线（守护会自动做，一般不用手跑）
python D:\Skills\skill-router\ops.py unwire    # 回滚到 cc-switch 直连
python D:\Skills\skill-router\ops.py skills    # 重建索引 + doctor
python D:\Skills\skill-router\ops.py backup    # git 备份状态（backup now 立刻提交并推两个远端）
```

### 技能库备份：两个 git 远端，不做本地备份

| 库 | 本地 | GitHub | GitCode |
| --- | --- | --- | --- |
| 统一技能库 | `D:\Skills`（就地 `git init`，零复制） | `chicatancau-create/ai-skills`（private） | `zhoumoyukuai/ai-skills`（private） |
| Qoder 工具箱（已并入本库，仅留 `web-kimi`） | `D:\QoderToolkit` | `chicatancau-create/qoder-toolkit`（private） | `zhoumoyukuai/qoder-toolkit`（private） |

- **自动保持最新**：`wire_guard` 每轮顺带调 `git_backup.py`，**10 分钟去抖 + 只在真有改动时**提交推送，
  推完回读 `ls-remote` 核对 SHA。日志 `D:\AI-Tool-State\git-backup\backup.log`。
- **`.gitattributes` 设 `* -text`**：本库文件编码是混合的（有 BOM、有 CRLF、有 LF），
  备份必须字节一致，禁止 git 顺手规范化。**必须在第一次 `git add` 之前就位**——
  2026-11-15 实测踩过：首次 add 早于该文件，79 个文件被 CRLF→LF 入库，
  补属性后 `git rm -r --cached .` 并没真正清空索引，靠 `git add --renormalize .` 才修好。
- **备份的验收标准是「从远端克隆回来逐文件 sha256 一致」，不是「push 返回 0」。**
  复核脚本 `G:\AIrenwu\脚本库\06_建仓与双推\verify_restore.py`（4 个远端各浅克隆一次全量比对）。
- **7 个技能按许可排除在远端之外**（`.gitignore` 按目录排除，本地仍可用）：
  `docx`/`pdf`/`pptx`/`xlsx`（Anthropic 专有，明文禁止在 Services 外保留副本、禁止转移第三方）、
  `reverse-trace`/`reverse-wechat-miniapp`（无 LICENSE，PROVENANCE 限定仅本机自用）、
  `webapp-building`（泄露的 Kimi 技能，上游明示无任何使用许可）。原 QoderToolkit 的 `web-kimi` 同一泄露来源，**未并入本库**（仍在 `D:\QoderToolkit\web-kimi`）。
  **私有仓库不能解决这一条**——上传到托管平台本身就是「转移给第三方」。依据见 `BACKUP_SCOPE.md`。
- `git_backup.py` 提交前会**再查一遍暂存路径**，命中排除目录就拒绝提交并 reset，不靠 `.gitignore` 单点。
- 恢复：`git clone <远端> D:\Skills` → `wire_agents.py --apply` → `router.py sync` → `ops.py wire`。
  headroom 的常驻代理与 261MB 模型缓存不在仓库里，需另跑 `seed_kompress.py` 与 `headroom install apply`。

### 两个常驻守护（登录即起，20 秒一轮，不用管）

- **`wire_guard.py --watch`**：**cc-switch 每次 attach/detach 都会重写客户端 BASE_URL**，
  把 8787 改回 15721，headroom 从此被静默绕过（不报错、只是不再省 token）。
  守护自动接回。规则：**仅当 cc-switch 处于 proxy+attached 才动**；
  用户主动切 direct 一律不碰；写前必验 8787 `/health`=200，否则不接（免得把 Agent 打进黑洞）。
  日志 `D:\AI-Tool-State\wire-guard\guard.log`。
- **`skill_shield.py`**（被守护每轮调用）：库文件丢了从 **`D:\Skills-mirror`** 还原，
  窗口联接丢了重建。**从不删除、从不覆盖非空库文件**。日志同目录 `shield.log`。

### ⚠️ 绝不要用资源管理器删 `D:\Skills-active` 里的东西

那是**联接**。2026-11-15 02:04:06 实际发生过一次：有人删了窗口内容，
**Windows shell 跟随联接把 `D:\Skills\headroom` 与 `skill-router` 的真源一起回收了**，
12 个文件全没，全机 Agent 同时失去两个默认技能。
（判据：文件进了回收站 ⇒ shell 删除，不是 Python `rmtree`。）
已从回收站 `$I` 元数据取证并 100% 还原。**停用技能请移到 `D:\Skills-disabled`，不要删窗口。**
自愈盾能兜底，但**镜像只能还原它已有的版本**——刚写还没镜像的内容仍会丢。

**判据纪律**：`verify` 里如果**两跳（15721 直连 与 8787 经 headroom）表现一致地失败**，
那是上游账户/线路的问题，**不是 headroom 的问题**，不要去改 headroom 或回滚接线。
去看 `C:\Users\Admin\.cc-switch\logs\cc-switch.log`。
`/v1/models` 返回 200 不算数——余额不足只在真实补全请求上以 403 露出。
上游 `moyucccx.top` 有间歇性挂起，超时会**在两跳之间随机出现**，重试即可。

**判「headroom 到底有没有在省」只认 `ops.py savings`，不许用单发探针的 token 差值。**
三种「测出来是 0」但其实是正常的情况（都从源码核实过）：
1. 单发冷请求 → cache 模式没有上一轮前缀，整段历史算 frozen prefix（`frozen=N`）。
2. 工具名是 `read_file` 之类 → `HEADROOM_PROTECT_READS=1` 主动排除（`excluded_tool`），
   因为 Agent 要按原字节打补丁，绝不能有损压缩文件读取。
3. 密集大 JSON → `ratio_too_high`，`accuracy_guard=strict` 宁可不压。
反过来，**上游 prompt 缓存会伪造出「省了 99.8%」**（headroom 账本其实是
`tok_saved=0 cache_read=64000`）。要对比就用唯一 seed 打散缓存。

### 部署命令（幂等，改配置就重跑这一条）

必须带 `--providers manual` 且**不给 `--target`**，否则 headroom 会自己改 Agent 的
BASE_URL 从而绕过 cc-switch。`coding` profile 的 19 个变量来自
`headroom agent-savings --profile coding --format shell`，**不要漏**：cache 模式只压最新增量，
而增量就是 tool/user 观测，`HEADROOM_COMPRESS_USER_MESSAGES=1` 不开就没东西可压。

```
headroom install apply --preset persistent-task --runtime python --scope user \
  --providers manual --port 8787 --no-rate-limit --no-telemetry \
  --env HEADROOM_OFFLINE=1 \
  --env ANTHROPIC_TARGET_API_URL=http://127.0.0.1:15721 \
  --env OPENAI_TARGET_API_URL=http://127.0.0.1:15721/v1 \
  --env HEADROOM_TIKTOKEN_LOAD_TIMEOUT_SECONDS=2 \
  --env HF_HOME=D:\uv\data\huggingface \
  --env HEADROOM_MODE=cache --env HEADROOM_SAVINGS_PROFILE=coding \
  --env HEADROOM_SAVINGS_TARGET=0.50 --env HEADROOM_COMPRESS_USER_MESSAGES=1 \
  --env HEADROOM_COMPRESS_SYSTEM_MESSAGES=0 --env HEADROOM_PROTECT_RECENT=0 \
  --env HEADROOM_PROTECT_ANALYSIS_CONTEXT=1 --env HEADROOM_MIN_TOKENS=10 \
  --env HEADROOM_MAX_ITEMS=15 --env HEADROOM_SMART_CRUSHER_COMPACTION=1 \
  --env HEADROOM_FORCE_KOMPRESS=0 --env HEADROOM_ACCURACY_GUARD=strict \
  --env HEADROOM_TOOL_SEARCH=1 --env HEADROOM_DEDUPE=1 \
  --env HEADROOM_LOSSLESS_THEN_LOSSY=1 --env HEADROOM_PROTECT_READS=1 \
  --env HEADROOM_CODE_AWARE_ENABLED=1 --env HEADROOM_LOSSLESS=0 \
  --env HEADROOM_MIN_CHARS_FOR_BLOCK=25
```

输出里 `ERROR: Access is denied.` 是改计划任务被拒，紧跟的 `successfully created` 才是结果，
**不是失败**。开机自启靠启动文件夹的 `headroom-autostart.vbs`（`schtasks /create` 本机一律被拒）。

**ML 压缩器 Kompress 的本钱**：`D:\uv\data\huggingface\hub\` 里预置的 261MB ONNX
（`chopratejas/kompress-v2-base` @ `b1563631b35bfdcee37587ad530147497d820d4c`）+ ModernBERT 分词器。
`HEADROOM_OFFLINE=1` **只拦网络回退、放行缓存命中**，所以预置后离线也能用。
清掉缓存会让它**静默退回结构压缩**（不报错，只是省得少）。重建走 hf-mirror
（`huggingface.co` 本机超时 10060，`hf-mirror.com` 通）；报错里那句
`requires onnxruntime or torch` 是误导——onnxruntime 1.32.0 装得好好的，真因是离线闸。

## 硬规则

- **不要 pin。** `router.py pin` 会把技能常驻进默认窗口，破坏「只开两个」的设定。
  只有用户明确说「让某某技能一直开着」时才用。
- **不要改 `D:\Skills-active`。** 那是默认窗口，由运维脚本管。
- **不要往技能源目录写运行时产物。** 缓存/输出一律放
  `D:\AI-Tool-State`（环境变量 `AI_SHARED_SKILLS_STATE_DIR`）。
- **本机 `python3` 是坏存根，PATH 上的 `python` 指向 Doubao 沙箱运行时。**
  写脚本一律显式写解释器绝对路径。可用的：
  `C:\Users\Admin\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe`
- **报错/超时/乱码/命令失败先查 `local-ai-handbook`**，这台机器基本都踩过并记了。
- 逆向类技能（`spider-king`、`wechat-miniapp-reverse`）**只对已授权目标使用**。

## 技能索引（53 个）

格式：`技能名` — 用途 → 目录（目录与技能名不同时才标出）

### 必开（不用选，已经在）
- `skill-router` — 本技能，任务路由
- `headroom` — 省 token：压缩送进 LLM 的工具输出/日志/JSON（发送省，不是输出省）

### 文档 / 办公
- `docx` — Word .docx/.dotx 读写编辑
- `xlsx` — Excel/CSV/TSV 表格读写与公式
- `pptx` — PowerPoint .pptx/.potx 读写编辑
- `pdf` — PDF 读取/提取/合并/拆分/表单/OCR
- `ppt-master` — PPT 母版/批量生成与归属校验 → `D:\Skills\ppt-master`
- `frontend-slides` — HTML 演示文稿（可由 PPT 转换）→ `sickn33-frontend-slides`

### 全栈开发流水线（按阶段选，不要整套全开）
- `fs-fullstack` — 总控：新项目/重构/加模块时第一个读
- `fs-plan` — 阶段0 需求分析与技术选型
- `fs-scaffold` — 阶段1 脚手架与工程化初始化
- `fs-frontend` — 阶段2 前端页面/组件/hooks 实现
- `fs-frontend-ui` — 阶段2 UI/UX 与无障碍
- `fs-backend` — 阶段3 后端 API 设计与实现
- `fs-database` — 阶段4 数据库设计与数据层
- `fs-testing` — 阶段5 测试
- `fs-security` — 阶段6 安全审查与加固
- `fs-code-review` — 阶段6后 代码审查与质量门禁
- `fs-performance` — 阶段7 性能优化
- `fs-deploy` — 阶段8 部署与运维
- `fs-docs` — 文档规范（README/API/ADR/CHANGELOG）
- `fullstack-dev` — 全栈后端架构与前后端联调
- `ios-application-dev` — iOS（UIKit/SnapKit/SwiftUI/HIG）

### 前端设计
- `landing-page-design` — **动态网页落地页**：滚动揭示/逐词点亮/动效曲线/转化结构（MIT，elayadesign）
- `figma-designer` — Figma 设计稿/组件库/设计变量（**需 Figma MCP，本机未装，只能给建议**）
- `impeccable` — 高质量界面/海报/落地页，避免 AI 通用感（Apache-2.0）
- `web-taste` — 网页审美评审与改造 → `D:\Skills\web-taste`（MIT）
- `webapp-building` — Kimi 前端流程与 shadcn 脚手架参考 → **泄露内容，仅本机学习，禁止对外交付**

### 搜索 / 外部服务
- `web-search` — Brave 网页搜索 → `brave-web-search`
- `tavily-search` — Tavily LLM 优化搜索
- `github` — gh CLI 操作 issue/PR/CI/api
- `dws` — 钉钉全套（表格/日程/通讯录/审批/考勤/文档/云盘/邮箱/听记）

### 本机运维 / 环境
- `local-ai-handbook` — 《AI本地使用手册》检索入口（报错/乱码/超时/提权/路由先查）
- `windows-gui-control` — 操控 GUI（截图/点按钮/快捷键），**不抢用户前台**
- `xd-authoring` — 生成/修改 Adobe XD .xd 与交互
- `vision-tool` — 本地视觉：看图/识字/对比图/分析截图
- `obsidian-vault-validation` — Obsidian 学习库结构改动后校验
- `diagnose-windows-sandbox-acl` — DSH 沙箱「拒绝访问/读不到/写不了」时查并修 ACL

### 技能自身 / 流程
- `requirement-translator` — 模糊口语需求 → 结构化可执行规格 → `barry-liu-888-requirement-translator`
- `skill-creator` — 创建/更新技能的规范
- `darwin-skill` — 技能 8 维评分与自动优化
- `find-skills` — 发现/安装可复用技能
- `self-improving-agent` — 记录错误/纠正/经验
- `checkpoint` — 存进度进 memory-keeper 防丢 → `barnhardt-enterprises-inc-checkpoint`

### 逆向（仅授权目标）
- `spider-king` — 纯 Web 协议逆向 → 无浏览器 Python 采集器 → `reverse-trace`
- `wechat-miniapp-reverse` — 微信小程序/WMPF 逆向调试 → `reverse-wechat-miniapp`

### Qoder 取证方法论（已并入本库，都在 `D:\Skills\<名>`）
- `qoder-toolkit` — 工具箱总入口（含本机硬规则）
- `headless-cdp-visual-acceptance` — 无头 CDP 视觉验收
- `verify-app-security-claims` — 核实应用的安全声明
- `visual-tool-add-section` — 给可视化工具加板块
- `codeweave-visual-rebuild-rerun` — CodeWeave 视觉重建复跑（60-cell）
- `localstorage-data-shape-seeding` — 按真实数据形状给 localStorage 播种
- `install-github-skill-on-windows-qoder` — 在 Windows Qoder 上装 GitHub 技能

## 索引维护

库里加了新技能后跑一次 `router.py sync`，它会重建 `catalog.json` 与 `CATALOG.md`。
本文件里的索引是给人和模型看的精简版，`CATALOG.md` 是带完整路径的全量版。
两者不一致时以 `CATALOG.md` 为准。
