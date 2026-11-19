---
name: feedback-round-then-push-both-remotes
description: 每轮收尾把同一 commit 推到三个远端（GitHub origin、GitCode domestic、AtomGit atomgit），AtomGit 是任务交付目标；新增/改动 remote 必须在回复里点名，别让用户发现「第三端」。
metadata:
  type: feedback
---

这台机器上每轮动手工作收尾的固定流程（用户 2026-11-07 要求「写死」）：

1. **动手 → commit → 推到全部三个远端**：
   - `origin` = GitHub `chicatancau-create/fullstack-study-library`
   - `domestic` = GitCode `zhoumoyukuai/fullstack-study-library`
   - `atomgit` = AtomGit `zhoumoyukuai/fullstack-study-library`（任务描述里的交付地址）
2. **推完即交回用户**，由网页端 AI 规划下一轮，本地不自行连跑。
3. 回复里给出每个远端 `main` 的实测 SHA（`git ls-remote --heads <remote> main`），不能只贴一次 push 输出。

**Why:** 2026-11-08 用户看到 `domestic` 指向 gitcode.com 时问「这是哪个网站？怎么还有第三端？」——此前一直把 AtomGit 当成 `domestic`，实际 `domestic` 是 GitCode；`atomgit` 是我为了让本仓库能推 AtomGit 新加的 remote，加之前没有说明。用户对远端拓扑很敏感，且 AtomGit 才是他要的交付仓库。

**How to apply:**
- 新增 remote 属于可见状态变化：加完立刻在回复里说明用途与 URL；不要默认用户知道。
- 推 AtomGit 若没有可用凭据，不要伪造成功；只读 `ls-remote` 不能证明可写。推送后必须用 `ls-remote` 复核远端 SHA。
- 实测 AtomGit 有时回 `Everything up-to-date`，但 `ls-remote atomgit main` 已经是本轮新提交（2026-11-09 连续多次）；不要把这行当失败，也不要当成功——只认 `ls-remote` 的 SHA。
- GitHub 直连常被重置，按 URL 挂 `http://127.0.0.1:7897`（见 [[reference-git-push-needs-local-proxy]]）。
- 明确路径 `git add`，别 `git add -A` 吞别人 WIP（见 [[feedback-never-git-add-dirs-in-codeweave]]）。
- 这条不覆盖 force-push、改写历史、删除来源、首次建仓；任务级显式禁令（如「不 push」）优先。

Related: [[feedback-autonomous-execution]], [[reference-git-credential-manager-windows]], [[feedback-rigor-audit]], [[feedback-check-remotes-before-missing]]
