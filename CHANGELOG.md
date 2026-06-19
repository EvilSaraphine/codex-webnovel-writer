# Changelog

All notable changes to this project are documented here. This project follows the Keep a Changelog format.

## [1.0.0] - 2026-06-19

### Added

- Codex-native plugin and Skills structure.
- Novel project initialization with generic templates.
- Structured planning files for volumes, chapter plans, timeline, arcs, scenes, and conflicts.
- Single-chapter workflow with draft template, chapter summary, and continuity checks.
- Character state tracking.
- Foreshadowing hook tracking.
- Chapter index generation.
- Local Retrieval / Light RAG using local files and Python standard library only.
- Context pack generation for chapter writing.
- Write brief generation for pre-drafting preparation.
- Full write workflow with write workspace and finalize-write steps.
- Deep review reports for single chapters and chapter ranges.
- Doctor health check for project structure, JSON files, indexes, summaries, planning, state records, retrieval, and generic content safety.
- AI phrasing / style check for common AI-flavored expressions and style risks.
- Query workflow for local project files.
- Learn Skill for recording preferences, style constraints, and long-term project memory.
- Generic open-source tool principle: templates and examples use placeholders only; user novel content belongs in separate initialized projects.

### Notes

- No external dependencies are required.
- Local retrieval runs locally by default; it does not require network access, APIs, embedding providers, or model downloads.
- Review, doctor, write-brief, write, and style-check workflows are designed to preserve user-authored drafts and avoid automatic prose rewrites.
