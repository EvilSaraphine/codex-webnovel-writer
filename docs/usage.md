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

## 结构化规划工作流

1. 使用 `plan-init` 初始化规划文件：

```bash
python3 scripts/webnovel.py plan-init ../sample-novel-project
```

2. 使用 `add-volume` 添加卷：

```bash
python3 scripts/webnovel.py add-volume ../sample-novel-project 1 第一卷
```

3. 使用 `add-chapter-plan` 添加章纲：

```bash
python3 scripts/webnovel.py add-chapter-plan ../sample-novel-project 1 第001章
```

4. 使用 `add-scene` 添加场景卡：

```bash
python3 scripts/webnovel.py add-scene ../sample-novel-project 1 1
```

5. 使用 `add-timeline-event` 添加时间线事件：

```bash
python3 scripts/webnovel.py add-timeline-event ../sample-novel-project 1 示例事件
```

6. 使用 `add-arc` 添加人物线或关系线：

```bash
python3 scripts/webnovel.py add-arc ../sample-novel-project main-arc 主线关系
```

7. 使用 `planning-status` 检查规划完整度：

```bash
python3 scripts/webnovel.py planning-status ../sample-novel-project
```

8. 使用 `outline-export` 导出人工可读大纲：

```bash
python3 scripts/webnovel.py outline-export ../sample-novel-project
```

## 本地检索工作流

1. 使用 `build-index` 建立本地索引：

```bash
python3 scripts/webnovel.py build-index ../sample-novel-project
```

2. 使用 `retrieve` 查询相关片段：

```bash
python3 scripts/webnovel.py retrieve ../sample-novel-project 示例伏笔
```

3. 使用 `context-pack` 为章节写作生成上下文包：

```bash
python3 scripts/webnovel.py context-pack ../sample-novel-project 1
```

4. 让 Codex 根据 `context-pack` 和 `webnovel-retrieve` Skill 辅助写作：

```text
Use webnovel-retrieve and 章节索引/context-packs/第001章-context.md to prepare chapter 1.
```

5. 写完后运行 `index`、`chapter-summary` 和 `continuity-check`：

```bash
python3 scripts/webnovel.py index ../sample-novel-project
python3 scripts/webnovel.py chapter-summary ../sample-novel-project 1
python3 scripts/webnovel.py continuity-check ../sample-novel-project
```

## 项目体检工作流

推荐在写作或结构更新后运行 doctor 做只读体检：

1. 写作或更新结构后运行 `index`：

```bash
python3 scripts/webnovel.py index ../sample-novel-project
```

2. 运行 `build-index` 更新本地检索索引：

```bash
python3 scripts/webnovel.py build-index ../sample-novel-project
```

3. 运行 `doctor`：

```bash
python3 scripts/webnovel.py doctor ../sample-novel-project
```

4. 根据 `审查报告/doctor-report.md` 修复问题。doctor 只给诊断和建议，不会自动修复。

5. 再次运行 deep 体检：

```bash
python3 scripts/webnovel.py doctor ../sample-novel-project --deep
```

## 章节深度审查工作流

推荐在章节完成后运行结构化深度审查：

1. 写完章节。

2. 运行 `chapter-summary`：

```bash
python3 scripts/webnovel.py chapter-summary ../sample-novel-project 1
```

3. 运行 `index`：

```bash
python3 scripts/webnovel.py index ../sample-novel-project
```

4. 运行 `build-index`：

```bash
python3 scripts/webnovel.py build-index ../sample-novel-project
```

5. 运行 `context-pack`：

```bash
python3 scripts/webnovel.py context-pack ../sample-novel-project 1
```

6. 运行 `review`：

```bash
python3 scripts/webnovel.py review ../sample-novel-project 1
```

7. 查看 `审查报告/第001章-deep-review.md`。

8. 用户自行决定是否修改正文或更新状态文件。review 只给诊断和建议，不会自动修复。

## 反 AI 句式与风格审查工作流

推荐在章节完成后、deep review 前后配合使用 style-check：

1. 写完章节。

2. 运行 `style-rules` 确认规则文件存在：

```bash
python3 scripts/webnovel.py style-rules ../sample-novel-project
```

3. 运行 `style-check`：

```bash
python3 scripts/webnovel.py style-check ../sample-novel-project 正文/第001章.md
```

4. 查看 `审查报告/第001章-style-report.md`。

5. 人工决定命中句是否保留、弱化、改写或删除。style-check 只读，不自动修改正文。

6. 再运行 review 和 doctor：

```bash
python3 scripts/webnovel.py review ../sample-novel-project 1
python3 scripts/webnovel.py doctor ../sample-novel-project
```

批量检查章节范围：

```bash
python3 scripts/webnovel.py style-check-range ../sample-novel-project 1 5
```

用户可以编辑 `设定集/AI句式禁区.md`，补充项目自定义风险词、禁区和例外。命中结果只是启发式提示，需要结合上下文人工判断。

## 写作任务书工作流

推荐在正式写正文前生成写作任务书：

1. 补章纲、人物、伏笔、场景卡、时间线。

2. 运行 `prepare-write`：

```bash
python3 scripts/webnovel.py prepare-write ../sample-novel-project 1
```

3. 阅读 `章节索引/write-briefs/第001章-write-brief.md`。

4. 让 Codex 根据任务书写或修订 `正文/第001章.md`。

5. 写完后运行：

```bash
python3 scripts/webnovel.py chapter-summary ../sample-novel-project 1
python3 scripts/webnovel.py index ../sample-novel-project
python3 scripts/webnovel.py build-index ../sample-novel-project
python3 scripts/webnovel.py review ../sample-novel-project 1
python3 scripts/webnovel.py doctor ../sample-novel-project
```

write-brief 和 prepare-write 都不会自动生成正文；任务书只作为写作参考。

## 完整章节写作流水线

推荐用 v0.9 写作流水线组织单章写作：

1. 补充结构化规划，包括章纲、人物、伏笔、场景卡和时间线。

2. 运行 `write`：

```bash
python3 scripts/webnovel.py write ../sample-novel-project 1
```

3. 让 Codex 阅读：

- `章节索引/write-workspace/第001章-write-instruction.md`
- `章节索引/write-briefs/第001章-write-brief.md`
- `章节索引/context-packs/第001章-context.md`

4. 让 Codex 写或修订 `正文/第001章.md`。

5. 运行 `finalize-write`：

```bash
python3 scripts/webnovel.py finalize-write ../sample-novel-project 1
```

6. 查看 `审查报告/第001章-deep-review.md` 和 `审查报告/doctor-report.md`。

7. 用户决定是否手动更新人物、伏笔和设定。finalize-write 不会自动修改这些状态文件。
