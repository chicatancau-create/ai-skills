python3 scripts/svg_quality_checker.py <template_workspace>/templates --template-mode --canonical-authoring
python3 scripts/mirror_template_materialize.py <import_workspace> <template_workspace>
python3 scripts/svg_to_pptx.py <import_workspace> --roundtrip
python3 scripts/template_preview_pptx.py <template_workspace>
```

Template import defaults to the canonical layered `svg/` backing tree and
creates compact `authoring-svg/` in the same transaction. Use
`--inheritance-mode both` only when a separate self-contained `svg-flat/`
verification tree plus `authoring-svg-flat/` is required. No derived narrative
digest is generated because `analysis/manifest.json` already owns those facts.

`pptx_template_import.py` creates the lightweight authoring bundle in the same
transaction as its immutable backing. `svg_authoring_view.py` remains the
standalone projection entry point for external SVG and migrations. Before the
transaction publishes, it also factors eligible non-semantic decoration into
`icons/imported/`. Recognized native shapes become one visible geometry carrier
plus at most one structured text body; recognized tables keep
one compact semantic JSON payload plus a preview cache. The projection removes
duplicate render geometry and import-only identity/payload attributes while
retaining text, images, stable ids, root Master/Layout markers, native-shape
intent, and document-local `data-pptx-source-ref` values. It also promotes a
common page font to the root and removes inherited presentation declarations
that merely repeat the root/group value.
Relative local image references are rewritten so the projected copy still
renders from its new location. The bundle's `authoring_summary.json` is the
model-readable current-file index; `authoring_manifest.json` records
source/authoring hashes and object paths for tools without duplicating opaque
payload and does not enter model context. Only unsupported, text-free,
schema-free source ornaments may become compact `native-restore` image proxies whose
hashed SVG previews live under `images/source-object-previews/`. Unchanged
proxies restore the original native PowerPoint objects; complete removal deletes
a Slide-local source object, while inherited-proxy removal and any proxy or
preview edit fail export. Imported
model-facing frames and safe
transform page coordinates use at most two decimals; immutable lossless SVGs
retain the original precision. In-place vector/picture extraction
refreshes the summary automatically; use `--refresh-summary` after other direct
IR edits. The full imported SVG remains unchanged as native-payload backing.
Template creation edits the IR and materializes validated `templates/*.svg`;
the layered IR directory itself is not a final template or direct release
export source. A complete-page flat IR may be selected with
`--roundtrip`: `authoring_roundtrip.py` reads `authoring-svg-flat/`, regenerates its
deterministic extraction baseline, restores unchanged refs from the immutable
layered backing, and sends the temporary result through preserve export while
leaving edited/deleted/new authoring content in place.

An imported round-trip workspace may optionally add root `page_plan.json` to
select, reorder, repeat, or omit source slides during export. The v1 shape is
minimal: top-level `schema: "ppt-master.roundtrip-page-plan.v1"` plus a
non-empty ordered `pages` array; every entry requires one-based
`source_slide` and may name a unique `authoring-svg-flat/` filename in `svg`.
A copied SVG is diffed against the baseline for its declared source slide.
Move a cross-page object with
`svg_authoring_view.py <authoring-dir> --adopt-object <from.svg>:<element-id>
--into <target.svg>` rather than pasting raw SVG. The helper rebuilds the copy
without source identity, inlines source-owned imported vectors, refuses source
proxies, resolves id collisions, and refreshes `authoring_summary.json`.
`notes/<svg-stem>.md` implicitly overrides notes for that output page; when it
