# 用户规定：Viap 清理前两项必检（2026-11-24，长期有效）

用户规定（原话意图）：以后用 Viap 清理数据/内存时，默认先①检测 D 盘迁移效果还在不在②结合本机情况检测 Viap 是否需要更新。

- 必检①：`D:\PyCharm\Python\python.exe -X utf8 D:\AI-Tool-State\disk-audit\health_check.py`（54 联接目标/探针落 D/幽灵扫描/双守护，全绿退出 0）；或双守护 `migrate_guard.py` + `migrate_guard_appdata.py` --quiet 退出 0。`D:\DevCache*` 是真源，永远不是可清理的重复数据；幽灵清理只清目标缺失的失效联接。
- 必检②：本机包 `H:\下载\Viap`（v1.3.3）对比 github.com/Chunyu33/viap releases/latest；有新版先核 SHA256；确认安装状态（当前未安装）；已安装则先导入本机 54 联接历史。
- 规则全文：手册 `03-通用/04-工程规范与安全/规则-用Viap清理前必检D盘联接效果与Viap更新.md`；任务区 `G:\AIrenwu\04_磁盘与系统\磁盘整理\Viap-完全使用手册.md` 第〇节。
- 2026-11-24 17:27 体检基线：54 联接异常 0、探针 5/5、幽灵 0、守护全正常；应用无崩溃；Viap 仍最新 v1.3.3。
- 用户另决定：`D:\AI-Tool-State\disk-audit\updater-cache-bak\`（DSH 旧安装缓存 574.9 MB）**永久保留不删**。
