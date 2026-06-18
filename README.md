# codex-webnovel-writer

## 项目简介

`codex-webnovel-writer` 是一个 Codex 原生的长篇网文/小说写作工作流项目，提供 Codex Skills、项目模板和简单 CLI，用于初始化小说项目、生成大纲、写章节、审查一致性、查询设定和伏笔。

它是通用写作工具，不是某一本小说的作品仓库，也不包含任何具体小说内容。项目重点是把长篇创作中常见的设定、总纲、章节大纲、正文、审查报告、人物状态、伏笔记录和章节索引整理成稳定的 Markdown 文件结构，方便 Codex 在较小上下文内完成可追踪的协作。

用户自己的小说项目应放在独立目录中，例如：

```bash
python3 scripts/webnovel.py init ../my-novel-project
```

本工具仓库本体只保存插件、Skills、CLI、文档和通用模板。

## 为什么做 Codex 版本

这个项目受到 `lingfengQAQ/webnovel-writer` 的产品思路启发。原项目是 Claude Code 版本，主要依赖 Claude Code 的插件、slash commands 和 skills 机制，因此不能直接在 Codex 中原样使用。

因为我主要使用 OpenAI Codex，所以重新做了一版 Codex-native 实现：使用 Codex 插件目录、Codex Skills、普通 Markdown 模板和一个轻量 Python CLI 来组织小说写作流程。

本项目不是原项目的 fork，也不复制原项目源码、README、SKILL.md、agent 文案或模板文本；这里只参考“长篇小说写作工作流”这一抽象思路，并用 Codex 原生结构重新实现。

## 功能特性

- 提供 `.codex-plugin/plugin.json`，可作为本地 Codex 插件源使用。
- 提供 11 个面向小说工作流的 Codex Skills：
  - `webnovel-init`：初始化小说项目目录和基础文件。
  - `webnovel-plan`：生成或修订总纲、卷纲、章节大纲和时间线。
  - `webnovel-write`：根据大纲、设定、人物状态和伏笔记录起草章节。
  - `webnovel-review`：审查连续性、人物状态、节奏、伏笔和 AI 味。
  - `webnovel-query`：从项目文件中查询设定、人物、伏笔、章节进度和时间线。
  - `webnovel-learn`：记录用户偏好、写作禁区、人物修正和长期项目记忆。
  - `webnovel-chapter`：围绕单章进行写作准备、摘要、状态更新建议和连续性检查。
  - `webnovel-plan-structured`：维护卷纲、章纲、时间线、人物线、场景卡和冲突线。
  - `webnovel-retrieve`：使用本地检索结果和章节上下文包辅助写作、查询和审查。
  - `webnovel-doctor`：对小说项目做只读体检，生成诊断报告和修复建议。
  - `webnovel-review-deep`：对单章或章节范围做结构化深度审查。
- 提供 `scripts/webnovel.py`，支持初始化项目、查看路径、结构检查、结构化规划、章节模板、章节摘要、章节索引、关键词查询、人物记录、伏笔记录、状态概览、连续性检查和审查报告模板生成。
- 提供中文小说项目模板，使用稳定 Markdown 文件保存长期记忆。
- 强调上下文经济：按任务读取必要文件，而不是每次加载整个小说项目。

## v0.2 新增能力

v0.2 增加了基础项目记忆与索引能力：

- `章节索引/chapters.json`：由 CLI 扫描 `正文/` 后生成，记录章节号、标题、路径、字数和更新时间。
- `人物状态/characters.json`：保存结构化人物条目，便于后续查询和维护。
- `伏笔记录/hooks.json`：保存结构化伏笔条目，记录状态、引入位置、关联人物和备注。
- `审查报告/review-template.md`：用于生成单章审查报告。
- `设定集/写作偏好.md` 和 `设定集/风格禁区.md`：用于沉淀长期写作偏好和禁区。
- `webnovel-learn` Skill：用于把用户反馈整理为可复用的项目长期记忆。

