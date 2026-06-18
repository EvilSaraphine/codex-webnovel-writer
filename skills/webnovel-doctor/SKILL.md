---
name: webnovel-doctor
description: Run read-only project health checks for a Codex-native webnovel workspace and interpret doctor reports without network access or automatic fixes.
---

# Webnovel Doctor

## Purpose

Use this Skill when the user wants Codex to inspect whether a novel project initialized by this tool is structurally healthy.

Doctor is diagnostic. It gives findings and repair suggestions, but it does not automatically fix project files and does not treat findings as new story canon.

## CLI Command

Run:

```bash
python3 scripts/webnovel.py doctor <project_path>
python3 scripts/webnovel.py doctor <project_path> --deep
```

The command writes `审查报告/doctor-report.md`. Apart from that report file, doctor should not modify the project.

## Check Scope

Doctor checks:

- project structure
- core template files
- JSON readability
- chapter index records
- chapter summary files
- chapter plans and draft correspondence
- character state records
- foreshadowing hook records
- structured planning files
- local retrieval index files
- generic content safety risks in examples and templates

`--deep` adds more detailed lists, such as scanned chapter files, JSON file status, and local retrieval source files.

## Safety Rules

- Do not automatically repair files.
- Do not rewrite drafts, settings, outlines, character state, foreshadowing records, or planning files as part of doctor work.
- Do not convert a detected inconsistency into a new setting.
- Do not read external network resources.
- Do not install dependencies, start services, call APIs, or use embedding providers.
- If the checked project is a user's real novel project, private content safety terms may be false positives; report them as risks for user review.

## Generic Content Rule

This repository is a general-purpose tool. Keep examples generic and do not write private story content, real unpublished settings, real character names, plot scenes, unreleased prose, or specific IP content into this tool repository.

Use placeholders such as `主角A`, `角色B`, `示例地点`, `示例伏笔`, `第一卷`, and `第001章`.
