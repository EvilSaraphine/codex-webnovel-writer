---
name: webnovel-review
description: Review webnovel outlines or chapters for continuity, consistency, AI-like prose, pacing, foreshadowing setup/payoff, character state, serialization hooks, and missing record updates. Use when the user asks to审查, polish, diagnose, or produce a review report for novel content.
---

# Webnovel Review

## Inputs To Inspect

- Target chapter or outline.
- Source chapter outline if reviewing a draft.
- Nearby chapters when continuity matters.
- Relevant `设定集/`, `人物状态/`, `伏笔记录/`, and `章节索引/` files.

## Review Categories

Report issues in this order:

1. Continuity and canon conflicts.
2. Character state or motivation drift.
3. Plot logic and cause-effect gaps.
4. Pacing, scene pressure, and chapter hook strength.
5. Foreshadowing setup, payoff, or accidental reveal.
6. AI flavor: generic phrasing, over-explanation, repetitive sentence rhythm, hollow emotion, vague action.
7. Missing project record updates.

## Output Format

Use a concise report:

- Verdict.
- High-risk issues.
- Medium-risk issues.
- Style and pacing suggestions.
- Record updates needed.
- Optional rewrite targets.

When asked to save a report, place it under `审查报告/` with a filename tied to the chapter or outline.

## Guardrails

- Separate objective errors from taste-based suggestions.
- Do not rewrite full chapters unless requested.
- Cite source files or sections when possible.

