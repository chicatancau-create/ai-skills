# 第三方技能来源与许可登记
生成时间：2026-11-15 02:41。本文由脚本从 **frontmatter 字段 / `.agents\.skill-lock.json` / 各技能自带的 `PROVENANCE.md` 与 `LICENSE`** 汇总，**没有推测来源**；查不到的就写「来源未记录」。

> 本仓库是**个人备份**，不是再分发。下面标「未声明」的技能，其授权状态未知，**不要公开转发或商用**。

## 一、本机自建（19 个）

| 目录 | 说明 |
| --- | --- |
| `fs-backend` | 后端 API 设计与实现规范(阶段3)。编写 RESTful API、路由、中间件、认证授权、输入校验、错误处理、日志、分页排序过滤、文件上 |
| `fs-code-review` | 代码审查与质量门禁(阶段6后持续使用)。提交代码前自检、审查 PR、配置 lint/format/typecheck 门禁、重构、控制复杂度 |
| `fs-database` | 数据库设计与数据层规范(阶段4)。设计表结构、字段类型、主键外键、索引、编写迁移、使用仓库兼容的 ORM/查询工具、处理事务与并发、防止 N |
| `fs-deploy` | 部署与运维(阶段8)。准备生产部署、编写 Dockerfile/docker-compose、管理生产环境变量、CI/CD 流水线、域名与  |
| `fs-docs` | 文档编写规范。编写 README、API 文档、架构说明与决策记录(ADR)、变更日志(CHANGELOG)、代码注释时使用。文档与代码同步 |
| `fs-frontend` | 前端开发规范(阶段2)。在 webapp-building 完成结构、视觉、状态和交互设计后，编写仓库实际使用的 React/Next.js |
| `fs-frontend-ui` | UI/UX 与无障碍规范(阶段2配合 webapp-building 使用)。设计界面、配色与排版、响应式布局、组件可访问性(ARIA/键盘 |
| `fs-fullstack` | 全栈项目开发总控流程。当用户发起全栈网站/应用的完整开发任务(新项目、重构、加功能模块)时第一个加载。本技能定义从需求到部署的闭环，并按阶段 |
| `fs-performance` | 性能优化(阶段7)。优化页面加载速度、当前 Core Web Vitals、图片、字体、bundle 体积、后端响应时间、数据库查询、缓存策 |
| `fs-plan` | 全栈项目需求分析与技术选型(阶段0)。开始新项目、梳理需求、选择技术栈、设计系统架构、拆分里程碑时使用。产出需求文档、技术选型决策、数据模型 |
| `fs-scaffold` | 项目脚手架与工程化初始化(阶段1)。技术栈确定后初始化项目、配置 TypeScript、ESLint、Prettier、Git 规范、环境变 |
| `fs-security` | 安全审查与加固(阶段6)。审查认证授权漏洞、注入攻击、XSS/CSRF/SSRF、密钥管理、依赖漏洞、数据隐私合规时使用。按当前 OWASP |
| `fs-testing` | 测试规范(阶段5)。编写单元测试、组件测试、集成测试、E2E 测试、测试数据管理、覆盖率门禁时使用。优先采用仓库已有测试栈；新依赖按当前官方 |
| `local-ai-handbook` | 本机（这台 Windows）《AI本地使用手册》（G:\AIrenwu\本地AI使用手册）的**默认前置知识库**。每次任务开始前先检索、任务结束前判断是否 |
| `obsidian-vault-validation` | Validate an Obsidian learning vault after structural or routing edits. |
| `skill-router` | 本机技能总路由，默认必开。Use at the START of EVERY task on this machine, before de |
| `vision-tool` | 本地视觉能力(看图/识别图片/分析截图)。当需要理解图片内容、识别图中文字、对比多张图片、分析截图时使用。连接本机牧羊人(Herdsman  |
| `windows-gui-control` | 这台 Windows 上「操控电脑 / 操作 GUI / 截图看界面 / 点按钮 / 发快捷键 / 打开某软件里的文件」的唯一标准做法。** |
| `xd-authoring` | 生成或修改 Adobe XD 文件（.xd）的本机唯一标准做法。用户让你「做一个 XD 文件 / 课件 .xd / 交互原型 / 给这个 x |

## 二、第三方引入（25 个）

| 目录 | frontmatter name | 来源 | 许可 | 自带 LICENSE |
| --- | --- | --- | --- | --- |
| `barnhardt-enterprises-inc-checkpoint` | `checkpoint` | skillstore slug `barnhardt-enterprises-inc-checkpoint`（2026-10-02 装入） | **未声明** | 无 |
| `barry-liu-888-requirement-translator` | `requirement-translator` | skillstore slug `barry-liu-888-requirement-translator`（2026-10-02 装入） | **未声明** | 无 |
| `brave-web-search` | `web-search` | OpenClaw 预装（slug=brave-web-search，2026-08-11，version=3e088af6…） | **未声明** | 无 |
| `darwin-skill` | `darwin-skill` | WorkBuddy 市场（skillId=skill_2053081519859650560，v1.0.0）；正文上游 URL `github.com/alchaincyf/darwin-skill` | **未声明** | 无 |
| `diagnose-windows-sandbox-acl` | `diagnose-windows-sandbox-acl` | 2026-11-15 01:38 由外部放入本库（DSH 侧技能）；**上游未记录** | **未声明** | 无 |
| `docx` | `docx` | Anthropic 官方文档技能；OpenClaw 预装（`.clawx-preinstalled.json` slug=docx，2026-08-11，version=b29e7cf6…） | **专有** `LICENSE.txt`：© 2025 Anthropic, PBC. All rights reserved.（禁止在 Services 外保留副本 / 转移第三方） | 有 |
| `dws` | `dws` | 钉钉官方 DingTalk Workspace CLI（随包 `NOTICE`：Copyright 2026 Alibaba Group） | Apache-2.0（随包 `LICENSE` + `NOTICE`） | 有 |
| `figma-designer` | `figma-designer` | `github.com/elayadesign/ai-design-skills` @ `456d9e0d3e2d`（2026-11-01），见 PROVENANCE.md | MIT（随包 `LICENSE`，Copyright (c) 2026 Elaya） | 有 |
| `find-skills` | `find-skills` | OpenClaw 预装（slug=find-skills，2026-08-11，version=e173b8c8…） | **未声明** | 无 |
| `fullstack-dev` | `fullstack-dev` | WorkBuddy 市场（skillId=skill_2053082011994116096，v1.0.0） | MIT（frontmatter `license`） | 无 |
| `github` | `github` | WorkBuddy 市场（skillId=skill_2053082027691548672，v1.0.0） | **未声明** | 无 |
| `headroom` | `headroom` | `github.com/headroomlabs-ai/headroom` 的 `skills/headroom/SKILL.md` 原文 + 本机安装事实段 | Apache-2.0（上游仓库） | 无 |
| `impeccable` | `impeccable` | WorkBuddy 市场（skillId=skill_2053082862415904768，v2.0.0）；frontmatter `homepage: github.com/pbakaus/impeccable`；正文引用 `anthropics/skills` 的 frontend-design | Apache-2.0（frontmatter 声明，基于 Anthropic frontend-design）。**瑕疵：声明「See NOTICE.md」但包内无 NOTICE.md** | 无 |
| `ios-application-dev` | `ios-application-dev` | WorkBuddy 市场（skillId=skill_2053082181124681728，v1.0.0） | MIT（frontmatter `license`） | 无 |
| `landing-page-design` | `landing-page-design` | `github.com/elayadesign/ai-design-skills` @ `456d9e0d3e2d`（2026-11-01），见 PROVENANCE.md | MIT（随包 `LICENSE`，Copyright (c) 2026 Elaya） | 有 |
| `pdf` | `pdf` | Anthropic 官方文档技能；OpenClaw 预装（slug=pdf，2026-08-11，version=b29e7cf6…） | **专有** © 2025 Anthropic, PBC.（同 docx） | 有 |
| `pptx` | `pptx` | Anthropic 官方文档技能；OpenClaw 预装（slug=pptx，2026-08-11，version=b29e7cf6…） | **专有** © 2025 Anthropic, PBC.（同 docx） | 有 |
| `reverse-trace` | `spider-king` | 本机下载包 `H:\下载\06-skill-mcp-3.0\trace（skill）.zip`（第三方分发，非官方市场） | **包内无 LICENSE，许可状态未知**；PROVENANCE 限定仅本机自用 | 无 |
| `reverse-wechat-miniapp` | `wechat-miniapp-reverse` | 本机下载包 `H:\下载\06-skill-mcp-3.0\wechat-miniapp-reverse(小程序逆向skill).zip` | **包内无 LICENSE，许可状态未知**；PROVENANCE 限定仅本机自用 | 无 |
| `self-improving-agent` | `self-improving-agent` | OpenClaw 预装（slug=self-improving-agent，2026-08-11，version=114ca7b5…）；正文上游 `github.com/pskoett/pskoett-ai-skills`（v4.0.0） | **未声明** | 无 |
| `sickn33-frontend-slides` | `frontend-slides` | skillstore slug `sickn33-frontend-slides`（2026-10-02）；frontmatter `source: github.com/zarazhangrui/frontend-slides` | **未声明** | 无 |
| `skill-creator` | `skill-creator` | WorkBuddy 市场（`_skillhub_meta.json` skillId=skill_2053082698440450048，v0.2.0） | Apache-2.0（随包 `LICENSE.txt` 全文） | 有 |
| `tavily-search` | `tavily-search` | OpenClaw 预装（slug=tavily-search，2026-08-11，version=ea5e8201…） | **未声明** | 无 |
| `webapp-building` | `webapp-building` | **泄露内容**：与 `D:\QoderToolkit\web-kimi` 逐文件 sha256 比对 173/175 字节相同；web-kimi 的 PROVENANCE 记来源 `QvvvvvvQ/skills_leaks` 的 `Kimi/skills/webapp-building` | **没有任何使用许可**（上游 README 明示）。仅本机学习研究，禁止二次分发 | 无 |
| `xlsx` | `xlsx` | Anthropic 官方文档技能；OpenClaw 预装（slug=xlsx，2026-08-11，version=b29e7cf6…） | **专有** © 2025 Anthropic, PBC.（同 docx） | 有 |

## 三、目录名与 frontmatter `name` 不一致（已知例外，不要「顺手改」）

| 目录 | name | 为什么保留 |
| --- | --- | --- |
| `barnhardt-enterprises-inc-checkpoint` | `checkpoint` | skillstore slug 带厂商前缀，`.skill-lock.json` 按此 key 记录 |
| `barry-liu-888-requirement-translator` | `requirement-translator` | 同上 |
| `brave-web-search` | `web-search` | 上游 name 就是 `web-search`；目录名加了引擎前缀便于区分 tavily |
| `reverse-trace` | `spider-king` | 自带闸门 `scripts/validate_skill.py` 硬校验 name 必须是 `spider-king`，改了会多一条 ERROR |
| `reverse-wechat-miniapp` | `wechat-miniapp-reverse` | 与上游包名一致；Qoder 等按目录名登记，`reverse-` 前缀已足够区分 |
| `sickn33-frontend-slides` | `frontend-slides` | 同上 |

路由已验证：`router.py show <name>` 对上述每一个都能解析到正确目录，**不一致不影响使用**。

## 四、重复与分叉

- `D:\Skills\webapp-building` 与 `D:\QoderToolkit\web-kimi` **同名（name 都是 `webapp-building`）且同源**：175 个文件中 **173 个字节完全相同**，只有 `SKILL.md` 不同（4783 B vs 2537 B），前者多 `agents/openai.yaml`，后者多 `PROVENANCE.md`。
  **没有合并**：`qoder-toolkit\SKILL.md` 正文硬编码 `D:\QoderToolkit\web-kimi\scripts\template\`，合并会打断 Qoder 侧路由。
  **2026-11-15 修**：`D:\Skills\webapp-building` 原本丢掉了限制条款，已补 `PROVENANCE.md`。

## 五、被排除在 git 远端备份之外的技能

下列技能**仍在本地、仍可用，但永远不会被 push**（`.gitignore` 已按目录排除）。完整依据与重新取得方式见 `BACKUP_SCOPE.md`。

| 技能 | 原因 |
| --- | --- |
| `docx` | Anthropic 专有：禁止在 Services 之外保留副本、禁止转移第三方 |
| `pdf` | 同上 |
| `pptx` | 同上 |
| `xlsx` | 同上 |
| `reverse-trace` | 无 LICENSE，PROVENANCE 限定仅本机自用、不二次分发 |
| `reverse-wechat-miniapp` | 同上 |
| `webapp-building` | 泄露的 Kimi 产品技能，上游明示没有任何使用许可 |

**私有仓库不能解决这一条**：上传到托管平台本身就是「转移给第三方」。

## 六、已知瑕疵（不编造修补）

- `impeccable` frontmatter 写「See NOTICE.md for attribution」，但包内**没有 NOTICE.md**（实测目录只有 `SKILL.md`、`_icon.png`、`_skillhub_meta.json`、`references`）。上游包自带的断引用，**没有伪造署名文件**。
