---
name: webnovel-write-brief
description: Use chapter write task briefs to prepare Codex or a human author for drafting without automatically generating prose or changing project state.
---

# Webnovel Write Brief

## Purpose

Use this Skill when the user wants to prepare for drafting or revising a chapter from a generated writing task brief.

The write brief is a reference document. It does not create chapter prose, does not change canon, and should not be treated as a new setting record.

## CLI Commands

```bash
python3 scripts/webnovel.py write-brief <project_path> <chapter_number>
python3 scripts/webnovel.py write-brief-status <project_path>
python3 scripts/webnovel.py prepare-write <project_path> <chapter_number>
```

`write-brief` generates `章节索引/write-briefs/第XXX章-write-brief.md`.

`prepare-write` prepares pre-writing materials by running index, build-index, context-pack, and write-brief. It still does not generate正文.

## Source Material

A write brief is assembled from:

- chapter plan
- volume plan
- character state
- foreshadowing records
- timeline events
- scene cards
- conflict lines
- local retrieval context pack
- previous deep review report
- chapter summary

Before writing prose, read the task brief first. Then inspect referenced source files when a decision affects canon or continuity.

## Safety Rules

- Strictly separate confirmed settings from task brief suggestions.
- Do not automatically write task brief content back into settings, outlines, character state, hook records, summaries, or drafts.
- Do not invent missing setting details when the brief says information is insufficient.
- Ask the user to fill missing settings, character state, hook details, timeline, scene cards, or conflict records when needed.
- After writing or revising a chapter, run `chapter-summary`, `index`, `build-index`, `review`, and `doctor`.
- Do not read external network resources, call APIs, install dependencies, or use embedding providers.

## Generic Content Rule

This repository is a general-purpose tool. Keep examples generic and do not write private story content, real unpublished settings, real character names, plot scenes, unreleased prose, or specific IP content into this tool repository.

Use placeholders such as `主角A`, `角色B`, `示例地点`, `示例伏笔`, `第一卷`, and `第001章`.
