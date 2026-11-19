---
name: power-scheme-registry-clutter
description: This box accumulates duplicate Windows power plans in the registry from third-party tools (Driver Booster re-imports its plan every run); how to enumerate them and clean safely
metadata:
  type: reference
---

Power plans live as one registry key per scheme under
`HKLM\SYSTEM\CurrentControlSet\Control\Power\User\PowerSchemes\<GUID>`, with `FriendlyName` /
`Description` as **REG_EXPAND_SZ** (not REG_SZ — a regex that only accepts REG_SZ finds nothing), plus
sibling values `ActivePowerScheme`, `ActiveOverlayAcPowerScheme`, `ActiveOverlayDcPowerScheme`.

State measured 2026-10-03: 18 keys existed while `powercfg /list` showed only 2 (平衡 + 卓越性能 active)
and `powercfg /query <GUID>` could load 17 of them. Provenance of the surplus:
- **5× "Driver Booster Power Plan"** — IObit Driver Booster imports its own plan on every run; 4 were
  byte-identical to each other. Expect these to reappear; the fix is in Driver Booster's settings, not here.
- **PowerX v2** under the synthetic GUID `66666666-6666-6666-6666-666666666666` (third-party tweak pack).
- Duplicate "卓越性能"×4 and "高性能"×3 — clones made by tweak scripts; the Microsoft originals keep the
  `SCHEME_MIN` / `OVERLAY_*` alias lines, the clones don't.
- `...3af9b8d9-...` "High Performance Overlay" was an empty husk (`powercfg` → "覆盖方案为空").

**How to apply:** back up first (`reg export ...PowerSchemes file.reg /y`, ~205 KB, UTF-16), diff candidate
duplicates by normalizing `powercfg /query` output (strip the scheme header, mask GUIDs, hash) before
claiming they are redundant, and never delete the GUIDs named by the three `Active*` values.
`powercfg /delete <GUID>` worked from a **non-elevated** shell for all 9 removals — no UAC needed.
After cleanup: 9 keys left, active scheme unchanged.

**12 天后的复账（2026-11-15 实测）**：仍是 **9 个键、归一化哈希后无重复组**，活动方案仍是 `30e90e4f…`（卓越性能 /
名字在注册表里是 `Performance`）。同期 `D:\IObitDriverBooster` 目录 mtime 停在 11-02 ⇒ 没再运行过，所以「每跑一次复发」
这一条**只观察到一次，未二次复现**（故意不再运行它）。新增判据：`Attributes` 全是 `0x0`，
所以**名字叫 `Overlay` 的键并不代表它是 AC 电源覆盖方案**，别按名字归类；内建方案的 `FriendlyName` 存的是
`@%SystemRoot%\...` 间接字符串，要按 GUID 兜底成人名。
工具与账目已固化在 `G:\AIrenwu\脚本库\09_机器体检与垃圾扫描\power_schemes.py`（`--backup` 会拒绝 TEMP 落点）；
11-03 存在 `%TEMP%\regbk` 的那份 `.reg` 已在 11-11 的更新重启里被清掉，替代基线改放
`G:\AIrenwu\01_任务归档\2026-11-03_后台进程盘点\02_证据日志\电源方案基线-20261115\`。
手册记录：`E:\本地AI使用手册\03-通用\03-调试与验证\踩坑-电源计划被驱动更新工具复制成同名方案且FriendlyName是REG_EXPAND_SZ.md`。
