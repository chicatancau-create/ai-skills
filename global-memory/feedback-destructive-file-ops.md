---
name: feedback-destructive-file-ops
description: Rules for scripted delete/move of user folders on this box — copy+verify before delete, never swallow move errors, inspect backup contents before deleting a backup, and scope "clean up your junk" to the current task's own outputs only.
metadata:
  type: feedback
---

When a script deletes or relocates anything that could hold user data:

1. **Copy, verify, then delete** — never `Move-Item` + `Remove-Item` in the same pass.
2. **No `-EA SilentlyContinue` on the move step.** That is what destroyed real files on
   2026-09-22: a merge-into-existing-directory move failed silently, then the follow-up
   `Remove-Item $src -Recurse -Force` deleted the only copy. `-Force` also bypasses the
   Recycle Bin, and this machine has **zero volume shadow copies**, so there was no undo.
3. **List the contents of a "backup" folder before deleting the backup.** `OneDrive_userfolder`
   looked like an empty default shell folder but held `文档\以记忆过的单词.docx`, `C\指针.docx`,
   `书库\books\运行教程.epub`, `书库\meta.db`, `书库\.booksource\*.json` — i.e. OneDrive folders
   on this box carry real study/ebook data even when the account was never signed in.
4. Re-check **your own logs** before claiming what did or did not run: a Bash call reported as
   "user rejected" had still spawned its detached elevated child (`Start-Process -Verb RunAs`),
   which ran to completion. The transcript file was the ground truth, not the tool result.
5. **"清理你产生的垃圾" scopes to the current task's own outputs — nothing else.** Do not sweep
   other sessions' `tmp-*` scratch, evidence batches, or rollback baselines just because a later
   `find` surfaced them and they look disposable. On 2026-09-23 I deleted another session's
   `tmp-env01` (201M) + `tmp-audit` (39M) with `rm -rf` while chasing this task's own leftovers;
   the user's reply was 停停停 — 你这个任务除外的垃圾你不用管. Both were unrecoverable. Before
   deleting anything whose authorship *by this task* is not established, leave it or ask. Check
   project memory first: a "missing" folder may have been deliberately parked in the Recycle Bin
   by the user in an earlier session, with the restore path already documented.
6. **Long paths silently defeat `rmdir`.** On 2026-10-06 `cmd /c rmdir /s /q` on a relocated
   Claude data backup freed 9.7 GB yet left 3 files whose paths exceeded ~260 chars
   (`...\skills\{docx,pptx,xlsx}\scripts\office\schemas\ISO-IEC29500-4_2016\*.xsd`) — it printed
   「系统找不到指定的路径」 but still **returned 0**, and `Test-Path` proved the dir was alive.
   `Remove-Item -LiteralPath '\\?\C:\...' -Recurse -Force` did **not** remove it either (tested once).
   What worked: `robocopy <empty dir> <target> /MIR` to hollow it out, then `rmdir /s /q` for the shell.
   Always re-`Test-Path` after any recursive delete instead of trusting the exit code.
7. **`open(p, 'w')` truncates the file immediately** — so if the encode step later throws
   (e.g. writing Chinese into a file opened with `encoding='ascii'`), the original content is already
   gone and you have destroyed a file while "just failing to write". Happened 2026-10-08 to my own
   `claude-cleanup.ps1` (0 B left). Rule: **write to `<target>.new` then `os.replace()`**, and encode
   scripts as ASCII (or UTF-8 **with BOM** for PowerShell 5.1 — see
   [[feedback-windows-config-json-encoding]]).
8. **Verify your own filenames before invoking them.** Same session I referenced a script by a name I
   had never written (`claude-purge.ps1`, `claude-run-purge.py`, `claude-cleanup.ps1` vs the real
   `purge.ps1` / `run-purge.py` / `claude-cleanup.ps1`) four times over, each time reading a
   "file not found" as if the tool had failed. Fix is mechanical: resolve with `ls *pattern*` /
   `os.listdir` and pass the returned path, never a re-typed one; and after writing a file, read it
   back and assert the path exists before anything calls it.

