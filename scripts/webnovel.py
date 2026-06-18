#!/usr/bin/env python3
"""Small CLI for codex-webnovel-writer."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
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
    "webnovel-doctor",
    "webnovel-review-deep",
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
    "审查报告/doctor-report-template.md",
    "审查报告/deep-review-template.md",
    "审查报告/review-summary-template.md",
    ".webnovel/.gitkeep",
    ".webnovel/retrieval-config.json",
]
SEARCH_DIRS = ["设定集", "大纲", "正文", "伏笔记录", "人物状态", "章节索引"]
SUPPORTED_RETRIEVAL_SUFFIXES = {".md", ".txt", ".json"}
DOCTOR_SAFETY_TERMS = ["KpopNovel", "韩娱", "TWICE", "林予安", "崔道允", "三点十七", "精神科", "财阀"]


def main() -> int:
    sys.argv = [normalize_cli_dash(arg) for arg in sys.argv]
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

    doctor_parser = subparsers.add_parser("doctor", help="run read-only novel project health checks")
    doctor_parser.add_argument("path", type=Path, help="novel project path")
    doctor_parser.add_argument("--deep", action="store_true", help="include detailed diagnostic lists")

    deep_review_parser = subparsers.add_parser("review", help="run a read-only structured chapter review")
    deep_review_parser.add_argument("path", type=Path, help="novel project path")
    deep_review_parser.add_argument("chapter_number", help="chapter number")

    review_range_parser = subparsers.add_parser("review-range", help="run structured reviews for a chapter range")
    review_range_parser.add_argument("path", type=Path, help="novel project path")
    review_range_parser.add_argument("start_chapter", help="start chapter number")
    review_range_parser.add_argument("end_chapter", help="end chapter number")

    review_status_parser = subparsers.add_parser("review-status", help="show deep review report coverage")
    review_status_parser.add_argument("path", type=Path, help="novel project path")

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
    if args.command == "doctor":
        return cmd_doctor(args.path, args.deep)
    if args.command == "review":
        return cmd_deep_review(args.path, args.chapter_number)
    if args.command == "review-range":
        return cmd_review_range(args.path, args.start_chapter, args.end_chapter)
    if args.command == "review-status":
        return cmd_review_status(args.path)
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


def cmd_doctor(path: Path, deep: bool) -> int:
    target = path.expanduser().resolve()
    findings: list[dict] = []
    details: dict[str, list[str]] = {
        "structure": [],
        "json": [],
        "chapter_index": [],
        "chapter_summary": [],
        "planning": [],
        "character": [],
        "hook": [],
        "retrieval": [],
        "generic_safety": [],
        "deep": [],
    }

    if not target.exists():
        print(f"Error: path does not exist: {target}")
        return 1
    if not target.is_dir():
        print(f"Error: path is not a directory: {target}")
        return 1

    doctor_check_structure(target, findings, details)
    json_states = doctor_check_json(target, findings, details)
    chapter_numbers = doctor_check_chapters(target, json_states, findings, details, deep)
    doctor_check_summaries(target, chapter_numbers, findings, details)
    doctor_check_plan_correspondence(target, chapter_numbers, json_states, findings, details)
    doctor_check_characters(json_states, findings, details)
    doctor_check_hooks(json_states, findings, details)
    doctor_check_planning(json_states, findings, details)
    doctor_check_retrieval(target, json_states, findings, details, deep)
    doctor_check_generic_safety(target, findings, details)

    counts = count_findings(findings)
    report = build_doctor_report(target, deep, counts, findings, details)
    report_path = target / "审查报告" / "doctor-report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")

    print(f"Doctor: PASS={counts['PASS']} WARN={counts['WARN']} ERROR={counts['ERROR']}")
    for section in [
        "structure",
        "json",
        "chapter_index",
        "chapter_summary",
        "planning",
        "character",
        "hook",
        "retrieval",
        "generic_safety",
    ]:
        print(f"- {section}: {summarize_section(findings, section)}")
    important = [item for item in findings if item["level"] in {"ERROR", "WARN"}][:5]
    if important:
        print("\nTop suggestions:")
        for item in important:
            print(f"- [{item['level']}] {item['message']}")
    print(f"\nReport written: {report_path}")
    return 1 if counts["ERROR"] else 0


def cmd_deep_review(path: Path, chapter_number: str) -> int:
    target = path.expanduser().resolve()
    error = validate_novel_root(target)
    if error:
        print(f"Error: {error}")
        return 1
    number = parse_positive_int(chapter_number, "chapter_number")
    if number is None:
        return 1
    result = run_deep_review(target, number)
    write_deep_review_report(target, number, result)
    counts = count_review_findings(result["findings"])
    print(f"Review 第{number:03d}章: PASS={counts['pass']} WARN={counts['warning']} ERROR={counts['error']}")
    print(f"Report written: {result['report_path']}")
    return 1 if counts["error"] else 0


def cmd_review_range(path: Path, start_chapter: str, end_chapter: str) -> int:
    target = path.expanduser().resolve()
    error = validate_novel_root(target)
    if error:
        print(f"Error: {error}")
        return 1
    start = parse_positive_int(start_chapter, "start_chapter")
    end = parse_positive_int(end_chapter, "end_chapter")
    if start is None or end is None:
        return 1
    if end < start:
        print("Error: end_chapter must be greater than or equal to start_chapter")
        return 1

    results = []
    total = {"pass": 0, "warning": 0, "error": 0}
    for number in range(start, end + 1):
        result = run_deep_review(target, number)
        write_deep_review_report(target, number, result)
        counts = count_review_findings(result["findings"])
        for key in total:
            total[key] += counts[key]
        results.append((number, result, counts))
        print(f"Review 第{number:03d}章: PASS={counts['pass']} WARN={counts['warning']} ERROR={counts['error']}")

    summary_path = write_review_summary(target, start, end, results, total)
    print(f"Summary written: {summary_path}")
    return 1 if total["error"] else 0


def cmd_review_status(path: Path) -> int:
    target = path.expanduser().resolve()
    error = validate_novel_root(target)
    if error:
        print(f"Error: {error}")
        return 1
    report_dir = target / "审查报告"
    report_dir.mkdir(parents=True, exist_ok=True)
    deep_reports = sorted(report_dir.glob("第*章-deep-review.md"))
    summaries = sorted(report_dir.glob("review-summary-第*-第*章.md"), key=lambda item: item.stat().st_mtime if item.is_file() else 0)
    chapter_numbers = {parse_chapter_number(path) for path in find_chapter_files(target)}
    chapter_numbers.discard(None)
    reviewed_numbers = {parse_chapter_number(path) for path in deep_reports}
    reviewed_numbers.discard(None)
    missing = sorted(number for number in chapter_numbers if number not in reviewed_numbers)

    print("Review status:")
    print(f"- report_dir: {report_dir}")
    print(f"- deep_review_reports: {len(deep_reports)}")
    print(f"- draft_chapters: {len(chapter_numbers)}")
    print(f"- chapters_missing_deep_review: {len(missing)}")
    for number in missing:
        print(f"  - 第{number:03d}章")
    if summaries:
        print(f"- latest_review_summary: {relative_path(target, summaries[-1])}")
    else:
        print("- latest_review_summary: none")
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


def run_deep_review(root: Path, chapter_number: int) -> dict:
    findings: list[dict] = []
    data: dict[str, object] = {}
    chapter_path = chapter_file_path(root, chapter_number)
    chapter_text = read_text(chapter_path) if chapter_path.is_file() else ""
    data["chapter_path"] = chapter_path
    data["chapter_text"] = chapter_text

    review_check_chapter_body(root, chapter_number, chapter_path, chapter_text, findings)
    review_check_index(root, chapter_number, findings)
    review_check_summary(root, chapter_number, findings)

    chapter_plans = review_load_json(root, "大纲/chapter_plans.json", "plan_alignment", findings, expected_type=list)
    chapter_plan = find_record_by_number(chapter_plans, "chapter_number", chapter_number) if isinstance(chapter_plans, list) else None
    data["chapter_plan"] = chapter_plan
    review_check_chapter_plan(chapter_number, chapter_text, chapter_plans, chapter_plan, findings)

    characters = review_load_json(root, "人物状态/characters.json", "character", findings, expected_type=list)
    review_check_characters_deep(chapter_number, chapter_text, characters, findings)

    hooks = review_load_json(root, "伏笔记录/hooks.json", "hook", findings, expected_type=list)
    review_check_hooks_deep(chapter_text, hooks, findings)

    timeline = review_load_json(root, "大纲/timeline.json", "timeline", findings, expected_type=list)
    review_check_timeline(chapter_number, timeline, findings)

    scenes = review_load_json(root, "大纲/scenes.json", "scene_conflict", findings, expected_type=list)
    conflicts = review_load_json(root, "大纲/conflicts.json", "scene_conflict", findings, expected_type=list)
    review_check_scenes_conflicts(chapter_number, scenes, conflicts, findings)

    review_check_retrieval_context(root, chapter_number, findings)
    review_check_setting_risks(root, chapter_number, chapter_text, findings)

    report_path = root / "审查报告" / f"第{chapter_number:03d}章-deep-review.md"
    return {"findings": findings, "report_path": report_path, "chapter_plan": chapter_plan}


def review_add(findings: list[dict], level: str, category: str, message: str, suggestion: str = "") -> None:
    findings.append({"level": level, "category": category, "message": message, "suggestion": suggestion})


def count_review_findings(findings: list[dict]) -> dict[str, int]:
    counts = {"pass": 0, "warning": 0, "error": 0}
    for item in findings:
        level = item.get("level")
        if level in counts:
            counts[level] += 1
    return counts


def review_load_json(root: Path, relative: str, category: str, findings: list[dict], expected_type=None):
    path = root / relative
    if not path.is_file():
        review_add(findings, "warning", category, f"missing JSON file: {relative}", "补齐该文件，或运行对应初始化命令。")
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        review_add(findings, "error", category, f"invalid JSON in {relative}: {exc}", "先修复 JSON 格式，再重新运行 review。")
        return None
    if expected_type is not None and not isinstance(data, expected_type):
        review_add(findings, "error", category, f"{relative} has unexpected JSON type", f"该文件应为 {expected_type.__name__}。")
        return None
    review_add(findings, "pass", category, f"read JSON: {relative}", "")
    return data


def review_check_chapter_body(root: Path, chapter_number: int, chapter_path: Path, chapter_text: str, findings: list[dict]) -> None:
    category = "chapter_structure"
    if not chapter_path.is_file():
        review_add(findings, "error", category, f"missing chapter draft: {relative_path(root, chapter_path)}", "先生成或补齐正文文件。")
        return
    review_add(findings, "pass", category, f"chapter draft exists: {relative_path(root, chapter_path)}", "")
    word_count = count_words(chapter_text)
    if word_count == 0:
        review_add(findings, "warning", category, f"chapter draft is empty: 第{chapter_number:03d}章", "补写正文后再审查。")
    elif word_count < 200:
        review_add(findings, "warning", category, f"chapter draft is short: {word_count} non-space characters", "确认这是草稿、短章，还是需要补充正文。")
    else:
        review_add(findings, "pass", category, f"chapter draft has content: {word_count} non-space characters", "")


def review_check_index(root: Path, chapter_number: int, findings: list[dict]) -> None:
    category = "index_summary"
    chapters = review_load_json(root, "章节索引/chapters.json", category, findings, expected_type=list)
    if not isinstance(chapters, list):
        return
    record = find_record_by_number(chapters, "chapter_number", chapter_number)
    if record is None:
        review_add(findings, "warning", category, f"chapter not listed in chapters.json: 第{chapter_number:03d}章", "运行 `index` 更新章节索引。")
    else:
        review_add(findings, "pass", category, f"chapter is listed in chapters.json: 第{chapter_number:03d}章", "")
    for item in chapters:
        if not isinstance(item, dict):
            continue
        path = item.get("path")
        if isinstance(path, str) and not (root / path).is_file():
            review_add(findings, "warning", category, f"indexed chapter path is missing: {path}", "运行 `index` 或修正 chapters.json。")


def review_check_summary(root: Path, chapter_number: int, findings: list[dict]) -> None:
    category = "index_summary"
    summary_path = summary_file_path(root, chapter_number)
    if not summary_path.is_file():
        review_add(findings, "warning", category, f"missing chapter summary: {relative_path(root, summary_path)}", "运行 `chapter-summary` 生成摘要。")
        return
    text = read_text(summary_path)
    review_add(findings, "pass", category, f"chapter summary exists: {relative_path(root, summary_path)}", "")
    if count_words(text) < 80:
        review_add(findings, "warning", category, f"chapter summary is short: {relative_path(root, summary_path)}", "补全本章发生事项、人物变化、伏笔和承接点。")
    else:
        review_add(findings, "pass", category, "chapter summary has enough structure/content", "")


def review_check_chapter_plan(chapter_number: int, chapter_text: str, chapter_plans, chapter_plan, findings: list[dict]) -> None:
    category = "plan_alignment"
    if not isinstance(chapter_plans, list):
        return
    if chapter_plan is None:
        review_add(findings, "warning", category, f"missing chapter_plan for 第{chapter_number:03d}章", "运行 `add-chapter-plan` 并补齐目标、冲突、角色、场景和伏笔字段。")
        return
    review_add(findings, "pass", category, f"chapter_plan exists for 第{chapter_number:03d}章", "")
    core_values = [
        chapter_plan.get("goal"),
        chapter_plan.get("conflict"),
        chapter_plan.get("scenes"),
        chapter_plan.get("characters"),
    ]
    if all(is_empty_value(value) for value in core_values):
        review_add(findings, "warning", category, "chapter_plan goal/conflict/scenes/characters are all empty", "补齐章纲核心字段后再判断章节对齐。")
    else:
        review_add(findings, "pass", category, "chapter_plan has at least one core planning field", "")
    for name in list_value(chapter_plan.get("characters")):
        if name and name not in chapter_text:
            review_add(findings, "warning", category, f"planned character not found in chapter text: {name}", "确认角色是否应出场，或更新章纲。")
    for field in ["hooks_to_introduce", "hooks_to_advance", "hooks_to_resolve"]:
        for hook in list_value(chapter_plan.get(field)):
            if hook and hook not in chapter_text:
                review_add(findings, "warning", category, f"planned hook not found in chapter text: {hook}", f"确认 `{field}` 是否已在正文体现，或更新章纲/伏笔记录。")


def review_check_characters_deep(chapter_number: int, chapter_text: str, characters, findings: list[dict]) -> None:
    category = "character"
    if not isinstance(characters, list):
        return
    if not characters:
        review_add(findings, "warning", category, "characters.json is empty", "建议补充人物状态记录。")
        return
    for index, item in enumerate(characters, start=1):
        if not isinstance(item, dict):
            review_add(findings, "warning", category, f"character record #{index} is not an object", "修正 characters.json 结构。")
            continue
        name = item.get("name")
        if not name:
            review_add(findings, "warning", category, f"character record #{index} missing name", "补齐 name 字段。")
            continue
        last_seen = item.get("last_seen_chapter")
        if name in chapter_text and isinstance(last_seen, int) and last_seen < chapter_number:
            review_add(findings, "warning", category, f"character appears but last_seen_chapter is older: {name}", "确认是否需要更新人物状态。")
    review_add(findings, "pass", category, f"character records checked: {len(characters)}", "")


def review_check_hooks_deep(chapter_text: str, hooks, findings: list[dict]) -> None:
    category = "hook"
    if not isinstance(hooks, list):
        return
    if not hooks:
        review_add(findings, "warning", category, "hooks.json is empty", "建议补充伏笔记录。")
        return
    for index, item in enumerate(hooks, start=1):
        if not isinstance(item, dict):
            review_add(findings, "warning", category, f"hook record #{index} is not an object", "修正 hooks.json 结构。")
            continue
        missing = [field for field in ["title", "status"] if not item.get(field)]
        if missing:
            review_add(findings, "warning", category, f"hook record #{index} missing field(s): {', '.join(missing)}", "补齐伏笔 title/status 字段。")
        title = item.get("title")
        if title and title in chapter_text:
            review_add(findings, "warning", category, f"hook title appears in chapter text: {title}", "确认该伏笔 status 是否需要更新。")
    review_add(findings, "pass", category, f"hook records checked: {len(hooks)}", "")


def review_check_timeline(chapter_number: int, timeline, findings: list[dict]) -> None:
    category = "timeline"
    if not isinstance(timeline, list):
        return
    events = [item for item in timeline if isinstance(item, dict) and item.get("chapter_number") == chapter_number]
    if not events:
        review_add(findings, "warning", category, f"no timeline event for 第{chapter_number:03d}章", "如本章推进事件，建议补充 timeline event。")
    else:
        review_add(findings, "pass", category, f"timeline events for chapter: {len(events)}", "")
    seen = []
    for index, item in enumerate(timeline, start=1):
        if not isinstance(item, dict):
            continue
        number = item.get("chapter_number")
        if number is None:
            review_add(findings, "warning", category, f"timeline event #{index} missing chapter_number", "补齐时间线章节号。")
        elif number in seen:
            review_add(findings, "warning", category, f"timeline chapter_number repeated: {number}", "确认重复是否代表同章多事件；必要时补 order 或 notes。")
        seen.append(number)


def review_check_scenes_conflicts(chapter_number: int, scenes, conflicts, findings: list[dict]) -> None:
    category = "scene_conflict"
    if isinstance(scenes, list):
        chapter_scenes = [item for item in scenes if isinstance(item, dict) and item.get("chapter_number") == chapter_number]
        if not chapter_scenes:
            review_add(findings, "warning", category, f"no scene card for 第{chapter_number:03d}章", "运行 `add-scene` 或补齐 scenes.json。")
        else:
            review_add(findings, "pass", category, f"scene cards for chapter: {len(chapter_scenes)}", "")
        for item in chapter_scenes:
            scene_id = item.get("scene_id") or f"chapter {chapter_number}"
            missing = [field for field in ["purpose", "conflict", "outcome"] if not item.get(field)]
            if missing:
                review_add(findings, "warning", category, f"scene {scene_id} missing field(s): {', '.join(missing)}", "补齐场景目的、冲突和结果，便于审查节奏。")
    if isinstance(conflicts, list):
        active = [
            item
            for item in conflicts
            if isinstance(item, dict) and str(item.get("status", "")).lower() in {"active", "open", "进行中", "开启"}
        ]
        if not active:
            review_add(findings, "warning", category, "no active/open conflict records", "如项目需要结构化冲突线，补充 conflicts.json。")
        else:
            review_add(findings, "pass", category, f"active/open conflict records: {len(active)}", "")


def review_check_retrieval_context(root: Path, chapter_number: int, findings: list[dict]) -> None:
    category = "retrieval_context"
    pack_path = context_pack_path(root, chapter_number)
    if pack_path.is_file():
        review_add(findings, "pass", category, f"context pack exists: {relative_path(root, pack_path)}", "")
        if count_words(read_text(pack_path)) < 120:
            review_add(findings, "warning", category, "context pack is short", "确认 context-pack 是否包含足够的相关片段。")
    else:
        review_add(findings, "warning", category, f"context pack missing: {relative_path(root, pack_path)}", "运行 `context-pack` 生成写作上下文包。")
    index_path = root / RETRIEVAL_DIR / "retrieval-index.json"
    if not index_path.is_file():
        review_add(findings, "warning", category, "retrieval-index.json missing", "运行 `build-index` 建立本地检索索引。")
        return
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        review_add(findings, "error", category, f"invalid retrieval-index.json: {exc}", "修复索引 JSON 或重新运行 `build-index`。")
        return
    built_at = parse_datetime(str(index.get("built_at", "")))
    if not built_at:
        review_add(findings, "warning", category, "retrieval index missing valid built_at", "重新运行 `build-index`。")
        return
    stale = []
    for source in [chapter_file_path(root, chapter_number), root / "大纲" / "chapter_plans.json"]:
        if source.is_file() and datetime.fromtimestamp(source.stat().st_mtime, timezone.utc) > built_at:
            stale.append(relative_path(root, source))
    if stale:
        review_add(findings, "warning", category, "retrieval index may be stale: " + ", ".join(stale), "运行 `build-index` 更新索引。")
    else:
        review_add(findings, "pass", category, "retrieval index is current for chapter draft and chapter plans", "")


def review_check_setting_risks(root: Path, chapter_number: int, chapter_text: str, findings: list[dict]) -> None:
    category = "setting_risk"
    if "待填写" in chapter_text:
        review_add(findings, "warning", category, "chapter still contains placeholder text: 待填写", "补齐模板占位内容后再进入正式审查。")
    else:
        review_add(findings, "pass", category, "no obvious placeholder marker found in chapter text", "")
    safety_matches = []
    targets = [
        chapter_file_path(root, chapter_number),
        summary_file_path(root, chapter_number),
        context_pack_path(root, chapter_number),
    ]
    for path in targets:
        if not path.is_file():
            continue
        text = read_text(path)
        for line in text.splitlines():
            if any(term in line for term in DOCTOR_SAFETY_TERMS):
                safety_matches.append(f"{relative_path(root, path)}: {line.strip()[:120]}")
                break
    if safety_matches:
        review_add(findings, "warning", category, "generic content safety terms found", "对 examples/templates/docs 应清理；真实用户项目可自行判断是否忽略。")
        for item in safety_matches:
            review_add(findings, "warning", category, item, "检查是否为不应进入通用示例的内容。")
    else:
        review_add(findings, "pass", category, "no generic content safety terms found in reviewed files", "")


def write_deep_review_report(root: Path, chapter_number: int, result: dict) -> None:
    findings = result["findings"]
    counts = count_review_findings(findings)
    report_path = result["report_path"]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    template = read_review_template(root, "deep-review-template.md")
    risk_level = "error" if counts["error"] else ("warning" if counts["warning"] else "pass")
    report = template.format(
        chapter_padded=f"{chapter_number:03d}",
        review_target=f"正文/第{chapter_number:03d}章.md",
        created_at=datetime.now(timezone.utc).isoformat(),
        summary=f"- pass：{counts['pass']}\n- warning：{counts['warning']}\n- error：{counts['error']}",
        risk_level=risk_level,
        chapter_structure_check=format_review_category(findings, "chapter_structure"),
        plan_alignment_check=format_review_category(findings, "plan_alignment"),
        character_check=format_review_category(findings, "character"),
        hook_check=format_review_category(findings, "hook"),
        timeline_check=format_review_category(findings, "timeline"),
        scene_conflict_check=format_review_category(findings, "scene_conflict"),
        index_summary_check=format_review_category(findings, "index_summary"),
        retrieval_context_check=format_review_category(findings, "retrieval_context"),
        setting_risk_check=format_review_category(findings, "setting_risk"),
        questions=format_review_questions(findings),
        fix_suggestions=format_review_suggestions(findings),
        post_write_todos=format_review_todos(findings),
        raw_findings=format_raw_review_findings(findings),
    )
    report_path.write_text(report, encoding="utf-8")


def write_review_summary(root: Path, start: int, end: int, results: list, total: dict[str, int]) -> Path:
    output_path = root / "审查报告" / f"review-summary-第{start:03d}-第{end:03d}章.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    template = read_review_template(root, "review-summary-template.md")
    high_priority = []
    chapter_reports = []
    for number, result, counts in results:
        report_path = result["report_path"]
        chapter_reports.append(
            f"- 第{number:03d}章：pass={counts['pass']} warning={counts['warning']} error={counts['error']} | {relative_path(root, report_path)}"
        )
        for item in result["findings"]:
            if item["level"] in {"error", "warning"}:
                high_priority.append(f"- 第{number:03d}章 [{item['level']}] {item['message']}")
    report = template.format(
        review_range=f"第{start:03d}章-第{end:03d}章",
        created_at=datetime.now(timezone.utc).isoformat(),
        pass_count=total["pass"],
        warning_count=total["warning"],
        error_count=total["error"],
        high_priority_issues="\n".join(high_priority[:20]) if high_priority else "- 暂无高优先级问题。",
        next_steps=(
            "- 先处理 error，再处理 warning。\n"
            "- 用户自行决定是否修改正文或更新状态文件。\n"
            "- 修改后重新运行 `chapter-summary`、`index`、`build-index`、`context-pack` 和 `review`。"
        ),
        chapter_reports="\n".join(chapter_reports) if chapter_reports else "- 暂无分章报告。",
    )
    output_path.write_text(report, encoding="utf-8")
    return output_path


def read_review_template(root: Path, name: str) -> str:
    project_template = root / "审查报告" / name
    if project_template.is_file():
        return read_text(project_template)
    return read_text(TEMPLATE_DIR / "审查报告" / name)


def format_review_category(findings: list[dict], category: str) -> str:
    items = [item for item in findings if item["category"] == category]
    if not items:
        return "- 暂无检查项。"
    return "\n".join(format_review_item(item) for item in items)


def format_review_item(item: dict) -> str:
    suggestion = item.get("suggestion") or "无需处理。"
    return f"- level: {item['level']} | category: {item['category']} | message: {item['message']} | suggestion: {suggestion}"


def format_review_questions(findings: list[dict]) -> str:
    questions = [item for item in findings if item["level"] in {"warning", "error"}]
    if not questions:
        return "- 暂无需要用户确认的问题。"
    return "\n".join(f"- {item['message']}" for item in questions[:12])


def format_review_suggestions(findings: list[dict]) -> str:
    suggestions = []
    for item in findings:
        if item["level"] in {"warning", "error"} and item.get("suggestion"):
            suggestions.append(f"- [{item['level']}] {item['suggestion']}")
    return "\n".join(suggestions) if suggestions else "- 暂无建议修复项。"


def format_review_todos(findings: list[dict]) -> str:
    todos = [
        "- 如修改正文，重新运行 `chapter-summary`。",
        "- 如新增或调整章节文件，重新运行 `index`。",
        "- 如改动设定、大纲、正文、人物或伏笔记录，重新运行 `build-index`。",
        "- 如继续写下一章，重新运行 `context-pack`。",
    ]
    if any(item["category"] == "character" and item["level"] == "warning" for item in findings):
        todos.append("- 检查是否需要更新 `人物状态/characters.json`。")
    if any(item["category"] == "hook" and item["level"] == "warning" for item in findings):
        todos.append("- 检查是否需要更新 `伏笔记录/hooks.json`。")
    return "\n".join(todos)


def format_raw_review_findings(findings: list[dict]) -> str:
    return "\n".join(format_review_item(item) for item in findings)


def find_record_by_number(records, field: str, number: int):
    if not isinstance(records, list):
        return None
    for item in records:
        if isinstance(item, dict) and item.get(field) == number:
            return item
    return None


def list_value(value) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if item]
    if value:
        return [str(value)]
    return []


def is_empty_value(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, list):
        return not value
    return False


def add_finding(findings: list[dict], details: dict[str, list[str]], section: str, level: str, message: str) -> None:
    findings.append({"section": section, "level": level, "message": message})
    details.setdefault(section, []).append(f"[{level}] {message}")


def count_findings(findings: list[dict]) -> dict[str, int]:
    counts = {"PASS": 0, "WARN": 0, "ERROR": 0}
    for item in findings:
        level = item.get("level")
        if level in counts:
            counts[level] += 1
    return counts


def summarize_section(findings: list[dict], section: str) -> str:
    section_items = [item for item in findings if item.get("section") == section]
    errors = sum(1 for item in section_items if item.get("level") == "ERROR")
    warnings = sum(1 for item in section_items if item.get("level") == "WARN")
    passes = sum(1 for item in section_items if item.get("level") == "PASS")
    return f"PASS={passes} WARN={warnings} ERROR={errors}"


def doctor_check_structure(root: Path, findings: list[dict], details: dict[str, list[str]]) -> None:
    add_finding(findings, details, "structure", "PASS", f"project directory exists: {root}")
    for dirname in NOVEL_DIRS:
        if (root / dirname).is_dir():
            add_finding(findings, details, "structure", "PASS", f"directory exists: {dirname}")
        else:
            add_finding(findings, details, "structure", "ERROR", f"missing required directory: {dirname}")
    if (root / RETRIEVAL_DIR).is_dir():
        add_finding(findings, details, "structure", "PASS", f"directory exists: {RETRIEVAL_DIR}")
    else:
        add_finding(findings, details, "structure", "WARN", f"missing local retrieval directory: {RETRIEVAL_DIR}")

    core_files = [
        "AGENTS.md",
        "正文/chapter-template.md",
        "章节索引/summary-template.md",
        "审查报告/review-template.md",
        "审查报告/continuity-report-template.md",
        "审查报告/doctor-report-template.md",
    ]
    for relative in core_files:
        if (root / relative).is_file():
            add_finding(findings, details, "structure", "PASS", f"core template exists: {relative}")
        else:
            add_finding(findings, details, "structure", "WARN", f"missing core template: {relative}")


def doctor_check_json(root: Path, findings: list[dict], details: dict[str, list[str]]) -> dict[str, dict]:
    json_files = [
        "人物状态/characters.json",
        "伏笔记录/hooks.json",
        "章节索引/chapters.json",
        "大纲/volumes.json",
        "大纲/chapter_plans.json",
        "大纲/timeline.json",
        "大纲/arcs.json",
        "大纲/scenes.json",
        "大纲/conflicts.json",
        ".webnovel/retrieval-config.json",
        ".webnovel/chunks.json",
        ".webnovel/retrieval-index.json",
    ]
    states = {}
    for relative in json_files:
        file_path = root / relative
        state = {"path": file_path, "relative": relative, "exists": file_path.is_file(), "valid": False, "data": None}
        states[relative] = state
        if not file_path.is_file():
            details["deep"].append(f"- {relative}: missing")
            level = "WARN"
            if relative in {".webnovel/chunks.json", ".webnovel/retrieval-index.json"}:
                message = f"missing retrieval index file: {relative}; run build-index when retrieval is needed"
            elif relative.startswith("大纲/"):
                message = f"missing structured planning JSON: {relative}; run plan-init when planning is needed"
            else:
                message = f"missing JSON file: {relative}"
            add_finding(findings, details, "json", level, message)
            continue
        try:
            state["data"] = json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            details["deep"].append(f"- {relative}: invalid")
            add_finding(findings, details, "json", "ERROR", f"invalid JSON in {relative}: {exc}")
            continue
        state["valid"] = True
        details["deep"].append(f"- {relative}: valid")
        add_finding(findings, details, "json", "PASS", f"valid JSON: {relative}")
    return states


def doctor_scan_chapter_candidates(root: Path) -> tuple[list[Path], list[Path]]:
    draft_dir = root / "正文"
    chapter_files = []
    abnormal_files = []
    if not draft_dir.is_dir():
        return chapter_files, abnormal_files
    for draft in sorted(draft_dir.glob("**/*")):
        if not draft.is_file() or draft.name.startswith("."):
            continue
        if draft.name == "chapter-template.md":
            continue
        if draft.suffix.lower() not in {".md", ".txt"}:
            continue
        if parse_chapter_number(draft) is None:
            abnormal_files.append(draft)
        else:
            chapter_files.append(draft)
    return chapter_files, abnormal_files


def doctor_check_chapters(
    root: Path,
    json_states: dict[str, dict],
    findings: list[dict],
    details: dict[str, list[str]],
    deep: bool,
) -> set[int]:
    chapter_files, abnormal_files = doctor_scan_chapter_candidates(root)
    chapter_numbers = {parse_chapter_number(path) for path in chapter_files}
    chapter_numbers.discard(None)
    if deep:
        details["deep"].append("### 扫描到的章节文件")
        details["deep"].extend(f"- {relative_path(root, path)}" for path in chapter_files)
        if not chapter_files:
            details["deep"].append("- 暂无章节文件。")

    if abnormal_files:
        for file_path in abnormal_files:
            add_finding(findings, details, "chapter_index", "WARN", f"abnormal chapter filename: {relative_path(root, file_path)}")
    else:
        add_finding(findings, details, "chapter_index", "PASS", "no abnormal chapter filenames found")

    chapters_state = json_states.get("章节索引/chapters.json", {})
    records = chapters_state.get("data") if chapters_state.get("valid") else []
    if not isinstance(records, list):
        add_finding(findings, details, "chapter_index", "ERROR", "章节索引/chapters.json must contain an array")
        records = []
    indexed_paths = []
    indexed_numbers = []
    for item in records:
        if not isinstance(item, dict):
            add_finding(findings, details, "chapter_index", "WARN", "chapters.json contains a non-object item")
            continue
        indexed_paths.append(item.get("path"))
        indexed_numbers.append(item.get("chapter_number"))

    duplicates = sorted(number for number in set(indexed_numbers) if number is not None and indexed_numbers.count(number) > 1)
    if duplicates:
        add_finding(findings, details, "chapter_index", "ERROR", f"duplicate chapter_number in chapters.json: {duplicates}")
    else:
        add_finding(findings, details, "chapter_index", "PASS", "no duplicate chapter_number in chapters.json")

    indexed_path_set = {path for path in indexed_paths if isinstance(path, str)}
    for draft in chapter_files:
        draft_relative = relative_path(root, draft)
        if draft_relative not in indexed_path_set:
            add_finding(findings, details, "chapter_index", "WARN", f"chapter draft not indexed: {draft_relative}")
    for indexed_path in indexed_path_set:
        if not (root / indexed_path).is_file():
            add_finding(findings, details, "chapter_index", "WARN", f"indexed chapter file is missing: {indexed_path}")
    if chapter_files and all(relative_path(root, draft) in indexed_path_set for draft in chapter_files):
        add_finding(findings, details, "chapter_index", "PASS", "all chapter drafts are listed in chapters.json")
    return {number for number in chapter_numbers if isinstance(number, int)}


def doctor_check_summaries(root: Path, chapter_numbers: set[int], findings: list[dict], details: dict[str, list[str]]) -> None:
    if not chapter_numbers:
        add_finding(findings, details, "chapter_summary", "PASS", "no chapter drafts require summaries yet")
        return
    missing = []
    for number in sorted(chapter_numbers):
        if not summary_file_path(root, number).is_file():
            missing.append(number)
    if missing:
        add_finding(findings, details, "chapter_summary", "WARN", "missing summary files: " + ", ".join(f"第{number:03d}章" for number in missing))
    else:
        add_finding(findings, details, "chapter_summary", "PASS", "all chapter drafts have summary files")


def doctor_check_plan_correspondence(
    root: Path,
    chapter_numbers: set[int],
    json_states: dict[str, dict],
    findings: list[dict],
    details: dict[str, list[str]],
) -> None:
    state = json_states.get("大纲/chapter_plans.json", {})
    records = state.get("data") if state.get("valid") else []
    if not isinstance(records, list):
        add_finding(findings, details, "planning", "ERROR", "大纲/chapter_plans.json must contain an array")
        return
    plan_numbers = {item.get("chapter_number") for item in records if isinstance(item, dict)}
    missing_plans = sorted(number for number in chapter_numbers if number not in plan_numbers)
    plans_without_drafts = sorted(number for number in plan_numbers if isinstance(number, int) and number not in chapter_numbers)
    if missing_plans:
        add_finding(findings, details, "planning", "WARN", "draft chapters without chapter_plan: " + ", ".join(f"第{number:03d}章" for number in missing_plans))
    else:
        add_finding(findings, details, "planning", "PASS", "all draft chapters have matching chapter_plan records")
    if plans_without_drafts:
        add_finding(findings, details, "planning", "WARN", "chapter_plan records without drafts: " + ", ".join(f"第{number:03d}章" for number in plans_without_drafts))
    else:
        add_finding(findings, details, "planning", "PASS", "no chapter_plan records are ahead of drafts")


def doctor_check_characters(json_states: dict[str, dict], findings: list[dict], details: dict[str, list[str]]) -> None:
    state = json_states.get("人物状态/characters.json", {})
    records = state.get("data") if state.get("valid") else []
    if not isinstance(records, list):
        add_finding(findings, details, "character", "ERROR", "人物状态/characters.json must contain an array")
        return
    if not records:
        add_finding(findings, details, "character", "WARN", "characters.json is empty; consider adding character state records")
        return
    for index, item in enumerate(records, start=1):
        if not isinstance(item, dict):
            add_finding(findings, details, "character", "WARN", f"character record #{index} is not an object")
            continue
        if not item.get("name"):
            add_finding(findings, details, "character", "WARN", f"character record #{index} is missing name")
    add_finding(findings, details, "character", "PASS", f"character records: {len(records)}")


def doctor_check_hooks(json_states: dict[str, dict], findings: list[dict], details: dict[str, list[str]]) -> None:
    state = json_states.get("伏笔记录/hooks.json", {})
    records = state.get("data") if state.get("valid") else []
    if not isinstance(records, list):
        add_finding(findings, details, "hook", "ERROR", "伏笔记录/hooks.json must contain an array")
        return
    if not records:
        add_finding(findings, details, "hook", "WARN", "hooks.json is empty; consider adding foreshadowing records")
        return
    for index, item in enumerate(records, start=1):
        if not isinstance(item, dict):
            add_finding(findings, details, "hook", "WARN", f"hook record #{index} is not an object")
            continue
        missing = [field for field in ["title", "status"] if not item.get(field)]
        if missing:
            add_finding(findings, details, "hook", "WARN", f"hook record #{index} missing field(s): {', '.join(missing)}")
    add_finding(findings, details, "hook", "PASS", f"hook records: {len(records)}")


def doctor_check_planning(json_states: dict[str, dict], findings: list[dict], details: dict[str, list[str]]) -> None:
    labels = {
        "大纲/volumes.json": "volumes",
        "大纲/chapter_plans.json": "chapter_plans",
        "大纲/timeline.json": "timeline",
        "大纲/arcs.json": "arcs",
        "大纲/scenes.json": "scenes",
        "大纲/conflicts.json": "conflicts",
    }
    overview = []
    for relative, label in labels.items():
        state = json_states.get(relative, {})
        if not state.get("exists"):
            overview.append(f"{label}: missing")
            continue
        data = state.get("data")
        if not state.get("valid") or not isinstance(data, list):
            overview.append(f"{label}: invalid")
            if state.get("valid"):
                add_finding(findings, details, "planning", "ERROR", f"{relative} must contain an array")
            continue
        overview.append(f"{label}: {len(data)}")
    add_finding(findings, details, "planning", "PASS", "planning overview: " + "; ".join(overview))


def doctor_check_retrieval(
    root: Path,
    json_states: dict[str, dict],
    findings: list[dict],
    details: dict[str, list[str]],
    deep: bool,
) -> None:
    config_state = json_states.get(".webnovel/retrieval-config.json", {})
    chunks_state = json_states.get(".webnovel/chunks.json", {})
    index_state = json_states.get(".webnovel/retrieval-index.json", {})
    if config_state.get("exists"):
        add_finding(findings, details, "retrieval", "PASS", "retrieval config exists")
    else:
        add_finding(findings, details, "retrieval", "WARN", "missing retrieval-config.json")
    if not chunks_state.get("exists") or not index_state.get("exists"):
        add_finding(findings, details, "retrieval", "WARN", "local retrieval index missing; run build-index")
        return
    chunks = chunks_state.get("data")
    index = index_state.get("data")
    if not isinstance(chunks, list):
        add_finding(findings, details, "retrieval", "ERROR", ".webnovel/chunks.json must contain an array")
        return
    if not isinstance(index, dict):
        add_finding(findings, details, "retrieval", "ERROR", ".webnovel/retrieval-index.json must contain an object")
        return
    expected_count = index.get("chunk_count")
    if expected_count != len(chunks):
        add_finding(findings, details, "retrieval", "WARN", f"retrieval chunk_count mismatch: index={expected_count}, chunks={len(chunks)}")
    else:
        add_finding(findings, details, "retrieval", "PASS", f"retrieval chunk_count matches: {len(chunks)}")
    source_files = index.get("source_files")
    if not isinstance(source_files, list) or not source_files:
        add_finding(findings, details, "retrieval", "WARN", "retrieval index source_files is empty")
        source_files = []
    else:
        add_finding(findings, details, "retrieval", "PASS", f"retrieval source_files: {len(source_files)}")
    if deep:
        details["deep"].append("### 本地检索索引源文件")
        details["deep"].extend(f"- {item}" for item in source_files)
        if not source_files:
            details["deep"].append("- 暂无 source_files。")
    built_at = parse_datetime(str(index.get("built_at", "")))
    if built_at:
        stale_sources = find_stale_retrieval_sources(root, config_state.get("data"), source_files, built_at)
        if stale_sources:
            add_finding(findings, details, "retrieval", "WARN", "retrieval index may be stale; newer source files: " + ", ".join(stale_sources[:8]))
        else:
            add_finding(findings, details, "retrieval", "PASS", "retrieval index is not older than scanned source files")
    else:
        add_finding(findings, details, "retrieval", "WARN", "retrieval-index.json missing valid built_at")


def find_stale_retrieval_sources(root: Path, config_data, source_files: list, built_at: datetime) -> list[str]:
    candidates = []
    if isinstance(config_data, dict):
        try:
            config = {
                "include_dirs": config_data.get("include_dirs") if isinstance(config_data.get("include_dirs"), list) else [],
                "exclude_patterns": config_data.get("exclude_patterns") if isinstance(config_data.get("exclude_patterns"), list) else [],
            }
            candidates.extend(iter_retrieval_files(root, config))
        except (OSError, ValueError):
            candidates = []
    if not candidates:
        candidates = [root / item for item in source_files if isinstance(item, str)]
    stale = []
    for file_path in candidates:
        if not file_path.is_file():
            continue
        if relative_path(root, file_path) == "审查报告/doctor-report.md":
            continue
        updated = datetime.fromtimestamp(file_path.stat().st_mtime, timezone.utc)
        if updated > built_at:
            stale.append(relative_path(root, file_path))
    return sorted(set(stale))


def doctor_check_generic_safety(root: Path, findings: list[dict], details: dict[str, list[str]]) -> None:
    matches = []
    scan_roots = [root]
    for base in scan_roots:
        for file_path in sorted(base.glob("**/*")):
            if not file_path.is_file():
                continue
            if any(part in {".git", "__pycache__"} for part in file_path.parts):
                continue
            if file_path.suffix.lower() not in {".md", ".txt", ".json", ".py"}:
                continue
            text = read_text(file_path)
            for line in text.splitlines():
                if any(term in line for term in DOCTOR_SAFETY_TERMS):
                    matches.append(f"{relative_path(root, file_path)}: {line.strip()[:120]}")
                    break
    if matches:
        add_finding(findings, details, "generic_safety", "WARN", f"generic content safety terms found: {len(matches)}")
        details["generic_safety"].extend(matches)
    else:
        add_finding(findings, details, "generic_safety", "PASS", "no generic content safety terms found")


def parse_datetime(value: str) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def build_doctor_report(
    root: Path,
    deep: bool,
    counts: dict[str, int],
    findings: list[dict],
    details: dict[str, list[str]],
) -> str:
    template_path = root / "审查报告" / "doctor-report-template.md"
    if template_path.is_file():
        template = read_text(template_path)
    else:
        template = read_text(TEMPLATE_DIR / "审查报告" / "doctor-report-template.md")
    risk_level = "ERROR" if counts["ERROR"] else ("WARN" if counts["WARN"] else "PASS")
    suggestions = [f"[{item['level']}] {item['message']}" for item in findings if item["level"] in {"ERROR", "WARN"}]
    if not suggestions:
        suggestions = ["暂无必须修复项。"]
    next_steps = [
        "根据本报告先修复 ERROR，再处理 WARN。",
        "结构或正文更新后运行 `python3 scripts/webnovel.py index <project_path>`。",
        "检索相关文件更新后运行 `python3 scripts/webnovel.py build-index <project_path>`。",
        "修复后再次运行 `python3 scripts/webnovel.py doctor <project_path> --deep`。",
    ]
    if deep:
        deep_items = details.get("deep", [])
        deep_details = "\n".join(deep_items) if deep_items else "暂无 deep 详情。"
    else:
        deep_details = "未启用 deep 模式。"
    return template.format(
        created_at=datetime.now(timezone.utc).isoformat(),
        project_path=root,
        mode="deep" if deep else "normal",
        summary=f"- PASS：{counts['PASS']}\n- WARN：{counts['WARN']}\n- ERROR：{counts['ERROR']}",
        structure_check=format_report_items(details.get("structure", []), "暂无结果。"),
        json_check=format_report_items(details.get("json", []), "暂无结果。"),
        chapter_index_check=format_report_items(details.get("chapter_index", []), "暂无结果。"),
        chapter_summary_check=format_report_items(details.get("chapter_summary", []), "暂无结果。"),
        planning_check=format_report_items(details.get("planning", []), "暂无结果。"),
        character_check=format_report_items(details.get("character", []), "暂无结果。"),
        hook_check=format_report_items(details.get("hook", []), "暂无结果。"),
        retrieval_check=format_report_items(details.get("retrieval", []), "暂无结果。"),
        generic_safety_check=format_report_items(details.get("generic_safety", []), "暂无结果。"),
        risk_level=risk_level,
        fix_suggestions=format_report_items(suggestions, "暂无必须修复项。"),
        next_steps=format_report_items(next_steps, "暂无下一步建议。"),
        deep_details=deep_details,
    )


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


def normalize_cli_dash(value: str) -> str:
    if value.startswith("–"):
        return "--" + value[1:]
    return value


if __name__ == "__main__":
    raise SystemExit(main())
