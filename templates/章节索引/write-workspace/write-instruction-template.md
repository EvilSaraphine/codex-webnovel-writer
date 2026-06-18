# 第{chapter_padded}章写作指令

- 本章写作入口：{entry}
- 生成时间：{created_at}
- 说明：本文件用于组织写作流程，不会自动生成正文。

## 需要先阅读的文件

- 写作任务书：{write_brief_path}
- context-pack：{context_pack_path}
- 章纲：{chapter_plan_path}
- 正文草稿：{draft_path}

## 写作任务书路径

{write_brief_path}

## context-pack 路径

{context_pack_path}

## 章纲路径

{chapter_plan_path}

## 正文草稿路径

{draft_path}

## 写作注意事项

- 不要编造未确认设定。
- 不要自动改人物、伏笔、大纲 JSON 或设定文件。
- 任务书和 context-pack 只作为参考，不是新设定。
- 如信息不足，先提示用户补充。
- 正文写在 `正文/第{chapter_padded}章.md`。

## 写后必须运行的命令

```bash
python3 scripts/webnovel.py finalize-write {project_path} {chapter_number}
```
