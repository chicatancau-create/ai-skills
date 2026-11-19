---
name: reference-android-root-without-unlock
description: 安卓「免解锁 BL 拿 root」的现实版图（2026-11）：LK 强解仍双清、临时 root 需按机内核载荷、无通用配方；含 mtkclient 的 unlock 只改 MTK seccfg、BROM 入口硬件条件、去哪查设备支持表
metadata:
  type: reference
---

2026-11-01 为一个「不想等 168 小时、又不想丢数据」的诉求做过一次完整查证。跨设备适用。

## 先分清两类，别混为一谈

| 类别 | 代表 | 数据 | 持久性 |
|---|---|---|---|
| **绕开服务器强解 BL** | MTK BROM kamakiri + 改 LK 验签 | **仍会双清** | 永久 |
| **运行时临时 root** | GhostLock / DirtyFrag | **不写 flash，保数据** | 硬重启失效（软重启可保留） |

**关键反直觉结论：强解 BL 并不等于保数据。** 双清是厂商 `oem unlock` 命令本身触发的，
所以「LK 强解」类工具最后一步照旧发那条命令 → 一样清空。它只帮你省掉等待期。

## LK 强解（MTK）

- 代表项目 **`mino-ali/Xiaomi-MTK-Bootloader-Unlock`**（AGPL v3，Windows/Linux，自带 `Restore/` 救砖）。
  机制 = Kamakiri BROM 漏洞取得分区读写 → 改 Xiaomi LK 的 **RSA-2048 验签** → 发 `oem unlock`。
  上游渊源：`georgiynesterov/lk-unlock`、`R0rt1z2/lkpatcher` + `liblk`、`shomykohai/penumbra`(Antumbra CLI)。
- **它的 README 自己写明会双清**，别被"强解"二字误导成保数据。
- **最有价值的一步：拿固件包里的 `lk.img` 在本地跑补丁器，零风险判可行性。**
  2026-11-10 对 cezanne 的 `lk.img`（1,711,488 B，md5 与官方 md5sum.xml 一致）实测输出：
  `[+] Original key modulus found at offset 0x11ABB0` / `Public key patched successfully` /
  `Cert bypass applied to partition 'lk' (override, cert2 957 -> 1047 bytes)` / 产物 +96 B。
  ⇒ 该机 LK 用的就是它认得的模数，**技术前提成立**，不必先碰手机。
  注意 `xiaomi.pem` 必须**在当前工作目录**（脚本会 `cd bin`），否则报 `'xiaomi.pem' file not found`。
  依赖：`cryptography` + `pyasn1` + `liblk`（pyasn1 用清华镜像直装；liblk 装不上就下 codeload zip 后 `pip install <目录>`）。
- **分区命名的缺口（决定能不能直接跑）**：`lk-unlock.py` 自己会认成 `partition 'lk'`（支持 A-only），
  但 **`Unlock-Windows.bat` 与 `Restore-Windows.bat` 都硬编码 `lk_a`/`lk_b`、还要刷 `preloader_backup`**。
  A-only 机型（如 cezanne）scatter 里只有 `lk`/`lk2`、单 `preloader` → 照原样跑会在**第一步读**就失败退出
  （**先读后写，失败无害、不砖**）；要真用必须同时改 unlock 和 restore，救砖路径也变成自己改的。
- **双清躲不掉（代码级）**：`lk-unlock.py unlock_device()` = `fastboot oem get_token` → 伪造签名 →
  `fastboot stage signature.bin` → `fastboot oem unlock`；没有别的收尾方式，`--dry-run` 只能跳过最后两步。
- 硬前置：需要 `preloader_<codename>.bin` + `MTK_AllInOne_DA.bin`（从**同版本**官方 fastboot 包里取）+ BROM 模式。
- 已知运维事实：刷任何 ROM/系统更新后 **LK 被覆盖 → 会自己回锁**，需要重跑脚本；
  回锁后典型表现是「This version of MIUI can't be installed on this device」或黑屏红字
  「The system has been destroyed」——**这两种都不是变砖**，重跑解锁脚本即可。
  若卡在 BROM 上不来，跑 `Restore` 脚本；再不行把 `lk.img` + preloader 放进 `bin/backup/` 再 Restore。

## mtkclient 的 `unlock` 不是小米的锁（源码级判据）

