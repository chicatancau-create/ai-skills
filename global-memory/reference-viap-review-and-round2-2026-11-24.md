# Viap 评审结论与第二轮强关迁移（2026-11-24）

## Viap
- 本地 `H:\下载\Viap` 三包 SHA256 与 GitHub Chunyu33/viap v1.3.3（2026-11-16，即最新）官方 release digest 全符，**无需更新**。
- **未安装**：与 DSH-Guard 同机制（NTFS Junction），装第二套会形成平行迁移历史；本机批量/守护/回滚已由 DSH-Guard 覆盖。
- 完全使用手册（工作区）：`G:\AIrenwu\04_磁盘与系统\磁盘整理\Viap-完全使用手册.md`；便携版评审副本 `D:\AI-Tool-State\viap-review\portable\viap.exe`；官方 README 存档 `D:\AI-Tool-State\viap-review\README.md`。
- 若将来安装：先用「扫描目录联接重建历史」导入本机 50 个受守护联接；勿重复迁移已是联接的目录；勿手动删 D 侧真源；幽灵清理只清失效联接。

## 第二轮强关迁移（用户批准）
8 目录 / 26323 文件 / 8.02 GB：PowerToys(local 0.99G)、IDM(roaming 1.11G)、com.qoder.app.stable(0.88G)、com.qodercn.app.stable(0.55G)、Tencent(roaming 3.03G，含微信数据)、QQ(0.30G)、QQEX(0.57G)、puccinialin(local 0.59G=Rust 工具链缓存，13 内嵌联接重建)。全部重开验证存活（Qoder×14 经官方 Launcher）。守护清单 local 12 + roaming 13 + home 25 = 50 联接。C 剩余 147.0 GB。

## 三个可复用教训
1. **DSH 会话 pwsh 子进程继承 `ELECTRON_RUN_AS_NODE=1`**（系统/用户级没有）→ 启动 Electron 应用进纯 node 模式、无参静默退出 0 无日志；`--help` 输出 `Usage: node [options]` 即此症。启动前 `$env:ELECTRON_RUN_AS_NODE=$null`（包装器 `D:\AI-Tool-State\disk-audit\start_qoder_clean.ps1`）。
2. **提权进程/服务须提权关**：非提权 taskkill 杀不掉提权 PowerToys（WinError 32）、Stop-Service 停不掉 wetype_service（WinError 5）；`Start-Process powershell -Verb RunAs` 静默提权 worker 解决（ConsentPromptBehaviorAdmin=0）。PS 5.1 按 ANSI 读无 BOM UTF-8 ps1 → 脚本内中文正则乱码永不命中，匹配模式用 ASCII。
3. **Python 3.12+（实测 3.15.2）`os.path.islink()` 对 junction 返回 False**（mount point 0xa0000003 不算 symlink）；`os.readlink()` 正常（带 `\\?\` 前缀）。判定联接用 readlink try/except 或 `migrate_dir.is_reparse()`。

## 仍留待开机
EmulatorCacheMigrate（SYSTEM 开机任务）：.android 4.7G / Android 4.3G / Huawei 6.6G（鸿蒙模拟器）/ CapCut 2.7G（剪映），共约 17.9 GB，成功后自删。DSH 更新器 pending 0.2.3-alpha.2（287 MB）交应用自带更新流程。