## v0.3 新增能力

v0.3 增加了围绕单章写作的流水线：

- `webnovel-chapter` Skill：说明单章写作前后应读取的项目文件、工作包准备方式、摘要产出、状态更新建议和最终检查命令。
- `正文/chapter-template.md`：用于生成 `正文/第XXX章.md` 的章节写作模板。
- `章节索引/summaries/`：保存单章摘要，辅助长篇连续性维护。
- `章节索引/summary-template.md`：用于生成结构化章节摘要。
- `审查报告/continuity-report-template.md`：用于生成项目连续性检查报告。
- `continuity-check`：检查关键 JSON、章节索引、正文与摘要是否对应，并输出 `审查报告/continuity-report.md`。

## v0.4 新增能力

v0.4 增加了结构化规划系统：

- `webnovel-plan-structured` Skill：用于生成和维护长篇规划结构。
- `大纲/volumes.json`：卷级规划。
- `大纲/chapter_plans.json`：章级规划。
- `大纲/timeline.json`：时间线。
- `大纲/arcs.json`：人物线、关系线、事业线等长期线索。
- `大纲/scenes.json`：场景卡。
- `大纲/conflicts.json`：冲突线。
- `大纲/planning-guide.md`：规划文件使用说明。
- `outline-export`：把结构化 JSON 导出为人工可读的 `大纲/outline-export.md`。

## v0.5 新增能力

v0.5 增加了 Local Retrieval / Light RAG。第一版默认本地运行，不联网，不需要 API，不使用 embedding provider，也不下载模型。

- `webnovel-retrieve` Skill：指导 Codex 使用检索结果和 context pack 辅助写作、查询和审查。
- `.webnovel/retrieval-config.json`：本地检索配置。
- `.webnovel/chunks.json`：由 `build-index` 生成的文本切块。
- `.webnovel/retrieval-index.json`：由 `build-index` 生成的索引元数据。
- `章节索引/context-packs/`：保存章节写作前的上下文包。
- `build-index`：扫描设定、大纲、正文、人物状态、伏笔记录、章节摘要、审查报告和结构化规划文件，建立本地索引。
- `retrieve`：用关键词和简单打分召回相关片段。
- `context-pack`：根据 `大纲/chapter_plans.json` 为某章生成写作上下文包。
- `retrieval-status`：查看本地检索配置和索引状态。

这不是完整语义 RAG，而是轻量本地检索。它适合写作前上下文召回、设定查询、连续性检查辅助。未来可以选择性支持 embedding provider，但不会作为默认依赖。

## v0.6 新增能力

v0.6 增加了 Doctor 项目体检系统。doctor 默认只读，不联网，不使用 API，不使用 embedding provider，不安装依赖，也不会自动修复项目文件。

doctor 会检查：

- 项目结构
- JSON 文件
- 章节索引
- 章节摘要
- 结构化规划
- 人物状态
- 伏笔记录
- 本地检索索引
- 通用内容安全

doctor 会生成 `审查报告/doctor-report.md`，报告中列出 PASS、WARN、ERROR、风险等级和建议修复项。除生成该报告外，它不会修改正文、设定、人物、伏笔或大纲文件。

## v0.7 新增能力

v0.7 增加了 Review 深度审查系统。review 默认只读，不联网，不使用 API，不使用 embedding provider，不自动改正文，也不自动写回设定、人物、伏笔、大纲或章节摘要。

review 会检查：

- 章节结构完整性
- 章纲对齐
- 人物状态变化
- 伏笔引入、推进、回收
- 时间线连续性
- 场景目标和冲突
- 章节索引和章节摘要
- 本地检索上下文
- 设定一致性风险
- 后续待办

review 会生成 Markdown 审查报告，例如 `审查报告/第001章-deep-review.md` 和 `审查报告/review-summary-第001-第005章.md`。风格/反 AI 句式检测将在后续版本作为专项审查加入。

