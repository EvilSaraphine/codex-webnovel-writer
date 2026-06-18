# AGENTS.md

## Project Rules

- This repository is a Codex-native plugin for webnovel writing workflows.
- Do not depend on Claude Code, Claude slash commands, or Claude-specific file conventions.
- Keep root-level guidance short. Put task-specific process details in `skills/*/SKILL.md`.
- Prefer stable Markdown files over hidden state. Novel memory should live in the project folders listed below.
- Write Chinese novel artifacts in Chinese unless the user requests another language.
- Preserve user-authored drafts, outlines, and notes. Do not rewrite large creative text unless explicitly asked.
- When editing novel content, keep changes scoped to the requested chapter, outline, report, or record.
- For review tasks, separate objective continuity issues from subjective style suggestions.
- For query tasks, cite the source files used when possible.

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
- `scripts/webnovel.py`: small CLI for init, where, and check.
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