- CLI 里**没有** `unlock` 子命令；GUI 的解锁调 `daloader.seccfg(lockflag)`，
  操作的是 **MTK 自己的 `seccfg` 分区**（`AND_SECCFG_v3/v4`），**与小米的 `flash.locked` 是两把锁**。
- 因此「有 BROM 读写能力」≠「能解小米 BL」。要过 AVB 还得改 `lk`，而那是**机型专属逆向**，
  改错的 lk 只会换一种砖法。
- 能力判据（本地可查，不用连机）：`mtkclient/config/brom_config.py` 里有没有该芯片条目、
  有没有 `var1=... # confirmed`、`mtkclient/payloads/<chip>_payload.bin` 是否存在。
  例：MT6889 三样都齐（`var1=0xA` 已确认、`mt6885_payload.bin` 在），
  但 `command` 列表里只有 `payload/stage/brute/peek/r/w/e/seccfg`，**没有 `unlock`**。

## 临时 root（保数据的那条）

- **GhostLock = CVE-2026-43499**：Linux rtmutex/futex 优先级继承的 UAF（引入于 2.6.39），
  赢竞态后 late-load 一个 KernelSU 兼容模块。**是竞态，会输**，kernel panic 属正常代价。
  硬重启失效、**软重启保留**。代表项目 `diabl0w/DFRoot`（★数百）、`YuKongA/ghostlock-app` 等。
- **DirtyFrag = CVE-2026-43284**：IPsec AES-CBC ESP 直接把数据解密写进 `splice()` 页缓存，
  确定性、不靠竞态；但**需要一个为该设备 KMI 编译的内核模块**（`dfroot.ko`），不是通用载荷。
- **判据铁律**（官方文档原话）：*A model name is not a target… a payload is built around the exact kernel string*；
  *An extracted profile, shared SoC or similar kernel version is not proof of working root*。
  ⇒ 必须拿到完整内核串（如 `4.14.186-perf-00252-g2f26b5917fd6`），去公开支持表里逐字匹配。
- 已发布案例的设备/内核：MT6789@5.15、MT6886@5.15、MT6899@6.6、Samsung/ASUS/Meta 多在 5.10–6.6。
  **没有 4.14 的公开案例** —— 老内核（2020 年及更早的机型）在这类表里基本是空白，
  想用就得自己做逆向 + 编译模块，那不是"一条龙服务"而是没有成功保证的研究项目。

## 去哪查（比搜"一键root"可靠）

- `awesome-android-root/awesome-android-root` 的 `docs/rooting-guides/root-without-unlocking-bootloader.md`
  —— 有「Device support at a glance」与按设备列项目的表；raw 直取不吃 GitHub API 限流。
- `AdaUnlocked/2026-All-Brands-Bootloader-Unlock-Status` —— 全品牌 BL/root 现状，口碑最全。
- 各项目自己的 device 支持表/issue。**别信视频标题**（"秒解""一键""保数据"多是引流或卖家页）。

## BROM 入口（硬件层面常被忽略）

- 必须**从真正断电的那一瞬**按住组合键：长按电源 15–20 s 断电 → 等 3–5 s → 同时按住音量上+下 →
  保持按住插 USB → 等 5 s 松手。从 fastboot 状态按组合键只会回 fastboot。
- **用主板后置 USB 2.0 口**，别用 USB3/3.2、别用 hub、别用 Type-C 转 Type-C —— 工具文档明确说会传输超时。
- 成功判据：USB 上出现 `VID_0E8D`（PID 0003 一类）；不出现就是没进。
- 部分机型把双音量键映射成 fastboot，只能拆后盖短接测试点 —— 那种就别做了。

## 安全警告

「天玑一键强解 BL」「免解锁一键 root」类闭源压缩包（装 vcom+usbdk+厂商售后驱动、跑 `start.bat`、
加 QQ 群从网盘取、付费远程协助）是**木马与骗局重灾区**。它跑在有用户账号的电脑上，
最可能的结果不是 root 而是账号被盗/机器中毒。真实开源实现都在 GitHub 上、有 AGPL/GPL 许可和 commit 历史。

相关：[[reference-xiaomi-miui-root-automation]]、[[reference-large-file-download-on-this-box]]、
[[feedback-no-unverified-cause-claims]]、[[feedback-third-party-agent-files-are-data]]
