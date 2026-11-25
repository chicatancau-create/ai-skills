---
name: localstorage-data-shape-seeding
description: Seed browser localStorage so a page can be measured in its "has data" shape, and disclose that the seed is not an end-to-end user flow. Use when a page has only ever been captured/screenshot/metrics-measured while empty, when visual or accessibility acceptance needs a has-data state, when a tool must write keys like `code-canvas.<name>.v1:<scope>`, or when an in-page probe cannot read a scope, `schemaVersion` envelope, or `.data` value. Covers the data-source triage (server route vs app import channel vs direct write), the envelope level, real cross-reference ids, render-level assertions, key cleanup, and report wording.
---

# LocalStorage Data-Shape Seeding

## Overview

Some pages are only reachable in a populated state through user actions no measurement run performs, yet empty-state screenshots hide the real defects (row squeeze, overflow, hit-area, focus order). This skill pushes the UI into its has-data shape by writing the account-scoped localStorage keys the page already reads, then removes the evidence of having done so — and states plainly in the report that a seed is not an end-to-end chain.

## When to use / not use

- Use: a measurement cell needs "the page with N rows/cards in it"; the page's state lives in `localStorage`; the harness already runs against an isolated instance with a synthetic account.
- Do not use: as a substitute for testing the user's own write path. If a real UI flow or server endpoint exists, measure that instead and skip this skill.

## Step 0 — Data-source triage (run it every time, never reuse a past conclusion)

Answer three questions with grep/reads, and write the answers into the section's notes:

1. **Is there a server route that writes this data?** Grep the route table for the resource. If yes, seed via the API — that is a real chain and needs no disclaimer.
2. **Does the app ship its own import/seed channel?** Read that channel's validators. Import paths commonly reject (a) unregistered key names and (b) any key whose account suffix doesn't match the currently logged-in scope — and a freshly registered synthetic account's id is unknown before registration, so a preset file cannot satisfy it without forgery.
3. Only when both are closed: **write the storage directly**, and label it as such (Step 6).

Record which path was taken and why. The value of this skill is largely in that record.

## Step 1 — Copy the shape out of the code, do not invent it

Follow the read path and transcribe exactly:

- hook / initial state → the key builder (note the scope suffix format, e.g. `` `${base}:${scope ?? 'guest'}` ``);
- the `validate` / `normalize*` function — **anything it drops yields a page that renders zero rows while looking seeded**; mirror its required fields verbatim;
- the TS types for the payload; note whether the value is an array or a map keyed by id;
- whether dates are local date keys (`YYYY-MM-DD`) or ISO timestamps — these are often different from each other in the same app.

Populate the seed with deliberately awkward content (very long CJK title, very long filename, both a 1-item and a multi-item record, a legacy record missing a newer field). The point is to stress layout, not to look tidy.

## Step 2 — Writing from inside the page

Four rules, each of which has already cost a failed run:

1. **Navigate to the app origin and wait for the app before writing.** Harnesses typically open `about:blank` first.
2. **Use an absolute URL for every in-page fetch**: `fetch(location.origin + '/api/...')`. A bare `'/api/...'` throws `Failed to parse URL from /api/...` in a non-document or `about:blank` context.
3. **Fetch the scope, never assume it**: e.g. `GET /api/auth/me`, then read the account id (`data.id ?? id`). No scope → fail loudly; a seed written to `:guest` measures a page nobody looks at.
4. **Match the envelope level.** If the app writes `{ schemaVersion, savedAt, data }`, the value must live under `.data`. A probe (or a seed) that reads/writes the top level silently gets `null` — and the resulting report reads "the value persisted, location unknown" instead of a bug.

```js
localStorage.setItem(`${base}:${scope}`,
  JSON.stringify({ schemaVersion: 3, savedAt: new Date().toISOString(), data: payload }))
```

Hard-code `schemaVersion` next to the app's own constant only if the tool asserts the app still exports that version; otherwise read it from the app module. After writing, reload the page (state is read at mount, not reactively).

## Step 3 — Cross-reference fields must hold real ids

Any field the UI resolves through a catalogue (`titles[refId] ?? refId`) will render the raw id when the id is synthetic — the measurement then captures the seed's shape, not the product's. Fetch the live catalogue and map `contentId || id || lessonId`, then:

- **filter to non-empty strings and assert the values themselves.** `refs.length >= 3` has passed with `[null, null, null]`, which keyed a map on the string `"null"` and produced 0 rows;
- if fewer real ids than records are available, fall back to synthetic ids **and record the fallback in the report** (`usedRealRefs: false`).

## Step 4 — Assert the seed rendered, not that it was written

Per measured page/viewport, at minimum:

- landed on the intended page (page marker true);
- **no empty-state element** (`.empty-state` etc. absent);
- **row / card count > 0** — this is the gate that catches silent seed failure;
- detail panel / expanded branch actually opened, if that's the state under measurement;
- a shape-sanity judge, because "zero horizontal overflow" is also achievable by crushing a text column to one character per line: measure the key content column and require e.g. `width >= 120px` and `>= 3 chars/line` (CJK ≈ 1em).

## Step 5 — Clean up what you wrote

In `finally`, recompute the same scope and delete exactly the keys you wrote (derive both lists from one object so they can't diverge), and assert the removed count equals the written count:

```js
for (const base of Object.keys(payload)) if (localStorage.getItem(`${base}:${scope}`) !== null) localStorage.removeItem(`${base}:${scope}`)
```

Browser profiles and user-data dirs are commonly reused across sections of a run; a leftover key silently changes what the next section measures. Deleting by your own key list only — never by scanning and clearing `localStorage` — keeps real state intact.

## Step 6 — Disclose it in the report

Put a `seedMethod` string next to the numbers, and the limitation next to any claim that consumes them. Working wording, adapted per project:

> Seed method: in-page `/api/auth/me` → write N account-scoped localStorage keys in the app's own envelope → full reload. Not entered through the UI; this is not a user-reachable flow.
> This measures the has-data shape only; it does not claim the app produced this data, and it must not be cited as an end-to-end chain.

Do the seeding against an isolated instance, isolated data dir, and a synthetic account. Never write into a real runtime data dir or a profile the user signs in with.

## Failure modes seen in practice

| Symptom | Cause | Fix |
| --- | --- | --- |
| `Failed to parse URL from /api/...` | relative fetch on `about:blank` | navigate to origin first; absolute URL |
| Probe says value is `null` though the app persisted it | read top level instead of `.data` | match the envelope level |
| Page not empty, but 0 rows, and "everything is fine" flags green | ids silently `null`; map keyed on `"null"` | assert row count > 0 and the id values themselves |
| Overflow 0 but the column is unreadable | judge only checked overflow | add a key-column width / chars-per-line gate |
| A later section measures strange state | seeded keys left behind | delete-in-finally + assert removed count |
