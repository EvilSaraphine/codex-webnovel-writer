# codex-webnovel-writer

## 项目简介

`codex-webnovel-writer` 是一个 Codex 原生的长篇网文/小说写作工作流项目，提供 Codex Skills、项目模板和简单 CLI，用于初始化小说项目、生成大纲、写章节、审查一致性、查询设定和伏笔。

它不是完整的写作应用，也不包含数据库或发布系统。项目重点是把长篇创作中常见的设定、总纲、章节大纲、正文、审查报告、人物状态、伏笔记录和章节索引整理成稳定的 Markdown 文件结构，方便 Codex 在较小上下文内完成可追踪的协作。

## 为什么做 Codex 版本

这个项目受到 `lingfengQAQ/webnovel-writer` 的产品思路启发。原项目是 Claude Code 版本，主要依赖 Claude Code 的插件、slash commands 和 skills 机制，因此不能直接在 Codex 中原样使用。

因为我主要使用 OpenAI Codex，所以重新做了一版 Codex-native 实现：使用 Codex 插件目录、Codex Skills、普通 Markdown 模板和一个轻量 Python CLI 来组织小说写作流程。

本项目不是原项目的 fork，也不复制原项目源码、README、SKILL.md、agent 文案或模板文本；这里只参考“长篇小说写作工作流”这一抽象思路，并用 Codex 原生结构重新实现。

## 功能特性

- 提供 `.codex-plugin/plugin.json`，可作为本地 Codex 插件源使用。
- 提供 6 个面向小说工作流的 Codex Skills：
  - `webnovel-init`：初始化小说项目目录和基础文件。
  - `webnovel-plan`：生成或修订总纲、卷纲、章节大纲和时间线。
  - `webnovel-write`：根据大纲、设定、人物状态和伏笔记录起草章节。
  - `webnovel-review`：审查连续性、人物状态、节奏、伏笔和 AI 味。
  - `webnovel-query`：从项目文件中查询设定、人物、伏笔、章节进度和时间线。
  - `webnovel-learn`：记录用户偏好、写作禁区、人物修正和长期项目记忆。
- 提供 `scripts/webnovel.py`，支持初始化项目、查看路径、结构检查、章节索引、关键词查询、人物记录、伏笔记录和审查报告模板生成。
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
│   └── webnovel-learn/
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
└── 章节索引/
```

主要目录用途：

- `设定集/`：世界观、规则、势力、地点、能力体系、创作原则等稳定设定。
- `大纲/`：总纲、卷纲、章节大纲、时间线和剧情弧线。
- `正文/`：章节草稿和修订稿。
- `审查报告/`：一致性、节奏、人物状态、伏笔和文本问题的审查结果。
- `伏笔记录/`：伏笔设置位置、预期回收、当前状态。
- `人物状态/`：人物目标、关系、资源、秘密、伤势和知识状态。
- `章节索引/`：章节进度、大纲、正文、审查和发布准备状态。

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
python3 scripts/webnovel.py init ~/novels/my-story
```

之后可以用自然语言让 Codex 调用对应 Skill，例如：

```text
Use webnovel-plan to create a 20-chapter outline for volume 1.
Use webnovel-write to draft chapter 1 from 大纲/第001章.md.
Use webnovel-review to review 正文/第001章.md and save a report.
Use webnovel-query to list unpaid foreshadowing before chapter 10.
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

搜索项目文件：

```bash
python3 scripts/webnovel.py query ~/novels/my-story 林予安
```

添加人物记录：

```bash
python3 scripts/webnovel.py add-character ~/novels/my-story 林予安
```

添加伏笔记录：

```bash
python3 scripts/webnovel.py add-hook ~/novels/my-story "三点十七"
```

生成某章审查报告：

```bash
python3 scripts/webnovel.py review-template ~/novels/my-story 1
```

`init` 会创建必要目录，并在缺失时写入一些基础文件，例如 `设定集/世界观.md`、`设定集/写作偏好.md`、`设定集/风格禁区.md`、`大纲/总纲.md`、`大纲/时间线.md`、`章节索引/章节索引.md`、`章节索引/chapters.json`、`伏笔记录/伏笔总表.md`、`伏笔记录/hooks.json`、`人物状态/人物总表.md` 和 `人物状态/characters.json`。

完整示例：

```bash
python3 scripts/webnovel.py init examples/KpopNovel
python3 scripts/webnovel.py index examples/KpopNovel
python3 scripts/webnovel.py query examples/KpopNovel 林予安
python3 scripts/webnovel.py add-character examples/KpopNovel 林予安
python3 scripts/webnovel.py add-hook examples/KpopNovel "三点十七"
python3 scripts/webnovel.py review-template examples/KpopNovel 1
```

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
