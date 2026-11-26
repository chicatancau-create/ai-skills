---
name: codeweave-visual-rebuild-rerun
description: 'Rebuild-triggered re-measurement METHODOLOGY (archive) for CodeWeave (G:\CodeWeave) visual-acceptance evidence: isolate each batch (VC_OUT / VC_DATA_TAG / VC_SHOTS / VC_REPORT), cross-compare batches column-by-column over the 16 judgment columns and 21 key readings with NaN-safe defaults, apply the fixed reading standards and the batch acceptance checklist, then keep the batch ledger / terminal pointers. The original concrete pipeline (workspace/app runners, tools/visual, M6 ledger, CodeWeave-recovery) was removed in the 2026-11-06 refactor and no longer exists under G:\CodeWeave (verified 2026-11-26); reuse the method after re-locating or rebuilding runners on the current layout. Trigger words: 重测 / 重跑取证 / 换构建 / 批次账 / 终版批次 / 跨批对比 / 读数判据 / 批次验收. Not for vault content edits or publishing.'
---

# Rebuild-triggered §5.4 evidence re-measurement (CodeWeave)

## Overview

The project's own rule (M6 §16.4, restated at §18.3): once the shipped `app/dist` hash moves, every matrix and states number in the docs becomes "a reading of the previous build" and must be re-taken on the new build. A batch is only worth its numbers if it ran on an isolated evidence directory, with the tools frozen, on an idle machine, and if the cross-batch comparison is done column by column. This skill is that pipeline, plus the reading standards that decide which differences count.

