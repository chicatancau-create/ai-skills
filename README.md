# D:\Skills — 本机 AI 智能体统一技能库

所有 Agent 共用这一份技能实体。**本目录是唯一真源**，各工具通过目录联接（Junction）接入。

> 本仓库同时是备份：GitHub + GitCode 双远端。恢复方法见文末。

## 一、两层结构（默认只开两个）

| 目录 | 角色 |
| --- | --- |
| `D:\Skills` | **全量库**，53 个技能实体，唯一真源 |
| `D:\Skills-active` | **默认窗口**，只放 `headroom` + `skill-router` 两条联接 |
| `D:\Skills-disabled` | 停用区，不参与自动发现，保留可恢复源文件 |

各 Agent 的技能根指向 **`D:\Skills-active`**，所以任何 Agent 启动时只加载两个技能：

1. **`skill-router`** — 判断本次任务需要哪些技能，然后**直接 read `D:\Skills\<目录>\SKILL.md`**。
2. **`headroom`** — 省 token（压缩送进 LLM 的工具输出），常驻代理 `127.0.0.1:8787`。

**为什么用「读文件」而不是「改目录」**：多数 Agent 在会话开始时快照技能列表，会话中改目录看不见；读文件任何 Agent 都即时生效，而且其他技能的 description 永不进上下文。

## 二、当前联接（实测）

| Agent 技能根 | 形态 | 指向 |
| --- | --- | --- |
| Claude Code | 整目录 Junction | `D:\Skills-active` |
| DSH / Agents 规范 | 整目录 Junction | `D:\Skills-active` |
| OpenCode | 整目录 Junction | `D:\Skills-active` |
| WorkBuddy 国内版 | 整目录 Junction | `D:\Skills-active` |
| WorkBuddy 国际版 | 真实目录，2 个条目 | 逐项联接 |
| OpenClaw | 真实目录，2 个条目 | 逐项联接 |
| Codex | 真实目录，3 个条目 | 逐项联接 |
| Qoder | 真实目录，2 个条目 | 逐项联接 |
| Qoder CN | 真实目录，2 个条目 | 逐项联接 |
| Herdsman | 真实目录，2 个条目 | 逐项联接 |
| DSH 私有 | 真实目录，2 个条目 | 逐项联接 |
| cc-switch | 真实目录，11 个条目 | 逐项联接 |

## 三、⚠️ 联接的毁灭点（已经踩三次）

**联接给了唯一真源，也给了唯一毁灭点。**

用资源管理器删除 / 批量搬迁工具「移动」任一 Agent 技能根里的联接时，**Windows shell 会跟随联接，把 `D:\Skills` 里的真源一起删掉**。

已发生：2026-11-15 02:04:06、02:22:56、02:23:43 三次，`headroom` 与 `skill-router` 全部文件被回收。

**纪律**：

- 停用技能 → 移到 `D:\Skills-disabled`，**不要删 `D:\Skills-active` 里的条目**。
- 批量搬迁 Agent 数据目录前 → 先摘掉技能根里的联接，或先把本库复制到搬迁范围外。
- 判据：**文件进了回收站 ⇒ 是 shell 删的，不是 Python `rmtree`**（后者不进回收站）。
- 兜底：`skill_shield.py` 每 20 秒自愈一次，但**刚写还没镜像的内容仍会丢**；真正的兜底是本仓库的 git 远端。

## 四、技能清单（53 个）

标 LOCK 的**不进 git 远端备份**（许可禁止再分发），仍在本地可用；依据见 `BACKUP_SCOPE.md`。

### 全栈开发流水线 fs-*（13 个，自建）

