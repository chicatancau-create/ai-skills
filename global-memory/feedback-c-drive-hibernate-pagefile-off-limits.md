---
name: feedback-c-drive-hibernate-pagefile-off-limits
description: C 盘清理时休眠文件与虚拟内存属于「不动项」——可以报出大小,但不要关休眠或改 pagefile,除非用户主动要求。
metadata:
  type: feedback
---

做 C 盘(或任何系统盘)清理时,**`hiberfil.sys` 与 `pagefile.sys` 默认不碰**。
可以量出它们的大小并写进报告,但要归入「按你的要求没动」的说明,不要执行
`powercfg /hibernate off`、也不要改虚拟内存大小或搬家。

**Why**：2026-09-28 全量体检 C 盘后我给出一份 A 级清理清单(含关休眠省 12.47 GB、
页面文件 12 GB 缩到 4 GB,实测峰值只用了 129 MB),用户明确回了一句
「A 不动休眠和虚拟内存」。休眠/快速启动和「内存吃紧时有兜底」对他有价值,
省下的空间不是他优先考虑的目标。

**How to apply**：清理类任务先按「可再生缓存 / 重复的驱动包 / 安装包残留」找空间,
把休眠与页面文件当作**最后手段并需单独批准**。要动它们之前照例先量证据
(`Win32_PageFileUsage` 的 PeakUsage、内存容量),把「代价」写清楚,而不是只写能省多少。
同一次任务里用户也接受了这套做法:先只读预检 → 逐条删除留审计日志 → 回查没误删登录态数据。

相关：[[feedback-destructive-file-ops]]、[[feedback-autonomous-execution]]、[[feedback-rigor-audit]]

**Where it actually lives (verified 2026-10-03):** the pagefile is **`H:\pagefile.sys` = 10.00 GiB**, not on C:.
So any "clean up the data drive" sweep must treat H:\ root's `pagefile.sys` (attrs hidden+system) as a
no-touch item too. Same volume also carries `.pnpm-store`, `WpSystem`, `MapData`, `DeliveryOptimization`,
`WUDownloadCache` and `Program Files\ModifiableWindowsApps` — Windows Store / update plumbing relocated to H:,
not junk.
