---
name: webnovel-chapter
description: Prepare, draft, summarize, and check a single webnovel chapter using Codex-native project files, chapter indexes, character state, hook records, and continuity checks.
---

# Webnovel Chapter

## Purpose

Use this Skill when the user wants to work around one specific chapter: prepare a writing package, draft or revise the chapter, create a post-writing summary, suggest state updates, and run continuity checks.

This Skill does not require external models, RAG, or hidden memory. Use the project files as the source of truth.

## Standard Workflow

1. Read `AGENTS.md` for project-level rules.
2. Read relevant files under `设定集/`.
3. Read relevant files under `大纲/`, especially the target chapter outline and nearby outlines.
4. Read `人物状态/characters.json`.
5. Read `伏笔记录/hooks.json`.
6. Read `章节索引/chapters.json`.
7. Generate or inspect the chapter work package for the requested chapter number.
8. Draft or revise `正文/第XXX章.md` according to the user's request.
9. After writing, generate or update `章节索引/summaries/第XXX章-summary.md`.
10. Suggest updates to character state and hook state.
11. Run:
    - `python3 scripts/webnovel.py index <project_path>`
    - `python3 scripts/webnovel.py continuity-check <project_path>`

## Chapter Work Package

For the target chapter, gather only the relevant context:

- Target chapter number and current draft path.
- Target chapter outline, if present.
- Previous and next chapter summaries, if present.
- Relevant setting rules.
- Characters likely to appear and their current `characters.json` state.
- Hooks that may be introduced, advanced, paid off, or protected.
- Existing chapter index entry, if present.

Do not load the whole novel unless the user explicitly asks for a broad audit.

## Writing Guidance

- Write Chinese novel artifacts in Chinese unless the user requests another language.
- Preserve user-authored drafts and outlines. For revision tasks, keep edits scoped to the requested chapter or scene.
- Do not pay off hooks early unless the outline or user asks for it.
- Keep the chapter aligned with character knowledge, resources, relationships, wounds, and secrets.
- End with a hook, decision, reveal, pressure point, or unresolved question suitable for serial reading.

## Post-Writing Summary

After the chapter draft is complete, update the chapter summary with:

- 章节号
- 章节标题
- 本章发生了什么
- 人物状态变化
- 新增伏笔
- 回收伏笔
- 未解决问题
- 下一章承接点

The summary should be concise and factual. It is a continuity aid, not marketing copy.

## State Update Suggestions

After writing or revising, list suggested updates separately:

- `人物状态/characters.json`: status, last seen chapter, role changes, relationship changes, resources, injuries, knowledge.
- `伏笔记录/hooks.json`: new hooks, advanced hooks, paid-off hooks, related characters, notes.
- `章节索引/chapters.json`: refresh through the `index` command.
- `章节索引/summaries/`: refresh through `chapter-summary` if needed.

Ask for confirmation before making substantive canon changes unless the user explicitly requested automatic updates.

## Final Checks

Run `index` and `continuity-check` at the end of the workflow when the CLI is available. Report any warnings clearly, distinguishing file-management issues from creative suggestions.
