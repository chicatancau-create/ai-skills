---
name: feedback-backup-and-write-authorization
description: For irreversible/out-of-project work — back up outside the project dir, take per-file pre-write copies before touching the vault, and follow the plan doc's own stated first action instead of doing everything
metadata:
  type: feedback
---

When a task touches files outside the repo or could discard work, ask once up front and then proceed autonomously within that answer:

- **Backups go outside the project directory**, not into an existing in-project `.backups/`. Chosen: `E:\CodeWeave-recovery\<date>-<milestone>\` with `git/`, `manifests/`, `backup/`, `reports/`. Reason: an in-project backup is damaged by the very migration it protects against.
- **Writes to the external vault are allowed only per-file**: take a pre-write copy (`manifests/pre-write/`) and work in a short maintenance window. Never bulk-rewrite the vault to satisfy a task.
- **Follow the plan document's own declared first action** (e.g. "首个实施动作是 M0 … 然后 M1") rather than interpreting "modify the project per the docs" as "do every milestone". The user picked the narrow, documented option when offered the full range.
- Verify backups by re-hashing (source vs manifest vs copy) and report exact changed/missing/extra counts; report the write scope the same way (e.g. "changed 2, extra 1, 722 untouched") to prove nothing outside the authorized files moved.
- **When repairing damage an earlier AI pass did to vault text, assert against that pass's own `.before` copy — never re-read the prose and "fix" by judgment.** The assertion that makes a repair provable rather than a new edit: *repaired line minus the added annotation == the pre-write line, byte for byte*, plus *the pre-write line really was the broken shape* (e.g. exactly one missing `）`). Say explicitly when the file has no other legitimate change mixed in (annotations only; no verification status, no transcribed values). Log the correction in the same 结构整理记录 as a new numbered section, quoting the earlier claim being corrected rather than deleting it, and re-run the vault's own three tools.

**Why:** the user's standing ask is strict adherence to the engineering files with no drift; the files themselves require a designated independent recovery directory and per-change authorization for irreversible steps.

**How to apply:** any time a task involves moving/deleting directories, `git reset/clean`, migrating data stores, or writing outside the working dirs. Ask the scope + backup-location questions in one batch, then don't re-ask for routine in-repo edits.

Related: [[feedback-vault-engineering-rules]], [[feedback-rigor-audit]], [[user-role]]
