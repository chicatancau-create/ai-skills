---
name: feedback-no-backup-for-junk-deletes
description: For deletions of dead/junk files the user wants them gone outright — no staged copies, no recover dir; keep backups only for changes with real regret risk
metadata:
  type: feedback
---

When cleaning up dead files (scratch scripts, stale snapshots, dead session caches, duplicate registry
entries), **delete them and don't leave a backup copy behind**. Don't stage a `_recover\` tree or ask
whether to keep it.

**Why:** on 2026-10-03, after I copied 113 cleaned items into `C:\Users\Admin\_recover\qoder-scratch-20261003`
with per-file sha256 verification, the user's reply was "把这些备份全部删了,不需要回本……没用的东西就删了
就行,无所谓". The verification pass was useful for *judging* dead-vs-alive; the retained copies were pure
noise to them.

**How to apply:** still run the evidence step first (references from skills/scheduler/env, live process
command lines, whether paths inside the script still exist) and still confirm scope before registry or
cross-session deletes — that part is about *not deleting live things*, not about rollback. Then just
remove. Keep real backups only where the change is (a) hard to reconstruct and (b) plausibly regretted —
e.g. vault content edits per [[feedback-backup-and-write-authorization]], originals per
[[feedback-destructive-file-ops]]. Not for `%TEMP%` scratch or a `reg export` nobody will import.

Related: [[user-role]], [[feedback-autonomous-execution]], [[qoder-artifact-locations]]
