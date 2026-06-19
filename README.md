# codex-webnovel-writer

Codex-native long-form webnovel writing workflow with planning, local retrieval, review, doctor, and style-check tools.

- 当前版本：`1.0.0`
- 许可证：MIT
- 运行要求：Python 3 标准库；不新增外部依赖

## 项目定位

`codex-webnovel-writer` 是面向 Codex 的长篇网文 / 小说写作工作流工具。它提供 Codex Skills、`AGENTS.md` 项目约束、通用模板和一个轻量 Python CLI，用稳定 Markdown / JSON 文件组织规划、写作、检索、审查和项目记忆。

本仓库是通用开源工具，不是某一本小说的作品仓库，也不包含具体小说内容。用户自己的小说项目应由 `init` 命令生成到独立目录中。

本项目不依赖 Claude Code、Claude slash commands 或 Claude-specific 文件约定。

## 为什么做 Codex 版本

Claude Code 版本的 webnovel writing workflow 不能直接在 Codex 中原样使用。本项目用 Codex Skills、`AGENTS.md`、templates 和 Python CLI 重新实现同类长篇写作流程，保留“规划、写作、审查、记忆、查询”的工作流思路，但不复制外部项目源码、模板或文案。

## 功能特性

| 功能 | 命令 | 说明 |
| --- | --- | --- |
| Check | `python3 scripts/webnovel.py check` | 检查插件源码或小说项目结构。 |
| Init | `python3 scripts/webnovel.py init <project_path>` | 初始化独立小说项目目录和基础模板。 |
| Structured Planning | `python3 scripts/webnovel.py plan-init <project_path>` | 初始化卷纲、章纲、时间线、场景卡、冲突线等结构化规划文件。 |
| Chapter Workflow | `python3 scripts/webnovel.py chapter <project_path> <chapter>` | 生成单章草稿模板和摘要模板。 |
| Local Retrieval | `python3 scripts/webnovel.py build-index <project_path>` | 建立本地关键词检索索引；默认本地运行，不联网、不需要 API、不使用 embedding provider。 |
| Query Retrieval | `python3 scripts/webnovel.py retrieve <project_path> <query>` | 从本地索引召回相关片段。 |
| Context Pack | `python3 scripts/webnovel.py context-pack <project_path> <chapter>` | 为章节写作生成上下文包。 |
| Write Brief | `python3 scripts/webnovel.py write-brief <project_path> <chapter>` | 生成章节写作任务书。 |
| Full Write Workflow | `python3 scripts/webnovel.py write <project_path> <chapter>` | 准备草稿、context-pack、write-brief 和写作指令。 |
| Finalize Write | `python3 scripts/webnovel.py finalize-write <project_path> <chapter>` | 写后生成摘要、索引、检索索引、deep review 和 doctor 报告。 |
| Deep Review | `python3 scripts/webnovel.py review <project_path> <chapter>` | 结构化审查章节，不自动修改正文。 |
| Doctor | `python3 scripts/webnovel.py doctor <project_path>` | 只读项目体检，检查结构、JSON、索引、摘要、规划、人物、伏笔、检索和通用内容安全。 |
| Style Check | `python3 scripts/webnovel.py style-check <project_path> 正文/第001章.md` | 检查反 AI 句式和风格风险，只生成报告，不自动修改正文。 |
| Query | `python3 scripts/webnovel.py query <project_path> <keyword>` | 在项目文件中按关键词查询设定、伏笔、人物和章节信息。 |
| Learn | `webnovel-learn` Skill | 将用户偏好、写作禁区、人物修正和长期记忆沉淀到项目文件。 |

## Quick Start

```bash
python3 scripts/webnovel.py check
python3 scripts/webnovel.py init ../sample-novel-project
python3 scripts/webnovel.py plan-init ../sample-novel-project
python3 scripts/webnovel.py write ../sample-novel-project 1
python3 scripts/webnovel.py finalize-write ../sample-novel-project 1
python3 scripts/webnovel.py doctor ../sample-novel-project
```

常用专项命令：

```bash
python3 scripts/webnovel.py style-rules ../sample-novel-project
python3 scripts/webnovel.py style-check ../sample-novel-project 正文/第001章.md
python3 scripts/webnovel.py review ../sample-novel-project 1
python3 scripts/webnovel.py query ../sample-novel-project 示例伏笔
```

## Recommended Workflow

1. 初始化：`init` 创建独立小说项目。
2. 规划：`plan-init` 后补充卷纲、章纲、时间线、场景卡和冲突线。
3. 准备写作：`write` 生成或保留章节草稿，并准备 context-pack、write-brief 和 write-instruction。
4. 写正文：用户或 Codex 根据任务书和上下文包写作，不把未确认推测写成事实。
5. 写后收尾：`finalize-write` 生成摘要、更新索引、重建本地检索、运行 deep review 和 doctor。
6. 专项审查：按需运行 `review`、`doctor`、`style-check`，人工决定是否保留、弱化、改写或删除正文。

## 通用工具项目原则

- 本仓库只保存插件、Skills、CLI、文档和通用模板。
- 不提交用户私人小说内容、真实作品设定、真实角色名、剧情片段、未公开文本或特定 IP 内容。
- 模板、测试样例和文档示例使用通用占位内容，例如 `主角A`、`角色B`、`某个旧物`、`第一卷`、`第001章`、`示例伏笔`、`示例地点`。
- 用户小说内容应放在由本工具初始化出来的独立项目目录中，而不是放进工具仓库本体。
- 审查类命令默认只读；检测结果是提示，需要人工结合上下文确认。

## Project Structure

插件源码：

```text
codex-webnovel-writer/
├── .codex-plugin/plugin.json
├── AGENTS.md
├── skills/
├── scripts/webnovel.py
├── templates/
├── docs/
├── CHANGELOG.md
├── README.md
└── LICENSE
```

初始化后的小说项目：

```text
sample-novel-project/
├── AGENTS.md
├── 设定集/
├── 大纲/
├── 正文/
├── 审查报告/
├── 伏笔记录/
├── 人物状态/
├── 章节索引/
└── .webnovel/
```

详细结构见 [docs/project-structure.md](docs/project-structure.md)。

## Documentation

- [Usage](docs/usage.md)
- [Project Structure](docs/project-structure.md)
- [Release Notes](docs/release.md)
- [Changelog](CHANGELOG.md)

## Roadmap

- v1.1: test suite and CI
- v1.2: packaging and install script
- v1.3: optional embedding provider
- v1.4: dashboard
- v1.5: richer style-check rules and configurable rule packs

## License

MIT License. See [LICENSE](LICENSE).
