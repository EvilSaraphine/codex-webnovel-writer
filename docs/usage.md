# Usage

## Initialize a Novel Project

```bash
python3 scripts/webnovel.py init ../sample-novel-project
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

## 工具仓库与作品仓库分离

`codex-webnovel-writer` 是工具仓库，用来保存 Codex Skills、CLI、模板和文档。用户自己的小说项目应该由 `init` 命令生成到独立目录。

不建议把真实作品内容、私人设定、真实角色名、剧情片段或未公开文本提交到本工具仓库。工具仓库中的示例应使用通用占位内容。

推荐使用独立目录：

```bash
python3 scripts/webnovel.py init ../sample-novel-project
python3 scripts/webnovel.py chapter ../sample-novel-project 1
python3 scripts/webnovel.py index ../sample-novel-project
```

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
python3 scripts/webnovel.py check ../sample-novel-project
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
python3 scripts/webnovel.py chapter ../sample-novel-project 1
```

2. 让 Codex 根据 `webnovel-chapter` Skill 写作或修订该章。

```text
Use webnovel-chapter to draft chapter 1.
```

3. 使用 `chapter-summary` 生成结构化章节摘要：

```bash
python3 scripts/webnovel.py chapter-summary ../sample-novel-project 1
```

4. 使用 `index` 更新章节索引：

```bash
python3 scripts/webnovel.py index ../sample-novel-project
```

5. 使用 `update-state` 查看人物和伏笔状态概览：

```bash
python3 scripts/webnovel.py update-state ../sample-novel-project
```

6. 使用 `continuity-check` 检查连续性和缺失文件：

```bash
python3 scripts/webnovel.py continuity-check ../sample-novel-project
```

7. 使用 `review-template` 生成单章审查报告：

```bash
python3 scripts/webnovel.py review-template ../sample-novel-project 1
```
