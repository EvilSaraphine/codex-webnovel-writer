---
name: webnovel-style-check
description: Check chapter prose for AI-flavored phrasing and style risks using local heuristic rules, producing a read-only report with human-review suggestions.
---

# Webnovel Style Check

## Purpose

Use this Skill when the user wants Codex to inspect a chapter for common AI-flavored phrasing, over-explained emotional analysis, mechanical transitions, forced profundity, summary-like judgment, and slogan-like lines.

This Skill is diagnostic only. It produces a style risk report and does not automatically modify chapter prose.

## What To Check

Focus on these risk types:

- 总结式表达：替读者总结关系、情绪、命运或主题。
- “不是……而是……”式假深刻表达：用对称句式制造结论感，但缺少场景支撑。
- 过度完整的主题句：句子像章节主旨说明，而不是人物正在经历的事。
- 抽象心理解释：直接分析创伤、防御机制、依恋、控制欲等。
- 机械转折：用“然而事情并没有”“但他不知道的是”“命运早已”等推进剧情。
- 抽象名词堆叠：距离感、破碎感、宿命感、安全感等密集出现。
- 比喻词堆叠：单句或连续句中过度使用“像是 / 仿佛 / 好像”。
- 说明书式人物分析：用概括性说明介绍人物性格、过往和动机。
- 章末强行升华：用命运、齿轮、开始、注定等收束章节。
- 过度因果归纳：替读者解释“所以”“正因如此”“这也解释了”。
- 过度金句化：句子像可摘抄标语，压过人物和场景。
- 翻译腔和说明腔：使用“这意味着”“显然”“毫无疑问”等说明文口吻。

## Report Requirements

Each finding should include:

- 命中原句
- 问题类型
- 风险等级：`low` / `medium` / `high`
- 为什么像 AI
- 建议处理：保留 / 弱化 / 改写 / 删除
- 改写方向

## Judgment Rules

- Do not automatically rewrite the chapter.
- Do not mechanically replace phrases.
- Do not mark all literary expression as AI-flavored.
- Treat findings as prompts for human confirmation, not final verdicts.
- Consider local context, narrator style, genre, rhythm, and whether repetition is intentional.
- If a sentence is functional, voice-consistent, or intentionally stylized, suggest keeping it.

## Revision Direction

Prefer craft directions over full replacement prose:

- 用一个动作替代总结。
- 用停顿、视线、身体反应承载心理变化。
- 用一段对话暴露关系变化。
- 删除升华句，让场景停在动作或物件上。
- 把心理分析拆成身体反应和选择。
- 把因果解释藏进人物行为。
- 保留信息空白，不要替读者下结论。
- 用具体场景细节替代抽象名词。

## CLI Commands

```bash
python3 scripts/webnovel.py style-rules <project_path>
python3 scripts/webnovel.py style-check <project_path> <chapter_file>
python3 scripts/webnovel.py style-check-range <project_path> <start_chapter> <end_chapter>
```

Reports are written under `审查报告/`. The commands use only local files and Python standard library behavior.

## Generic Content Rule

This repository is a general-purpose tool. Keep examples generic and do not write private story content, real unpublished settings, real character names, plot scenes, unreleased prose, or specific IP content into this tool repository.

Use placeholders such as `主角A`, `角色B`, `示例地点`, `示例伏笔`, `第一卷`, and `第001章`.
