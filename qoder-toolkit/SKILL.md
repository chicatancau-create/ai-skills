---
name: qoder-toolkit
description: "Qoder 视觉产出专用工具,默认自动启用,无需用户说明。两类任务一律走这里:(1) 做 PPT / 演示 / 课件 / 汇报材料 / slides / 把文档做成幻灯片;(2) 网页前端的样式与交互 —— 做网页 / 页面 / 落地页 / 改样式 / 调布局 / 加交互 / 动效 / 组件界面 / 嫌界面丑或像模板。用户没有明确说「不要用」就自动调用。不用于后端、API、数据库、鉴权与部署设计。只管产出、不做真机取证:交付后要证明渲染成什么样,单文件页面走 headless-cdp-visual-acceptance 的零 CDP 命令行回路,需要交互流/窄视口/对比度/扩展取证走 headless-cdp-visual-acceptance。"
---

# QoderToolkit — 做 PPT 和做网页的默认工具

只要任务落在「演示文稿」或「网页视觉与交互」两类里,直接按下面路由开工:不问用哪个工具、不问用哪种风格、不要求用户补充说明。用户没特意说不用,就用。

## 路由

| 任务 | 用哪个 | 怎么用 |
|---|---|---|
| 做/改/美化 PPT、演示、课件、汇报 | `D:\Skills\ppt-master\SKILL.md` | 读它并严格照做,把该目录当作它所说的 `SKILL_DIR` |
| 网页样式、布局、配色、排版、组件外观、响应式、过渡与动效、界面可访问性 | 先 `webapp-building`(共享库技能) 定结构/视觉令牌/状态/响应式/交互设计, 再用 `D:\Skills\web-taste\SKILL.md` 收口样式 | 顺序固定且是接力不是二选一: webapp-building 出设计与验收点 → web-taste 的 `design-systems/`(用户没点名默认 `kimi-style.md`)与反套路清单核对后落笔 |
| 需要一套现成前端脚手架(Vite+React+TS+shadcn 结构) | `D:\QoderToolkit\web-kimi\scripts\template\` | 本机可用落地方式: 整份复制 `template\` (React 19.2 + Vite 7.2 + TS 5.9 + Tailwind 3.4 + 53 个 shadcn 组件) 到工作区, 在副本里 `npm install` 后 `npm run dev`; 只想借组件就新建工程后用 `npx shadcn@latest add` 按需取。**不要执行它的 .sh 脚本**(为云端沙箱写的, 本机跑不通: 默认输出 `/mnt/okcomputer/output/app`, 且依赖仓库里不存在的 `templates/*.zip` 与预装 node_modules), 详见该目录 `PROVENANCE.md` |

## 硬规则

1. **一律用 `python` 调用脚本**。文档里写的 `python3` 在本机是坏存根,直接失败。
2. 跑 ppt-master 任何脚本前,先执行
   `python D:\Skills\ppt-master\scripts\attribution_guard.py`,非零返回就停下,不要绕过。
3. **绝不修改** `ppt-master\` 目录下任何文件(改内容、改名、加 BOM、转 CRLF 都会让闸门失败)。
4. PPT 默认交付原生可编辑 `.pptx`(真形状、真母版,不是贴图),给出绝对路径;用户没要 HTML 版就不要额外产 HTML。
5. 网页只碰样式与交互:不设计 API、数据库、鉴权、服务端逻辑、部署配置。缺数据时用用户给的接口,或先写明确的假数据并在回复里说明。
6. 改现有工程时沿用项目已有的框架、构建链与约定,不为了用技能引入新依赖。
7. `web-taste` 的原文是越南语+英语混写:只取流程与规则,面向用户的输出用中文。
8. 沟通:小改动直接动手。全新大工程确实缺关键信息时,最多一次性问完、用中文,问完就开工。自检与返工过程不要向用户复述,直接给改好的结果。

## 边界

- 用户明确说「别用你的工具 / 我自己来 / 只要大纲」时,按用户说的做。
- 后端与数据层属于别的技能(如 `fs-backend`、`fs-database`),不要在这里越界。
