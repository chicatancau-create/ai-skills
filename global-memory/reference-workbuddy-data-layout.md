---
name: reference-workbuddy-data-layout
description: WorkBuddy 国内版数据在 ~/.workbuddy（userData 要从进程 --user-data-dir 拿）；工作空间下拉是 sessions.cwd 派生的、UI 无删除入口，清理用软删标记 deleted_at=-1。
metadata:
  type: reference
---

WorkBuddy（国内版，`D:\WorkBuddyAI\WorkBuddy.exe`，2026-11-03 实测 V5.9.3）的本机数据落位与列表机制。

**数据在哪**：`C:\Users\Admin\.workbuddy\`（**不是** `%APPDATA%\WorkBuddy`，那两个同名目录里搜不到项目名）。
真实 userData 只能从进程命令行拿：`Get-CimInstance Win32_Process` → `--user-data-dir=C:\Users\Admin\.workbuddy\app`。
国际版是另一套：`~\.workbuddy-ai\app`。核心库是 `~\.workbuddy\workbuddy.db`（SQLite + drizzle 迁移）。

**工作空间下拉为什么一直累加、且没有删除按钮**：它是**派生视图** ——
`sessions` 表里出现过的 `cwd` 去重，外加 `workspaces` 表的"最近打开"（本机 `workspaces` 只有 1 行，下拉却有 5 项）。
应用**不校验 cwd 是否还存在**，所以项目搬走或删掉后死路径照样列着。asar 全文搜不到"删除工作空间"类文案 ⇒ 这版没有该功能。

**清理的正确做法**（2026-11-03 实跑：6 条死路径会话清掉，下拉从 5 项降到 3 项）：

1. 备份 `workbuddy.db` **和 `-wal`、`-shm`** 三个文件（只备主库不够，WAL 里有未合并的写）。
2. 先完全退出应用。`CloseMainWindow` 关不掉 —— Electron 会缩进托盘，剩 8 个进程；要 `Stop-Process -Force`，否则内存态会回写。
3. 软删除用应用自己的写法：**`sessions.deleted_at = -1`**（INTEGER，**不是时间戳** —— 从已软删的既有行里学）。别 `DELETE` 行，保留可逆性。
4. `workspaces` 表里指向不存在目录的行可以直接 `DELETE`。
5. 重启核对。回滚：`update sessions set deleted_at=null where id in (...)`，或还原备份。

**判"死路径"的唯一依据**是 `os.path.isdir(cwd)` 为假；目录还在的一律保留（本机 `E:\OBsidian` 的 12 个会话就是这么留下的）。
注意 `cwd` 里正反斜杠混用（`E:/fullstack-code` 与 `E:\OBsidian`），判存在前先归一化。

**顺带一条**：WorkBuddy 的模型列表/价格缓存在 `~\.dsh\.workbuddy*-catalog.json` 这类文件里是**另一个体系**（DSH 插件写的），
插件卸载后那些目录就成了孤儿缓存、不会自更新 —— 别拿它当"当前价格"。

相关：[[reference-dsh-desktop-internals]]、[[reference-windows-permission-denied-as-missing]]、[[feedback-autostart-keep-clean-useless-only]]
