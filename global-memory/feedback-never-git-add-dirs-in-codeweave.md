---
name: feedback-never-git-add-dirs-in-codeweave
description: In E:\CodeWeave\workspace the user keeps dozens of uncommitted WIP files; `git add -A <dir>` sweeps them into your commit — stage explicit paths and re-verify
metadata:
  type: feedback
---

Never `git add -A <dir>` (or `git add <dir>`) in this repo. Stage the exact files you changed, then
verify with `git show --name-only --format= HEAD | grep -cE "frontend/|tools/visual/..."` before moving on.

**Why:** 2026-10-02 I ran `git add -A CHANGELOG.md tools 【后端数据服务】_BACKEND_DATA ...` to commit the
separation work. `tools/` contains five files the user had modified but not committed
(`app-instance.mjs`, `probe-login-structure.mjs`, `probe-nav.mjs`, `visual-check.mjs`, `visual-states.mjs`),
so they landed inside my feature commit — content preserved but misattributed, and the user's
work-in-tree was silently consumed. Recovering needed `git reset --soft HEAD~1` + `git restore --staged <5 files>`.

The tell: the §13 inventory already recorded **29 pre-existing `M` files**. After any staging step,
`git status --porcelain | grep -c "^ M"` should still read 29; if it drops, you just took someone's work.

**How to apply:** before every commit here, (1) list what you actually edited, (2) stage those paths only,
(3) count unstaged `^ M` lines against the recorded baseline, (4) confirm a deliberately-changed file
you *did* touch (e.g. `tools/visual/paths.mjs`) still appears staged.

**Same trap even with explicit paths (2026-11-02, `E:\fullstack-code`):** 多个 Qoder 会话共用同一个 git 索引 —— 我按显式路径 add 了自己的 16 个文件，
另一会话**先前已暂存**的 `Web/node/class.js` 仍被我的 commit 卷走（`git commit` 提交的是整个索引，不是你刚 add 的那些）。
防法：提交前在 **git 根**跑 `git status --short`，看第一列有没有别人的 `A`/`M`；只 `git status --short <自己的子目录>` 是看不到的。
补救：`git reset --soft HEAD~1` → `git restore --staged <他们的路径>` → `git commit -F <消息文件>`。两个坑：`restore --staged` 的路径相对当前目录，
人在子目录里会报 `pathspec did not match`（先 cd 到 git 根）；消息文件要在 reset 之前就写好，否则链路中断后拿不到原文。
对方文件的处置：退回未跟踪（`??`），内容不丢，但需要他们重新 `git add` —— 要如实告知。

Related: [[feedback-destructive-file-ops]], [[feedback-verify-subagent-file-claims]], [[feedback-rigor-audit]], [[feedback-bulk-regex-source-rewrites]]

**Path drift (verified 2026-10-03):** `E:\CodeWeave` no longer exists. CodeWeave now sits at
`G:\CodeWeave\` split into 工作区/应用端/移动端/网页端, and `G:\CodeWeave\工作区` has **no `.git`** — so
the repo root is not where this note's paths say. Re-locate the git root before applying this rule.