| 目录 | 用途 |
| --- | --- |
| `fs-backend` | 后端 API 设计与实现规范(阶段3)。编写 RESTful API、路由、中间件、认证授权、输入校验、错误处理、日志、分页排序过滤、文件上传时使用。优先遵循仓库既有框架和官方当前文档，API 文档优先采用 OpenAP |
| `fs-code-review` | 代码审查与质量门禁(阶段6后持续使用)。提交代码前自检、审查 PR、配置 lint/format/typecheck 门禁、重构、控制复杂度、规范 Git 提交时使用。目标: 代码像一个人写的, 可读可维护。 |
| `fs-database` | 数据库设计与数据层规范(阶段4)。设计表结构、字段类型、主键外键、索引、编写迁移、使用仓库兼容的 ORM/查询工具、处理事务与并发、防止 N+1 查询时使用。 |
| `fs-deploy` | 部署与运维(阶段8)。准备生产部署、编写 Dockerfile/docker-compose、管理生产环境变量、CI/CD 流水线、域名与 HTTPS、健康检查、备份与回滚、监控日志时使用。目标: 一键部署, 可回滚,  |
| `fs-docs` | 文档编写规范。编写 README、API 文档、架构说明与决策记录(ADR)、变更日志(CHANGELOG)、代码注释时使用。文档与代码同步维护, 是交付物的一部分。 |
| `fs-frontend` | 前端开发规范(阶段2)。在 webapp-building 完成结构、视觉、状态和交互设计后，编写仓库实际使用的 React/Next.js/TypeScript 或其他前端页面、组件、hooks、数据获取、表单、状态管 |
| `fs-frontend-ui` | UI/UX 与无障碍规范(阶段2配合 webapp-building 使用)。设计界面、配色与排版、响应式布局、组件可访问性(ARIA/键盘/焦点)、暗色模式、SEO 元数据时使用。按当前 W3C/WCAG 官方资料和项 |
| `fs-fullstack` | 全栈项目开发总控流程。当用户发起全栈网站/应用的完整开发任务(新项目、重构、加功能模块)时第一个加载。本技能定义从需求到部署的闭环，并按阶段调度 Kimi 前端设计、规划、脚手架、前端、后端、数据库、测试、安全、代码审查 |
| `fs-performance` | 性能优化(阶段7)。优化页面加载速度、当前 Core Web Vitals、图片、字体、bundle 体积、后端响应时间、数据库查询、缓存策略时使用。先测量后优化, 用数据说话。 |
| `fs-plan` | 全栈项目需求分析与技术选型(阶段0)。开始新项目、梳理需求、选择技术栈、设计系统架构、拆分里程碑时使用。产出需求文档、技术选型决策、数据模型草案、里程碑计划, 是后续所有阶段的基础。 |
| `fs-scaffold` | 项目脚手架与工程化初始化(阶段1)。技术栈确定后初始化项目、配置 TypeScript、ESLint、Prettier、Git 规范、环境变量、目录结构、CI 基础流水线时使用。产出一个 lint/typecheck/t |
| `fs-security` | 安全审查与加固(阶段6)。审查认证授权漏洞、注入攻击、XSS/CSRF/SSRF、密钥管理、依赖漏洞、数据隐私合规时使用。按当前 OWASP 官方清单、框架安全公告和项目风险逐项审查。 |
| `fs-testing` | 测试规范(阶段5)。编写单元测试、组件测试、集成测试、E2E 测试、测试数据管理、覆盖率门禁时使用。优先采用仓库已有测试栈；新依赖按当前官方文档核对。测试随功能同步交付, 不做事后补测。 |

### 前端 / 设计 / 演示

| 目录 | 用途 |
| --- | --- |
| `darwin-skill` | Darwin Skill (达尔文.skill): autonomous skill optimizer inspired by Karpathy's autoresearch. Evaluates SKILL.md f |
| `figma-designer` | Design inside Figma the way this designer does: real variables, text styles, auto layout and components, on a  |
| `fullstack-dev` | Full-stack backend architecture and frontend-backend integration guide. TRIGGER when: building a full-stack ap |
| `impeccable` | Distinctive, production-grade frontend UI; avoids generic AI aesthetics. Use when building or styling web comp |
| `ios-application-dev` | iOS application development guide covering UIKit, SnapKit, and SwiftUI. Includes touch targets, safe areas, na |
| `landing-page-design` | Complete system for building high converting landing pages: intake questions, page structure, layout selection |
| `sickn33-frontend-slides` | Create stunning, animation-rich HTML presentations from scratch or by converting PowerPoint files. Use when th |
| `webapp-building` 🔒 | Use as the default Kimi design and implementation workflow for frontend work, including visual design, UI syst |

### 文档 / 表格 / 检索

