# codex-webnovel-writer

Codex-native MVP for planning, writing, reviewing, and querying long-form web novels. It borrows the product idea of a structured webnovel writing workspace, but it does not depend on Claude Code or Claude slash commands. The operating model is Codex Skills plus a local Codex plugin manifest.

## What It Provides

- A Codex plugin manifest at `.codex-plugin/plugin.json`.
- Five focused Skills under `skills/`:
  - `webnovel-init`: initialize a novel project workspace.
  - `webnovel-plan`: create volume outlines, chapter outlines, and timelines.
  - `webnovel-write`: draft chapters from chapter outlines.
  - `webnovel-review`: review consistency, AI tone, pacing, foreshadowing, and character state.
  - `webnovel-query`: query characters, settings, foreshadowing, and chapter status.
- A small CLI at `scripts/webnovel.py` with `init`, `where`, and `check`.
- Templates for a reusable Chinese webnovel project structure.

## Install

Use this repository as a local Codex plugin source.

```bash
git clone <this-repo-url> codex-webnovel-writer
cd codex-webnovel-writer
python3 scripts/webnovel.py check
```

The plugin manifest declares:

```json
{
  "name": "codex-webnovel-writer",
  "skills": "./skills/"
}
```

If your Codex setup supports local plugin installation, point it at this repository. During development, you can also use the Skills directly by referencing this repository path.

## Usage

Initialize a novel workspace:

```bash
python3 scripts/webnovel.py init ~/novels/my-story
```

Show detected paths:

```bash
python3 scripts/webnovel.py where ~/novels/my-story
```

Validate this plugin source or a novel workspace:

```bash
python3 scripts/webnovel.py check
python3 scripts/webnovel.py check ~/novels/my-story
```

## Codex Skills Calling Style

Ask Codex for the workflow you need and name the Skill when useful:

- `Use webnovel-init to create a new project in ./novels/星火纪元.`
- `Use webnovel-plan to generate volume 1 outline and chapter outlines 1-10.`
- `Use webnovel-write to draft chapter 3 from 大纲/第003章.md.`
- `Use webnovel-review to inspect 正文/第003章.md for consistency and AI flavor.`
- `Use webnovel-query to summarize current character state for 林澈.`

Each Skill keeps its own process instructions so `AGENTS.md` can stay small and project-level.

## Project Positioning

This is an MVP for Codex-native webnovel production. It focuses on structure, repeatable workflows, and context economy. It is not a full writing application, database, or publishing system.

