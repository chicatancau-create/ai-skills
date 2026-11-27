# Template Resources

## Reusable template kinds

Brand, Style, Layout, and Deck are independent kinds, not stages of one inheritance hierarchy — each owns a different segment.

| Kind | Owns | Does not own | Discovery index |
|---|---|---|---|
| [`brands/`](./brands/) | Identity: color, typography, logo, voice, icon style | Page structure or SVG roster | [`brands_index.json`](./brands/brands_index.json) |
| [`styles/`](./styles/) | Direction/method: communication method, visual language, composition rhythm, information-expression defaults | Official identity, current-project application, structure, or roster | [`styles_index.json`](./styles/styles_index.json) |
| [`layouts/`](./layouts/) | Brand-neutral structure: canvas, Master/Layout graph, page types, slots, SVG roster | Identity or a recurring application | [`layouts_index.json`](./layouts/layouts_index.json) |
| [`decks/`](./decks/) | A recurring presentation family: application context + integrated identity + structure | — | [`decks_index.json`](./decks/decks_index.json) |

PowerPoint package objects are compilation targets, not kinds: Theme values and identity assets project from resolved identity rules (Brand, Deck, or the current project); Layout rules project into Master/Layout/Placeholder topology, semantic text roles, and spatial behavior; Deck combines both with descriptive application context and actual prototypes; Style guides method and expression without creating a package object or overriding resolved identity. Downstream planning decides which prototypes and content to use and records the exporter values, so one compiled Master may hold both structural geometry and brand visuals under separately owned rules.

New workspaces enter [`Create Template`](../workflows/create-template.md), which dispatches exactly one child ([`Create Brand`](../workflows/create-template/create-brand.md), [`Create Style`](../workflows/create-template/create-style.md), [`Create Layout`](../workflows/create-template/create-layout.md), [`Create Deck`](../workflows/create-template/create-deck.md)). Selection, mode defaults, preselection, `library` / `explicit` labels, cardinality, and installation are owned by [`routing.md`](../workflows/routing.md) §7 and [`apply-template-workspace`](../workflows/stages/apply-template-workspace.md).

## Orthogonal contracts

| Axis | Values | Meaning |
|---|---|---|
| Template kind | `brand` / `style` / `layout` / `deck` | Which reusable contract the package owns |
| Selection source | `library` / `explicit` | Discovery provenance only (index-derived root vs exact unregistered root); no semantic effect |
| Internal creation strategy | `standard` / `fidelity` / `mirror` | AI-derived Create Layout/Deck implementation (author a compact or broad roster, or materialize validated source facts); persisted for tools, never a user choice |
| Internal application plan | `template_reuse_scope` plus optional `template_adherence` | Strategist-derived literal, structural, or style-only use and strict/adaptive exporter behavior |
| PPTX structure | `flat` / `structured` | Plans using template structure compile declared Masters and Layouts; Style-only, style-scope, brand-only, and free design stay Slide-local; a Style beside Layout/Deck never changes the structure plan |

Never use these axes as synonyms or expose them as a mode matrix; a mirror-created deck is an ordinary reusable `deck` and forces no future page count or order.

## Workspace contract

```text
<template_workspace>/
├── templates/     # the Design Spec (naming below); optional Layout/Deck SVGs and native_payloads.json.gz
├── images/        # optional bitmaps; SVG href ../images/<name>
├── icons/imported/   # optional imported vectors, one canonical copy; data-icon="imported/<name>"
└── exports/       # optional review evidence; never a template input
```

