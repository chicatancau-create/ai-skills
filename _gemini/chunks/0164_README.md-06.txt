  --operation intersect \
  --source circle \
  --source card \
  --id overlap
```

The first source owns result paint and is the primary geometry for `subtract`.
Local and ancestor transforms are baked into SVG-root coordinates. Replace the
operands with every returned path at the root in the primary operand's z-order;
`fragment` returns multiple stable sibling paths. Operands may be supported
closed geometry or supported horizontal implicit-LTR direct `<text>` whose exact
OpenType weight/style can be resolved; repeat `--font-dir PATH` for additional
font roots. Text is shaped to glyph outlines before the operation, so the
result remains editable freeform geometry but is no longer editable text. See
[`references/native-shape-authoring.md`](../references/native-shape-authoring.md)
§6 for the closed operand and failure contract.

External-source migration and explicit picture normalization:

```bash
python3 scripts/extract_svg_assets.py <layered_svg_dir> --icons-dir <icons_dir> --icon-namespace imported --inplace --id-prefix layered
python3 scripts/extract_svg_assets.py <flat_svg_dir> --icons-dir <icons_dir> --icon-namespace imported --reuse-inventory <layered_inventory.json> --inplace --id-prefix flat
python3 scripts/extract_svg_pictures.py "<svg_file>" --select "<group_id>" --resource-root "<workspace>" --images-dir "<picture_assets_dir>" --inplace  # optional create-template normalization: one selected group -> one SVG picture
python3 scripts/svg_quality_checker.py <template_workspace>/templates --template-mode --canonical-authoring
python3 scripts/mirror_template_materialize.py <import_workspace> <template_workspace>  # Type A mirror only; destination owns no roster
```

PPTX template import and round-trip import run vector readability extraction in
their staging transaction before the first authoring bundle is published. The
manual extraction commands above are only for external SVG/migration input.

`extract_svg_assets.py` extracts only non-semantic decoration. Any subtree that
contains a semantic object, text, table, chart, relationship, or other
meaning-bearing authoring content stays inline. Each imported asset and its
placeholder declare `data-pptx-asset-role="decoration"`; the v2 inventory
records the same role, and round-trip/template consumers reject missing or
different roles. The extractor fingerprints each eligible subtree before
generated-ID namespacing. Process the layered authoring view first, then pass its inventory to
the flat view with `--reuse-inventory`; matching flat subtrees reference the
existing layered asset instead of creating a duplicate file. Only unmatched
flat-only vectors create new assets. Create-template stores these assets once in
`<workspace>/icons/imported/` and writes decoration-marked
`data-icon="imported/<name>"` references.
Inventories retain any `data-pptx-source-ref` values carried by the extracted
subtree, so re-inlining preserves authoring-manifest object identity.
Rerunning a namespaced pass against an already rewritten projection inventories
the existing references without progressively wrapping more parent geometry.

Post-processing and export:

```bash
# Run only when the Design Spec's effective Speaker Notes outcome is enabled.
python3 scripts/total_md_split.py <project_path>
python3 scripts/finalize_svg.py <project_path>
python3 scripts/svg_to_pptx.py <project_path>
```

When Speaker Notes is disabled, skip `total_md_split.py` and append
`--no-notes` to `svg_to_pptx.py` so stale files under `notes/` cannot be
embedded.

