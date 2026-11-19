---
name: feedback-clean-room-git-archive
description: 验证“干净环境可复现”时用 git archive HEAD 导出到临时目录再装依赖跑门禁，不复制工作树；manifest 也要在 archive 里 verify，CRLF/被忽略文件会造成哈希漂移
metadata:
  type: feedback
---

做“干净目录/干净环境复现”时，用 `git archive HEAD <project-path> | tar -x -C $(mktemp -d)` 只导出已跟踪文件，
在新目录执行 `npm ci` / Maven 构建并跑项目自己的 `run_project.sh`；不要 `cp -r` 工作树。

**Why:** 复制工作树会把 `node_modules`、`target`、未跟踪的本地补丁带进去，掩盖“锁文件/提交是否自足”；
2026-11-07 对 7 个项目做该复现，全部退出码 0，才敢把“干净目录通过”与普通“本机自测”区分开。

**How to apply:**
- 结果里同时记录主机、Node/JDK、服务版本，并明确“同一台机器/同一批本地服务，不是独立 OS/CI”。
- 只导出目标子目录，避免把整个 monorepo 复制一遍；临时目录用后删除。
- 2026-11-07 同一方法也用于 **E03–E13 共 11 个实验**：导出整个 `06-实验代码` 以保留 `_shared` 依赖，再逐个 `npm ci` + 实验脚本，11/11 退出码 0。
- **有些实验把结果重定向到 `evidence/run.txt`，stdout 是空的**：`rc=0` + 空日志不等于有输出。必须把临时目录里的 `evidence/run.txt` 复制出来并看关键字（`PASS/exit=/ok=`），否则会漏掉“静默成功/静默失败”。
- 与 [[feedback-rigor-audit]] 配套：干净目录通过 ≠ 限定范围验收通过。
- **manifest 也要在 archive 里 verify**：`git archive HEAD | tar -x` 后逐项目跑 `node scripts/manifest.mjs verify evidence/manifest.json`，再决定是否加 CI。2026-11-08 用此法发现 P02/P03/P04/P05/B5-01 在 CI 会 `HASH MISMATCH`：工作树是 CRLF、仓库 checkout 是 LF；P02 还把被 `.gitignore` 忽略的 `p02-dump.sql` 写进 manifest，干净导出必然 `MISSING`。
- 修法是给 evidence/deploy/migrations 的文本加 `.gitattributes` `text eol=lf`，先提交证据字节，再重算 manifest；被忽略的 dump/备份不要放进 manifest，只引用 `backup.txt` 一类已跟踪摘要。
- **一键 archive 复核**：2026-11-08 新增 `scripts/verify_archive.sh`，一次导出两个仓库并验 source-only + 14 个实验 + 8 个项目；`git archive` 出来的临时目录不是 git 仓库，`source-only` 这类用 `git ls-files` 的工具会退出 128，先 `git init -q && git add -A` 再跑。最终 `ARCHIVE VERIFY PASS` 才能替代被计费卡住的 CI。
- **重跑实验后先提交证据再重算 manifest**：E04 重跑产生 CRLF，manifest 按工作树哈希生成，archive 里 6 个文件 `HASH MISMATCH`；统一 LF 并重算后才通过。manifest 的 `command exit=0` 只在真的重跑过时填写，没重跑不要补。
