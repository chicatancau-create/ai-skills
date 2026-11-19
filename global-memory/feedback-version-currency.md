---
name: feedback-version-currency
description: Tech-version policy the user set: keep only 主流 + 最新 (drop EOL entirely), verify against official pages with a date stamp, never fabricate patch numbers, and fix course-era records by annotation not rewriting
metadata:
  type: feedback
---

For any version/technology statement in this vault:

- **Two columns only — 主流版本 and 最新版本.** Anything EOL/obsolete is deleted from the comparison, not footnoted (CentOS, JDK 8, Python 3.8, MySQL 5.7/8.0, Oracle 23ai 及更早, Spring Cloud Netflix, Vue 2, Bootstrap 3/4, HTTP/1.1, .NET Framework, Docker ≤28). Not-yet-GA releases (e.g. Maven 4 RC) are not "latest" either.
- **Verify on the official page in-session and record the check date** (e.g. "2026-09-19 联网核实"). Do not state versions from memory, and do not invent small-version numbers — where unverified, write 以官网为准.
- Prefer 本机实测 from 进度追踪 §2 for "latest installed", but flag when the local release sits on an EOL line (current example: MySQL 8.0.45 → upgrade direction 8.4 LTS).
- **Evidence layer is immutable.** The user explicitly chose "加时效横幅 + README" over rewriting `视频转写/` ASR transcripts or course-era 转写提炼. Corrections to outdated commands/语法 go into the volume header's 「版本时效（2026）」 note and the 技术版本对照表, leaving the original record intact.
- Watch for release-line renames that make old knowledge wrong (Oracle's line is now "AI Database 26ai"; MySQL moved to LTS/Innovation; Docker majors move fast).

**Why:** the user said "以Out的版本直接剔除出去，我不需要淘汰的技术" and asked for revision "对照官方的最新技术文稿" — they want the vault to say what to use *now*, with a traceable basis.

**How to apply:** whenever a version number is written or reviewed here, cite the official source page and date; when asked to "update to latest", update the knowledge/reference layer and annotate — never overwrite the evidence layer.

Related: [[feedback-rigor-audit]], [[reference-out-of-vault-resources]]
