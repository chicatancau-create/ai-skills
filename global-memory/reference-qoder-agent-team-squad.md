---
name: reference-qoder-agent-team-squad
description: Qoder Desktop 实验性功能 Agent Team（内部代号 squad）的实测边界：1 负责人+1~4 成员、字段名、云端注册、无 MCP 编程通道、任务仅支持文本输入。
metadata:
  type: reference
---

# Qoder Agent Team（squad）能改什么、不能改什么（2026-10-20 实测，0.4.8）

**结论：团队与 Agent 都是「登录身份 + 云端」资源，Agent 会话内没有任何可编程通道，只能交付粘贴包 + 人工点保存。**

- 功能内部名是 **squad**（不是 team）。i18n 取证入口：`app.asar` 里搜 `squadMemberLimit`、`squadInstructions`、`启用 Agent Team`。
- 人数上限：`选择一至四名成员` / `最多选择四位额外成员` / `已达到四位成员上限` → **1 团队负责人 + 4 成员 = 5**。被选为负责人会自动从成员里移除。
- 字段：团队 = 名称 / 说明 / **协作指令**（团队级全局指令放这里）；Agent = 名称 / 说明（一句话）/ **工作指令**（指令内容）+ 模型 + 默认权限 + Skills/MCP/Plugins。**Agent 名称创建后不可改**（`创建后暂不支持修改名称`）。
- 保存动作：`PUT /api/v1/collaboration/team-profiles/:id`（`core.createTeamProfile`），会「为所选 Agent 开启 Agent Team 使用、完成云端注册并启动 Runtime」，**要求本机在线**。取证看 `AppData\Roaming\com.qoder.app.stable\logs\<启动>-<pid>-<hash>\collaboration.log` 的 `apiOperation` / `httpStatus`。
- 本地没有可写的团队文件：`~\.qoder`、`~\.qoder-cn`、`AppData\Roaming\com.qoder*` 里都没有 team/squad 配置；`main.sqlite` 无 squads 表；asar 里的 `localSquads` 只是本地可用性镜像（`{id, enabled, archivedAt, leaderAgentId, memberAgentIds}`），定义仍在云端。
- 会话侧通道缺失：`collaboration:skills` 技能能加载，但 `mcp_list`/`query_mcp` 里**没有 collaboration MCP server**（本机只有 sites / qmind / Presentations / repowiki / knowledge-center / js-reverse / browser-use / node-repl）。所以别承诺"我来建团队"，只能说"我给你粘贴包"。
- 硬限制：`Agent Team 任务暂仅支持文本输入`（带图/附件要先转文字）。成员开始工作后各用**独立会话**（跨成员上下文不连续）。
- 内置模板只有一个「交付智能体团队」，模板只填团队的名称/说明/协作指令，成员仍需手选；`squadTemplateAgentPresets` 说明模板可带 Agent 预设，但用户能否自定义模板**未证实**。
- 国际版 `D:\Qoder` + 国内版 `D:\Qoder CN` 是 0.4.8 同版本、同套 squad 界面，但**两套账号 + 两套用户数据根**（`~\.qoder` / `~\.qoder-cn`），团队不能同步 → 两边各建一遍（10 个 Agent + 2 个团队）。判 CN 是否登录：`com.qodercn.app.stable\auth.v1.dat` 存在 + collaboration.log 里 `core.listTeamProfiles` 回 200。

## 用 Computer Use 实际建团队时踩到的（2026-10-21 补）

- **「允许在 Agent Team 中使用」开关在创建表单里点不动**，必须保存后从列表行尾铅笔进编辑页再开；开了之后保存才触发云端注册（状态：正在注册 → 正在连接 → 在线）。成员选择器只列**已启用**的 Agent，未启用的会写 `此 Agent 当前不可用于 Team，请选择`。
- **列表页会整页不吃合成点击**：当行状态是 `Agent Team·正在重连` 时，铅笔和行尾开关点了都没反应，而同一页的左侧导航、右上「创建智能体」、表单里的输入框/下拉都正常。判据：点行尾开关后截图仍不翻转。**只有等重连完成或重启 Qoder**（重启会杀掉当前会话，别顺手做）。
- **别用 Ctrl+- 缩放来"躲遮挡"**：缩放后截图仍是 1262×768 但布局变密，导航项会整体上移一行，按旧印象点 (40,295) 会打到「数据导入」。要么先 `Ctrl+0` 复原，要么每次操作前重取截图并**按标签文字对齐 y**。
- **列表行尾按钮要点标题那一行**（成员/插件选择器同理）：点行中部或描述行不生效；行控件 y ≈ 标题 y + 13。
- **权限编辑器里的 Ctrl+A 会选中整页**而不是清空输入框；改筛选词要 Escape 关掉弹层再重开重打。
- **工具权限是「允许/禁止」两张表 + 每行一个工具名**（Read/Glob/Grep/Edit/Write/Bash），留空就是沿用默认「自动审批」（= 仅风险动作才问），所以"没配权限"≠"不能干活"。
- **国内版能力面是空的**：`~\.qoder-cn\` 下没有 skills 目录，创建表单里 Skills 显示「暂无已安装的 Skills」、Plugins 显示「暂无可用的 Plugins」——市场插件要在 CN 账号里单独装。对齐做法（已验证可行）：建 `C:\Users\Admin\.qoder-cn\skills`，用 `_winapi.CreateJunction(D:\QoderToolkit\<名>, 目标)` 逐个镜像国际版的 7 个联接；判据是 `GetFileAttributesW` 的 0x400 reparse 位 + 能读到 `SKILL.md`。
- **团队草稿不一定保得住**：离开创建表单再回来，可能带回旧草稿（会把名称/说明叠成两份），也可能被清空。每次回来先读计数器（名称 6/80、说明 70/500、协作指令 765/3200）再决定要不要覆盖。
- 保存团队可能**一次生成两条同名团队**（实测出现过 4 位成员 + 3 位成员各一条），收尾要回列表数一遍。

相关：[[reference-qoder-app-internals]]、[[feedback-agent-brief-trigger-words]]

