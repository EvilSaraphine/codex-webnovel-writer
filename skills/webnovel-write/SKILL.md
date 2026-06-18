---
name: webnovel-write
description: Guide Codex through the full local chapter writing workflow using write briefs, context packs, draft files, finalize checks, and review reports without calling external models or changing project state automatically.
---

# Webnovel Write

## Purpose

Use this Skill when the user wants Codex to write or revise a chapter after the local project has prepared the chapter workspace.

The CLI write workflow prepares materials. It does not call a model, does not access the network, and does not automatically generate full prose.正文创作 should happen only after reading the write instruction, write brief, context pack, and draft file.

## Full Writing Workflow

1. Run `python3 scripts/webnovel.py prepare-write <project_path> <chapter_number>` or `python3 scripts/webnovel.py write <project_path> <chapter_number>`.
2. Read `章节索引/write-workspace/第XXX章-write-instruction.md`.
3. Read `章节索引/write-briefs/第XXX章-write-brief.md`.
4. Read `章节索引/context-packs/第XXX章-context.md`.
5. Read `正文/draft-template.md` or the existing `正文/第XXX章.md` draft structure.
6. Write or revise `正文/第XXX章.md` in Chinese unless the user requests another language.
7. After writing, run `python3 scripts/webnovel.py finalize-write <project_path> <chapter_number>`.
8. Review `审查报告/第XXX章-deep-review.md` and `审查报告/doctor-report.md`.

## Writing Rules

- Do not invent unconfirmed settings.
- Do not silently change canon.
- Do not automatically edit `人物状态/characters.json`, `伏笔记录/hooks.json`, planning JSON, or setting files.
- If the write brief says information is missing, ask the user to fill the setting instead of forcing a detail.
- Keep chapter content aligned with the write brief, context pack, chapter plan, character state, foreshadowing records, timeline, scene cards, and conflict lines.
- Preserve planned reveals and do not pay off foreshadowing early unless requested.

## After Writing

After正文 changes, run:

```bash
python3 scripts/webnovel.py finalize-write <project_path> <chapter_number>
```

finalize-write creates or refreshes the chapter summary, updates the chapter index, rebuilds local retrieval, runs deep review, and runs doctor. It does not automatically repair warnings or update character, hook, outline, or setting records.

If review or doctor reports contain warnings or errors, show the user the report paths and ask which state files or prose should be updated.

## Generic Content Rule

This repository is a general-purpose tool. Keep examples generic and do not write private story content, real unpublished settings, real character names, plot scenes, unreleased prose, or specific IP content into this tool repository.

Use placeholders such as `主角A`, `角色B`, `示例地点`, `示例伏笔`, `第一卷`, and `第001章`.
