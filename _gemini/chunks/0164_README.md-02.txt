| Animation resources | `sound_sync.py` | [sound vocabulary and sync](../templates/sounds/README.md); [docs/pptx-animations.md](./docs/pptx-animations.md) |
| Spec maintenance | `update_spec.py`, `visualization_recall.py`; legacy `chart_recall.py` | [docs/update_spec.md](./docs/update_spec.md); [docs/visualization-recall.md](./docs/visualization-recall.md) |
| Image tools | `image_gen.py`, `image_treat.py`, `analyze_images.py`, `gemini_watermark_remover.py` | [docs/image.md](./docs/image.md) |
| Maintenance smokes | Inline temporary-project commands | [advanced image and motion](./docs/advanced-image-motion-smoke.md); [mask and gradient](./docs/mask-gradient-smoke.md); [multilingual text](./docs/multilingual-text-smoke.md) |
| Repo maintenance | `update_repo.py` | README install/update section |
| Troubleshooting | validation, preview, export, dependency issues | [docs/troubleshooting.md](./docs/troubleshooting.md) |

## High-Frequency Commands

Conversion:

```bash
python3 scripts/source_to_md.py <file-or-url-or-dir> [<file-or-url-or-dir> ...]
python3 scripts/source_to_md/pdf_to_md.py <file.pdf>
python3 scripts/source_to_md/ppt_to_md.py <deck.pptx>
python3 scripts/source_to_md/doc_to_md.py <file.docx>
python3 scripts/source_to_md/excel_to_md.py <workbook.xlsx>
python3 scripts/source_to_md/web_to_md.py <url>
python3 scripts/pptx_to_svg.py <deck.pptx> -o <output_dir>  # reconstruction/reference SVG import
```

Project setup:

```bash
python3 scripts/project_manager.py init <project_name> [--format <registered_format>]
python3 scripts/project_manager.py import-sources <project_path> <source_files_or_dirs...>
python3 scripts/project_manager.py scaffold-spec <project_path>  # optional manual helper
python3 scripts/project_manager.py scaffold-lock <project_path>  # optional manual helper
python3 scripts/project_manager.py validate <project_path>
python3 scripts/project_manager.py page-context <project_path> P07 --record-usage
python3 scripts/project_manager.py page-context-report <project_path>
```

`--format` is optional and accepts registered canvas keys only. Pass it when
the actual canvas exactly matches one of those keys; otherwise omit it. Without
the flag, `init` creates `<name>_<YYYYMMDD>`, and authoring records the canvas
in `spec_lock.md` for Default Generate or the first SVG for Quick Generate.

`page-context` is an on-demand read-only current-page projection for diagnostics,
routing checks, or context measurement; normal generation retains the complete
Design Spec and lock once per valid execution context. Each invocation includes
the global lock projection as a continuity anchor set, not a color/font allowlist; large Design Specs,
prototype, and selected family visualization references are emitted only as scoped
path/SHA fingerprints and are read once per execution context. `--bundle` is a
deprecated compatibility no-op. `--record-usage` writes one derived snapshot
under `analysis/page-context/`; exact `o200k_base` token counts are optional and
degrade to `tokens: null` when `tiktoken` is absent. Telemetry may be partial.

Optional visualization-recall diagnostics and canonical validation:

```bash
python3 scripts/visualization_recall.py recall --page P03 --tag "time series" --tag "three metrics" --tag "direction over time"
python3 scripts/visualization_recall.py validate chart/line_chart
```

Template source import:

```bash
python3 scripts/pptx_template_import.py <template.pptx>
python3 scripts/pptx_template_import.py <template.pptx> --manifest-only
python3 scripts/pptx_template_import.py <template.pptx> --inheritance-mode both
python3 scripts/svg_authoring_view.py <imported-svg-or-dir> -o <output-dir> --projection-kind layered
python3 scripts/svg_authoring_view.py <authoring-dir> --refresh-summary
python3 scripts/svg_authoring_view.py <authoring-dir> --adopt-object <from.svg>:<element-id> --into <target.svg>
python3 scripts/stamp_native_fallbacks.py <svg-file-or-directory> --write
