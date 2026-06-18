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
SKILLS = [
    "webnovel-init",
    "webnovel-plan",
    "webnovel-write",
    "webnovel-review",
    "webnovel-query",
    "webnovel-learn",
]
TEMPLATE_FILES = [
    "AGENTS.md",
    "设定集/写作偏好.md",
    "设定集/风格禁区.md",
    "章节索引/chapters.json",
    "伏笔记录/hooks.json",
    "人物状态/characters.json",
    "审查报告/review-template.md",
]
SEARCH_DIRS = ["设定集", "大纲", "正文", "伏笔记录", "人物状态", "章节索引"]


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

    draft_dir = target / "正文"
    output_path = target / "章节索引" / "chapters.json"
    chapters = []
    for draft in sorted(draft_dir.glob("**/*")):
        if not draft.is_file() or draft.name.startswith("."):
            continue
        if draft.suffix.lower() not in {".md", ".txt"}:
            continue
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
    for relative in TEMPLATE_FILES:
        if not (root / "templates" / relative).is_file():
            errors.append(f"missing template file: templates/{relative}")
    for relative in ["章节索引/chapters.json", "伏笔记录/hooks.json", "人物状态/characters.json"]:
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
