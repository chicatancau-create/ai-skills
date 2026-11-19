---
name: feedback-vault-engineering-rules
description: In E:\OBsidian, obey the vault's own engineering files over generic initiative — no invented source cards, maintenance ≠ learning progress, always run the check tools and log changes
metadata:
  type: feedback
---

Work strictly inside the conventions the repository states for itself (`AGENTS.md`, `00-入口/AI教学协议`, `教学路由与分册边界`, `知识来源/来源登记与引用规范`, `资料库维护清单`). Concretely, as learned this project:

- Never create a course source card for material with no readable text (the registry forbids it); say why instead of inventing one. The user accepted this refusal when explained.
- Never renumber/recycle source-card IDs, never write new knowledge into legacy compat entries, never rename/delete 旧入口 — repair inbound links instead.
- Adding material or reorganizing structure never counts as learning progress: never touch mastery levels or stage status in 进度追踪 while doing maintenance, and say so explicitly in reports.
- After content edits run `python -X utf8 tools/check_vault.py`; after title/section changes run `tools/build_topic_index.py` (then `--check`). Report the actual tool output.
- Every work round gets appended to the 变更日志 (`00-入口/历史变更/...`), and structural rewrites of a "总" doc get an entry in its own history file with an old→new section-number map.

**Why:** the user's whole ask was "按照里面的工程文件进行" — the vault's value is that provenance and boundaries are auditable, and a plausible-looking shortcut destroys that.

**How to apply:** before editing anything in this vault, re-read the governing entry doc for that layer; when a request conflicts with a rule the file states, follow the rule and tell the user, don't silently satisfy the request.

- **笔记库不放代码与依赖**：同一份代码只允许存在于代码仓库（`E:\fullstack-code`），学习库里只放需求、验收、
  证据索引和链接。2026-11-09 清掉 `07-项目实现` 里 P02/P03/P04 的完整副本（约 760 MB，含 `node_modules`）——
  处理顺序是：先比两边差异 → 把副本独有的文件合并回代码仓库 → 验证 → 再删副本，旧实现归档到 `D:\_recover\`。
  07 现在是"指向代码仓库的索引页"，别再往它里面放代码。

Related: [[feedback-rigor-audit]], [[user-role]]
