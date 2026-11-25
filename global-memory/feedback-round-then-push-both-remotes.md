---
name: feedback-round-then-push-both-remotes
description: 每轮收尾把同一 commit 推到两端（GitHub origin、GitCode/AtomGit 同一平台）；新增/改动 remote 必须在回复里点名。GitCode 与 AtomGit 已合并，本机只有两端。
metadata:
  type: feedback
---

> 2026-11-25 纠正：GitCode 与 AtomGit 已合并为同一平台（gitcode.com 与 atomgit.com 同后端，账号/仓库互通，详见 [[reference-gitcode-atomgit-merged-scan]]）。本机只有**两端**：GitHub 与 GitCode/AtomGit。旧条曾把同一平台的两个域名误当多个平台，已废止。用户多次强调只有两端，对远端拓扑敏感。

这台机器上每轮动手工作收尾的固定流程（用户 2026-11-07 要求「写死」，2026-11-25 按合并事实纠正为两端）：

1. **动手 → commit → 推到两端**：
   - `origin` = GitHub `chicatancau-create/<repo>`
   - `gitcode`（部分仓库 remote 名仍叫 `atomgit`，URL 实为 gitcode.com）= GitCode/AtomGit `zhoumoyukuai/<repo>`（同一平台，任务交付目标）
   - 不再单独推「domestic + atomgit」两路——那是同一平台，重复。
2. **推完即交回用户**，由网页端 AI 规划下一轮，本地不自行连跑。
3. 回复里给出两端 `main` 的实测 SHA（`git ls-remote --heads <remote> main`），不能只贴一次 push 输出。

**Why:** 2026-11-08 用户看到 `domestic` 指向 gitcode.com 时质疑「这是哪个网站？怎么还有别的端？」——根因是把 GitCode 与 AtomGit 当成两个平台；2026-11-25 证实二者已合并，本机自始至终只有两端。用户对远端拓扑很敏感，新增/改动 remote 必须先说明。

**How to apply:**
- 新增 remote 属于可见状态变化：加完立刻在回复里说明用途与 URL；不要默认用户知道。
- 推 GitCode/AtomGit 若没有可用凭据，不要伪造成功；只读 `ls-remote` 不能证明可写。推送后必须用 `ls-remote` 复核远端 SHA。
- 实测有时回 `Everything up-to-date`，但 `ls-remote` 已是本轮新提交；不要把这行当失败或成功——只认 `ls-remote` 的 SHA。
- GitHub 直连可达性按轮漂，代理端口会漂（2026-11-25 活口 7890，7897 已死）；gh 当轮未手动挂代理即可用（见 [[reference-gitcode-atomgit-merged-scan]]、[[reference-github-mirror-from-this-box]]）。
- 明确路径 `git add`，别 `git add -A` 吞别人 WIP（见 [[feedback-never-git-add-dirs-in-codeweave]]）。
- 这条不覆盖 force-push、改写历史、删除来源、首次建仓；任务级显式禁令（如「不 push」）优先。

Related: [[feedback-autonomous-execution]], [[reference-git-credential-manager-windows]], [[feedback-rigor-audit]], [[feedback-check-remotes-before-missing]], [[reference-gitcode-atomgit-merged-scan]]
