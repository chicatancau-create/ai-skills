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
