is absent, source notes travel with the cloned page. Unchanged repeats clone
their private notes/chart/diagram/embedding parts, while media may stay shared;
slide-jump targets must map to exactly one output page. Without the file, the
identity round trip is unchanged. See
[`docs/svg-pipeline.md`](docs/svg-pipeline.md#round-trip-deck-page-plans) for
the schema, sidecar keying, fail-closed rules, and export receipt.

Run `python3 scripts/svg_quality_checker.py <workspace> --roundtrip` before a
round-trip export. The mode resolves the same identity or `page_plan.json`
output roster as the exporter and checks only new or changed text for supported
font stacks and sizes, estimated canvas containment, and horizontal capacity
against its owning `data-pptx-frame` or nearest rect fallback. Capacity is the
single-line width of each positioned line; the gate does not model vertical
wrapping. Explicit frame-width or canvas overflow is blocking, warnings are
advisory, and unchanged source refs, source proxies, plus
generated-project/template-only contracts are skipped.

`mirror_template_materialize.py` is the deterministic Type A mirror
validator/publisher. Template_Designer first reviews and authors the compact
layered `authoring-svg/` tree. The command loads its tool-only manifest and
validates it against immutable `svg/`,
`analysis/native_structure.json`,
`svg/inheritance.json`, `sources/source.pptx`, and any extracted-vector
inventory, then publishes the current visible authoring tree atomically. It
never replaces an unchanged visible subtree with lossless source XML; that
backing supplies provenance and supported non-visible semantics only. Mirror retains
only the Layout/Master chain reachable from each source Slide. Every output SVG
resolves Master + Layout + Slide context while keeping layer ownership explicit;
source identities unused by every Slide produce no SVG.
For a PPTX-backed mirror, `templates/source_themes.json` carries the exact Theme
bytes for each retained Master; it is validated tool input, not an SVG prototype
or model-editing surface.
Unchanged supported Slide-local/slot refs may recover native payload; edited
refs keep their current SVG fallback. Fixed Master/Layout wrappers are expanded
mechanically into direct atoms, source visibility flags become canonical root
metadata, and decoration-only imported vectors are copied once to
`icons/imported/`. Semantic objects remain inline. Large
opaque `txBody`, shape-style, and custom-geometry payloads are deduplicated into
`templates/native_payloads.json.gz`; repeated native restoration attributes
are stored there as short `data-pptx-native-ref` records. Structural metadata
stays inline, while checker, template-structure validation, and export hydrate
both layers in memory. Legacy inline payload and v1 payload-only stores remain
readable. The v1 execution manifest points to per-prototype
`ppt-master.template-text-slots.v2-min` diagnostic sidecars. They are derived
tool metadata and are not injected into model context. Checker and export
validate output attributes, topology, and resource hashes against the complete
prototype internally. Bitmap assets
and Office vector image media go to `images/`; audio, video, and opaque source
payloads go to their semantic workspace directories.
The destination must be empty, and the command does not write
`templates/design_spec.md`; Template_Designer owns that authored brief.

