# AGENTS.md

## Project Rules

- This repository is a Codex-native plugin for webnovel writing workflows.
- This repository is a general-purpose open source tool, not a repository for any specific novel.
- Do not depend on Claude Code, Claude slash commands, or Claude-specific file conventions.
- Keep root-level guidance short. Put task-specific process details in `skills/*/SKILL.md`.
- Prefer stable Markdown files over hidden state. Novel memory should live in the project folders listed below.
- Write Chinese novel artifacts in Chinese unless the user requests another language.
- Preserve user-authored drafts, outlines, and notes. Do not rewrite large creative text unless explicitly asked.
- When editing novel content, keep changes scoped to the requested chapter, outline, report, or record.
- For review tasks, separate objective continuity issues from subjective style suggestions.
- For query tasks, cite the source files used when possible.

## General Tool Project Principles

- Do not add user-private novel content, real unpublished settings, real character names, plot scenes, unreleased text, or specific IP content to this tool repository.
- Templates, test samples, and documentation examples must use generic placeholders such as `主角A`, `角色B`, `某个旧物`, `第一卷`, `第001章`, `示例伏笔`, and `示例地点`.
- User novel content should live in a separate project directory initialized by this tool, not in the tool repository itself.
- If examples are needed, use generic names such as `generic-novel` or `sample-project`.

## Design Principles

- Context economy: load only the files needed for the current writing task.
- Traceability: important plot, setting, character, and foreshadowing decisions should be recorded.
- Long-form continuity: maintain chapter index, character state, and foreshadowing records as the story grows.
- Human authorship: prioritize preserving the author's intent, voice, and pacing.
- Iterative workflow: plan, write, review, update state, then continue.

## File Index

- `.codex-plugin/plugin.json`: Codex plugin manifest.
- `skills/webnovel-init/SKILL.md`: initialize a novel workspace.
- `skills/webnovel-plan/SKILL.md`: create volume outlines, chapter outlines, and timelines.
- `skills/webnovel-write/SKILL.md`: draft chapters from outlines and state files.
- `skills/webnovel-review/SKILL.md`: review consistency, AI flavor, pacing, foreshadowing, and character state.
- `skills/webnovel-query/SKILL.md`: answer questions from project files.
- `skills/webnovel-learn/SKILL.md`: record preferences and long-term project memory.
- `skills/webnovel-chapter/SKILL.md`: manage single-chapter workflow.
- `skills/webnovel-plan-structured/SKILL.md`: maintain structured planning files.
- `scripts/webnovel.py`: small CLI for project setup, indexing, querying, state overview, and chapter workflow.
- `templates/AGENTS.md`: starter AGENTS file for a novel project.
- `templates/设定集/`: worldbuilding and rules.
- `templates/大纲/`: volume outlines, chapter outlines, and timelines.
- `templates/正文/`: chapter drafts.
- `templates/审查报告/`: review reports.
- `templates/伏笔记录/`: foreshadowing records and payoff status.
- `templates/人物状态/`: character state snapshots.
- `templates/章节索引/`: chapter index and progress records.
- `docs/usage.md`: user workflow guide.
- `docs/project-structure.md`: file structure reference.
