---
name: webnovel-plan-structured
description: Generate and maintain structured long-form novel planning files for volumes, chapter plans, timelines, arcs, scene cards, and conflict lines in a Codex-native webnovel project.
---

# Webnovel Plan Structured

## Purpose

Use this Skill when the user wants to create, revise, audit, or export the structural planning layer of a long-form novel project.

Planning files are the structure before drafting. They organize intent, sequence, pressure, character movement, hooks, and continuity targets. Do not put full prose scenes or chapter正文 into planning JSON.

## Standard Workflow

1. Read relevant files under `设定集/`.
2. Read relevant files under `大纲/`.
3. Read `人物状态/characters.json`.
4. Read `伏笔记录/hooks.json`.
5. Read `章节索引/chapters.json`.
6. Generate or update:
   - `大纲/volumes.json`
   - `大纲/chapter_plans.json`
   - `大纲/timeline.json`
   - `大纲/arcs.json`
   - `大纲/scenes.json`
   - `大纲/conflicts.json`
   - `大纲/planning-guide.md` when guidance needs clarification.
7. Run `python3 scripts/webnovel.py planning-status <project_path>` when available.
8. Run `python3 scripts/webnovel.py outline-export <project_path>` when the user wants a readable Markdown outline.

Load only the files needed for the requested planning scope.

## File Roles

- `volumes.json`: volume-level promise, goal, central conflict, chapter range, and major hooks.
- `chapter_plans.json`: chapter-level goal, POV, scenes, characters, hooks, conflict, ending hook, and status.
- `timeline.json`: ordered events, time labels, locations, consequences, and related chapters.
- `arcs.json`: character arcs, relationship arcs, career arcs, and other long-running lines.
- `scenes.json`: scene cards with location, participants, purpose, conflict, outcome, and hooks.
- `conflicts.json`: external, internal, relationship, resource, mystery, or setting conflict lines.

JSON files are for machine-readable structure. Markdown files are for human-readable explanation and exports.

## Generic Content Rule

This repository is a general-purpose tool. Keep examples generic and do not write private story content, real unpublished settings, real character names, plot scenes, unreleased prose, or specific IP content into this tool repository.

Use placeholders such as:

- `主角A`
- `角色B`
- `示例地点`
- `示例伏笔`
- `第一卷`
- `第001章`
- `示例冲突`

When working inside a user's separate novel project, preserve their content and follow that project's `AGENTS.md`.

## Planning Guidelines

- Keep planning entries concise and structural.
- Put references to hooks in hook fields instead of embedding payoff prose.
- Use chapter numbers and IDs consistently so CLI checks can compare plans, drafts, and summaries.
- Prefer adding records to JSON over creating one-off freeform notes when the information should be reused.
- Use Markdown exports to review the plan as a human-readable outline.

## Output Style

When returning a planning result:

- List files updated.
- Mention any missing related records, such as scenes without chapter plans.
- Separate structural gaps from creative suggestions.
- Recommend the next CLI command, such as `planning-status` or `outline-export`.
