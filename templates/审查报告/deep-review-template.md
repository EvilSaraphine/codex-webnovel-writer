# 第{chapter_padded}章深度审查报告

- 审查对象：{review_target}
- 生成时间：{created_at}
- 说明：review 是只读审查，只给诊断和建议；不会自动改正文，也不会自动写回设定、人物、伏笔、大纲或章节摘要。

## 审查摘要

{summary}

## 风险等级

{risk_level}

## 章节结构检查

{chapter_structure_check}

## 章纲对齐检查

{plan_alignment_check}

## 人物状态检查

{character_check}

## 伏笔检查

{hook_check}

## 时间线检查

{timeline_check}

## 场景与冲突检查

{scene_conflict_check}

## 章节索引与摘要检查

{index_summary_check}

## 本地检索上下文检查

{retrieval_context_check}

## 设定一致性风险

{setting_risk_check}

## 风格与 AI 句式风险

- 本报告不自动调用 style-check。
- 详细检测请单独运行：`python3 scripts/webnovel.py style-check <project_path> 正文/第{chapter_padded}章.md`
- style-check 只生成风格风险报告，不自动修改正文；命中结果需要人工结合上下文确认。

## 需要用户确认的问题

{questions}

## 建议修复项

{fix_suggestions}

## 写作后待办

{post_write_todos}

## 原始检查项

{raw_findings}
