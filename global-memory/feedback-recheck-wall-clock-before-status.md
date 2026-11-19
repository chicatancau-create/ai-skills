---
name: feedback-recheck-wall-clock-before-status
description: 报「现状」前先跑 date、对比 HEAD、并重新核对远端 refs/分支；会话续接后上一轮现状结论默认作废。
metadata:
  type: feedback
---

任何「项目现在是什么状态 / 完成了多少 / 缺什么」的判断，动手前先 `date` + `git log -1` + 目标文件 `wc -l`；涉及多远端时还要 `git fetch --all` 并比对各 remote 的 main。任一变化，上一轮结论全部作废重测。

**Why**：2026-10-11 我从 10-06 续接的会话里连续用旧事实说话（Qt 页数、Main.qml 行数），实际已过 5 天、HEAD 前进、计划跑完 P0；根因是只看相对 mtime、没看绝对日期。2026-11-08 又出现同类：本地和 GitHub 都停在 `01329dc`，我据此差点判「MS6–MS11 规范不存在」，而 AtomGit main 已到 `5739c94`，只是没 fetch。

**How to apply**：
- 相对 mtime 只判断「是否正在被写」，判断「今天几号」必须 `date`；写日期进提交/文档前再跑一次。
- 会话续接（summary / restored_files）后，第一条现状回答前重跑 `date`、`git log`、`git ls-remote`。
- 多远端仓库：`git for-each-ref refs/remotes` 看是否有未 fetch 的领先提交，再查 `git ls-tree`。
- **凡是「倒计时 / 等待期 / 到点没到点」的判断，第一条命令必须是 `date`，不许用上一轮的时间感。**
  2026-11-10 这一轮又犯两次：先把 11-01 当成 10-31（说"我 11 点多量的是 59 个应用"），
  后把 11-10 当成 11-01（据此算出"还剩 5.9 天"，实际已超期 67 小时）。
  同一会话里第 3 次了 ⇒ 在长会话里「今天几号」几乎一定会漂，不能靠相对推算。
- **同一会话的相邻 turn 之间也可能隔几天，不止续接时.** 2026-11-09→11-11→11-12 三次：我拿上一 turn 的「现在」继续说话，而执行方已推进数十提交、甚至把我刚报的缺陷修掉了。用户附件的 mtime 常是真实日期的线索（附件 11-11 22:56 而我以为还是 11-09）。**每个新 turn 的第一条现状命令仍是 `date`**；交接发现/结论前再核一次该发现是否已被对方关闭，别交过期缺陷。
- 同类教训：[[feedback-rigor-audit]]、[[feedback-no-unverified-cause-claims]]、[[feedback-check-remotes-before-missing]]。
