---
name: reference-sqlite-wal-checkpoint-on-close
description: Opening a WAL-mode SQLite file read-write — even just to COUNT rows — silently checkpoints and deletes -wal/-shm on last-connection close, so "measure without mutating" needs mode=ro or a copy.
metadata:
  type: reference
---

Verified 2026-10-08 on an app-owned SQLite file in WAL mode (original path deleted) (and it also quietly changed the file I was auditing):

- `sqlite3.connect(path)` defaults to read-write. Even if you only run `select count(*)`, when the **last** connection to a
  WAL database closes, SQLite performs a passive checkpoint and typically removes `-wal` / `-shm`.
  Consequence: a claim like "the `-wal` sidecar is 304 KB, not checkpointed" can evaporate between measuring and reporting,
  and the main `.db` file grows (4 KB → 147 KB) with no write from you.
- A genuinely read-only probe needs `sqlite3.connect("file:...?mode=ro", uri=True)` — but note the flip side:
  **`mode=ro` cannot run WAL recovery**, so if the `-shm` is missing/stale it may error rather than repair.
  The safest inspection is: copy `.db` + `-wal` + `-shm` together to TEMP, query the copy read-write, discard the copy.
- Hashing before/after is what proves it: two `certutil -hashfile … SHA256` on the copy and the archived original matched,
  which is how the mutation was caught instead of assumed.

**Why it matters:** evidence work often states sizes/row counts as if the file were static. If the act of measuring mutates
the artifact, the follow-up numbers no longer describe what was originally observed — and any "备份只拷 .db 会丢 WAL"
warning becomes untestable because the WAL is gone.

**How to apply:** before reporting anything derived from a live SQLite file (WAL size, uncheckpointed rows, mtime),
copy the whole sidecar set to TEMP and measure the copy; if you already opened it read-write, say so and re-state the
post-checkpoint numbers rather than the pre-checkpoint ones. Related: [[feedback-rigor-audit]].
