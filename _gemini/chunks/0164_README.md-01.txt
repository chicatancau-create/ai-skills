# PPT Master Toolset

This directory contains user-facing scripts for conversion, project setup, SVG processing, source-preserving PPTX editing, export, recorded narration, and image generation.

## Directory Layout

- Top-level `scripts/`: runnable entry scripts
- `scripts/project_management/`: internals behind `project_manager.py`
- `scripts/source_to_md.py`: unified source-document → Markdown dispatcher
- `scripts/source_to_md/`: source-document → Markdown routing/batch helpers and backend converters (`_dispatcher.py`, `_batch.py`, `pdf_to_md.py`, `doc_to_md.py`, `excel_to_md.py`, `ppt_to_md.py`, `web_to_md.py`)
- `scripts/image_backends/`: internal provider implementations used by `image_gen.py`
- `scripts/tts_backends/`: internal TTS provider implementations used by `notes_to_audio.py`
- `scripts/template_import/`: internal PPTX reference-preparation helpers used by `pptx_template_import.py`
- `scripts/pptx_ooxml/`: shared OOXML intake, cloning, and package primitives
- `scripts/svg_finalize/`: internal post-processing helpers used by `finalize_svg.py`
- `scripts/docs/`: topic-focused script documentation
- `scripts/prompt_audit.py` + `scripts/prompt_audit_manifest.json`: maintainer-only prompt budget/governance lint (see [`docs/prompt_audit.md`](docs/prompt_audit.md)); the manifest is audit-only and never loaded as prompt context
- `scripts/assets/`: static assets consumed by scripts

## Quick Start

Typical end-to-end workflow:

```bash
python3 scripts/source_to_md.py <file-or-url-or-dir> [<file-or-url-or-dir> ...]
# or direct backend calls:
python3 scripts/source_to_md/pdf_to_md.py <file.pdf>
# or
python3 scripts/source_to_md/ppt_to_md.py <deck.pptx>
python3 scripts/source_to_md/excel_to_md.py <workbook.xlsx>
python3 scripts/project_manager.py init <project_name>
python3 scripts/project_manager.py import-sources <project_path> <source_files_or_dirs...>
python3 scripts/total_md_split.py <project_path>
python3 scripts/finalize_svg.py <project_path>
python3 scripts/animation_config.py scaffold <project_path>  # optional object-level animation overrides
python3 scripts/svg_to_pptx.py <project_path>
```

After `init`, project-scoped Python CLIs automatically record their command
envelopes and bounded material outcomes in
`<project_path>/validation/workflow.log`; invoke them directly, without a
logging wrapper. The log does not copy the full console stream.

Repository update:

```bash
python3 scripts/update_repo.py
```

## Script Index

| Area | Primary scripts | Documentation |
|------|-----------------|---------------|
| Conversion | `source_to_md.py`, `source_to_md/pdf_to_md.py`, `source_to_md/doc_to_md.py`, `source_to_md/excel_to_md.py`, `source_to_md/ppt_to_md.py`, `source_to_md/web_to_md.py`, `pptx_intake.py`, `pptx_to_svg.py` | [docs/conversion.md](./docs/conversion.md) |
| Project management | `project_manager.py`, `workflow_log.py`, `workflow_transcript.py`, `batch_validate.py`, `generate_examples_index.py`, `error_helper.py`, `pptx_template_import.py`, `pptx_delivery_check.py` | [docs/project.md](./docs/project.md) |
| SVG pipeline | `preset_shape_svg.py`, `shape_boolean_svg.py`, `svg_authoring_view.py`, `authoring_roundtrip.py`, `compact_svg_coordinates.py`, `compact_svg_styles.py`, `stamp_native_fallbacks.py`, `mirror_template_materialize.py`, `finalize_svg.py`, `svg_to_pptx.py`, `template_preview_pptx.py`, `total_md_split.py`, `svg_quality_checker.py`, `extract_svg_assets.py`, `extract_svg_pictures.py`, `animation_config.py`, `notes_to_audio.py`, `narration_sync.py` | [docs/svg-pipeline.md](./docs/svg-pipeline.md); [native shape authoring](../references/native-shape-authoring.md) |
| PPTX transitions | `pptx_transitions.py` | [docs/pptx-transitions.md](./docs/pptx-transitions.md) |
| PPTX animations | `pptx_animations.py`, `animation_config.py` | [docs/pptx-animations.md](./docs/pptx-animations.md) |
