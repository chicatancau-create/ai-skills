---
name: skill-placement-convention
description: Where newly authored Skills must live on this machine — D:\QoderToolkit (Qoder's own folder) with a per-skill junction into ~/.qoder/skills, not the shared D:\Skills library.
metadata:
  type: reference
---

Newly authored Skills go to `D:\QoderToolkit\<skill-name>\` (the user calls this folder "你专门的").
Registration = a **per-skill junction** `C:\Users\Admin\.qoder\skills\<skill-name>` → `D:\QoderToolkit\<skill-name>`,
so there is exactly one real copy.

**The link is not writable-through — build in this order** (proved 2026-09-23, corrected against what this
file used to claim):

1. `skill_manage` `create` while `~\.qoder\skills\<name>` does **not** exist. It writes a real dir there.
   Pre-creating the junction instead makes `create` fail with `SKILL_PATH_INVALID` — it will not traverse
   a link out of its allowed root.
2. Copy `SKILL.md` into `D:\QoderToolkit\<name>\`, `md5sum` both sides, only then delete the `.qoder` copy.
3. `rmdir` the emptied `.qoder\<name>`, then add the junction (`cmd //c rmdir` removes the link only; never
   `rm -r` a junction). Reading back through the link is the confirmation step.
4. Additively register the skill in `D:\QoderToolkit\README.md` (tree line + a bullet in 自建技能).

Do **not** add new skills to `D:\Skills` — that is the user's shared multi-agent library
(`dws`, `fs-*`, `vision-tool`, plus the `qoder-toolkit` entry shim), reached by every agent through
junctions at `~\.claude\skills`, `~\.agents\skills`, `~\.config\opencode\skills`. Qoder also scans those,
so a folder dropped in `D:\Skills` becomes visible to Qoder too.

Facts that cost a wrong turn each:

- **`skill_manage` can only write `SKILL.md`.** Schema (read 2026-09-24) is exactly
  `{action: create|patch|edit|delete, name, content, old_string, new_string}` — `content` is the whole
  SKILL.md, so there is **no way to bundle `scripts/`, `references/` or `assets/`** through it. A skill that
  genuinely needs helper files has to be shipped as inline snippets in SKILL.md, or the files written by
  other tools (which a skill-authoring session will usually forbid). Assume SKILL.md-only when planning.
  Also: `create` never overwrites an existing skill, `patch` requires exactly one match, `edit` keeps a
  backup, and built-in/plugin skills cannot be touched.
- **In a Skill-authoring session `skill_manage` is bound to exactly one skill name.** Measured 2026-09-24:
  `create`/`patch` for any *other* name returns bare `SKILL_TARGET_MISMATCH`, and `delete` is refused unconditionally.
  **Re-measured 2026-09-24 (22:5x), so the older "two roots hold a duplicate" explanation does not hold up:** with
  exactly one plain real dir at `~\.qoder\skills\<name>` (junction dropped, D: copy moved away, no second copy
  anywhere) `delete` still returned `SKILL_TARGET_MISMATCH`. Deleting a skill is therefore **not possible from an
  authoring session** — do it from the app UI or an ordinary chat session, and if you have to unwind a
  half-migration, restore the layout the ledger describes and verify by reading `SKILL.md` through the link.
  The guard lives in app.asar (`manage()` next to `SKILL_CONFIRMATION_REQUIRED`/`SKILL_HASH_CHANGED`) and compares
  `e.name !== r.skillName` against the evolution-session record — i.e. **the name in the recommendation JSON is a
  hard constraint, only the content is free**. So never promise "same content, different name"; if the intended
  name is taken or would collide, write the agreed content under the bound name and disambiguate in `description`
  + 适用边界 instead. Re-check `ls ~/.qoder/skills` right before writing — concurrent sessions are actively adding
  near-duplicate skills (2026-09-24: a same-topic skill appeared mid-session).
- **`patch`/`edit` return `SKILL_PATH_INVALID` when the target dir is a Junction.** Another session migrating a
  skill to `D:\QoderToolkit\<name>` + junction mid-task is enough; `skill_manage` will not traverse a link out of
  its root. Diagnose with `Get-ChildItem 'C:\Users\Admin\.qoder\skills' | Select Name,LinkType,Target`
  (`os.path.islink()` reads False on a junction, so Python alone will misreport it as a plain dir).
