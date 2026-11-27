Supported parsed column/bar/line/area, pie/doughnut, scatter, and bubble charts without a baked preview receive a deterministic readable fallback marked `data-pptx-fallback-kind="normalized"`. The importer additionally activates verified column/line/area combo charts, canonical OHLC stock charts, area charts with numeric date axes, verified scatter/bubble charts whose two value axes fit the closed `axes.x` / `axes.y` contract, radar charts, safe `of_pie` `serLines`, axis/title/legend normalization, and validated bar/column gap/overlap cases. Combo plots may retain independent primary/secondary category caches and workbook ranges. Both the category/value and XY contracts retain kind/position/visibility/label position/number format/min/max/major unit/reverse/major gridlines for native read-back. Scatter import derives effective `scatter_style` from uniform per-series line/marker/smooth state. The normalized XY fallback consumes only the two major-gridline flags; the C4/C5 additions do not expand the normalized renderer. `gapWidth` is accepted only as an integer in `0..500` and `overlap` only as an integer in `-100..100`; both normalize in native output, while malformed or out-of-range values fail closed. Safe common series paint forms and theme scheme colors are resolved; unknown series paint/style XML outside the explicit normalization boundaries still fails closed. Safe stock series style may pass the structural gate, but stock series, `hiLowLines`, and up-down bar local styling can still normalize under the data-object-first contract. The PowerPoint-native replacement remains allowed to normalize unmodeled no-fill/alpha/line/marker details and reports the route-level loss risk. Chart title/legend/axis titles and supported data-label flags are retained when the current schema can represent them. Fallback-only objects keep rendered SVG content or a baked chart preview and carry `data-pptx-replacement-status`, which validation and `--native-charts-and-tables` export report as a warning. An active marker without a renderer keeps `data-pptx-fallback-kind="placeholder"`; default export keeps the reconstruction-only placeholder and the native Chart/Table opt-in may still reconstruct it.

The ChartEx importer accepts exactly the validated treemap, sunburst, histogram, pareto, box-whisker, waterfall, and funnel data models. Supported hierarchy/category/value/series/subtotal data round-trips to native output; source style, axes, labels, and binning may normalize. Numeric caches must be non-empty and finite with exact contiguous point topology. This is not arbitrary ChartEx import or presentation fidelity, and the ChartEx native writer still only promises valid payload palette entries rather than full source styling.

Imported/template-owned table/chart markers carry
`data-pptx-native-authority="json"`; their inline JSON is authoritative and the
visible fallback is a derived preview, so fallback freshness does not veto
native export. Free-designed markers omit the authority attribute and are
SVG-first. After their visible fallback and JSON are synchronized, run
`stamp_native_fallbacks.py ... --write`; missing, invalid, or stale baselines
leave default fallback export available but make `--native-charts-and-tables`
fail closed. Only that explicit flag activates Chart/Table replacement; marker
presence, semantic tables, and imported chart packages do not. Legacy marker
spellings and `--native-objects` remain read-compatible.

Exporter-canonical classic charts also recover canonical solid series/slice
colors and exact one- or two-paragraph title styling; two paragraphs retain
their `title` / `subtitle` roles. Slide-number fields resolve to the display
number defined by `firstSlideNum`; standalone master/layout SVGs retain their
literal field fallback because they are shared by multiple slides.

Image generation:

```bash
python3 scripts/image_gen.py "A modern futuristic workspace"
python3 scripts/image_gen.py --list-backends
