---
name: read-chat-session-limits
description: mcp__builtin__read_chat_session returns a small bounded snapshot that cannot be paged back, so verifying claims from an older turn requires artifacts on disk, not more reads
metadata:
  type: reference
---

`read_chat_session` (builtin MCP) is **bounded and forward-only**. Measured 2026-09-24 on session
`54dc12ce-c69c-4a31-a0c6-309024312398`:

- `turnLimit: 20` still returned ~10 messages, and `includeToolOutputs: true` only filled in the
  **most recent completed turn** — earlier turns came back with `tools: []`.
- `hasMoreBefore: true` persisted; the schema has **no offset/cursor/page param**, so older turns are
  simply unreachable. Repeated calls with bigger budgets return the same window.
- Failed assistant turns appear as `status: "failed"` with empty text (the source session had four
  aborted "你创建一个登录页" turns before the one that ran) — so a missing turn is not evidence nothing happened.

**But older turns are on disk — read the transcript, don't give up.** Full history lives at
`C:\Users\Admin\.qoder\projects\<cwd-slug>\<sessionId>.jsonl` (one JSON object per line; `message.content`
holds `text` / `tool_use` / `tool_result` blocks; 1446 lines / 2.7 MB for one long session). Dump it to a
UTF-8 file with Python and read that — **printing Chinese to this Bash console mojibakes it through GBK**, so
`print()` is useless for verification. This recovered every claimed pitfall of the 2026-09-23 skill-install
session (self-nested 23-level copy, `WinError 145`, ghost `payload` skill) that `read_chat_session` could not show.

**How to apply:** when asked to "核实过程、用户纠正、失败原因" from a referenced session, expect the tool to
show only the last turn. Then read that session's `.jsonl`, and fall back to **durable artifacts**: the
harness/output scripts the turn wrote, screenshots, `git log --oneline` in any nested repo, and this memory
system. Then state explicitly which claims are code-verified vs. only present in the request text.

Specifically for skill-authoring sessions: a recommendation JSON handed to you may quote numbers that never
appear in any readable transcript (e.g. a "2951→1456" scroll-drift figure with zero hits in the files).
Do not transcribe such figures into the Skill — surface them as unverified and ask. See
[[feedback-no-unverified-cause-claims]].

Related: [[skill-placement-convention]], [[inapp-browser-verification]]
