---
name: obsidian-vault-validation
description: Validate an Obsidian learning vault after structural or routing edits. Use when changing README links,分册 boundaries, OCR routing, or teaching metadata.
user-invocable: false
allowed-tools: Read, Grep, Glob, Bash
---

## When to use

Use for E:\OBsidian maintenance after Markdown, routing, OCR helper, or index changes. It validates structure and tooling; it does not establish learner mastery or textbook correctness.

## Inputs / context

Check `00-入口/AI教学协议.md`, `全栈工程师学习计划/进度追踪.md`, current `git status --short`, and the changed-file list first.

## Procedure

1. Inspect changed paths and preserve the separation between progress facts, logs, plans, knowledge, sources, and roadmap.
2. Run `python -B -X utf8 tools/check_vault.py`.
3. Run `python -B -X utf8 tools/build_topic_index.py --check`.
4. Run `python -B -X utf8 tools/test_vault_tools.py`.
5. For OCR work, use bounded extraction such as `python -B -X utf8 tools/read_ocr.py --book 01 --start 23 --end 24`; treat `pN` as OCR sequence markers, not verified print pages.
6. Read modified Markdown snippets to catch literal PowerShell escapes, duplicate numbering, broken links, and stale counts.

## Efficiency plan

Run the three repository checks together after a coherent edit batch; inspect only changed snippets unless a check fails. Stop structural claims at the tool boundary.

## Pitfalls and fixes

- `PASS` does not prove content correctness or learner mastery: require independent practice and evidence.
- Missing/ambiguous links or stale volume counts: use explicit paths and unique headings, then rerun checks.
- Broad cleanup risks deleting protected OCR/history files: enumerate exact targets and verify hashes before removal.

## Verification checklist

- Structure check passes.
- Topic index check passes.
- Tool tests pass.
- Changed Markdown has real newlines and correct numbering.
- No progress level was raised without learner evidence.