## 通用项目原则

本仓库是通用开源工具，不是某一本小说的项目仓库。仓库中不应提交用户私人小说内容、真实作品设定、真实角色名、剧情片段、未公开文本或特定 IP 内容。

所有模板、测试样例和文档示例都应使用通用占位内容，例如 `主角A`、`角色B`、`某个旧物`、`第一卷`、`第001章`、`示例伏笔` 和 `示例地点`。

用户自己的小说内容应放在由本工具初始化出来的独立项目目录中，而不是放进工具仓库本体。如果需要保留示例目录，请使用 `generic-novel`、`sample-project` 这类通用名称。

## 项目结构

插件源码结构：

```text
codex-webnovel-writer/
├── .codex-plugin/plugin.json
├── AGENTS.md
├── skills/
│   ├── webnovel-init/
│   ├── webnovel-plan/
│   ├── webnovel-write/
│   ├── webnovel-review/
│   ├── webnovel-query/
│   ├── webnovel-learn/
│   ├── webnovel-chapter/
│   ├── webnovel-plan-structured/
│   ├── webnovel-retrieve/
│   ├── webnovel-doctor/
│   └── webnovel-review-deep/
├── scripts/webnovel.py
├── templates/
├── docs/
├── README.md
└── LICENSE
```

初始化后的小说项目通常包含：