- **`create` failing with bare `SKILL_OPERATION_FAILED` (no app-log trace) = your YAML, not the disk.**
  Measured 2026-09-24 creating `install-github-skill-on-windows-qoder`: the first attempt was rejected because
  the one-line `description` contained an ASCII colon followed by a space (`核心顺序: 实测…`), which breaks a
  YAML plain scalar; nothing was written and `%APPDATA%\com.qoder.app.stable\logs\<run>\main.log` had **no**
  corresponding entry (unlike plugin-install failures, which do log a `stage`/`errorCode`). Retry with full-width
  `：` or a dash, and always grep the current run log before blaming the app's write path.
  Second variant measured the same day creating `verify-page-in-headless-edge`: a space followed by `#` inside
  the plain scalar (`…必须走 #PROBE 节点…`) is a YAML comment start and gets rejected the same bare way.
  Safest is to wrap the whole `description` in double quotes — that neutralizes both `: ` and ` #`; then
  verify it came back as one line of the expected length rather than assuming.

  Companion code measured 2026-09-24 (a later `create` that was since deleted): frontmatter that has
  `name` but **no `description`** is rejected as bare `SKILL_DOCUMENT_INVALID` — write both fields on the
  first attempt; `create` is atomic, so a rejection leaves nothing on disk (confirm with `ls ~/.qoder/skills`).
- **Windows deep-path / junction deletion facts** (measured 2026-09-24 on Python 3.14.2, preserved here after the
  `install-github-skill-on-windows-qoder` skill that carried them was folded away and deleted):
  - Plain `os.makedirs` dies at nesting level 8 (path 271 chars) with `WinError 3` — a self-nested copy can be
    built only halfway, so a bad copy can leave a tree no plain call can finish removing.
  - Plain `shutil.rmtree` on such a tree raises **`WinError 145` (directory not empty)** and has already eaten
    part of it; `shutil.rmtree('\\' + '\\' + '?' + '\\' + abspath)` removes it in one go. Build that prefix with
    `chr(92)` in snippets — backslash literals get mangled on the way into files.
  - Before any recursive delete, `os.path.isjunction(p)` first and drop links with `os.rmdir` only. On this
    box's 3.14 `shutil.rmtree` did *not* follow a junction into its target, but that is version-dependent — never
    rely on it. Order: `rmdir` the link, then `rmtree` the entity.
  - Copy guard that earns its keep: `assert not os.path.abspath(dst).startswith(src + os.sep) and dst != src`
    before `copytree`, plus a source-vs-destination file count afterwards. Wrong target arithmetic is how a skill
    gets copied inside itself.
  - "Installed but the skill list doesn't show it": each root lists **only its direct children**, and a real dir
    sitting outside a scanned root is invisible. Confirm by comparing against the session's available-skills
    list, never by `ls` alone.
- **Qoder plugin-upload failure route** (the two diagnosis skills that documented it were deleted by a
  concurrent session on 2026-09-24; these are what survived): grep
  `%APPDATA%\com.qoder.app.stable\logs\<run-id>\main.log` for `"stage":"...","errorCode":"..."` and count across
  run stamps. Measured here: `publish` + `EXTENSION_INSTALL_WRITE_FAILED` 18x and
  `package-extract` + `EXTENSION_PACKAGE_TOO_MANY_FILES` 1x. Three different archive layouts failing at the same
  stage with the same code means it is the app, not the package; prove it by renaming a same-bytes `.tmp` over
  `~/.qoder/plugins/installed_plugins_v2.json` — if the rename succeeds nothing holds the file locked, so the fix
  is a full app restart, not another repack. That registry is itself written tmp+rename, so the
  `installed_plugins_v2.json.<uuid>.tmp` litter is failed writes: move it aside, never `rmtree` that directory.
  A rejected 12,994-file package is the only measured data point; the actual file-count threshold is **not**
  printed in the log, so don't state a number.
