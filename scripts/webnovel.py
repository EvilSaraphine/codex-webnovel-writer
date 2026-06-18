#!/usr/bin/env python3
"""Small CLI for codex-webnovel-writer."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = PLUGIN_ROOT / "templates"
NOVEL_DIRS = ["设定集", "大纲", "正文", "审查报告", "伏笔记录", "人物状态", "章节索引"]
SKILLS = ["webnovel-init", "webnovel-plan", "webnovel-write", "webnovel-review", "webnovel-query"]


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

    args = parser.parse_args()
    if args.command == "init":
        return cmd_init(args.path, args.force)
    if args.command == "where":
        return cmd_where(args.path)
    if args.command == "check":
        return cmd_check(args.path)
    parser.error("unknown command")
    return 2


def cmd_init(path: Path, force: bool) -> int:
    target = path.expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)
    copy_template_agents(target, force)
    for dirname in NOVEL_DIRS:
        (target / dirname).mkdir(parents=True, exist_ok=True)
    seed_files(target)
    print(f"Initialized webnovel project: {target}")
    return cmd_check(target)


def copy_template_agents(target: Path, force: bool) -> None:
    source = TEMPLATE_DIR / "AGENTS.md"
    destination = target / "AGENTS.md"
    if destination.exists() and not force:
        return
    shutil.copyfile(source, destination)


def seed_files(target: Path) -> None:
    seeds = {
        "设定集/世界观.md": "# 世界观\n\n- 类型与核心卖点：\n- 世界规则：\n- 禁忌与代价：\n",
        "设定集/创作原则.md": "# 创作原则\n\n- 目标读者：\n- 叙事口味：\n- 避免事项：\n",
        "大纲/总纲.md": "# 总纲\n\n- 核心钩子：\n- 主角弧线：\n- 主要矛盾：\n- 结局方向：\n",
        "大纲/时间线.md": "# 时间线\n\n| 顺序 | 事件 | 影响 |\n| --- | --- | --- |\n",
        "章节索引/章节索引.md": "# 章节索引\n\n| 章节 | 标题 | 状态 | 大纲 | 正文 | 审查 |\n| --- | --- | --- | --- | --- | --- |\n",
        "伏笔记录/伏笔总表.md": "# 伏笔总表\n\n| 编号 | 设置位置 | 内容 | 预期回收 | 状态 |\n| --- | --- | --- | --- | --- |\n",
        "人物状态/人物总表.md": "# 人物总表\n\n| 人物 | 当前状态 | 目标 | 秘密 | 关系变化 |\n| --- | --- | --- | --- | --- |\n",
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
    if not (root / "templates" / "AGENTS.md").is_file():
        errors.append("missing templates/AGENTS.md")
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


def count_lines(path: Path) -> int:
    if not path.is_file():
        return 0
    return len(path.read_text(encoding="utf-8").splitlines())


if __name__ == "__main__":
    raise SystemExit(main())

