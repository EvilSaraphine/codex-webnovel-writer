---
name: webnovel-query
description: Query a webnovel project for character facts, setting rules, foreshadowing status, chapter progress, timeline details, continuity questions, and source-backed summaries. Use when the user asks where something is recorded, what is canon, what happened to a character, which chapters are done, or what foreshadowing remains unpaid.
---

# Webnovel Query

## Search Order

Pick the smallest useful set:

- Characters: `人物状态/`, then relevant `正文/` and `大纲/`.
- Setting and rules: `设定集/`.
- Foreshadowing: `伏笔记录/`, then chapter outlines and drafts.
- Chapter status: `章节索引/章节索引.md`, then `正文/` and `大纲/`.
- Timeline: `大纲/时间线.md`, nearby outlines, and drafts.

## Answer Style

- Answer directly first.
- List source files used.
- Mark uncertain facts as uncertain.
- Distinguish canon from plan, draft, and suggestion.
- If records disagree, show the conflict and recommend which file should be updated.

## Common Queries

- "某人物现在在哪里，目标是什么？"
- "第 12 章有哪些未回收伏笔？"
- "这个能力规则之前怎么写的？"
- "哪些章节只有大纲没有正文？"
- "这段剧情和时间线冲突吗？"

Use `rg` for file discovery when working in a local project.

