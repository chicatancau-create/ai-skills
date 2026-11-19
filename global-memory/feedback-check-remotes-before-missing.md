---
name: feedback-check-remotes-before-missing
description: 任务声称的规范/工程文件在本地不存在时，先 fetch 所有远端并比对各 remote 的 main 与分支，再下「缺失」结论；MS6–MS11 就躺在 atomgit/main 上。
metadata:
  type: feedback
---

当任务描述说「仓库里已有某批工程文件」，而本地工作树里没有时，**先检查所有 remote 的所有分支**，再判断文件缺失。

**Why:** 2026-11-08 的完工任务声称 `09-整合任务/MS6–MS11` 与 `完工标准.md` 已存在。本地和 GitHub/GitCode 的 main 都只有 MS0–MS5，我一度准备自己起草六份规范；随后 `git fetch atomgit` 发现 **AtomGit 的 main 已前进到 `5739c94`**，正好新增了这 7 个文件（8 个旧文件 + MS6–MS11 + 完工标准 = 15）。如果当时直接按提示词自拟验收标准，会把「按规范执行」偷换成「自己出题自己答」。

**How to apply:**
- 先 `git remote -v`、`git fetch --all`、`git for-each-ref refs/remotes`，再对每个候选 main 跑 `git ls-tree -r --name-only <remote>/main -- <path>`。
- 若某远端领先且本地是祖先，`git merge --ff-only <remote>/main` 引入规范，别重写、别覆盖。
- 本地/单一远端没有 ≠ 不存在；但也不能反过来假设远端一定有——每一条都要有 `ls-tree`/`ls-remote` 证据。
- 引入后再执行；执行报告里注明规范来自哪个远端与 commit。

Related: [[feedback-recheck-wall-clock-before-status]], [[feedback-round-then-push-both-remotes]], [[feedback-no-unverified-cause-claims]], [[feedback-rigor-audit]]
