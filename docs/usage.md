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

## 推荐单章工作流

1. 使用 `chapter` 生成章节模板：

```bash
python3 scripts/webnovel.py chapter ~/novels/my-story 1
```

2. 让 Codex 根据 `webnovel-chapter` Skill 写作或修订该章。

```text
Use webnovel-chapter to draft chapter 1.
```

3. 使用 `chapter-summary` 生成结构化章节摘要：

```bash
python3 scripts/webnovel.py chapter-summary ~/novels/my-story 1
```

4. 使用 `index` 更新章节索引：

```bash
python3 scripts/webnovel.py index ~/novels/my-story
```

5. 使用 `update-state` 查看人物和伏笔状态概览：

```bash
python3 scripts/webnovel.py update-state ~/novels/my-story
```

6. 使用 `continuity-check` 检查连续性和缺失文件：

```bash
python3 scripts/webnovel.py continuity-check ~/novels/my-story
```

7. 使用 `review-template` 生成单章审查报告：

```bash
python3 scripts/webnovel.py review-template ~/novels/my-story 1
```