- **The junction step often gets skipped.** Checked 2026-09-24: `verify-app-security-claims` had been left as
  a plain real dir by `skill_manage`; it has since been migrated (moved to `D:\QoderToolkit\<name>` + junction
  re-attached). Re-check with
  `Get-ChildItem 'C:\Users\Admin\.qoder\skills' | Select Name,LinkType,Target` before claiming where a skill
  lives. Migrating work **another** session left in place still needs the user's ask first; migrating a skill
  this session just created is fine.
- **One ledger only**: registration goes into `D:\QoderToolkit\README.md` (tree line + a bullet in 自建技能).
  A separate `REGISTRY.md` was created once on 2026-09-24 and deleted for the same reason — two ledgers drift.
- `skill_manage` (create/edit/patch) always targets `C:\Users\Admin\.qoder\skills`, which is a **real
  directory**, not a junction to `D:\Skills`. Its `delete` refuses with `SKILL_TARGET_MISMATCH` when the
  same skill name exists under two roots — so never leave a second copy behind.
- **After a skill is migrated to a junction, `skill_manage` can no longer touch it at all.** Measured
  2026-09-25: `patch` on `headless-cdp-visual-acceptance`, `patch` on `verify-app-security-claims`, and
  `delete` on `verify-page-in-headless-edge` all returned bare `SKILL_PATH_INVALID` (while `old_string` was
  confirmed present by `grep -c` = 1, so it is the link, not the content). Consequences to state up front
  when planning any edit to an already-migrated skill: it needs direct file writes to
  `D:\QoderToolkit\<name>\SKILL.md` **plus user authorization**, since the whole point of `skill_manage` is
  its validation; and deleting means `cmd //c rmdir` the link + send the folder to the Recycle Bin
  (`Microsoft.VisualBasic.FileIO.FileSystem::DeleteDirectory(...,'SendToRecycleBin')`) — take a per-file
  backup with `md5sum` first, because nothing but the Trash/backup is left. Merging two skills this way also
  means re-pointing every inbound reference: grep the name across both scan roots, `D:\QoderToolkit` and
  `D:\Skills`, and expect the ledger (`README.md` tree line + bullet + 家族路由表) to name it too.
- **`SKILL_TARGET_MISMATCH` is not limited to `delete`/duplicates, and is not always your fault.** Measured
  2026-09-24 in a skill-authoring session: `edit`, a zero-diff `patch` (identical old/new string) and even
  `create` of a name that exists nowhere all returned bare `SKILL_TARGET_MISMATCH`, while the target skill sat
  untouched as a single plain dir in `~\.qoder\skills` (hash stable, no second copy under any root) and a
  parallel session successfully created a skill minutes earlier. No app-log trace, no offset param, and
  `session-env/<id>/` had no root override — **root cause unresolved**. Triage before rewriting content:
  (1) no-op `patch` on the target, (2) `create` a throwaway name, (3) re-list every root for duplicates. If
  both refusals persist with no duplicate, it is tool/session-side — retry in a fresh session rather than
  falling back to Write/Bash on the skills dir.
  **Follow-up same day**: the failed session never wrote anything (target file stayed byte-identical), and a
  parallel session later migrated that skill to `D:\QoderToolkit\<name>` + junction. So a mid-flight migration by
  another session is a plausible trigger — check `LinkType` on the entry before assuming content caused it, but
  don't expect a confirmed root cause.
- Skills stored under `D:\QoderToolkit` are visible **only to Qoder** (nothing junctions that folder into the
  shared library). Say so rather than assuming other agents will see them.
