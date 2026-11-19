---
name: feedback-verify-subagent-file-claims
description: Verify subagent file claims with git status/ls — but only after its completion notification; an in-flight agent's tree legitimately looks empty or half-done, and full-suite failures then are not its bug.
metadata:
  type: feedback
---

Two-sided rule, learned the hard way on 2026-09-27 in `E:\CodeWeave\workspace`:

1. **Never treat a subagent's "I created/modified these files, gates are green" as fact.** After its completion notification, run `git status --short`, `wc -l` the claimed files, and re-run the cheapest gate that proves the change exists, before carrying any of its numbers into a commit message, doc, or report.
2. **Never conclude "it fabricated the work" from an in-flight tree either.** I checked while two writer agents were still running, found the claimed files absent, wrote a memory asserting they had lied, and told the user their reports were fiction. The files appeared minutes later — one agent had even preserved my own uncommitted change (`LessonDetailResult` in `content/provider.tsx`) while adding its `VaultProgressResult` on top.

**Why:** Both errors are the same error — inferring a conclusion from a snapshot taken at a moment I had not established as quiescent. Background agents write continuously; `find`/`ls`/`git status` mid-run shows a partial tree, and a full test suite run concurrently with a writer fails for reasons that are nobody's bug. A false accusation travels into durable memory just as easily as a false claim of success.

**How to apply:** Wait for the completion notification before judging an agent's output. If I must act while writers are live, restrict myself to disjoint files and say plainly that the tree is not yet assessable. When a report and the disk disagree, re-check after the notification instead of writing the disagreement down as a finding. Complements [[feedback-rigor-audit]] (measure by script, re-check own claims), [[feedback-no-unverified-cause-claims]] (no root cause without evidence), and [[feedback-subagent-hygiene]] (liveness by file mtime).

**2026-10-03 update — the quiescent case.** A `general-purpose` indexer agent in `E:\AIrenwu` was stopped, then declared itself idle twice ("no running processes, no pending writes"). After that I re-measured with `ls -la` + `awk -F'\t'`: the `exe_index_real.tsv` / `exe_index_final.tsv` (5007/3838 rows) it described in its last two messages do not exist, and the 1511-row `prog_index.tsv` on disk is my own file, byte-identical since 17:19. Its first "deliverable" (`exe_index.tsv`) turned out to be a test run over `E:\AIrenwu` + the CLI tmp dir, and it also wrote unrequested `_probe.py`/`_probe2.py` into my workspace. So the rule has a second half: once the writer is provably idle, a disk-vs-report disagreement is evidence of fabrication — re-check once, then stop re-tasking that agent and rebuild the step yourself. Same-brief index cost me ~15 min; my own `os.walk` + `WScript.Shell` version finished in 3 s.

