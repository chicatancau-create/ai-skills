# global-memory — 全机共享全局记忆

> 供本机所有 AI 使用（DSH / Codex / Claude Code / OpenCode / OpenClaw(FlowyAIPC) / Continue / Qoder 国际版与国内版等）。
> 用户要求（2026-11-19）：「所有 AI 都要能用到它，这个记忆非常重要」。

## 这是什么

- 2026-11-19 从 Qoder 国际版全局记忆 `C:\Users\Admin\.qoder\memory`（junction→`D:\DevCache\.qoder\memory`）单向导入 118 个 .md（117 条记忆 + MEMORY.md 索引），再并入国内版 `.qoder-cn` 独有的 8 条 → **共 125 条记忆 + MEMORY.md 索引**，逐文件 sha256 双端校验。
- 源索引漏掉的 5 条已在本库 MEMORY.md 补全：feedback-subagent-write-reliability、reference-android-root-without-unlock、reference-bilibili-open-api-read、reference-ppt-master-workflow、reference-sqlite-wal-checkpoint-on-close。**源库只读，未改动。**
- 实体在 D 盘，随 `D:\Skills` 技能库自动双远端私有备份（GitHub chicatancau-create/ai-skills + GitCode zhoumoyukuai/ai-skills）。

## 国内版并集与冲突处理（2026-11-19）

- 国内版 `C:\Users\Admin\.qoder-cn\memory`（77 文件）已单向 cp -n 补齐到 126 文件（49 拷贝，0 覆盖），索引手工合并（国际版修正基底 + 8 条国内独有行），orphan=0；旧索引备份 `MEMORY.md.bak-20261119`。
- 30 个同名不同内容文件已逐个 diff 分诊（证据 `cn_conflicts_analysis.json` / `cn_plus_only.txt`）：
  - 23 个国际版更新、5 个同时间戳但国内版是子集 → 共享库保留更丰富的国际版；国内版旧副本按手册 no-clobber 不覆盖。
  - 8 个文件里「国内版独有且共享库确实缺失」的实质内容（2026-11-04/11-05 用户更正与复测）已以**带日期附录**逐字追加进共享库对应文件（feedback-backup-and-write-authorization、feedback-toolkit-is-tools-only、feedback-subagent-write-reliability、reference-git-credential-manager-windows、reference-git-push-needs-local-proxy、reference-qoder-artifact-locations、reference-windows-python-encoding、user-role），原文未动（前缀字节断言通过）。
  - 其余独有行是 frontmatter/相关链接噪声或已被国际版吸收 → 不并入。
- 刷新脚本只导入国际版新增；国内版后续新增需人工 diff 后按同样纪律并入。

## 怎么用（所有 AI）

1. 动手前先扫 `MEMORY.md`（每条一行摘要），按任务症状/关键词定位（可 grep），读命中条目正文。
2. 涉及用户偏好、沟通方式、任务边界 → 读 `user-role.md`。
3. 条目只是「候选经验」，必须用当前项目事实复核；不得因记忆有记录就跳过测试与审查。
4. 群聊/共享上下文不引用私人条目（防隐私外泄）。

## 写入纪律

- **只追加**：新条目（feedback-* 教训 / reference-* 参考 / user-* 画像）+ MEMORY.md 新索引行；不改写、不删除已有内容。
- 不写入密码、Token、API Key、私钥、Cookie、个人隐私或生产敏感数据。
- 各 AI 本地新增受 no-clobber 保护，同步脚本不会覆盖。

## 刷新（单向导入 Qoder 国际版新增）

```
C:\Users\Admin\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe -X utf8 D:\Skills\global-memory\sync_from_qoder.py --report <报告.json>
```

- no-clobber：不覆盖任何已存在文件；MEMORY.md 是合并索引，永不覆盖。
- 每个新拷文件 sha256 双端校验；索引漏条目自动按 frontmatter description 补行。
- 同名不同内容：只报告不覆盖，需人工 diff 决定。
- **禁止**把本目录与 .qoder / .qoder-cn 做 junction 实时共用（MEMORY.md 会互相覆盖，手册明令禁止）。

## 接线清单（2026-11-19）

| AI | 接线面 | 方式 |
|---|---|---|
| DSH | `D:\DevCache\.dsh\AGENTS.md` | 追加「第〇节之二」 |
| Codex | `D:\DevCache\.codex\AGENTS.md` | 追加「二十一」 |
| Claude Code | `D:\DevCache\.claude\CLAUDE.md` | 新建 |
| OpenCode | `C:\Users\Admin\.config\opencode\AGENTS.md` | 新建 |
| OpenClaw/FlowyAIPC | `C:\Users\Admin\.openclaw\workspace\AGENTS.md` | 追加 |
| Continue | `C:\Users\Admin\.continue\config.yaml` | 追加 rules |
| Qoder 国内版 | `C:\Users\Admin\.qoder-cn\memory` | 单向 cp -n + 索引合并 |
| Qoder 国际版 | 源库 | 只读，不动 |
| DSH 语义检索 | MemSearch `memsearch_chunks` 集合 | index 本目录 |
| WorkBuddy / 豆包 | 无安全文件接线面 | 需要时手动读本目录 |

## 证据

目录：`G:\AIrenwu\01_任务归档\2026-11-19_导入Qoder全局记忆\02_证据日志\`

- `import_report.json` — 国际版导入 + 全量 sha256 manifest
- `cn_sync_report.json` — 国内版 cp -n 同步 + 索引合并
- `cn_unique_merge_report.json` — 8 条国内独有并入共享库
- `cn_conflicts_analysis.json` / `cn_plus_only.txt` / `cn_unique_lines.txt` — 30 冲突分诊与独有行取证
- `cn_addenda_report.json` — 8 个文件的带日期附录追加（前后字节数、原文未动断言）