- Making the junction: `fsutil reparsepoint query` on a working one shows `0xa0000003`(装入点), so it must be a
  **junction**, not a symlink. What works from this Bash (re-verified 2026-09-23, two junctions created):
  `powershell -NoProfile -Command "New-Item -ItemType Junction -Path '<link>' -Target '<target>' | Out-Null"`,
  then confirm with `Get-ChildItem` showing `LinkType=Junction` + `Target`, and by reading `SKILL.md` through the link.
  Failing routes to skip: calling `cmd //c mklink /J ...` inline gives a mangled path-syntax error, and an inline
  `node -e` printed success while creating nothing (a scratch `.mjs` + `fs.symlinkSync(t, l, 'junction')` does work,
  it's just more steps than the PowerShell one-liner). Removing a link is `cmd //c rmdir "<link>"` — contents-safe.
- **`skill_manage` 也穿不过 junction 去改。** 2026-09-24 实测: 技能迁进 `D:\QoderToolkit` 并回挂 junction 之后,
  `patch` 直接返回 `SKILL_PATH_INVALID` —— 和 `create` 一样不肯越出允许根。要改已归案的自建技能, 只能走
  **摘→改→回写→重挂** 四步: `cmd //c rmdir <link>` 摘链接 → 把实体 `copytree` 成 `.qoder\skills\<name>` 真实目录
  (比对 SKILL.md 字节) → `skill_manage patch` → 把改后的 SKILL.md 拷回实体并比对 → 逐文件删除+`os.rmdir` 清掉
  真实目录(**先断言它不是 junction**, 否则递归删会穿透删实体) → 重新 `mklink /J` → 穿链接读回比对。
- **`SKILL_PATCH_NOT_UNIQUE` 大多是「压根没匹配上」，不是「匹配多了」。** 2026-09-24 两轮实测：
  (1) 我的 `old_string` 用了全角逗号/括号而文件里是半角 —— 零匹配却报 NOT_UNIQUE，换回半角后**同一条 patch 立刻成功**；
  (2) 另一条在 junction 态下报 NOT_UNIQUE，摘成真实目录后成功（那次锚点本身是对的）。
  排查顺序固定为：先用 Python 数 `old_string` 在文件里的**出现次数**（0 次＝标点/空格抄错了），
  再查 `LinkType` 是不是 junction，最后才怀疑工具口径。别急着重写内容或换锚点。
- **交付物别只留在工作区。** `E:\AIrenwu\qoder-toolkit-landing\`(落地页 + 登录页)在 2026-09-24 同一天的两轮
  对话之间整个消失, 不是我删的(我只删过三张 png) —— 并发会话会按自己的范围清理工作区。要长期留的东西
  落到集合包或明确告知用户位置, 并优先用「重跑取证回路可再生」的形态存在。
- `D:\QoderToolkit` is shared with live concurrent sessions and is partly automation-managed: make only
  **additive** edits to `README.md`, never rewrite existing lines. `ppt-master\` has an integrity gate
  (content/rename/BOM/CRLF changes fail), `web-kimi\` is a frozen snapshot.
- `D:\QoderToolkit\README.md` is LF-only, no BOM. Per this user's general rule, write text files with the
  Edit/Write tools or Python utf-8, not PowerShell. See [[windows-config-json-encoding]].

- **登记键是目录名，不是 frontmatter 的 `name`**（2026-10-11 探针实测）：建 `~\.qoder\skills\probe-shape-test\SKILL.md`
  且 `name: spider-king-probe`，可用技能列表里出现的是 **`probe-shape-test`**；`argument-hint`、`compatibility`
  这类 Claude Code 风格的多余 frontmatter 字段**不影响识别**。⇒ 想让某技能在列表里叫什么，就改目录名；
  第三方包若 `name` 与目录名不一致（例：`trace` 包内 `name: spider-king`），列表里只会看到目录名。
- **例外：用户明确要求"全机 AI 都能用"时，实体放 `D:\Skills`**（2026-10-11 授权安装 `reverse-trace` /
  `reverse-wechat-miniapp` 两个第三方逆向技能）。判据：`~\.agents\skills` 是 junction → `D:\Skills`，
  Qoder 也扫它，所以**放进 `D:\Skills` 就不要再在 `~\.qoder\skills` 建联接**（同名两条会被列成重复项）。
  标注类别的做法=目录名加前缀（`reverse-`）+ `description` 开头加 `【逆向工具·仅授权目标】`，
  并在包内写 `PROVENANCE.md`（无 LICENSE 的第三方包必写）。
- **改第三方 SKILL.md 的 frontmatter 要按文件自己的换行符来**：`trace` 的 SKILL.md **源包就是全 CRLF**（作者用
  Windows 编辑器写的），"顺手规范化"会污染字节比对。字符串手术插标记时留意引号标量——
  一次把 `description: "原文"` 改成 `description: "标记"原文"` 直接把 YAML 改坏，必须用 PyYAML 真解析复核。

Related: [[qoder-toolkit]], [[feedback-vault-engineering-rules]]