| 目录 | 用途 |
| --- | --- |
| `brave-web-search` | USE FOR web search. Returns ranked results with snippets, URLs, thumbnails. Supports freshness filters, SafeSe |
| `docx` 🔒 | Use this skill whenever the user wants to create, read, edit, or manipulate Word documents (.docx files) or Wo |
| `find-skills` | Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for  |
| `github` | Interact with GitHub using the `gh` CLI. Use `gh issue`, `gh pr`, `gh run`, and `gh api` for issues, PRs, CI r |
| `pdf` 🔒 | Use this skill whenever the user wants to do anything with PDF files. This includes reading or extracting text |
| `pptx` 🔒 | Use this skill any time a .pptx or .potx file is involved in any way — as input, output, or both. This include |
| `tavily-search` | Search the web with LLM-optimized results via the Tavily CLI. Use this skill when the user wants to search the |
| `xlsx` 🔒 | Use this skill any time a spreadsheet file is the primary input or output. This means any task where the user  |

### 本机运维 / 自建工具

| 目录 | 用途 |
| --- | --- |
| `diagnose-windows-sandbox-acl` | Use on Windows for unexpected DSH sandbox access denials: workspace writes or listing fail, or an ordinarily r |
| `headroom` | Use when a Python or TypeScript app sends large tool outputs, logs, JSON, search results or long chat history  |
| `local-ai-handbook` | 本机（这台 Windows）《AI本地使用手册》（G:\AIrenwu\本地AI使用手册）的**默认前置知识库**。每次任务开始前先检索、任务结束前判断是否回写；任务里出现报错、超时、编码乱码、命令失败、排版异常、插件/技能问题、AI  |
| `obsidian-vault-validation` | Validate an Obsidian learning vault after structural or routing edits. Use when changing README links,分册 bound |
| `self-improving-agent` | Captures learnings, errors, and corrections to enable continuous improvement. Use when: (1) A command or opera |
| `skill-creator` | Guide for creating effective skills. This skill should be used when users want to create a new skill (or updat |
| `skill-router` | 本机技能总路由，默认必开。Use at the START of EVERY task on this machine, before deciding which skill or capability to use. |
| `vision-tool` | 本地视觉能力(看图/识别图片/分析截图)。当需要理解图片内容、识别图中文字、对比多张图片、分析截图时使用。连接本机牧羊人(Herdsman AI)部署的 Qwen3.5-9B 多模态模型, 纯标准库 Python 实现, |
| `windows-gui-control` | 这台 Windows 上「操控电脑 / 操作 GUI / 截图看界面 / 点按钮 / 发快捷键 / 打开某软件里的文件」的唯一标准做法。**允许在前台操作，但不许抢用户的前台**：动手前先用 `useridle.py`  |
| `xd-authoring` | 生成或修改 Adobe XD 文件（.xd）的本机唯一标准做法。用户让你「做一个 XD 文件 / 课件 .xd / 交互原型 / 给这个 xd 加点击跳转 / 改画板布局 / 复刻某个 xd 的交互」时，先加载本 ski |

### 需求 / 进度

| 目录 | 用途 |
| --- | --- |
| `barnhardt-enterprises-inc-checkpoint` | Save current progress to memory-keeper to prevent work loss. Use when the user says save progress / checkpoint |
| `barry-liu-888-requirement-translator` | 需求转译 - 将主观、模糊、口语化的用户需求翻译为结构化、精确的AI可执行规格。 This skill should be used when the user gives a vague, subjective, or |

### 钉钉

| 目录 | 用途 |
| --- | --- |
| `dws` | 管理钉钉产品能力(AI表格/AI搜问/日历/通讯录/群聊与机器人/待办/审批/考勤/日志/DING消息/开放平台文档/钉钉文档/钉钉云盘/AI听记/邮箱/在线电子表格/知识库等)。当用户需要操作表格数据、管理日程会议、模 |

### 逆向（仅授权目标）

| 目录 | 用途 |
| --- | --- |
| `reverse-trace` 🔒 | 【逆向工具·仅授权目标】Pure-web protocol reverse skill: turn hostile browser clients into browser-free Python collectors. |
| `reverse-wechat-miniapp` 🔒 | 【逆向工具·仅授权目标】【微信小程序任务优先】微信小程序 / WeChat Mini Program / WMPF 逆向调试。强触发关键词：微信小程序、PC微信小程序、WMPF、WeChatAppEx、AppServic |

### 原 QoderToolkit 并入（9 个）

2026-11-25 从 `D:\QoderToolkit` 字节级迁入（`web-kimi` 因许可排除，仍在原库）。第三方来源见各自 `PROVENANCE.md`。

| 目录 | 用途 |
| --- | --- |
| `codeweave-visual-rebuild-rerun` | CodeWeave 视觉重建复跑（60-cell 矩阵） |
| `headless-cdp-visual-acceptance` | 无头 CDP 视觉验收 |
| `install-github-skill-on-windows-qoder` | 在 Windows Qoder 上安装 GitHub 技能 |
| `localstorage-data-shape-seeding` | 按真实数据形状给 localStorage 播种 |
| `ppt-master` | PPT 母版/批量生成与归属校验（MIT，约 89 MB，字节不可改） |
| `qoder-toolkit` | Qoder 工具箱总入口（本机硬规则 + 路由） |
| `verify-app-security-claims` | 核实应用的安全声明是否属实 |
| `visual-tool-add-section` | 给可视化工具加新板块 |
| `web-taste` | 网页审美/品味评审与改造（MIT） |

## 五、原第二库 QoderToolkit：已并入本库

`D:\QoderToolkit` → `D:\_整理\04-AI工具包\QoderToolkit`（总联接，隔离「另一个 AI 还在搬 D:\_整理」的风险）**不再是独立技能源**：其 9 个技能已于 2026-11-25 字节级迁入本库 `D:\Skills\<同名目录>`，索引、路由一律指向本库。

- **为什么迁**：两个库并存时，同一个技能名会在 `skill-router` 索引里撞车，且改一处忘另一处。
- **唯一保留在原库的**：`web-kimi`（上游 `QvvvvvvQ/skills_leaks` 泄露内容，无使用许可，不得再分发），仍在 `D:\QoderToolkit\web-kimi`，**不进本库、不进 git 远端**。
- **`ppt-master` 特别约定**：目录内任何文件字节不可改动（完整性闸门 `scripts\attribution_guard.py`），迁移是纯复制，闸门在新位置实测通过。
- 原库仍是独立 git 仓库（GitHub `chicatancau-create/qoder-toolkit` + GitCode `zhoumoyukuai/qoder-toolkit`），保留作历史备份。

## 六、规则

1. 新技能放 `D:\Skills\<name>\SKILL.md`，目录名小写字母数字连字符，**与 frontmatter `name` 同名**（已知例外见 `THIRD_PARTY.md`）。
2. `description` 必须说清**什么时候用**（触发词），长度 ≤1024 字符。
3. **运行时缓存 / 输出不得写入技能源目录**，用 `AI_SHARED_SKILLS_STATE_DIR`（本机 = `D:\AI-Tool-State`）。
4. 第三方技能必须留 `PROVENANCE.md`（来源 / commit / 许可）；许可未知的标注清楚。
5. 新增或改动后跑 `python D:\Skills\skill-router\router.py sync` 重建索引。
6. 不把框架 / 运行时 / 数据库 / 安全清单的版本写死；已有项目以仓库配置与锁文件为准。

## 七、日常运维

```powershell
$py = 'C:\Users\Admin\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe'
& $py D:\Skills\skill-router\ops.py status    # 代理 / 接线 / 窗口 / 12 个技能根
& $py D:\Skills\skill-router\ops.py savings   # headroom 真实省了多少
& $py D:\Skills\skill-router\ops.py guard     # 接线守护
& $py D:\Skills\skill-router\ops.py shield    # 自愈盾
& $py D:\Skills\skill-router\router.py match "这次任务描述"
& $py D:\Skills\skill-router\router.py doctor
```

## 八、从 git 恢复

```powershell
git clone https://github.com/chicatancau-create/ai-skills.git D:\Skills
# 国内：git clone https://gitcode.com/zhoumoyukuai/ai-skills.git D:\Skills
& $py D:\Skills\skill-router\wire_agents.py --apply   # 重建默认窗口与各 Agent 联接
& $py D:\Skills\skill-router\router.py sync
& $py D:\Skills\skill-router\ops.py wire --apply      # 接回 headroom 省 token 链路
```

**注意**：`headroom` 的常驻代理与模型缓存不在本仓库里（`D:\uv\tools\headroom-ai`、`D:\uv\data\huggingface\hub` 那 261 MB），恢复后需重跑 `seed_kompress.py` 与 `headroom install apply`，命令见 `headroom\SKILL.md`。