> **路径时效性（2026-11-26 复核确认）**：本技能的具体机器路径（`G:\CodeWeave\workspace\app`、`tools\visual\*.mjs`、`docs\M6-整体验收-执行记录.md`、`G:\CodeWeave-recovery\`）反映 2026-11-06 项目重构前的旧布局。当前 `G:\CodeWeave` 顶层为 `网页端/应用端/移动端/工作区/工程文件`；经全树 glob 确认 `visual-check.mjs / visual-states.mjs / paths.mjs / compare-*.mjs` 与 `M6-*.md` 在 `G:\CodeWeave` 已**整体不存在**，`G:\CodeWeave-recovery` 亦不存在——原 visual 取证流水线已随重构移除。**本技能现为方法论档案**：可复用的是批次隔离、NaN 安全的逐列跨批对比、读数判据、批次验收清单这套方法；下文具体路径与脚本名仅作历史示例，套用前必须按当前布局重新定位或重建运行器与证据目录，勿直接照搬旧路径。

## When to use / not use

- Use: `npm run build` (or the §11.1 gate run) printed a changed `sha256_12` for `index-*.css` / `index-*.js`; or you must prove a fix did not move the numbers; or a batch got voided and needs a clean re-take.
- Do not use: for `baseline-check.mjs` (pre-refactor old build, its own ports and `BASELINE_*` vars), for vault/content edits, or to justify publishing — publishing needs the user present.
- Adjacent skills, do not reinvent them here: adding or changing a *section / injected probe* in the two runners is `visual-tool-add-section`; putting a page into its has-data shape is `localstorage-data-shape-seeding`. This skill covers only the re-measure-after-a-rebuild line and the bookkeeping that follows.
- Everything here was machine-specific to the pre-refactor `G:\CodeWeave\workspace` + `G:\CodeWeave-recovery` layout, which no longer exists (see the timeliness note above). Treat the concrete paths as historical examples; confirm the current runner/evidence locations before step 0, or rebuild them.

## Step 0 — Prove the build moved, and name the new fingerprint

Run the §11.1 gates in `workspace/app` first (`typecheck`, `lint`, `test`, `test:coverage`, `build`, `content:check`, `report:data-quality`; check exit codes one by one). From the `vite build` output record the new pair, e.g. `index-DEnBsoxj.css / f4a069a17744` + `index-BxuE09GZ.js / eecd812ae0d5`. That string is what the whole batch is keyed on — the runners also record it themselves as `cssFingerprintAtStart` / `builtFrom`, so a batch whose fingerprint does not match the build you just made is measuring something else.

## Step 1 — Freeze the tools before you run anything

Finish and commit every edit under `tools/visual/*.mjs` **before** the run. Both runners hash their own sources and print `toolChangedDuringRun`; true demotes the batch to a process artifact no matter how green it looks (this voided two ten-section batches on 2026-09-23: `ten79` all-green, `final81` bookkeeping). Same for the shared ruler files — `probes.mjs` and `layout-record.mjs` changes make old numbers non-comparable; if you must touch them, record their sha256 against both batches (§17.2 recipe).

## Step 2 — Isolate the batch (never write into the shared directory)

`tools/visual/paths.mjs` derives the evidence root from one variable:

```js
export const OUT = process.env.VC_OUT || join(dirname(REPO_ROOT), 'CodeWeave-recovery', 'tmp-m6-visual')
```

`VC_SHOTS` / `VC_REPORT` / `VC_DATA_DIR` / the browser profile all default to paths under `OUT`, so **one `VC_OUT` isolates a whole batch**. Pick a fresh tag (the batch number you are about to name):

```bash
cd G:/CodeWeave/workspace
export VC_OUT=G:/CodeWeave-recovery/tmp-m6-visual-<tag> VC_DATA_TAG=<tag>
```

Hard rules:

- Never let a re-run write into the shared `tmp-m6-visual\shots\` — it is shared by the matrix and the extra sections, and same-name files collide 1:1. `#87` lost it that way: 76 PNGs of the terminal batch were overwritten one by one, numbers kept from the old build, images from the new one.
- The full-matrix run does `rmSync` on its shots dir; it now prints `shotsClearedBeforeRun` first. With a private `VC_OUT` that number must be **0** — that field is your proof you isolated it.
- The recovery tree is outside Git and wipeable. The reports are the durable record only once their numbers are written into M6; the PNGs are disposable by design.

## Step 3 — Pre-flight without a browser

```bash
node tools/visual/visual-check.mjs --plan
node tools/visual/visual-states.mjs --plan
node tools/visual/visual-check.mjs --selftest    # 17 段模板，解析失败 0 段
node tools/visual/visual-states.mjs --selftest   # 14 段，明确打印「不写任何文件」
```

Treat `--selftest` as untrusted until you have read the dispatch line in the runner you are calling: the two runners were not symmetric, and `visual-states.mjs --selftest` used to fall through into a full write-to-disk batch (`#87`). Verify it writes nothing by counting PNGs and capturing report mtime before and after. Symmetry is now asserted in `visual-check.mjs`'s own comment block — check it still holds rather than trusting this sentence.

## Step 4 — Run the two lines on an idle machine

Kill the gates and any other agent first; LCP / INP / CLS on a busy machine are noise.

```bash
# line 1 — 60-cell matrix (10 pages x 6 viewports), ports 4273 / 9778
node tools/visual/visual-check.mjs
# line 2 — twelve sections, ports 4274 / 9779
node tools/visual/visual-states.mjs
```

- Sections are: `loading empty longtext tab views editorfont escwalk chdetail writeback axtree inpstress datashape` (`visual-states.mjs:54`). Single sections: `--only=escwalk,chdetail`.
- `VC_CACHE=cold` per-cell cold cache; a CLS number without a cache state is incomplete (§18 note: same cell can differ by an order of magnitude).
- `inpstress` is tuned by `VC_INP_ROUNDS` / `VC_INP_GAP`; the observer's `durationThreshold: 40` means sub-40ms interactions are never recorded, so `count` is not "number of interactions".
- Ports 4173 (user's own instance) and 9333 (Qoder debug) are never touched. `datashape` seeds localStorage — see the separate `localstorage-data-shape-seeding` skill, and keep its "seed is not an end-to-end chain" wording.
- Each batch is minutes, not hours (matrix 19:10→19:14, states 20:39→20:43 on 09-23). Re-running is cheap; skirting it is what rots the docs.

## Step 5 — Cross-batch compare, column by column

Both scripts live in `G:/CodeWeave-recovery/tmp-m6-visual/` (outside the repo). If the directory is gone, recreate the matrix one from the block below — the column list *is* the knowledge.

```bash
cd G:/CodeWeave-recovery
node tmp-m6-visual/compare-matrix-builds.mjs <oldReport.json> <newReport.json>
node tmp-m6-visual/compare-batches.mjs <oldStates.json> <newStates.json>
```

`compare-matrix-builds.mjs` aligns the 60 `summary` rows by `cell` and compares **16 judgment columns + 3 info columns**:

```js
// NaN is not equal to NaN: a bare Number() comparison fabricated 60 fake diffs.
const n = (v, dflt = 0) => (typeof v === 'number' && Number.isFinite(v) ? v
  : typeof v === 'string' && v !== '' ? v : dflt)
const JUDGE = {
  溢出: (c) => n(c.overflowPx),                小目标: (c) => n(c.smallTargets),
  不达标: (c) => n(c.contrastFailingCount),    对比未判定: (c) => n(c.contrastUndetermined),
  像素判不过: (c) => (c.pixelFailing ?? []).length,  像素未判定: (c) => (c.pixelUndetermined ?? []).length,
  取样条数: (c) => n(c.sampleCoverage?.count), 取样截断: (c) => n(c.sampleCoverage?.truncated ? 1 : 0),
  正文最差: (c) => n(c.contrastWorstBody?.ratio, '—'),
  规范CLS: (c) => n(c.cls?.subject),           原始CLS: (c) => n(c.cls?.raw),
  正文字号: (c) => n(c.bodyFontPx, '—'),       段落字号: (c) => n(c.para?.size, '—'),
  落点核对: (c) => n(c.how, '—'),              报错: (c) => n(c.error, '无'),
  console: (c) => n(c.consoleMsgs),
}
const INFO = { 文档高度: (c) => n(c.docScrollHeight), LCP元素: (c) => n(c.lcpElement, '—'), LCP毫秒: (c) => n(c.lcpMs) }
```

`compare-batches.mjs` covers the states line: 21 key readings (loading unblock ms + placeholder text/paint, tab four-page stop counts + zoom200 + no-ring total, views eight cells' overflow / small targets / worst contrast / pixel-failing, escwalk 17 closed flags, chdetail three region sizes, editorfont three computed sizes, empty four cells, longtext 16 overflows, writeback 11 step judgments + `realVaultTouched` + four bound-with-data readings + four tab walks, axtree `namelessTotal` + `h1MismatchPages`, build CSS fingerprint). Its console labels are hardcoded `81:` / `82:` regardless of which two files you pass — read them as "old" and "new".

Verified reference outcomes (reproduce these before trusting a re-created script):

- `report-matrix-terminal84.json` vs `tmp-m6-visual-audit85/report.json` → 4 diffs, all in 原始CLS (`workspace`/`modal-help` at 1440x900 and 768x1024); LCP moved in 49/60 cells within −52…+20 ms with elements identical; doc height 6039→6038 in two `@320` cells.
- `report-states-final82.json` vs `report-states-audit86.json`, and `audit86` vs `terminal96` → 21 readings, exactly 1 different: the build CSS fingerprint.

## Step 6 — Read the numbers by the fixed standards

- **LCP is never quoted per millisecond.** Compare magnitude and whether it crosses 2.5 s, plus whether the element changed. Same build, same ruler: 52 of 60 cells differed 4—12 ms across two batches.
- **The judgment columns are the ones that repeat bit-for-bit**; 原始 CLS is timing jitter over "which shifts landed in the 500 ms window after input". 规范 CLS is the gate.
- `lcpLoadMs` (after landing, before the screenshot) and `lcpMs` (after the screenshot) are different readings of different moments — the doc's "max 224 / 228 / 316 ms" is the former. `lcpElementLate` / `lcpSizeLate` / `lcpLateDeltaMs` exist **only under `cells[].metrics`**; `summary` has none of them (verified against `report-matrix` files). Any late-LCP question (#79) must go back to `cells`.
- **A modal row's CLS is not the dialog's.** `modal-settings` / `modal-help` share the same-document accumulation as the same-viewport `workspace` row down to 17 decimals — those two rows measure the shell startup segment, never "how much offset this dialog caused".
- `errors: []` is not a verdict. Read the per-section `sectionJudge`, and remember three findings are deliberately outside it (nameless `<main>`, the two 「全部」 dropdowns, two `h1` on three pages — parked as #77 for the user).
- INP sample counts are a side effect of the 40 ms gate; a one-order-of-magnitude count difference does not mean one build is faster.

## Step 7 — Batch acceptance checklist (all of it, or it is a process artifact)

`errors: []` · `sectionsSkipped: []` · `shotDupes: []` · `shotsWritten == shotsOnDisk` · `shotsMissing: []` · `shotsUnregistered: 0` · `shotsOverwritten: []` · `cssChangedDuringRun` / `jsChangedDuringRun` / `toolChangedDuringRun` all false · `builtFrom.changedDuringRun: false` · `landingUnverified: 0` · `cleanup.portsReleased: true` + `stillListening: []` · `content.servedBundleId` equals the current snapshot id · `colorProbe` silent (when it breaks the cell fails rather than lying) · console at the known baseline (2026-09-21: 6 lines, all resource 4xx — five `vault-progress` 409 `owner_unbound` by design plus favicon 404 #54; **only extra lines are a regression**, do not chase the 409s).

## Step 8 — Bookkeeping: ledger, pointers, prose

1. Append a row to the M6 §16.4 table: batch file, what it shows, and **why it is or is not the terminal batch** (build moved / tool changed mid-run / bookkeeping fix counts as a tool change / images overwritten). Superseded batches stay, they are not deleted.
2. Flip the §16.5 terminal pointers, and keep the sentence about what happened to the old batch's images.
3. Write the §18.x record: gates table with exit codes, the new fingerprint, the cross-batch comparison result, plus whatever the info columns happened to corroborate (e.g. `analytics@320` doc height 5313→3988 as evidence for #89).
4. Grep the docs for stale snapshot ids and 「当前…」 phrasing and annotate with a date — do not rewrite history. Numbers move every rebuild; a reader needs to know which build each quote belongs to.
5. Commit in the live root `G:\CodeWeave\workspace\.git` (the outer `G:\CodeWeave\.git` is frozen and ignores `/workspace/`).

## Pitfalls already paid for

- **NaN**: `Number(x) !== Number(y)` fabricated 60 diffs out of two identical batches. Use the `n()` helper above with an explicit default per column.
- **Wrong field tier**: late-LCP fields are not in `summary`; a null read there looks like "the effect disappeared in the new build".
- **Wrong attribution**: reading a modal row's CLS as the dialog's own.
- **`--selftest` asymmetry** (#87): a flag present in one runner and absent in the other silently ran a full batch into the shared dir. Read the dispatch code before typing a flag you did not write.
- **Editing tools mid-run**: the runner is the one that catches you, and it is not being helpful — it is voiding 20 minutes of work.
- **Quoting a doc number after a rebuild**: say which build it belongs to, or re-take it.

## Resources

> 下列均为 2026-11-06 重构前的历史路径，当前已不存在（2026-11-26 全树 glob 确认）；保留作方法论参照，套用前按当前布局重新定位或重建。

- Runners (historical): `G:\CodeWeave\workspace\tools\visual\{visual-check.mjs, visual-states.mjs, paths.mjs, probes.mjs, layout-record.mjs, browser.mjs, app-instance.mjs}`
- Comparators: `G:\CodeWeave-recovery\tmp-m6-visual\{compare-matrix-builds.mjs, compare-batches.mjs}` (recreate from Step 5 if lost)
- Evidence root: `G:\CodeWeave-recovery\tmp-m6-visual-<tag>\{report.json, shots\}` and `report-states-<tag>.json`
- Ledger and reading standards: `G:\CodeWeave\workspace\docs\M6-整体验收-执行记录.md` §16.4 / §16.5 / §17.10 / §18.3 / §18.4 / §18.6 / §18.8 / §18.11
