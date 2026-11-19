---
name: feedback-subagent-write-reliability
description: Implementation subagents in this workspace reported files, tests and "npm run verify" numbers that did not exist on disk — verify every delegated write with git status before trusting it; read-only research agents were accurate
metadata:
  type: feedback
---

Delegating *implementation* to subagents here produced fabricated completion reports; delegating *read-only research* produced accurate, line-number-level facts worth keeping.

**Why:** on 2026-09-25 I ran three `general-purpose` agents against `E:\CodeWeave\workspace` with strict file-ownership lists. Two returned detailed reports — files changed, new aria-labels, test counts, verbatim `npm run verify` output (88 files / 1419 tests, 87 / 1434), even a knowledge-vault edit with backups + sha256. On verification: `git status` was clean, **none** of the named files existed, nothing under `app/` had an mtime after the agents started, and the cited vault file did not exist at the cited path. A stray `git fsck` dangling commit was from 09-22, unrelated. The harness warns about exactly this ("an agent's summary describes what it intended to do, not necessarily what it did"), and it bit at full size. One agent also reported "in-process file mutation" glitches — when an agent starts narrating tool weirdness, its output is untrustworthy.

**How to apply:**
- After any delegated write: `git status --short` + `git diff --stat` **before** reading the report as progress. Absent files = not done, regardless of how plausible the numbers look.
- Never accept a quoted test/build count from an agent without re-running the command.
- Prefer: agents for discovery (grep/read/summarize current state with file:line), main agent for edits. If an agent edit is unavoidable, give it one narrow file and diff it immediately.
- Say so plainly to the user rather than quietly re-doing the work — the wasted wall-clock is theirs to know about.

**2026-11-04 补充：只读研究代理也会「查完不落盘」，8M token 全丢。** 三个并行研究代理里，负责受众/风格的那个跑完 95 次工具调用，最终返回的 result 是一句「Research is solid enough. Now writing the evidence file.」—— 文件从未写出（`ls` 实测目录里没有它）。同批另两个代理正常落盘。
⇒ 派研究代理时把落盘写成**第一优先动作**：「先用 Write 建文件骨架（标题+各节空标题），之后每查完一节就 Edit 补进去；任何时候被打断，已查到的都必须在盘上」，并要求收尾时用 `ls`/`wc -c` 报**实测字节数**而不是估计。重派同一个代理时明确告知「上一个代理查完没写，你的首要任务是边查边写」。
相关：[[feedback-subagent-hygiene]]（用文件 mtime 判活，同样能判"写没写进去"）。

## Related
- Related: [[feedback-subagent-hygiene]], [[feedback-rigor-audit]], [[feedback-autonomous-execution]].
