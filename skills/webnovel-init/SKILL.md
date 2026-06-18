---
name: webnovel-init
description: Initialize a Codex-native webnovel project workspace from this plugin's templates. Use when the user wants to create a new novel project structure, set up AGENTS.md for a story, or prepare folders for settings, outlines, drafts, review reports, foreshadowing, character state, and chapter index.
---

# Webnovel Init

## Workflow

1. Choose the target project path from the user request.
2. If the path does not exist, create it.
3. Copy or recreate the template structure:
   - `AGENTS.md`
   - `设定集/`
   - `大纲/`
   - `正文/`
   - `审查报告/`
   - `伏笔记录/`
   - `人物状态/`
   - `章节索引/`
4. Add starter Markdown files only when useful for the user's immediate goal.
5. Run `python3 <plugin-root>/scripts/webnovel.py check <target-path>` if the script is available.

## Initial Files

Prefer these starter files for a blank project:

- `设定集/世界观.md`: premise, genre promise, power system, constraints.
- `设定集/创作原则.md`: tone, audience, update cadence, forbidden moves.
- `大纲/总纲.md`: core hook, protagonist arc, major conflicts, ending direction.
- `大纲/时间线.md`: dated or relative sequence of key events.
- `章节索引/章节索引.md`: chapter number, title, status, source outline, review state.
- `伏笔记录/伏笔总表.md`: setup, location, intended payoff, current status.
- `人物状态/人物总表.md`: active characters, current goals, secrets, relationships.

## Guardrails

- Keep the novel project's `AGENTS.md` under 150 lines.
- Do not place long plot summaries or full canon dumps in `AGENTS.md`.
- Store long-lived canon in the domain folders so future tasks can load only relevant files.

