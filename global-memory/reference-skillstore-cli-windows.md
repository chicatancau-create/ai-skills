---
name: reference-skillstore-cli-windows
description: Installing skillstore.io packs on this box needs two workarounds — Node proxy env vars (raw.githubusercontent.com is reset without them) and a single -a agent target (both skill roots symlink to D:\Skills so its self-link guard misses).
metadata:
  type: reference
---

`npx skillstore add @<pack>` (skillstore v0.1.13) fails on this machine for **two independent reasons**. Fix both or it rolls back everything.

**1. `fetch failed` on every skill download.** Manifest comes from `skillstore.io` (reachable), skill zips come from
`raw.githubusercontent.com/aiskillstore/marketplace`, which is **connection-reset on a direct route** here
(curl → `000`, Node → `ENOENT fetch failed`). Clash Verge's mixed port is `127.0.0.1:7897` and the WinINET system
proxy is enabled, but **Node's global `fetch` ignores the Windows system proxy**. Node here is v24, so set:

```
set NODE_USE_ENV_PROXY=1
set HTTPS_PROXY=http://127.0.0.1:7897
set HTTP_PROXY=http://127.0.0.1:7897
```

Do not persist these as User env vars: if Clash is ever off, every Node HTTPS call starts failing.

**2. `Pack member readback failed` → full rollback.** `~\.agents\skills` and `~\.claude\skills` are **both symlinks to
`D:\Skills`** (see [[reference-skill-placement-convention]]). skillstore treats `.agents\skills` as the canonical store
*and* as the Codex target; `linkSkillToDirectory` compares those with lexical `resolve()`, so the `.claude\skills\<slug>`
string differs and it creates a symlink **onto itself** inside `D:\Skills`. Readback then hits
`ELOOP: too many symbolic links encountered, scandir`. Workaround: **target one agent only**, e.g. `-a codex`.
Because both roots share `D:\Skills`, the other agent sees the skills anyway — no second link is needed.

Working command:

```
set NODE_USE_ENV_PROXY=1 && set HTTPS_PROXY=http://127.0.0.1:7897 && set HTTP_PROXY=http://127.0.0.1:7897
npx --yes skillstore add @<pack> -a codex --overwrite
```

**Diagnosis notes.** The CLI prints only `ERROR Installation failed` and swallows the cause; it is in
`dist/commands/add.js` → `readbackPackInstall` in `dist/lib/pack-install-truth.js`, whose `catch {}` is silent.
`DEBUG=1` makes `plugin-logger` print the real error and stack. On failure the tool renames staged dirs to
`.<slug>.pack-backup-<guid>` and rolls back cleanly — verify with `find /d/Skills -iname '*pack-backup*'` and a
reparse-point scan, both should be 0.

**Symptom that the run really worked:** `skillstore list` shows the slugs, `D:\Skills\<slug>\SKILL.md` is a real file
(not a link), and the Qoder skill listing shows the names **without** a leading dot or `pack-backup` suffix.
