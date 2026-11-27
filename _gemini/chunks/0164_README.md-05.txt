`template_preview_pptx.py` reads a template workspace, exports every complete `templates/*.svg` Slide prototype as one structured review slide, and verifies the resulting Master/Layout package. In a project root containing Layout and Deck specs, it previews the active Layout roster. Standalone `layout_<layout_key>.svg` definition files are rejected; every reusable Layout must be represented by a complete Slide prototype. This is an on-demand review action: its default output is `exports/<template_id>_template_preview.pptx`, and that directory need not exist before the command runs. It refuses an existing output unless an intentional re-export passes `--force`.

Native preset shape authoring (one or more registry-backed fragments on stdout):

```bash
python3 scripts/preset_shape_svg.py list --search arrow
python3 scripts/preset_shape_svg.py describe rightArrow --compact
python3 scripts/preset_shape_svg.py render rightArrow --id process-arrow --frame 120 180 240 96 --fill '#2563EB'
python3 scripts/preset_shape_svg.py render-batch --input - <<'JSON'
[
  {"preset":"chevron","id":"step-1","frame":[120,180,220,96],
   "fill":"#2563EB","stroke":"none","adjustments":{"adj":"val 42000"}},
  {"preset":"leftBrace","id":"group-brace","frame":[380,170,48,240],"fill":"none","stroke":"#111827","stroke_width":3}
]
JSON
```

Runtime capability discovery reads
[`preset-shape-vocabulary.md`](../references/preset-shape-vocabulary.md), which
lists all 187 exact names by Office category and objective contour family.
`list [--search QUERY]` and `list --grouped [--search QUERY]` remain optional
location views; they do not replace the complete vocabulary.
`describe --compact` returns the selected preset's objective identity, Office
category, family, scope, literal boundary, adjustments, connector/path facts,
connection sites, and text-rectangle availability. Plain `describe` preserves
the full nested semantics payload. A zero-match `list --search` remains
a failed lookup with exit code 1.

The helper never writes a page or project file. Select one exact semantic
stock-shape match, inspect the emitted fragment, and insert it into the
hand-authored SVG with the normal patch workflow. Semantic discovery does not
force ordinary rectangles, ellipses, or lines through `render`; use the
simplest exact authoring form from the native-shape reference. A rendered
project-owned preset is one compact atomic `<g>` with direct registry-generated
visible paths. When one effect is justified, optional `--filter-id softShadow`
references one existing direct page-level filter under the shared shadow/glow
contract and applies it once to a shape preset. Connector presets do not accept
that option. The helper does not create the filter definition. `render-batch`
accepts a non-empty JSON array using the snake_case forms of the single-render
options; it validates every item and duplicate id before printing, so one
invalid item produces no partial fragment output. The batch remains
fragment-only input for one current construction, not a page generator or
project manifest. `adjustments` is a JSON object keyed by guide name, unlike
the repeatable single-render `--adjust NAME=FORMULA` option.
Quality check and export rerender the registry instead of relying on a hidden
carrier, preview wrapper, or stored preview fingerprint. PPTX import and
round-trip SVGs deliberately keep their expanded carrier/preview evidence and
are not rewritten into this authored form. Keep ordinary rectangles, ellipses,
freeform geometry, charts, icons, and ambiguous silhouettes as regular SVG.
See [`references/shared-standards-core.md`](../references/shared-standards-core.md) §1.5 for
the normative contract and
[`references/native-shape-authoring.md`](../references/native-shape-authoring.md)
for selection and authoring guidance.

PowerPoint-style Merge Shapes materialization (source read-only; result paths
on stdout):

```bash
python3 scripts/shape_boolean_svg.py render slide.svg \
