Template `page_layouts` records authoring-input provenance, `pptx_masters` / `pptx_layouts` own unique reusable definitions, and `page_pptx_layouts` owns page assignment. Strict preserves its Master/Layout/slot contract; adaptive retains its Master and may use a new Layout key only when fixed Layout atoms or slot topology/bounds change. `standard` / `fidelity` inspect complete source structure evidence and author compact or broader useful Slide rosters. `mirror` materializes source Slides and their reachable identity graph without semantic synthesis or gap filling, while completing inherited context and mechanically expanding fixed-layer group wrappers into direct atoms.

Legacy structured/template contracts using `baseline`, `template`, `preserve`, `layout_strategy`, `data-pptx-layout-kind`, `distilled`/`utility`, direct atomic placeholders, or incomplete root Master identity must be replaced by a new workspace created through [`create-template`](../workflows/create-template.md). Generate new structured SVG pages from that workspace; do not upgrade the existing PPTX/SVG in place. Explicit flat free-design/Brand-only/Style-only projects intentionally omit root Master identity.

`pptx_to_svg.py` also writes a canonical `animations.json` whose default
transition is `none`. Page transitions produced by the current native
transition registry are read back with their effective options, exact duration,
automatic advance, and optional embedded WAV sound. Source transition XML
outside that closed writer/read-back contract remains diagnosed rather than
being normalized by guesswork.
Finite object-animation rows from the current writer are also projected when
their registry effect, effective options, pane order, trigger, exact duration,
relative delay, and top-level SVG group target all read back exactly. Advanced
timing, build/media trees, duration-less native rows, and unmapped targets stay
diagnosed/direct-preserve.

`pptx_to_svg.py` annotates verified text-grid tables and conservative chart data with `data-pptx-replace-with` beside the visible SVG fallback and places the payload in `<metadata type="application/json">`; the parent claim selects the chart or table schema. Imported table/chart groups under this contract carry `data-pptx-import-source="pptx"`, whether active or fallback-only. Table import covers exact physical row/grid topology, canonical rectangular merges, safe solid/no-fill per-side borders, plain multi-paragraph cells, and a closed run-rich paragraph schema. Each rich run requires `text` and may use only `bold`, `italic`, `underline`, `strike`, `color`, `font_size`, one `font_family`, `lang`, and `alt_lang`. A merge must use the exact `rowSpan` / `gridSpan` / `hMerge` / `vMerge` physical topology with empty merge slaves. Presentation-only source run XML without a non-empty `effectLst` / `effectDag` normalizes; a table-cell run effect disables native replacement and adds a blocking effect diagnostic. Relationship-bearing text, extensions, line breaks, fields, tabs, bullets, broken text topology, unsafe border XML, non-solid fills, and other merge encodings remain fallback-only. For table style `{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}`, the normalized SVG fallback resolves `wholeTbl`, `firstRow`, horizontal banding, theme colors/fonts, and direct cell/run overrides; other built-in/custom style families are not implied.

