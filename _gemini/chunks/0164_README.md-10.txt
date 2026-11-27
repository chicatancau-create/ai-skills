python3 scripts/analyze_images.py <project_path>/images
```

Generated-deck formulas do not use an image command. Author a native formula
marker in the page SVG; `svg_to_pptx.py` compiles its LaTeX metadata to editable
PowerPoint OMML. Forward compilation covers the explicitly documented Microsoft
365 LaTeX and mhchem input profiles and fails closed outside them.
`pptx_to_svg.py` also reconstructs PPT Master-owned, validator-clean OMML into
canonical block/inline formula markers with visible linear SVG previews. This
is a closed-vocabulary reverse import, not arbitrary third-party
OMML-to-LaTeX conversion; unknown OMML is reported and kept opaque in tolerant
mode. The retained `latex_render.py` utility is
standalone legacy rasterization only and is not connected to either Generate
profile.

Repository update:

```bash
python3 scripts/update_repo.py
python3 scripts/update_repo.py --skip-pip
```

## Recommendations

- Keep one user-facing entry point per workflow at the top level of `scripts/`
- Move provider-specific or helper internals into subdirectories
- Prefer the unified entry points `project_manager.py`, `finalize_svg.py`, and `image_gen.py`
- Use `svg_output/` for the only supported native PPTX export and `svg_final/` for self-contained SVG visual preview / picture insertion

## Related Docs

- [Conversion Tools](./docs/conversion.md)
- [Project Tools](./docs/project.md)
- [SVG Pipeline Tools](./docs/svg-pipeline.md)
- [PPTX Transition Core](./docs/pptx-transitions.md)
- [Image Tools](./docs/image.md)
- [Troubleshooting](./docs/troubleshooting.md)
- [Skill Entry](../SKILL.md)

_Last updated: 2026-07-11_
