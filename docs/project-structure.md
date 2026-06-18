# Project Structure

## Plugin Source

```text
codex-webnovel-writer/
├── .codex-plugin/plugin.json
├── skills/
├── scripts/webnovel.py
├── templates/
└── docs/
```

## Novel Workspace

```text
my-story/
├── AGENTS.md
├── 设定集/
├── 大纲/
├── 正文/
├── 审查报告/
├── 伏笔记录/
├── 人物状态/
└── 章节索引/
```

## Folder Roles

- `设定集/`: stable canon such as world rules, factions, locations, power systems, and style constraints.
- `大纲/`: total outline, volume outlines, chapter outlines, timelines, and arc plans.
- `正文/`: chapter drafts and revisions.
- `审查报告/`: review output for consistency, pacing, AI flavor, foreshadowing, and character state.
- `伏笔记录/`: setup and payoff tracking.
- `人物状态/`: current character knowledge, goals, relationships, wounds, resources, and secrets.
- `章节索引/`: progress table for outline, draft, review, and publication readiness.

## Context Policy

Do not load the whole project for every task. Pick files by workflow:

- Planning: settings, total outline, nearby outlines, foreshadowing, character state.
- Writing: target chapter outline, nearby drafts, relevant canon and state.
- Review: target draft, source outline, nearby continuity files.
- Query: search the relevant record folder first, then inspect outlines or drafts if needed.

