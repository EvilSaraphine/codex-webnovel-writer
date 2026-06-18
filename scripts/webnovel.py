#!/usr/bin/env python3
"""Small CLI for codex-webnovel-writer."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = PLUGIN_ROOT / "templates"
NOVEL_DIRS = ["设定集", "大纲", "正文", "审查报告", "伏笔记录", "人物状态", "章节索引"]
RETRIEVAL_DIR = ".webnovel"
RETRIEVAL_CONFIG = "retrieval-config.json"
SKILLS = [
    "webnovel-init",
    "webnovel-plan",
    "webnovel-write",
    "webnovel-review",
    "webnovel-query",
    "webnovel-learn",
    "webnovel-chapter",
    "webnovel-plan-structured",
    "webnovel-retrieve",
]
PLANNING_JSON_FILES = [
    "大纲/volumes.json",
    "大纲/chapter_plans.json",
    "大纲/timeline.json",
    "大纲/arcs.json",
    "大纲/scenes.json",
    "大纲/conflicts.json",
]
TEMPLATE_FILES = [
    "AGENTS.md",
    "设定集/写作偏好.md",
    "设定集/风格禁区.md",
    "大纲/planning-guide.md",
    *PLANNING_JSON_FILES,
    "正文/chapter-template.md",
    "章节索引/chapters.json",
    "章节索引/summary-template.md",
    "章节索引/summaries/.gitkeep",
    "章节索引/context-packs/.gitkeep",
    "伏笔记录/hooks.json",
    "人物状态/characters.json",
    "审查报告/review-template.md",
    "审查报告/continuity-report-template.md",
    ".webnovel/.gitkeep",
    ".webnovel/retrieval-config.json",
]
SEARCH_DIRS = ["设定集", "大纲", "正文", "伏笔记录", "人物状态", "章节索引"]
SUPPORTED_RETRIEVAL_SUFFIXES = {".md", ".txt", ".json"}


def main() -> int:
    parser = argparse.ArgumentParser(prog="webnovel.py")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="initialize a novel project")
    init_parser.add_argument("path", type=Path, help="target novel project path")
    init_parser.add_argument("--force", action="store_true", help="overwrite template AGENTS.md if it exists")

    where_parser = subparsers.add_parser("where", help="show detected project paths")
    where_parser.add_argument("path", type=Path, nargs="?", default=Path.cwd(), help="project path to inspect")

    check_parser = subparsers.add_parser("check", help="validate plugin source or novel project")
    check_parser.add_argument("path", type=Path, nargs="?", default=PLUGIN_ROOT, help="path to validate")

    index_parser = subparsers.add_parser("index", help="update chapter index from 正文/")
    index_parser.add_argument("path", type=Path, help="novel project path")

    query_parser = subparsers.add_parser("query", help="search project files by keyword")
    query_parser.add_argument("path", type=Path, help="novel project path")
    query_parser.add_argument("keyword", help="keyword to search")

    character_parser = subparsers.add_parser("add-character", help="add a character record")
    character_parser.add_argument("path", type=Path, help="novel project path")
    character_parser.add_argument("name", help="character name")

    hook_parser = subparsers.add_parser("add-hook", help="add a foreshadowing hook record")
    hook_parser.add_argument("path", type=Path, help="novel project path")
    hook_parser.add_argument("title", help="hook title")

    review_parser = subparsers.add_parser("review-template", help="create a chapter review report from template")
    review_parser.add_argument("path", type=Path, help="novel project path")
    review_parser.add_argument("chapter", help="chapter number")

    chapter_parser = subparsers.add_parser("chapter", help="create a chapter draft package")
    chapter_parser.add_argument("path", type=Path, help="novel project path")
    chapter_parser.add_argument("chapter", help="chapter number")

    summary_parser = subparsers.add_parser("chapter-summary", help="create a chapter summary file")
    summary_parser.add_argument("path", type=Path, help="novel project path")
    summary_parser.add_argument("chapter", help="chapter number")

    state_parser = subparsers.add_parser("update-state", help="show character and hook state overview")
    state_parser.add_argument("path", type=Path, help="novel project path")

    continuity_parser = subparsers.add_parser("continuity-check", help="check project continuity records")
    continuity_parser.add_argument("path", type=Path, help="novel project path")

    plan_init_parser = subparsers.add_parser("plan-init", help="initialize structured planning files")
    plan_init_parser.add_argument("path", type=Path, help="novel project path")

    volume_parser = subparsers.add_parser("add-volume", help="add a volume planning record")
    volume_parser.add_argument("path", type=Path, help="novel project path")
    volume_parser.add_argument("volume_number", help="volume number")
    volume_parser.add_argument("title", nargs="?", default="", help="optional volume title")

    chapter_plan_parser = subparsers.add_parser("add-chapter-plan", help="add a chapter planning record")
    chapter_plan_parser.add_argument("path", type=Path, help="novel project path")
    chapter_plan_parser.add_argument("chapter_number", help="chapter number")
    chapter_plan_parser.add_argument("title", nargs="?", default="", help="optional chapter title")

    timeline_parser = subparsers.add_parser("add-timeline-event", help="add a timeline event")
    timeline_parser.add_argument("path", type=Path, help="novel project path")
    timeline_parser.add_argument("chapter_number", help="chapter number")
    timeline_parser.add_argument("event", nargs="?", default="", help="optional event label")

    arc_parser = subparsers.add_parser("add-arc", help="add an arc record")
    arc_parser.add_argument("path", type=Path, help="novel project path")
    arc_parser.add_argument("arc_id", help="arc id")
    arc_parser.add_argument("title", nargs="?", default="", help="optional arc title")

    scene_parser = subparsers.add_parser("add-scene", help="add a scene card")
    scene_parser.add_argument("path", type=Path, help="novel project path")
    scene_parser.add_argument("chapter_number", help="chapter number")
    scene_parser.add_argument("scene_order", help="scene order")

    planning_status_parser = subparsers.add_parser("planning-status", help="show structured planning status")
    planning_status_parser.add_argument("path", type=Path, help="novel project path")

    outline_export_parser = subparsers.add_parser("outline-export", help="export structured planning to Markdown")
    outline_export_parser.add_argument("path", type=Path, help="novel project path")

    build_index_parser = subparsers.add_parser("build-index", help="build local retrieval index")
    build_index_parser.add_argument("path", type=Path, help="novel project path")

    retrieve_parser = subparsers.add_parser("retrieve", help="retrieve relevant local snippets")
    retrieve_parser.add_argument("path", type=Path, help="novel project path")
    retrieve_parser.add_argument("query", nargs="+", help="query text")

    context_pack_parser = subparsers.add_parser("context-pack", help="generate a chapter context pack")
    context_pack_parser.add_argument("path", type=Path, help="novel project path")
    context_pack_parser.add_argument("chapter_number", help="chapter number")

    retrieval_status_parser = subparsers.add_parser("retrieval-status", help="show local retrieval index status")
    retrieval_status_parser.add_argument("path", type=Path, help="novel project path")

    args = parser.parse_args()
    if args.command == "init":
        return cmd_init(args.path, args.force)
    if args.command == "where":
        return cmd_where(args.path)
    if args.command == "check":
        return cmd_check(args.path)
    if args.command == "index":
        return cmd_index(args.path)
    if args.command == "query":
        return cmd_query(args.path, args.keyword)
    if args.command == "add-character":
        return cmd_add_character(args.path, args.name)
    if args.command == "add-hook":
        return cmd_add_hook(args.path, args.title)
    if args.command == "review-template":
        return cmd_review_template(args.path, args.chapter)
    if args.command == "chapter":
        return cmd_chapter(args.path, args.chapter)
    if args.command == "chapter-summary":
        return cmd_chapter_summary(args.path, args.chapter)
    if args.command == "update-state":
        return cmd_update_state(args.path)
    if args.command == "continuity-check":
        return cmd_continuity_check(args.path)
    if args.command == "plan-init":
        return cmd_plan_init(args.path)
    if args.command == "add-volume":
        return cmd_add_volume(args.path, args.volume_number, args.title)
    if args.command == "add-chapter-plan":
        return cmd_add_chapter_plan(args.path, args.chapter_number, args.title)
    if args.command == "add-timeline-event":
        return cmd_add_timeline_event(args.path, args.chapter_number, args.event)
    if args.command == "add-arc":
        return cmd_add_arc(args.path, args.arc_id, args.title)
    if args.command == "add-scene":
        return cmd_add_scene(args.path, args.chapter_number, args.scene_order)
    if args.command == "planning-status":
        return cmd_planning_status(args.path)
    if args.command == "outline-export":
        return cmd_outline_export(args.path)
    if args.command == "build-index":
        return cmd_build_index(args.path)
    if args.command == "retrieve":
        return cmd_retrieve(args.path, " ".join(args.query))
    if args.command == "context-pack":
        return cmd_context_pack(args.path, args.chapter_number)
    if args.command == "retrieval-status":
        return cmd_retrieval_status(args.path)
    parser.error("unknown command")
    return 2


def cmd_init(path: Path, force: bool) -> int:
    target = path.expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)
    copy_template_agents(target, force)
    for dirname in NOVEL_DIRS:
        (target / dirname).mkdir(parents=True, exist_ok=True)
    copy_template_files(target, force)
    seed_files(target)
    print(f"Initialized webnovel project: {target}")
    return cmd_check(target)


def copy_template_agents(target: Path, force: bool) -> None:
    source = TEMPLATE_DIR / "AGENTS.md"
    destination = target / "AGENTS.md"
    if destination.exists() and not force:
        return
    shutil.copyfile(source, destination)


def copy_template_files(target: Path, force: bool) -> None:
    for relative in TEMPLATE_FILES:
        if relative == "AGENTS.md":
            continue
        source = TEMPLATE_DIR / relative
        destination = target / relative
        if not source.is_file():
            continue
        if destination.exists() and not force:
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)


def seed_files(target: Path) -> None:
    seeds = {
        "设定集/世界观.md": "# 世界观\n\n- 类型与核心卖点：\n- 世界规则：\n- 禁忌与代价：\n",
        "设定集/创作原则.md": "# 创作原则\n\n- 目标读者：\n- 叙事口味：\n- 避免事项：\n",
        "大纲/总纲.md": "# 总纲\n\n- 核心钩子：\n- 主角弧线：\n- 主要矛盾：\n- 结局方向：\n",
        "大纲/时间线.md": "# 时间线\n\n| 顺序 | 事件 | 影响 |\n| --- | --- | --- |\n",
        "章节索引/章节索引.md": "# 章节索引\n\n| 章节 | 标题 | 状态 | 大纲 | 正文 | 审查 |\n| --- | --- | --- | --- | --- | --- |\n",
        "伏笔记录/伏笔总表.md": "# 伏笔总表\n\n| 编号 | 设置位置 | 内容 | 预期回收 | 状态 |\n| --- | --- | --- | --- | --- |\n",
        "伏笔记录/长期伏笔.md": "# 长期伏笔\n\n用于记录跨卷、跨阶段回收的长期伏笔、主题意象和重要承诺。\n",
        "人物状态/人物总表.md": "# 人物总表\n\n| 人物 | 当前状态 | 目标 | 秘密 | 关系变化 |\n| --- | --- | --- | --- | --- |\n",
        "人物状态/人物修正记录.md": "# 人物修正记录\n\n用于记录用户确认过的人物设定修正、状态修正和关系修正。\n",
    }
    for relative, content in seeds.items():
        path = target / relative
        if not path.exists():
            path.write_text(content, encoding="utf-8")


def cmd_where(path: Path) -> int:
    target = path.expanduser().resolve()
    print(f"plugin_root: {PLUGIN_ROOT}")
    print(f"target: {target}")
    print(f"agents: {target / 'AGENTS.md'}")
    for dirname in NOVEL_DIRS:
        print(f"{dirname}: {target / dirname}")
    return 0


def cmd_index(path: Path) -> int:
    target = path.expanduser().resolve()
    error = validate_novel_root(target)
    if error:
        print(f"Error: {error}")
        return 1

    output_path = target / "章节索引" / "chapters.json"
    chapters = []
    for draft in find_chapter_files(target):
        text = read_text(draft)
        stat = draft.stat()
        chapters.append(
            {
                "chapter_number": parse_chapter_number(draft),
                "title": extract_title(text, draft),
                "path": relative_path(target, draft),
                "word_count": count_words(text),
                "updated_at": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
            }
        )
    chapters.sort(key=lambda item: (item["chapter_number"] is None, item["chapter_number"] or 0, item["path"]))
    write_json(output_path, chapters)
    print(f"Indexed {len(chapters)} chapter(s): {output_path}")
    return 0


def cmd_query(path: Path, keyword: str) -> int:
    target = path.expanduser().resolve()
    error = validate_novel_root(target)
    if error:
        print(f"Error: {error}")
        return 1
    if not keyword:
        print("Error: keyword must not be empty")
        return 1

    matches = []
    for dirname in SEARCH_DIRS:
        base = target / dirname
        if not base.is_dir():
            continue
        for file_path in sorted(base.glob("**/*")):
            if not file_path.is_file() or file_path.name.startswith("."):
                continue
            if file_path.suffix.lower() not in {".md", ".txt", ".json"}:
                continue
            text = read_text(file_path)
            for line_number, line in enumerate(text.splitlines(), start=1):
                if keyword in line:
                    matches.append((file_path, line_number, make_snippet(line, keyword)))
                    break

    if not matches:
        print(f"No matches for: {keyword}")
        return 0
    for file_path, line_number, snippet in matches:
        print(f"{relative_path(target, file_path)}:{line_number}: {snippet}")
    print(f"Found {len(matches)} file(s).")
    return 0


def cmd_add_character(path: Path, name: str) -> int:
    target = path.expanduser().resolve()
    error = validate_novel_root(target)
    if error:
        print(f"Error: {error}")
        return 1
    if not name:
        print("Error: character name must not be empty")
        return 1

    json_path = target / "人物状态" / "characters.json"
    records = read_json_array(json_path)
    if records is None:
        return 1
    if any(item.get("name") == name for item in records if isinstance(item, dict)):
        print(f"Character already exists: {name}")
        return 0
    records.append(
        {
            "name": name,
            "role": "",
            "status": "",
            "last_seen_chapter": None,
            "notes": "",
        }
    )
    write_json(json_path, records)
    print(f"Added character: {name}")
    return 0


def cmd_add_hook(path: Path, title: str) -> int:
    target = path.expanduser().resolve()
    error = validate_novel_root(target)
    if error:
        print(f"Error: {error}")
        return 1
    if not title:
        print("Error: hook title must not be empty")
        return 1

    json_path = target / "伏笔记录" / "hooks.json"
    records = read_json_array(json_path)
    if records is None:
        return 1
    if any(item.get("title") == title for item in records if isinstance(item, dict)):
        print(f"Hook already exists: {title}")
        return 0
    records.append(
        {
            "title": title,
            "status": "open",
            "introduced_in": None,
            "related_characters": [],
            "notes": "",
        }
    )
    write_json(json_path, records)
    print(f"Added hook: {title}")
    return 0


def cmd_review_template(path: Path, chapter: str) -> int:
    target = path.expanduser().resolve()
    error = validate_novel_root(target)
    if error:
        print(f"Error: {error}")
        return 1
    try:
        chapter_number = int(chapter)
    except ValueError:
        print(f"Error: chapter must be a number: {chapter}")
        return 1
    if chapter_number <= 0:
        print("Error: chapter must be greater than 0")
        return 1

    template_path = target / "审查报告" / "review-template.md"
    if not template_path.is_file():
        print(f"Error: missing review template: {template_path}")
        return 1
    chapter_padded = f"{chapter_number:03d}"
    output_path = target / "审查报告" / f"第{chapter_padded}章-review.md"
    if output_path.exists():
        print(f"Error: review report already exists: {output_path}")
        return 1
    content = read_text(template_path).format(
        chapter=chapter_number,
        chapter_padded=chapter_padded,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    output_path.write_text(content, encoding="utf-8")
    print(f"Created review report: {output_path}")
    return 0


def cmd_chapter(path: Path, chapter: str) -> int:
    target = path.expanduser().resolve()
    error = validate_novel_root(target)
    if error:
        print(f"Error: {error}")
        return 1
    chapter_number = parse_positive_int(chapter, "chapter")
    if chapter_number is None:
        return 1

    chapter_padded = f"{chapter_number:03d}"
    chapter_path = target / "正文" / f"第{chapter_padded}章.md"
    summary_path = summary_file_path(target, chapter_number)
    template_path = target / "正文" / "chapter-template.md"
    if not template_path.is_file():
        print(f"Error: missing chapter template: {template_path}")
        return 1

    if chapter_path.exists():
        print(f"Chapter already exists, not overwriting: {chapter_path}")
    else:
        content = read_text(template_path).format(
            chapter=chapter_number,
            chapter_padded=chapter_padded,
            title=f"第{chapter_padded}章",
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        chapter_path.write_text(content, encoding="utf-8")
        print(f"Created chapter draft: {chapter_path}")

    if summary_path.exists():
        print(f"Summary already exists, not overwriting: {summary_path}")
    else:
        try:
            create_summary_file(target, chapter_number, chapter_path)
        except FileNotFoundError as exc:
            print(f"Error: {exc}")
            return 1
        print(f"Created chapter summary: {summary_path}")
    return 0


def cmd_chapter_summary(path: Path, chapter: str) -> int:
    target = path.expanduser().resolve()
    error = validate_novel_root(target)
    if error:
        print(f"Error: {error}")
        return 1
    chapter_number = parse_positive_int(chapter, "chapter")
    if chapter_number is None:
        return 1
    chapter_path = chapter_file_path(target, chapter_number)
    if not chapter_path.is_file():
        print(f"Error: missing chapter draft: {chapter_path}")
        return 1
    try:
        output_path = create_summary_file(target, chapter_number, chapter_path)
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        return 1
    print(f"Created chapter summary: {output_path}")
    return 0


def cmd_update_state(path: Path) -> int:
    target = path.expanduser().resolve()
    error = validate_novel_root(target)
    if error:
        print(f"Error: {error}")
        return 1

    characters = load_json_array(target / "人物状态" / "characters.json")
    hooks = load_json_array(target / "伏笔记录" / "hooks.json")
    if characters is None or hooks is None:
        return 1

    print("Character state overview:")
    if characters:
        for item in characters:
            if not isinstance(item, dict):
                continue
            name = item.get("name", "")
            role = item.get("role", "")
            status = item.get("status", "")
            last_seen = item.get("last_seen_chapter")
            print(f"- {name} | role: {role or '-'} | status: {status or '-'} | last_seen: {last_seen}")
    else:
        print("- No character records yet.")

    print("\nHook state overview:")
    if hooks:
        for item in hooks:
            if not isinstance(item, dict):
                continue
            title = item.get("title", "")
            status = item.get("status", "")
            introduced = item.get("introduced_in")
            print(f"- {title} | status: {status or '-'} | introduced_in: {introduced}")
    else:
        print("- No hook records yet.")

    print("\nTip: use add-character and add-hook to add missing records.")
    return 0


def cmd_continuity_check(path: Path) -> int:
    target = path.expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []
    details: list[str] = []

    root_error = validate_novel_root(target)
    if root_error:
        print(f"Error: {root_error}")
        return 1

    for dirname in NOVEL_DIRS:
        if not (target / dirname).is_dir():
            errors.append(f"missing directory: {dirname}")

    chapters_path = target / "章节索引" / "chapters.json"
    characters_path = target / "人物状态" / "characters.json"
    hooks_path = target / "伏笔记录" / "hooks.json"
    chapters = load_json_array(chapters_path)
    characters = load_json_array(characters_path)
    hooks = load_json_array(hooks_path)
    if chapters is None:
        errors.append(f"cannot read JSON array: {relative_path(target, chapters_path)}")
        chapters = []
    if characters is None:
        errors.append(f"cannot read JSON array: {relative_path(target, characters_path)}")
        characters = []
    if hooks is None:
        errors.append(f"cannot read JSON array: {relative_path(target, hooks_path)}")
        hooks = []

    indexed_paths = {item.get("path") for item in chapters if isinstance(item, dict)}
    chapter_files = find_chapter_files(target)
    for draft in chapter_files:
        draft_relative = relative_path(target, draft)
        if draft_relative not in indexed_paths:
            warnings.append(f"chapter draft not indexed: {draft_relative}")
        chapter_number = parse_chapter_number(draft)
        if chapter_number is not None and not summary_file_path(target, chapter_number).is_file():
            warnings.append(f"missing summary for chapter {chapter_number:03d}")

    summary_dir = target / "章节索引" / "summaries"
    if not summary_dir.is_dir():
        warnings.append("missing summaries directory: 章节索引/summaries")

    details.append(f"chapters indexed: {len(chapters)}")
    details.append(f"chapter drafts: {len(chapter_files)}")
    details.append(f"characters: {len(characters)}")
    details.append(f"hooks: {len(hooks)}")

    report = build_continuity_report(target, details, warnings, errors)
    report_path = target / "审查报告" / "continuity-report.md"
    report_path.write_text(report, encoding="utf-8")

    print("Continuity check:")
    for item in details:
        print(f"- {item}")
    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"- {warning}")
    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"- {error}")
    print(f"\nReport written: {report_path}")
    return 1 if errors else 0


def cmd_plan_init(path: Path) -> int:
    target = path.expanduser().resolve()
    error = validate_novel_root(target)
    if error:
        print(f"Error: {error}")
        return 1

    created = []
    existing = []
    for relative in [*PLANNING_JSON_FILES, "大纲/planning-guide.md"]:
        source = TEMPLATE_DIR / relative
        destination = target / relative
        if destination.exists():
            existing.append(relative)
            continue
        if not source.is_file():
            print(f"Error: missing template file: {source}")
            return 1
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        created.append(relative)

    for relative in created:
        print(f"Created planning file: {relative}")
    for relative in existing:
        print(f"Planning file exists, not overwriting: {relative}")
    if not created:
        print("Planning files already initialized.")
    return 0


def cmd_add_volume(path: Path, volume_number: str, title: str) -> int:
    target = path.expanduser().resolve()
    error = validate_novel_root(target)
    if error:
        print(f"Error: {error}")
        return 1
    number = parse_positive_int(volume_number, "volume_number")
    if number is None:
        return 1
    json_path = target / "大纲" / "volumes.json"
    records = read_json_array(json_path)
    if records is None:
        return 1
    if any(item.get("volume_number") == number for item in records if isinstance(item, dict)):
        print(f"Volume already exists: {number}")
        return 0
    records.append(
        {
            "volume_number": number,
            "title": title,
            "goal": "",
            "central_conflict": "",
            "main_characters": [],
            "key_hooks": [],
            "start_chapter": None,
            "end_chapter": None,
            "status": "planned",
            "notes": "",
        }
    )
    write_json(json_path, records)
    print(f"Added volume: {number}")
    return 0


def cmd_add_chapter_plan(path: Path, chapter_number: str, title: str) -> int:
    target = path.expanduser().resolve()
    error = validate_novel_root(target)
    if error:
        print(f"Error: {error}")
        return 1
    number = parse_positive_int(chapter_number, "chapter_number")
    if number is None:
        return 1
    json_path = target / "大纲" / "chapter_plans.json"
    records = read_json_array(json_path)
    if records is None:
        return 1
    if any(item.get("chapter_number") == number for item in records if isinstance(item, dict)):
        print(f"Chapter plan already exists: {number}")
        return 0
    records.append(
        {
            "chapter_number": number,
            "title": title or f"第{number:03d}章",
            "volume_number": None,
            "goal": "",
            "pov": "",
            "scenes": [],
            "characters": [],
            "hooks_to_introduce": [],
            "hooks_to_advance": [],
            "hooks_to_resolve": [],
            "conflict": "",
            "ending_hook": "",
            "status": "planned",
            "notes": "",
        }
    )
    write_json(json_path, records)
    print(f"Added chapter plan: {number}")
    return 0


def cmd_add_timeline_event(path: Path, chapter_number: str, event: str) -> int:
    target = path.expanduser().resolve()
    error = validate_novel_root(target)
    if error:
        print(f"Error: {error}")
        return 1
    number = parse_positive_int(chapter_number, "chapter_number")
    if number is None:
        return 1
    json_path = target / "大纲" / "timeline.json"
    records = read_json_array(json_path)
    if records is None:
        return 1
    records.append(
        {
            "order": len(records) + 1,
            "chapter_number": number,
            "time_label": "",
            "event": event,
            "characters": [],
            "location": "",
            "consequences": "",
            "notes": "",
        }
    )
    write_json(json_path, records)
    print(f"Added timeline event for chapter: {number}")
    return 0


def cmd_add_arc(path: Path, arc_id: str, title: str) -> int:
    target = path.expanduser().resolve()
    error = validate_novel_root(target)
    if error:
        print(f"Error: {error}")
        return 1
    if not arc_id:
        print("Error: arc_id must not be empty")
        return 1
    json_path = target / "大纲" / "arcs.json"
    records = read_json_array(json_path)
    if records is None:
        return 1
    if any(item.get("arc_id") == arc_id for item in records if isinstance(item, dict)):
        print(f"Arc already exists: {arc_id}")
        return 0
    records.append(
        {
            "arc_id": arc_id,
            "arc_type": "",
            "title": title,
            "related_characters": [],
            "start_chapter": None,
            "end_chapter": None,
            "current_stage": "",
            "milestones": [],
            "status": "planned",
            "notes": "",
        }
    )
    write_json(json_path, records)
    print(f"Added arc: {arc_id}")
    return 0


def cmd_add_scene(path: Path, chapter_number: str, scene_order: str) -> int:
    target = path.expanduser().resolve()
    error = validate_novel_root(target)
    if error:
        print(f"Error: {error}")
        return 1
    chapter = parse_positive_int(chapter_number, "chapter_number")
    order = parse_positive_int(scene_order, "scene_order")
    if chapter is None or order is None:
        return 1
    json_path = target / "大纲" / "scenes.json"
    records = read_json_array(json_path)
    if records is None:
        return 1
    scene_id = f"ch{chapter:03d}-s{order:02d}"
    if any(item.get("scene_id") == scene_id for item in records if isinstance(item, dict)):
        print(f"Scene already exists: {scene_id}")
        return 0
    records.append(
        {
            "scene_id": scene_id,
            "chapter_number": chapter,
            "scene_order": order,
            "location": "",
            "characters": [],
            "purpose": "",
            "conflict": "",
            "outcome": "",
            "hooks": [],
            "notes": "",
        }
    )
    write_json(json_path, records)
    print(f"Added scene: {scene_id}")
    return 0


def cmd_planning_status(path: Path) -> int:
    target = path.expanduser().resolve()
    error = validate_novel_root(target)
    if error:
        print(f"Error: {error}")
        return 1

    missing = [relative for relative in PLANNING_JSON_FILES if not (target / relative).is_file()]
    data = load_planning_data(target)
    if data is None:
        return 1

    print("Planning status:")
    for key in ["volumes", "chapter_plans", "timeline", "arcs", "scenes", "conflicts"]:
        print(f"- {key}: {len(data[key])}")
    if missing:
        print("\nMissing planning files:")
        for relative in missing:
            print(f"- {relative}")
    else:
        print("\nMissing planning files: none")

    draft_numbers = {parse_chapter_number(path) for path in find_chapter_files(target)}
    draft_numbers.discard(None)
    plan_numbers = {item.get("chapter_number") for item in data["chapter_plans"] if isinstance(item, dict)}
    missing_plans = sorted(number for number in draft_numbers if number not in plan_numbers)
    plans_without_drafts = sorted(number for number in plan_numbers if number not in draft_numbers and number is not None)
    missing_summaries = sorted(number for number in draft_numbers if not summary_file_path(target, number).is_file())

    print("\nDraft chapters without chapter_plan:")
    print_number_list(missing_plans)
    print("\nChapter plans without draft:")
    print_number_list(plans_without_drafts)
    print("\nDraft chapters without summary:")
    print_number_list(missing_summaries)
    return 0


def cmd_outline_export(path: Path) -> int:
    target = path.expanduser().resolve()
    error = validate_novel_root(target)
    if error:
        print(f"Error: {error}")
        return 1
    data = load_planning_data(target)
    if data is None:
        return 1
    output_path = target / "大纲" / "outline-export.md"
    output_path.write_text(build_outline_export(data), encoding="utf-8")
    print(f"Exported outline: {output_path}")
    return 0


def cmd_build_index(path: Path) -> int:
    target = path.expanduser().resolve()
    error = validate_novel_root(target)
    if error:
        print(f"Error: {error}")
        return 1

    config = ensure_retrieval_config(target)
    if config is None:
        return 1

    chunks = []
    source_files = []
    now = datetime.now(timezone.utc).isoformat()
    for file_path in iter_retrieval_files(target, config):
        text = read_text(file_path)
        source_files.append(relative_path(target, file_path))
        for index, chunk_text in enumerate(split_text(text, config["chunk_size"], config["chunk_overlap"]), start=1):
            stat = file_path.stat()
            chunk_id = f"{len(chunks) + 1:06d}"
            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "path": relative_path(target, file_path),
                    "title": extract_title(text, file_path),
                    "text": chunk_text,
                    "char_count": len(chunk_text),
                    "updated_at": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                    "chunk_index": index,
                }
            )

    webnovel_dir = target / RETRIEVAL_DIR
    chunks_path = webnovel_dir / "chunks.json"
    index_path = webnovel_dir / "retrieval-index.json"
    write_json(chunks_path, chunks)
    write_json(
        index_path,
        {
            "version": config["version"],
            "provider": config["provider"],
            "built_at": now,
            "chunk_count": len(chunks),
            "source_files": source_files,
        },
    )
    print(f"Built local retrieval index: {index_path}")
    print(f"- chunks: {len(chunks)}")
    print(f"- source_files: {len(source_files)}")
    return 0


def cmd_retrieve(path: Path, query: str) -> int:
    target = path.expanduser().resolve()
    error = validate_novel_root(target)
    if error:
        print(f"Error: {error}")
        return 1
    if not query.strip():
        print("Error: query must not be empty")
        return 1

    config = ensure_retrieval_config(target)
    if config is None:
        return 1
    chunks = load_chunks(target)
    if chunks is None:
        return 1

    results = search_chunks(chunks, query, config["max_results"])
    if not results:
        print(f"No retrieval results for: {query}")
        print("Tip: run build-index after adding settings, outlines, chapter summaries, character state, or hook records.")
        return 0

    for rank, result in enumerate(results, start=1):
        chunk = result["chunk"]
        print(f"{rank}. score={result['score']:.2f} path={chunk.get('path')} chunk_id={chunk.get('chunk_id')}")
        print(f"   {make_retrieval_snippet(str(chunk.get('text', '')), query)}")
    return 0


def cmd_context_pack(path: Path, chapter_number: str) -> int:
    target = path.expanduser().resolve()
    error = validate_novel_root(target)
    if error:
        print(f"Error: {error}")
        return 1
    number = parse_positive_int(chapter_number, "chapter_number")
    if number is None:
        return 1

    config = ensure_retrieval_config(target)
    if config is None:
        return 1
    chunks = load_chunks(target)
    if chunks is None:
        return 1

    plan = find_chapter_plan(target, number)
    if plan is None:
        query = f"第{number:03d}章"
        results = []
        message = "No matching chapter_plan found. Generated an empty context pack template."
    else:
        query = build_chapter_plan_query(plan)
        results = search_chunks(chunks, query, config["max_results"]) if query else []
        message = f"Generated context pack for chapter {number:03d}."

    output_path = context_pack_path(target, number)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_context_pack(number, plan, query, results), encoding="utf-8")
    print(message)
    if plan is None:
        print("Tip: run add-chapter-plan first, then fill goal, characters, hooks, conflict, and notes.")
    print(f"Context pack written: {output_path}")
    return 0


def cmd_retrieval_status(path: Path) -> int:
    target = path.expanduser().resolve()
    error = validate_novel_root(target)
    if error:
        print(f"Error: {error}")
        return 1

    config_path = retrieval_config_path(target)
    chunks_path = target / RETRIEVAL_DIR / "chunks.json"
    index_path = target / RETRIEVAL_DIR / "retrieval-index.json"
    print("Retrieval status:")
    print(f"- config: {'exists' if config_path.is_file() else 'missing'} ({relative_path(target, config_path)})")
    print(f"- chunks: {'exists' if chunks_path.is_file() else 'missing'} ({relative_path(target, chunks_path)})")
    print(f"- index: {'exists' if index_path.is_file() else 'missing'} ({relative_path(target, index_path)})")

    if not index_path.is_file():
        print("Tip: run build-index to create the local retrieval index.")
        return 0
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Error: invalid retrieval index JSON: {exc}")
        return 1
    source_files = index.get("source_files", [])
    print(f"- chunk_count: {index.get('chunk_count', 0)}")
    print(f"- source_files: {len(source_files) if isinstance(source_files, list) else 0}")
    print(f"- built_at: {index.get('built_at', '-')}")
    return 0


def cmd_check(path: Path) -> int:
    target = path.expanduser().resolve()
    errors: list[str] = []
    if (target / ".codex-plugin" / "plugin.json").exists():
        check_plugin(target, errors)
    else:
        check_novel_project(target, errors)

    if errors:
        print("Check failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Check passed: {target}")
    return 0


def check_plugin(root: Path, errors: list[str]) -> None:
    manifest_path = root / ".codex-plugin" / "plugin.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid plugin.json: {exc}")
        return
    if manifest.get("name") != "codex-webnovel-writer":
        errors.append("plugin.json name must be codex-webnovel-writer")
    if manifest.get("skills") != "./skills/":
        errors.append("plugin.json skills must point to ./skills/")
    for skill in SKILLS:
        skill_file = root / "skills" / skill / "SKILL.md"
        check_skill(skill, skill_file, errors)
    for dirname in NOVEL_DIRS:
        if not (root / "templates" / dirname).is_dir():
            errors.append(f"missing template directory: templates/{dirname}")
    if not (root / "templates" / RETRIEVAL_DIR).is_dir():
        errors.append(f"missing template directory: templates/{RETRIEVAL_DIR}")
    for relative in TEMPLATE_FILES:
        if not (root / "templates" / relative).is_file():
            errors.append(f"missing template file: templates/{relative}")
    for relative in [
        "章节索引/chapters.json",
        "伏笔记录/hooks.json",
        "人物状态/characters.json",
        ".webnovel/retrieval-config.json",
        *PLANNING_JSON_FILES,
    ]:
        path = root / "templates" / relative
        if path.is_file():
            validate_json_file(path, errors)
    if count_lines(root / "AGENTS.md") > 150:
        errors.append("root AGENTS.md must be 150 lines or fewer")


def check_skill(expected_name: str, path: Path, errors: list[str]) -> None:
    if not path.is_file():
        errors.append(f"missing skill: {path}")
        return
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        errors.append(f"{path} missing YAML frontmatter")
        return
    frontmatter = match.group(1)
    fields = {}
    for line in frontmatter.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    if fields.get("name") != expected_name:
        errors.append(f"{path} frontmatter name must be {expected_name}")
    if not fields.get("description"):
        errors.append(f"{path} frontmatter description is required")


def check_novel_project(root: Path, errors: list[str]) -> None:
    if not root.exists():
        errors.append(f"path does not exist: {root}")
        return
    if not (root / "AGENTS.md").is_file():
        errors.append("missing AGENTS.md")
    elif count_lines(root / "AGENTS.md") > 150:
        errors.append("AGENTS.md must be 150 lines or fewer")
    for dirname in NOVEL_DIRS:
        if not (root / dirname).is_dir():
            errors.append(f"missing directory: {dirname}")


def validate_novel_root(root: Path) -> str | None:
    if not root.exists():
        return f"path does not exist: {root}"
    if not root.is_dir():
        return f"path is not a directory: {root}"
    missing = [dirname for dirname in NOVEL_DIRS if not (root / dirname).is_dir()]
    if missing:
        return f"missing required directory: {missing[0]}"
    return None


def parse_positive_int(value: str, label: str) -> int | None:
    try:
        number = int(value)
    except ValueError:
        print(f"Error: {label} must be a number: {value}")
        return None
    if number <= 0:
        print(f"Error: {label} must be greater than 0")
        return None
    return number


def chapter_file_path(root: Path, chapter_number: int) -> Path:
    return root / "正文" / f"第{chapter_number:03d}章.md"


def summary_file_path(root: Path, chapter_number: int) -> Path:
    return root / "章节索引" / "summaries" / f"第{chapter_number:03d}章-summary.md"


def find_chapter_files(root: Path) -> list[Path]:
    draft_dir = root / "正文"
    files = []
    for draft in sorted(draft_dir.glob("**/*")):
        if not draft.is_file() or draft.name.startswith("."):
            continue
        if draft.name == "chapter-template.md":
            continue
        if draft.suffix.lower() not in {".md", ".txt"}:
            continue
        if parse_chapter_number(draft) is None:
            continue
        files.append(draft)
    return files


def create_summary_file(root: Path, chapter_number: int, chapter_path: Path) -> Path:
    template_path = root / "章节索引" / "summary-template.md"
    if not template_path.is_file():
        raise FileNotFoundError(f"missing summary template: {template_path}")
    text = read_text(chapter_path) if chapter_path.is_file() else ""
    chapter_padded = f"{chapter_number:03d}"
    output_path = summary_file_path(root, chapter_number)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    content = read_text(template_path).format(
        chapter=chapter_number,
        chapter_padded=chapter_padded,
        title=extract_title(text, chapter_path) if text else f"第{chapter_padded}章",
        chapter_path=relative_path(root, chapter_path),
        word_count=count_words(text),
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    output_path.write_text(content, encoding="utf-8")
    return output_path


def build_continuity_report(root: Path, details: list[str], warnings: list[str], errors: list[str]) -> str:
    template_path = root / "审查报告" / "continuity-report-template.md"
    if template_path.is_file():
        template = read_text(template_path)
    else:
        template = (
            "# 连续性检查报告\n\n"
            "- 生成时间：{created_at}\n\n"
            "## 章节索引检查\n\n{chapter_index_check}\n\n"
            "## 人物状态检查\n\n{character_check}\n\n"
            "## 伏笔状态检查\n\n{hook_check}\n\n"
            "## 时间线检查\n\n{timeline_check}\n\n"
            "## 文件缺失检查\n\n{missing_file_check}\n\n"
            "## 建议修复项\n\n{fix_suggestions}\n"
        )

    warning_text = format_report_items(warnings, "未发现警告。")
    error_text = format_report_items(errors, "未发现错误。")
    detail_text = format_report_items(details, "暂无统计。")
    fix_items = errors + warnings
    return template.format(
        created_at=datetime.now(timezone.utc).isoformat(),
        chapter_index_check=detail_text,
        character_check=detail_text,
        hook_check=detail_text,
        timeline_check="第一版仅检查时间线文件是否存在；复杂时间线一致性需人工审查。",
        missing_file_check=error_text,
        fix_suggestions=format_report_items(fix_items, "暂无建议修复项。"),
        warnings=warning_text,
        errors=error_text,
    )


def format_report_items(items: list[str], empty_text: str) -> str:
    if not items:
        return empty_text
    return "\n".join(f"- {item}" for item in items)


def load_planning_data(root: Path) -> dict[str, list] | None:
    mapping = {
        "volumes": root / "大纲" / "volumes.json",
        "chapter_plans": root / "大纲" / "chapter_plans.json",
        "timeline": root / "大纲" / "timeline.json",
        "arcs": root / "大纲" / "arcs.json",
        "scenes": root / "大纲" / "scenes.json",
        "conflicts": root / "大纲" / "conflicts.json",
    }
    data = {}
    for key, path in mapping.items():
        records = load_json_array(path)
        if records is None:
            return None
        data[key] = records
    return data


def print_number_list(numbers: list[int]) -> None:
    if not numbers:
        print("- none")
        return
    for number in numbers:
        print(f"- 第{number:03d}章")


def build_outline_export(data: dict[str, list]) -> str:
    lines = [
        "# 结构化大纲导出",
        "",
        f"- 生成时间：{datetime.now(timezone.utc).isoformat()}",
        "",
        "## 卷纲列表",
        "",
    ]
    append_records(
        lines,
        data["volumes"],
        lambda item: f"- 第{item.get('volume_number')}卷：{item.get('title') or '未命名'} | 状态：{item.get('status') or '-'} | 目标：{item.get('goal') or '-'}",
    )
    lines.extend(["", "## 章纲列表", ""])
    append_records(
        lines,
        data["chapter_plans"],
        lambda item: f"- 第{int(item.get('chapter_number')):03d}章：{item.get('title') or '未命名'} | 卷：{item.get('volume_number')} | 目标：{item.get('goal') or '-'} | 结尾钩子：{item.get('ending_hook') or '-'}",
    )
    lines.extend(["", "## 时间线", ""])
    append_records(
        lines,
        data["timeline"],
        lambda item: f"- {item.get('order')}. 第{int(item.get('chapter_number')):03d}章 | {item.get('time_label') or '-'} | {item.get('event') or '-'} | 地点：{item.get('location') or '-'}",
    )
    lines.extend(["", "## 人物线/关系线", ""])
    append_records(
        lines,
        data["arcs"],
        lambda item: f"- {item.get('arc_id')}：{item.get('title') or '未命名'} | 类型：{item.get('arc_type') or '-'} | 阶段：{item.get('current_stage') or '-'} | 状态：{item.get('status') or '-'}",
    )
    lines.extend(["", "## 场景卡", ""])
    append_records(
        lines,
        data["scenes"],
        lambda item: f"- {item.get('scene_id')} | 第{int(item.get('chapter_number')):03d}章 / 场景{item.get('scene_order')} | 地点：{item.get('location') or '-'} | 目的：{item.get('purpose') or '-'}",
    )
    lines.extend(["", "## 冲突线", ""])
    append_records(
        lines,
        data["conflicts"],
        lambda item: f"- {item.get('conflict_id')}：{item.get('title') or '未命名'} | 类型：{item.get('conflict_type') or '-'} | 状态：{item.get('status') or '-'} | 利害关系：{item.get('stakes') or '-'}",
    )
    lines.append("")
    return "\n".join(lines)


def append_records(lines: list[str], records: list, formatter) -> None:
    if not records:
        lines.append("- 暂无记录。")
        return
    for item in records:
        if isinstance(item, dict):
            try:
                lines.append(formatter(item))
            except (TypeError, ValueError):
                lines.append(f"- {item}")


def retrieval_config_path(root: Path) -> Path:
    return root / RETRIEVAL_DIR / RETRIEVAL_CONFIG


def ensure_retrieval_config(root: Path) -> dict | None:
    config_path = retrieval_config_path(root)
    if not config_path.exists():
        source = TEMPLATE_DIR / RETRIEVAL_DIR / RETRIEVAL_CONFIG
        if not source.is_file():
            print(f"Error: missing default retrieval config template: {source}")
            return None
        config_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, config_path)
        print(f"Created default retrieval config: {config_path}")
    return load_retrieval_config(config_path)


def load_retrieval_config(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Error: invalid retrieval config JSON in {path}: {exc}")
        return None
    if not isinstance(data, dict):
        print(f"Error: retrieval config must contain an object: {path}")
        return None

    try:
        config = {
            "version": str(data.get("version") or "0.5"),
            "provider": str(data.get("provider") or "local"),
            "chunk_size": int(data.get("chunk_size") or 800),
            "chunk_overlap": int(data.get("chunk_overlap") or 120),
            "max_results": int(data.get("max_results") or 8),
            "include_dirs": data.get("include_dirs") if isinstance(data.get("include_dirs"), list) else [],
            "exclude_patterns": data.get("exclude_patterns") if isinstance(data.get("exclude_patterns"), list) else [],
        }
    except (TypeError, ValueError):
        print("Error: chunk_size, chunk_overlap, and max_results must be numbers")
        return None
    if config["provider"] != "local":
        print("Error: v0.5 only supports provider=local")
        return None
    if config["chunk_size"] <= 0:
        print("Error: chunk_size must be greater than 0")
        return None
    if config["chunk_overlap"] < 0 or config["chunk_overlap"] >= config["chunk_size"]:
        print("Error: chunk_overlap must be greater than or equal to 0 and smaller than chunk_size")
        return None
    if config["max_results"] <= 0:
        print("Error: max_results must be greater than 0")
        return None
    return config


def iter_retrieval_files(root: Path, config: dict) -> list[Path]:
    files = []
    exclude_patterns = [str(item) for item in config.get("exclude_patterns", [])]
    for dirname in config.get("include_dirs", []):
        base = root / str(dirname)
        if not base.is_dir():
            continue
        for file_path in sorted(base.glob("**/*")):
            if not file_path.is_file() or file_path.name.startswith("."):
                continue
            relative = relative_path(root, file_path)
            if file_path.suffix.lower() not in SUPPORTED_RETRIEVAL_SUFFIXES:
                continue
            if any(pattern and pattern in relative for pattern in exclude_patterns):
                continue
            files.append(file_path)
    return files


def split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(end - chunk_overlap, start + 1)
    return chunks


def load_chunks(root: Path) -> list | None:
    chunks_path = root / RETRIEVAL_DIR / "chunks.json"
    index_path = root / RETRIEVAL_DIR / "retrieval-index.json"
    if not chunks_path.is_file() or not index_path.is_file():
        print("Error: local retrieval index is missing. Run build-index first.")
        return None
    try:
        chunks = json.loads(chunks_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Error: invalid chunks JSON: {exc}")
        return None
    if not isinstance(chunks, list):
        print(f"Error: chunks JSON must contain an array: {chunks_path}")
        return None
    return chunks


def search_chunks(chunks: list, query: str, max_results: int) -> list[dict]:
    query_norm = normalize_text(query)
    tokens = tokenize_query(query)
    results = []
    for chunk in chunks:
        if not isinstance(chunk, dict):
            continue
        text = str(chunk.get("text", ""))
        title = str(chunk.get("title", ""))
        path = str(chunk.get("path", ""))
        haystack = normalize_text(text)
        title_norm = normalize_text(title)
        path_norm = normalize_text(path)
        score = 0.0
        if query_norm and query_norm in haystack:
            score += 10.0
        if query_norm and query_norm in title_norm:
            score += 8.0
        if query_norm and query_norm in path_norm:
            score += 4.0
        for token in tokens:
            if token in haystack:
                score += 2.0
            if token in title_norm:
                score += 2.0
            if token in path_norm:
                score += 1.0
        score += recent_bonus(chunk.get("updated_at"))
        if score > 0:
            results.append({"score": score, "chunk": chunk})
    results.sort(key=lambda item: (-item["score"], str(item["chunk"].get("path", "")), str(item["chunk"].get("chunk_id", ""))))
    return results[:max_results]


def normalize_text(value: str) -> str:
    return "".join(value.lower().split())


def tokenize_query(query: str) -> list[str]:
    raw_tokens = re.findall(r"[\u4e00-\u9fff]+|[A-Za-z0-9_]+", query.lower())
    tokens = set()
    for token in raw_tokens:
        token = token.strip()
        if not token:
            continue
        tokens.add(token)
        if re.fullmatch(r"[\u4e00-\u9fff]+", token) and len(token) > 2:
            for index in range(0, len(token) - 1):
                tokens.add(token[index : index + 2])
    return sorted(tokens, key=lambda item: (-len(item), item))


def recent_bonus(value) -> float:
    if not value:
        return 0.0
    try:
        updated = datetime.fromisoformat(str(value))
    except ValueError:
        return 0.0
    age_days = max((datetime.now(timezone.utc) - updated).total_seconds() / 86400, 0)
    return max(0.0, 1.0 - min(age_days, 365) / 365) * 0.5


def make_retrieval_snippet(text: str, query: str, width: int = 160) -> str:
    clean = " ".join(text.strip().split())
    if len(clean) <= width:
        return clean
    query_norm = normalize_text(query)
    clean_norm = normalize_text(clean)
    index = clean_norm.find(query_norm) if query_norm else -1
    if index < 0:
        for token in tokenize_query(query):
            index = clean_norm.find(token)
            if index >= 0:
                break
    if index < 0:
        index = 0
    start = max(0, index - width // 2)
    end = min(len(clean), start + width)
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(clean) else ""
    return f"{prefix}{clean[start:end]}{suffix}"


def find_chapter_plan(root: Path, chapter_number: int) -> dict | None:
    path = root / "大纲" / "chapter_plans.json"
    if not path.is_file():
        return None
    records = load_json_array(path)
    if records is None:
        return None
    for item in records:
        if isinstance(item, dict) and item.get("chapter_number") == chapter_number:
            return item
    return None


def build_chapter_plan_query(plan: dict) -> str:
    fields = [
        "title",
        "goal",
        "pov",
        "conflict",
        "ending_hook",
        "notes",
        "characters",
        "hooks_to_introduce",
        "hooks_to_advance",
        "hooks_to_resolve",
        "scenes",
    ]
    parts = []
    for field in fields:
        value = plan.get(field)
        if isinstance(value, list):
            parts.extend(str(item) for item in value if item)
        elif value:
            parts.append(str(value))
    return " ".join(parts).strip()


def context_pack_path(root: Path, chapter_number: int) -> Path:
    return root / "章节索引" / "context-packs" / f"第{chapter_number:03d}章-context.md"


def build_context_pack(chapter_number: int, plan: dict | None, query: str, results: list[dict]) -> str:
    lines = [
        f"# 第{chapter_number:03d}章写作上下文包",
        "",
        f"- 生成时间：{datetime.now(timezone.utc).isoformat()}",
        f"- 章节号：{chapter_number}",
        "",
        "## 章纲摘要",
        "",
    ]
    if plan is None:
        lines.append("- 未找到对应 `大纲/chapter_plans.json` 章纲。请先补充章纲。")
    else:
        lines.extend(format_chapter_plan_summary(plan))
    lines.extend(["", "## 检索 Query", "", query or "-"])
    setting_results = []
    state_results = []
    for result in results:
        path = str(result["chunk"].get("path", ""))
        if path.startswith(("伏笔记录/", "人物状态/", "章节索引/")) or path.startswith("大纲/timeline"):
            state_results.append(result)
        else:
            setting_results.append(result)
    lines.extend(["", "## 相关设定片段", ""])
    append_context_results(lines, setting_results, query)
    lines.extend(["", "## 相关人物/伏笔/时间线片段", ""])
    append_context_results(lines, state_results, query)
    lines.extend(
        [
            "",
            "## 写作前提醒",
            "",
            "- 检索片段只作为参考，不能替代用户确认过的设定和章纲。",
            "- 不要把检索片段当成新设定自动写回项目文件。",
            "- 如果关键设定、人物状态、伏笔或时间线信息缺失，先提示用户补充。",
            "- 写完后运行 `index`、`chapter-summary` 和 `continuity-check`。",
            "",
        ]
    )
    return "\n".join(lines)


def format_chapter_plan_summary(plan: dict) -> list[str]:
    return [
        f"- 标题：{plan.get('title') or '-'}",
        f"- 目标：{plan.get('goal') or '-'}",
        f"- 角色：{format_inline_list(plan.get('characters'))}",
        f"- 冲突：{plan.get('conflict') or '-'}",
        f"- 伏笔引入：{format_inline_list(plan.get('hooks_to_introduce'))}",
        f"- 伏笔推进：{format_inline_list(plan.get('hooks_to_advance'))}",
        f"- 伏笔回收：{format_inline_list(plan.get('hooks_to_resolve'))}",
        f"- 结尾钩子：{plan.get('ending_hook') or '-'}",
        f"- 备注：{plan.get('notes') or '-'}",
    ]


def format_inline_list(value) -> str:
    if isinstance(value, list):
        return "、".join(str(item) for item in value if item) or "-"
    return str(value) if value else "-"


def append_context_results(lines: list[str], results: list[dict], query: str) -> None:
    if not results:
        lines.append("- 暂无检索结果。")
        return
    for rank, result in enumerate(results, start=1):
        chunk = result["chunk"]
        lines.extend(
            [
                f"### {rank}. {chunk.get('path')} / {chunk.get('chunk_id')}",
                "",
                f"- score: {result['score']:.2f}",
                f"- title: {chunk.get('title') or '-'}",
                "",
                "> " + make_retrieval_snippet(str(chunk.get("text", "")), query, 220),
                "",
            ]
        )


def parse_chapter_number(path: Path) -> int | None:
    match = re.search(r"第\s*([0-9０-９]+)\s*章", path.stem)
    if not match:
        match = re.search(r"([0-9０-９]+)", path.stem)
    if not match:
        return None
    digits = match.group(1).translate(str.maketrans("０１２３４５６７８９", "0123456789"))
    return int(digits)


def extract_title(text: str, path: Path) -> str:
    for line in text.splitlines():
        title = line.strip().lstrip("#").strip()
        if title:
            return title
    return path.stem


def count_words(text: str) -> int:
    return len(re.findall(r"\S", text))


def make_snippet(line: str, keyword: str, width: int = 80) -> str:
    clean = " ".join(line.strip().split())
    index = clean.find(keyword)
    if index < 0 or len(clean) <= width:
        return clean
    start = max(0, index - width // 2)
    end = min(len(clean), start + width)
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(clean) else ""
    return f"{prefix}{clean[start:end]}{suffix}"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def read_json_array(path: Path) -> list | None:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        write_json(path, [])
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON in {path}: {exc}")
        return None
    if not isinstance(data, list):
        print(f"Error: JSON file must contain an array: {path}")
        return None
    return data


def load_json_array(path: Path) -> list | None:
    if not path.is_file():
        print(f"Error: missing JSON file: {path}")
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON in {path}: {exc}")
        return None
    if not isinstance(data, list):
        print(f"Error: JSON file must contain an array: {path}")
        return None
    return data


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def relative_path(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def validate_json_file(path: Path, errors: list[str]) -> None:
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid template JSON {path}: {exc}")


def count_lines(path: Path) -> int:
    if not path.is_file():
        return 0
    return len(path.read_text(encoding="utf-8").splitlines())


if __name__ == "__main__":
    raise SystemExit(main())
