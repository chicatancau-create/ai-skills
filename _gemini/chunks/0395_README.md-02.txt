**Hard rule — the container disambiguates, the filename carries the rest**: a library root keeps `templates/design_spec.md` (its `<kind_dir>/<template_id>/` names kind and id); a project root shares one flat `templates/` and keeps one `design_spec.<kind>.<id>.md` per kind, with filename kind/id equal to frontmatter `kind` / `<kind>_id`; the shapes never mix. One `templates/` holds one active roster — Layout when present, otherwise Deck — while both specs may coexist because Layout overrides only Deck structure. Either shape is a workspace root, and selecting it takes every kind it exposes. Empty optional directories are omitted; Style contributes only its spec; every kind ignores `exports/`.

## Design specification references

[`design_spec_reference.md`](./design_spec_reference.md) and [`spec_lock_reference.md`](./spec_lock_reference.md) own project-level authoring; their schemas own validation; `scaffolds/` files are optional CLI conveniences. Template specs are deliberately smaller — portable metadata plus only the rules the package owns; general SVG rules live in [`shared-standards-core.md`](../references/shared-standards-core.md).

## Visualization Templates

Page-local Shape-first catalog families, not kinds: Chart — value-driven geometry (33), planning map [`chart-vocabulary.md`](./charts/chart-vocabulary.md), index [`charts_index.json`](./charts/charts_index.json); Table — row × column fact grid (6), [`table-vocabulary.md`](./tables/table-vocabulary.md), [`tables_index.json`](./tables/tables_index.json). [`VISUALIZATION_TEMPLATE_AUTHORING.md`](./VISUALIZATION_TEMPLATE_AUTHORING.md) is the maintainer authoring contract. Qualitative Structure is a Slide-local Executor method, not a catalog; only Layout and Deck own reusable Master/Layout, page types, slots, and placeholders.

## Icon Library

[`icons/`](./icons/) holds 12,027 vectors across five libraries (`chunk-filled` 641, `tabler-filled` 1,055, `tabler-outline` 5,138, `phosphor-duotone` 1,518, `simple-icons` 3,675 brand logos); usage and style rules in [icons/README.md](./icons/README.md), licenses in [icons/THIRD_PARTY_NOTICES.md](./icons/THIRD_PARTY_NOTICES.md).

## Sound Library

[`sounds/`](./sounds/) is selected only through the post-motion pass in [`animations.md`](../references/animations.md) §2.2 ([usage](./sounds/README.md)); it is never a template or planning resource.
