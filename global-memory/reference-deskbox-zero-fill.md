---
name: reference-deskbox-zero-fill
description: 整文件被 0x00 覆写（尺寸保留、mtime 不可信）已发生三次：2026-10-03 E:\DeskBox，2026-10-08 与 2026-10-12 E:\fullstack-code；10-12 查明根因是 E/F/G 同在一块无 DRAM 的 NVMe 上反复掉电，判据是数非零字节
metadata:
  type: reference
---

`E:\DeskBox` 里的文件可能**不是"坏了"而是被整体零填充**：2026-10-03 16:34:50 该夹四个条目被同时
重建（PowerToys FindMyFolders 的 `fileAddedAt` 记录同一毫秒），约 40 个 `.lnk` 一度变成全 `0x00`，
`.lnk` 在 17:40 被重新生成，而 `VPN\fix-network.bat` 没人重建 —— 7541 字节全是 `0x00`，
`fsutil queryvaliddata` 显示不是稀疏文件（簇被物理覆写），回收站 / 编辑器历史 / D、H 盘全查过，
**原文无法恢复**。它的 mtime 还停在覆写前的 2026-09-17 09:57，所以"看修改时间"会误判成它没动过。

残骸记录（全零 + 还原的原 mtime）：`G:\AIrenwu\DeskBox-原件备份-20261003\VPN\fix-network.zeroed-7541B-mtime20260917.bak`

**Why:** 当时那次备份清单按 `.lnk` 建的，`fix-network.bat` 记的是 `COPY None（目标不存在）`——
备份覆盖率按扩展名漏了脚本类文件，所以现在没有任何一份原件可对照。

**How to apply:** 用户报"DeskBox 里的东西双击没反应"时，**第一步用 python 数前 64 字节是不是全零**，
而不是去查逻辑或权限；判死之后再按当前机器实况重写（`fix-network.bat` v2.0 = 2026-10-05 重写，
职责是重置 Clash Verge 的 `verge-mihomo` 内核 + 本机网络，只管 Clash Verge，参数 `check`/`deep`）。
再给 DeskBox 做备份时，先数目录里的文件类型分布，别只按 `.lnk` 建清单。

**第二次发生：2026-10-08 09:4x，`E:\fullstack-code\.git`（学习仓库）。** 同一失效模式——文件尺寸保留、
内容整份变 `0x00`：`.git/index` 4321 字节 nonzero=0（git 报 `bad signature 0x00000000`，此后该仓库
任何 git 命令直接 fatal），`git fsck` 另报 7 个 loose object 全零（共 22 条 error，objects 目录 66 个文件），
`git log` 两个提交仍可读。同期 `E:\fullstack-code\Harmony\` 下的 `MyFirstHarmony/`、`honmenxuexao/` 两个
工程目录整体消失，只剩当天新建的 `MyApplication/`；这两工程从未提交（HEAD 33 个文件里 0 个 Harmony 相关），
当前用户回收站仅 4 项无命中 → 内容基本无法恢复。**判据是 `sum(1 for b in data if b) == 0`，不是 mtime。**

**第三次发生：2026-10-12，`E:\fullstack-code` 整仓 + 其 node_modules。** 一次 `npm run dev` 报
`failed to load config ... SyntaxError: Invalid or unexpected token`，而配置文件本身干净 —— 真因是
`@vue/devtools-shared/dist/index.js` 等 29 个 node_modules 文件被零填充。全仓扫描：**4787 个文件里 715 个整文件 0x00**
（`Python\.venv` 658/764=86%、`Web\vue` 31、`.git` 18/92），另有 `progress.md`、`errors.md`、`Cpp\*.exe`、
`Web\js自学\*.html`、`Web\vue\public\favicon.ico`。判据仍是 `sum(1 for b in data if b) == 0`。

根因证据（同一次排查量到）：E:/F:/G: 三个分区都在 **Disk 1 = YMTC PC41Q-1TB-B（无 DRAM 缓存的 NVMe）** 上；
`chkdsk E: /scan` 未发现一致性问题、坏扇区 0 KB；`Get-StorageReliabilityCounter` 给 Wear=0、温度 32℃、错误计数器不上报；
近 30 天 System 日志 **9 次 Kernel-Power 41 + volmgr 161**（未正常关机）加多次 Ntfs 98/130/55。
→ 不是盘体磨损也不是 MFT 结构坏，而是**掉电时数据页未落盘、目录项与尺寸先落地**，读回就是全零。
所以：E: 上不要放唯一副本，遇到反复硬关机/崩溃重启就要按本模式预期出现"尺寸对、内容零"的文件。

git 修复的坑：`.git/index` 全零时 `git reset` 也修不好——索引条目要写 blob 的 size，而 HEAD 的树里有 7 个
loose object 已被清零（`git cat-file -s HEAD:README.md` 直接 inflate 报错）。可行做法是**完全不读 HEAD** 重建：
`git ls-files -o --exclude-standard -z | xargs -0 -n 400 git update-index --add --replace`，之后 `git status` 恢复，
但 `git reset` / `read-tree HEAD` 仍会失败，旧提交里那几个路径永久读不出。内容能从完好的 blob 捞回两个
（`Web/vue/README.md`、`errors.md`），`progress.md` 与根 `README.md` 的 blob 已死。快照与清单在
`D:\_backups\fullstack-code-20261012-1420\` 和 `D:\_backups\zeroed-files-20261012.txt`；
删掉 node_modules 重装后 3276 个文件 0 全零，证明损坏来自磁盘写入而不是 npm 缓存。
处置结果：能从 git 完好 blob 原样捞回的捞回（`Web/vue/README.md`、`errors.md`、`Cpp/.vscode/tasks.json`），
可再生的重建（node_modules、`.venv`、两个 mingw exe、`favicon.ico`），内容真丢的只有
`Web\js自学` 两页笔记与旧 `progress.md`（blob 也在死对象里）——按用户要求重写并标明是重建。
快照与清单**当天已按用户指示删除**（`D:\_backups` 整目录不存在了），仓库现状与本次事件记录落在
`E:\fullstack-code\progress.md`（该文件本身就是 2026-10-12 重建版）。

Related: [[reference-windows-batch-entry-encoding]], [[feedback-destructive-file-ops]], [[reference-qoder-artifact-locations]]