```text
my-story/
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

主要目录用途：

- `设定集/`：世界观、规则、势力、地点、能力体系、创作原则等稳定设定。
- `大纲/`：总纲、卷纲、章节大纲、时间线和剧情弧线。
- `正文/`：章节草稿和修订稿。
- `审查报告/`：一致性、节奏、人物状态、伏笔和文本问题的审查结果。
- `伏笔记录/`：伏笔设置位置、预期回收、当前状态。
- `人物状态/`：人物目标、关系、资源、秘密、伤势和知识状态。
- `章节索引/`：章节进度、大纲、正文、审查和发布准备状态。
- `.webnovel/`：本地检索配置、切块和索引元数据。

## 安装与使用

克隆本仓库：

```bash
git clone <this-repo-url> codex-webnovel-writer
cd codex-webnovel-writer
python3 scripts/webnovel.py check
```

插件清单位于 `.codex-plugin/plugin.json`：

```json
{
  "name": "codex-webnovel-writer",
  "skills": "./skills/"
}
```

如果你的 Codex 环境支持本地插件安装，可以将插件源指向本仓库。开发或试用时，也可以直接在 Codex 中引用本仓库里的 Skills。

初始化一个小说项目：

```bash
python3 scripts/webnovel.py init ../sample-novel-project
```

之后可以用自然语言让 Codex 调用对应 Skill，例如：

```text
Use webnovel-plan to create a 20-chapter outline for volume 1.
Use webnovel-write to draft chapter 1 from 大纲/第001章.md.
Use webnovel-review to review 正文/第001章.md and save a report.
Use webnovel-query to list unpaid foreshadowing before chapter 10.
Use webnovel-retrieve to prepare a context pack for chapter 1.
Use webnovel-doctor to inspect project health before a long writing session.
Use webnovel-review-deep to review chapter 1 before revision.
```

## Skills 说明

### webnovel-init

用于创建小说项目工作区，生成 `AGENTS.md`、设定、大纲、正文、审查报告、伏笔记录、人物状态和章节索引等目录，并可写入基础 Markdown 文件。

### webnovel-plan

用于规划总纲、卷纲、章节大纲、时间线、剧情节拍、冲突推进和伏笔安排。它会优先读取设定、总纲、相关大纲、伏笔记录、人物状态和章节索引。

### webnovel-write

用于根据章节大纲、设定、人物状态、伏笔记录和附近章节起草或修订正文。默认按中文网文写作场景处理，除非用户明确要求其他语言。

### webnovel-review

用于审查章节或大纲。审查重点包括客观连续性问题、人物状态偏移、剧情因果、节奏、伏笔设置或回收、AI 味和缺失的项目记录更新。

### webnovel-query

用于从项目文件中回答问题，例如人物当前状态、设定规则、未回收伏笔、章节进度、时间线和连续性冲突。回答时应尽量列出使用到的来源文件。

### webnovel-learn

用于记录用户偏好、写作禁区、人物设定修正、风格经验和项目长期记忆。它会把经验沉淀到 `设定集/写作偏好.md`、`设定集/风格禁区.md`、`人物状态/人物修正记录.md` 和 `伏笔记录/长期伏笔.md`。

### webnovel-chapter

用于围绕单章进行写作准备、章节草稿生成、写后摘要、状态更新建议和连续性检查。标准流程会读取 `AGENTS.md`、`设定集/`、`大纲/`、`人物状态/characters.json`、`伏笔记录/hooks.json` 和 `章节索引/chapters.json`，写作后运行 `index` 与 `continuity-check`。

### webnovel-plan-structured

用于生成和维护结构化长篇规划，包括卷纲、章纲、时间线、人物线、场景卡和冲突线。JSON 用于机器可读结构，Markdown 用于人工阅读说明；规划层不直接保存正文内容。

### webnovel-retrieve

用于在写作、查询和审查前使用本地索引召回相关片段。检索结果只能作为参考，不会替代用户确认过的设定、章纲、人物状态或伏笔记录，也不应被自动写回为新设定。

### webnovel-doctor

用于对小说项目做只读体检。检查范围包括项目结构、核心模板、JSON 可读性、章节索引、章节摘要、章纲与正文对应、人物状态、伏笔记录、结构化规划、本地检索索引和通用内容安全。doctor 只生成诊断和建议，不会自动修复。

### webnovel-review-deep

用于对单章或章节范围做结构化深度审查。检查章节结构、章纲对齐、人物状态、伏笔、时间线、场景冲突、章节索引、摘要、本地检索上下文和设定一致性风险。review 只生成诊断和建议，不会自动改正文或写回设定。

## CLI 使用

初始化小说项目：

```bash
python3 scripts/webnovel.py init ~/novels/my-story
```

显示插件和目标项目路径：

```bash
python3 scripts/webnovel.py where ~/novels/my-story
```

检查插件源码：

```bash
python3 scripts/webnovel.py check
```

检查小说项目：

```bash
python3 scripts/webnovel.py check ~/novels/my-story
```

生成或更新章节索引：

```bash
python3 scripts/webnovel.py index ~/novels/my-story
```

生成章节草稿模板和摘要文件：

```bash
python3 scripts/webnovel.py chapter ~/novels/my-story 1
```

根据已有正文生成待填写摘要：

```bash
python3 scripts/webnovel.py chapter-summary ~/novels/my-story 1
```

搜索项目文件：

```bash
python3 scripts/webnovel.py query ~/novels/my-story 主角A
```

添加人物记录：

```bash
python3 scripts/webnovel.py add-character ~/novels/my-story 主角A
```

添加伏笔记录：

```bash
python3 scripts/webnovel.py add-hook ~/novels/my-story "示例伏笔"
```

查看人物和伏笔状态概览：

```bash
python3 scripts/webnovel.py update-state ~/novels/my-story
```

检查章节索引、摘要、人物和伏笔记录：

```bash
python3 scripts/webnovel.py continuity-check ~/novels/my-story
```

生成某章审查报告：

```bash
python3 scripts/webnovel.py review-template ~/novels/my-story 1
```

`init` 会创建必要目录，并在缺失时写入一些基础文件，例如 `设定集/世界观.md`、`设定集/写作偏好.md`、`设定集/风格禁区.md`、`大纲/总纲.md`、`大纲/时间线.md`、`正文/chapter-template.md`、`章节索引/章节索引.md`、`章节索引/chapters.json`、`章节索引/summary-template.md`、`伏笔记录/伏笔总表.md`、`伏笔记录/hooks.json`、`人物状态/人物总表.md` 和 `人物状态/characters.json`。

完整示例：

```bash
python3 scripts/webnovel.py init ../sample-novel-project
python3 scripts/webnovel.py index ../sample-novel-project
python3 scripts/webnovel.py query ../sample-novel-project 主角A
python3 scripts/webnovel.py add-character ../sample-novel-project 主角A
python3 scripts/webnovel.py add-hook ../sample-novel-project "示例伏笔"
python3 scripts/webnovel.py review-template ../sample-novel-project 1
```

v0.3 单章流水线示例：

```bash
python3 scripts/webnovel.py chapter ../sample-novel-project 1
python3 scripts/webnovel.py chapter-summary ../sample-novel-project 1
python3 scripts/webnovel.py update-state ../sample-novel-project
python3 scripts/webnovel.py continuity-check ../sample-novel-project
python3 scripts/webnovel.py index ../sample-novel-project
```

v0.4 结构化规划示例：

```bash
python3 scripts/webnovel.py plan-init ../sample-novel-project
python3 scripts/webnovel.py add-volume ../sample-novel-project 1 第一卷
python3 scripts/webnovel.py add-chapter-plan ../sample-novel-project 1 第001章
python3 scripts/webnovel.py add-scene ../sample-novel-project 1 1
python3 scripts/webnovel.py add-timeline-event ../sample-novel-project 1 示例事件
python3 scripts/webnovel.py add-arc ../sample-novel-project main-arc 主线关系
python3 scripts/webnovel.py planning-status ../sample-novel-project
python3 scripts/webnovel.py outline-export ../sample-novel-project
```

v0.5 Local Retrieval / Light RAG 示例：

```bash
python3 scripts/webnovel.py build-index ../sample-novel-project
python3 scripts/webnovel.py retrieve ../sample-novel-project 示例伏笔
python3 scripts/webnovel.py context-pack ../sample-novel-project 1
python3 scripts/webnovel.py retrieval-status ../sample-novel-project
```

v0.6 Doctor 项目体检示例：

```bash
python3 scripts/webnovel.py doctor ../sample-novel-project
python3 scripts/webnovel.py doctor ../sample-novel-project --deep
```

`--deep` 也兼容中文输入法环境中容易出现的 `–deep` 写法。

v0.7 Review 深度审查示例：

```bash
python3 scripts/webnovel.py review ../sample-novel-project 1
python3 scripts/webnovel.py review-range ../sample-novel-project 1 5
python3 scripts/webnovel.py review-status ../sample-novel-project
```

review 会生成 Markdown 审查报告，但不会自动修改正文，也不会自动写回设定。风格/反 AI 句式检测将在后续版本作为专项审查加入。

## 后续路线

- 未来可以选择性支持 embedding provider，用于更好的语义检索；这应保持为可选能力，不影响基础 CLI 和 Skills 工作流。
- 继续完善章节摘要、人物状态和伏笔状态之间的同步检查。

## 与 Claude Code 版本的区别

- 本项目面向 Codex，不依赖 Claude Code 插件机制。
- 本项目不使用 Claude slash commands。
- 本项目的工作流入口是 Codex Skills 和一个简单 Python CLI。
- 本项目的模板、Skill 指令和项目文案均为重新编写。
- 本项目使用 `.codex-plugin/plugin.json` 声明插件结构。
- 本项目把长期记忆保存在普通 Markdown 文件中，方便人工编辑、版本管理和跨工具阅读。

## 开源许可

本项目使用 MIT License。详见 [LICENSE](LICENSE)。

## 致谢

感谢 `lingfengQAQ/webnovel-writer` 提供的产品思路启发。该项目证明了“把长篇小说创作拆成可复用工作流，并用文件记录长期连续性”这一方向有实际价值。

本仓库是在这个抽象思路上，为 OpenAI Codex 使用场景重新实现的一套结构和流程。