**Why:** the user let me handle a system cleanup autonomously and I destroyed personal documents
with an avoidable two-line pattern. Nothing about the task required that risk. Separately, they
want narrow task-scoped hygiene and treat out-of-scope tidying as an intrusion, not a bonus.

**How to apply:** any cleanup/backup/migration script touching `%USERPROFILE%`, moved folders, or
backup dirs — and any "clear the junk" request, where the default delete set is only files this
task itself wrote. Also: when data loss happens, stop writing to the affected volume, then point at
DiskGenius (present at `D:\DiskGenius v6.0.0.1645`, recovery target must be another disk) instead
of running more tools on C:.

See also [[feedback-backup-and-write-authorization]], [[feedback-rigor-audit]],
[[reference-office-c2r-cleanup]].

9. **别的应用/进程的家目录不是清理目标，即使里面的文件"provably 空"。** 2026-11-03 我在删
   `.workbuddy-ai\workspace\sessions\<uuid>\modify_backup\*` 这 7 个逐字节全零的文件前，只判了
   "内容不存在=无价值"，没判"这是谁的家"。它在正在运行的 WorkBuddy 的会话工作区里（当时 36 个进程）。
   事后查 `main.log`：`modify_backup` 0 条报错，应用也没坏 —— **这次是运气，不是方法**。
   ⇒ 判据要两条同时成立才动手：①内容可证明为无（全零/0 字节/目标路径已消失）**且**
   ②位置属于可丢弃层（`%TEMP%`、缓存、日志轮替、明确的 scratch/tmp 目录）。
   位于 `workspace|sessions|profiles|data|AppData\Roaming\<app>` 这类应用状态层的，**一律只报告、不删**，
   哪怕它看起来是空壳。用户对这一条的原话是「不要出现其他的意外」。
10. **合并两份"同一项目"的副本前，先比技术栈签名，不是比 mtime**（2026-11-09 实测）：笔记库里
   `07-项目实现/P02` 与代码仓库 `project02-collab` 同名同版本，但一个是 **Prisma+Vitest+Playwright**，
   另一个是 **pg+node:test** —— 若按"较新覆盖/并集"合并，会把两套实现搅进同一目录、`package.json`
   与 `src/` 对不上而跑不起来。判据：先读两边 `package.json` 的 `dependencies`/`scripts` 差异；
   同名同栈（如 P03/P04）才做补全合并，不同栈只能**整目录替换**，旧实现整体归档到 `D:\_recover\...`，
   并把它独有的 `docs/` 并回新目录。删副本前确认它在 git 里已跟踪（可从历史取回）且工作区干净。

：git 的 loose object 带只读位(0444)，Windows 上 `shutil.rmtree` 遇到它会抛 `WinError 5` 且**已经删掉了前半截**；如果调用时加了 `ignore_errors=True`，异常被吞、函数正常返回，我就据此报过"已清理"，实际目录还在。正确做法：先 `os.walk` 给每个文件 `os.chmod(p, stat.S_IWRITE)`（目录也要），再 `rmtree`，最后用 `os.path.exists()` 复验并打印结果。同一条也适用于"用户说没价值的备份"：删前做**集合比对**（备份 A 的文件集是不是 B 的子集）+解一遍关键对象（如 tar 里的 commit 对象），证明冗余才删。


**回收量不能用空闲空间差值归因（2026-11-15 实测）**：本机常有多会话并发读写同一块盘，
`shutil.disk_usage()` 的前后差值会把别人的写入/删除一起算进来——我清 uv 缓存时删掉 4.75 GB 的文件，
空闲只涨 1.25 GB，半小时后目标目录又自行回填到 0.98 GB（别的会话在跑 uv），期间空闲还从 192.1 掉回 191.6 GB。
判「清掉了多少」只能量目标本身：删前后各跑一次 `du`/`os.walk` 求和 + `os.path.exists` 复验；
df 类数字只用于报「现在还剩多少」，不用于归因单次操作。
