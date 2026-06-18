# Usage

## Initialize a Novel Project

```bash
python3 scripts/webnovel.py init ~/novels/my-story
```

The command creates:

- `AGENTS.md`
- `设定集/`
- `大纲/`
- `正文/`
- `审查报告/`
- `伏笔记录/`
- `人物状态/`
- `章节索引/`

It also seeds starter Markdown files for worldbuilding, total outline, timeline, chapter index, foreshadowing, and character state.

## Use With Codex

Use natural language and name the Skill when the workflow matters:

```text
Use webnovel-plan to create a 20-chapter outline for volume 1.
Use webnovel-write to draft chapter 1 from 大纲/第001章.md.
Use webnovel-review to review 正文/第001章.md and save a report.
Use webnovel-query to list unpaid foreshadowing before chapter 10.
```

## Validate

Validate this plugin source:

```bash
python3 scripts/webnovel.py check
```

Validate a novel project:

```bash
python3 scripts/webnovel.py check ~/novels/my-story
```

## Recommended Loop

1. Initialize the project with `webnovel-init`.
2. Build `设定集/` and `大纲/总纲.md`.
3. Use `webnovel-plan` for volume and chapter outlines.
4. Use `webnovel-write` for chapter drafts.
5. Use `webnovel-review` before marking a chapter ready.
6. Update `人物状态/`, `伏笔记录/`, and `章节索引/`.
7. Use `webnovel-query` whenever continuity is unclear.

