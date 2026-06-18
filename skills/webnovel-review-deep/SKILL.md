---
name: webnovel-review-deep
description: Run structured deep chapter reviews for a Codex-native webnovel project using local files only, producing diagnostic reports without rewriting story content.
---

# Webnovel Review Deep

## Purpose

Use this Skill when the user wants Codex to review one chapter or a chapter range with structured, evidence-based checks.

The review is diagnostic. It gives findings and suggestions, but it does not automatically edit drafts, write back settings, update character state, or change foreshadowing records.

## Review Scope

Review checks:

- chapter structure completeness
- chapter plan alignment
- character state changes
- foreshadowing introduced, advanced, or resolved
- timeline continuity
- scene goals and conflicts
- chapter summary and chapter index coverage
- local retrieval context support
- setting consistency risks
- follow-up tasks

The v0.7 implementation uses local files, fields, keywords, and structural checks only. It does not perform style or anti-AI phrasing detection yet; that remains a future focused review.

## CLI Commands

```bash
python3 scripts/webnovel.py review <project_path> <chapter_number>
python3 scripts/webnovel.py review-range <project_path> <start_chapter> <end_chapter>
python3 scripts/webnovel.py review-status <project_path>
```

Reports are written under `审查报告/`.

## Safety Rules

- Do not automatically rewrite chapter prose.
- Do not automatically write findings back into settings, outlines, character state, hook records, summaries, or indexes.
- Do not treat speculation as fact.
- Distinguish objective missing files or record mismatches from subjective craft suggestions.
- If information is missing, ask the user to provide the setting or run `build-index` / `context-pack`.
- Do not read external network resources, call APIs, install dependencies, or use embedding providers.

## Generic Content Rule

This repository is a general-purpose tool. Keep examples generic and do not write private story content, real unpublished settings, real character names, plot scenes, unreleased prose, or specific IP content into this tool repository.

Use placeholders such as `主角A`, `角色B`, `示例地点`, `示例伏笔`, `第一卷`, and `第001章`.
