---
name: webnovel-retrieve
description: Use local retrieval results and generated context packs to support writing, querying, and reviewing a Codex-native webnovel project without network access or embedding providers.
---

# Webnovel Retrieve

## Purpose

Use this Skill when the user wants Codex to use local retrieval results before writing, answering project questions, or reviewing continuity.

This is a light local retrieval workflow. It uses project files as reference material only. Retrieval results do not replace the user's confirmed setting, outline, character state, foreshadowing records, or chapter text.

## CLI Commands

- `python3 scripts/webnovel.py build-index <project_path>` builds `.webnovel/chunks.json` and `.webnovel/retrieval-index.json` from local Markdown, text, and JSON files.
- `python3 scripts/webnovel.py retrieve <project_path> <query>` searches the local index and prints ranked snippets.
- `python3 scripts/webnovel.py context-pack <project_path> <chapter_number>` reads the matching record in `大纲/chapter_plans.json`, retrieves related snippets, and writes `章节索引/context-packs/第XXX章-context.md`.
- `python3 scripts/webnovel.py retrieval-status <project_path>` checks whether config, chunks, and index files exist and reports index metadata.

## Standard Workflow

1. Run `build-index` after updating settings, outlines, chapter drafts, character state, foreshadowing records, chapter summaries, review reports, or structured planning files.
2. Run `retrieve` for direct questions about relevant settings, hooks, character state, chapter summaries, or timelines.
3. Run `context-pack` before drafting or revising a chapter.
4. Read the generated context pack together with the target chapter plan and the project `AGENTS.md`.
5. Use retrieved snippets as pointers to source files, then inspect the source files when the decision is important.

## Safety Rules

- Treat retrieval results as reference snippets, not new canon.
- Do not automatically write retrieved snippets back into settings, outlines, character records, hook records, or chapter drafts.
- Do not infer a new setting solely because a retrieved snippet appears relevant.
- If retrieval results are sparse, contradictory, or missing key information, tell the user what setting, character state, timeline, or foreshadowing detail needs to be supplied.
- Separate objective continuity evidence from creative suggestions during review.

## Generic Content Rule

This repository is a general-purpose tool. Keep examples generic and do not write private story content, real unpublished settings, real character names, plot scenes, unreleased prose, or specific IP content into this tool repository.

Use placeholders such as `主角A`, `角色B`, `示例地点`, `示例伏笔`, `第一卷`, and `第001章`.
