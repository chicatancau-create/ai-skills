---
name: reference-xiaomi-miui-root-automation
description: 小米/MIUI 解锁与 adb 驱动手机 UI 的实测判据：miflash_unlock 必须管理员才认设备、MIUI input tap 需「USB调试(安全设置)」、AOD 会劫持 uiautomator dump、安全锁屏下 screencap 返回 0 字节、dumpsys account 掩码的是小米ID、BROM 入口必须真断电
metadata:
  type: reference
---

2026-10-31 在给用户做 Redmi K30 Ultra 解锁时逐条实测出来的，跨项目适用（他有长期「安卓刷机线」）。

## 解锁工具

- **`miflash_unlock.exe` 必须以管理员运行才会枚举 fastboot 设备。** 普通令牌下它一直显示「当前未连接手机」，
  而**同一时刻** `fastboot devices` 和工具自带的 `fastboot.exe`(v31.0.3) 都能正常看到设备 —— 所以不是驱动、
  不是版本、不是抢占。**判据**：先用命令行 fastboot 证明设备在，再怀疑工具的权限级别。
  本机 `Start-Process -Verb RunAs` 静默提权可用。
- 工具**重启即丢登录态**（CEF 内嵌登录窗，账号框变空），每次重启都要用户重新输密码。别为了"重新枚举设备"随手杀它。
- 官方下载页 `http://www.miui.com/unlock/download.html`（2026-10-31 实测存活）直链
  `https://cdn.cnbj1.fds.api.mi-img.com/flash-tool/miflash_unlock_7.6.727.43.zip`，
  包内自带 `MiUsbDriver.exe` / `driver_install_64.exe` / `fastboot.exe`，驱动一并解决。
- **绑定成功的判据不是页面文字**：`BootloaderStatusActivity` 绑定成功后仍显示「当前设备已锁定」+ 原按钮，
  只弹 toast。Android **不把 toast 文字写进 logcat**，只能趁它显示时截屏抓帧。
- 绑定前置三条（页面自己写的，必须实测核对）：SIM 已插入、**WLAN 关闭且移动数据打开**、账号已登录。
  查：`getprop gsm.sim.state`（`LOADED,ABSENT` = 槽1有卡）、`settings get global wifi_on` / `mobile_data`。

## 账号会话失效会让「绑定」静默作废（2026-11-10 的真相）

- 手机上点「绑定账号和设备」若弹 **「验证失败，请重新登录您的账号再次尝试」**，说明小米账号的**登录会话已失效**；
  此时服务端认为绑定不成立，解锁工具会回一个**整天数**（如「请 144 个小时后再试」，144=6×24）而不是递减的剩余小时。
- 这条比任何服务端猜测都可靠：**整天的数字 + 手机侧「验证失败」= 绑定作废，不是"卡住了"**。
  修法是手机上重登账号 → 重新绑定 → 从成功那一刻重算 168 小时。
- 别把 `dumpsys account` 里 `Account {name=3271***537}` 当成"账号还正常"——本地有记录 ≠ 会话有效。

## 提权窗口我点不动（UIPI）

- 工具是**管理员进程**，我这边 bash 派生的 python 是**非提权** → `mouse_event`/`SendInput` 返回成功但窗口收不到。
  ⇒ miflash_unlock 的最后那个「解锁」按钮只能由用户点；别把"点了没反应"当成 UI 坏了。
- `BringWindowToTop` 之后窗口 rect 会变，按上一次截图的坐标点会打空 —— 每次点击前重新取 rect。

## adb 驱动 MIUI 界面

- **`input tap` 需要开发者选项里的「USB调试（安全设置）」打开**，否则静默无效（不报错、什么都不发生）。
  判据：`input tap` 后 `logcat | grep MIUIInput` 应出现 `MotionEvent action=0x0 ... channel '<目标Activity>'`。
- **AOD（熄屏显示）会劫持 `uiautomator dump`**：抓到的是 `com.miui.aod` 的树，节点文字数为 0，
  看起来像"页面是空的"。先 `input keyevent KEYCODE_WAKEUP` 再 dump，并检查 dump 里的 `package=` 是不是目标包。
- **安全锁屏（PIN/图案）下 `screencap` 返回 0 字节文件**（系统对 FLAG_SECURE 拒绝截屏），
  `exec-out screencap -p > x.png` 会得到空文件、PIL 报 `UnidentifiedImageError`。
  这同时是"手机设了密码锁"的判据 —— 别把它当成截图命令写错了。
- **我不会猜或试用户的 PIN。** 需要进 UI 时明确请他解锁一次，并 `svc power stayon true` 保持不熄，
  用完还原 false。
- MIUI 的 Settings Activity 名与 AOSP 不同：`com.android.settings/.Settings$XiaomiAccountActivity` **不存在**（Error type 3）。
  可用：`.Settings$DevelopmentSettingsDashboardActivity`、`.Settings$ManageAccountsSettingsActivity`、
  `com.xiaomi.account/.ui.AccountSettingsActivity`。找不到就 `pm dump com.android.settings | grep -oE "...(Account|Xiaomi)[A-Za-z]*Activity"`。

## 账号身份的掩码陷阱（差点让我误判成两个账号）

- `dumpsys account` 里 `Account {name=3271***537, type=com.xiaomi}` 掩码的是**小米ID**（保留前 4 后 3），
  而解锁工具/账号页显示的往往是**手机号**。两者格式对不上 ≠ 不同账号。
- 正解：开 `com.xiaomi.account/.ui.AccountSettingsActivity`，页面同时给出「小米ID」和「手机号：191****5327」，
  程序化比对后**只报匹配/不匹配**，不把完整号码打进对话。
- 解锁要求「手机登录的账号」与「工具登录的账号」完全一致，否则报「账号不一致」并按官方说法再等 5-7 天。

## MTK BROM / fastboot

- **BROM 只在"从上电那一刻就按住组合键"时命中。** 从 fastboot 状态按双音量键只会回到 fastboot；
  `VID_0E8D` 不出现就是没进。正确时序：长按电源 ~20 s 强制断电 → 等 3 s → **同时按住音量上+下不放** →
  保持按住时插 USB → 再等 5 s 松手。部分小米 MTK 机型把双音量键映射成 fastboot，那就只能拆后盖短接测试点。
- `adb pull /sdcard/x.png <本地>` 在 Git Bash 下会被 MSYS 改写路径（报 `C:/Users/.../.qoder/bin/git/sdcard/...`），
  加 `MSYS_NO_PATHCONV=1`；或干脆 `adb exec-out screencap -p > 本地文件` 让 bash 做重定向。
- 判防回滚：`fastboot getvar anti` 对比固件包内 `images/anti_version.txt`，**相同即同版本刷入不触发 ARB**。

## 小米固件取址

- 官方线刷包命名 `<codename>_images_V<ver>_<date>_12.0_cn_<md5前10位>.tgz`（**gzip tar，不是 zip**）。
  文件名尾部那 10 位就是该文件 md5 的前 10 位，可自洽校验。
- 包内 `misc.txt` 自述 `device=` 与 `build_number=`，是机型/版本的**第四五重确认**来源。
- 包内 `md5sum.xml` 给出**每个镜像文件**的官方 md5，抽出 `boot.img` 后应与之比对。
- 索引站 `xmfirmwareupdater.com/miui/<codename>/` 路径会变（`/miui/lpi/` 直接 404），别按旧结构猜 URL。

## 解锁工具的三个界面态（2026-11-10 又踩一遍）

- **点「登录」后弹出的白屏 `https://unlock.update.miui.com/sts?d=pt_...` 不代表登录失败。**
  登录 POST 通常已经成功，只是那个 SSO 跳转页在内嵌 CEF 里渲染不出来。判据：**关掉白屏（WM_SYSCOMMAND/SC_CLOSE 有效，
  WM_CLOSE 无效）→ 截主窗口**，若已出现「免责声明·同意/不同意」就是登进去了。别急着重登、更别杀进程重启。
- **「登录」按钮变暗橙（文字发灰）= 禁用态**，多半是上方账号框被清空（页面滚动/刷新导致预填丢失）。
  亮红才是可点态。看颜色就能区分，别硬点。
- 报错码要分开记：**144 小时 = 绑定作废**（见上一节）；**1004「未知错误，稍后重试」= 服务端拒绝**
  （「正在验证设备信息」是绿勾、卡在「正在解锁」）。1004 常见诱因是账号刚登录/刚绑定尚未生效、或账号触发风控；
  连续重试会加重风控，隔 12–24 小时再试比连点有效。
- 「正在解锁」显示 50% 转圈**不是卡死**，但若此时设备已离开 fastboot，工具就会空等到超时再回 1004。
  进度条跑起来时用 `fastboot devices` + `adb devices` 确认设备还在 fastboot。

## PnP 的 `Status=Unknown` 不等于「在位」

- `Get-PnpDevice` 里 `Status = Unknown` 的条目**可能是历史记录**：同一份列表里明显没插的
  `REDMI K90 Max` 也是 Unknown。**判在位只有两个硬判据**：`Get-PnpDevice -PresentOnly` 能列出来，
  或者出现 `Status = OK`。
- 我曾据一条 `USB\VID_0E8D&PID_0003\...  Status=Unknown` 的 BROM 记录宣布「BROM 进去了」——**是过度断言**。
  后来 `-PresentOnly` 从来没列出过 0E8D，说明那只是残影。

## MTK BROM 入口与 WinUSB（2026-11-10 实测，未打通）

- **`adb reboot edl` 不可靠**：一次把手机带出 Android 但没枚举、一次干脆当普通重启回到 Android。
  双音量键三次全部落到 fastboot（`VID_18D1&PID_D00D` 是 Google fastboot 的 ID）。
  ⇒ 这台 cezanne 很可能把 BROM 入口关掉了，真要进只能拆后盖短接测试点。
- BROM 若出现，会以 **COM 口（usbser）**形式枚举，`antumbra` **不认 COM 口**（会一直打
  `Waiting for MTK device` 然后挂住），必须先把 `VID_0E8D&PID_0003` 绑成 **WinUSB**。
- `wdi-simple.exe -t 0` 报 `libwdi:error [check_dir] Unable to create directory 'usb_driver'` +
  `Access denied` + `exit=-3`，真因是 **bin 目录里残留了上一次失败留下的 `usb_driver` 目录**；
  删掉它再跑即 `Installing driver(s)... Success`（`exit=0`）。卸载设备节点前先 `pnputil /export-driver` 备份原 VCOM 驱动。
- pyusb 在这台机器 `NoBackendError: No backend available`（缺 libusb DLL），所以别用 pyusb 轮询抓 BROM。

## `Xiaomi-MTK-Bootloader-Unlock`（LK 强解）的适配事实

- 该仓库 **`lk-unlock.py` 支持 A-only**：跑完会自己打印 `Cert bypass applied to partition 'lk'`（不是 `lk_a`）。
  **只有外层 `Unlock-Windows.bat` 把分区名写死成 `lk_a`/`lk_b`**，A-only 机型（如 cezanne，scatter 里只有
  `lk`/`lk2`，`lk_a` 命中 0）必须先改脚本，否则第一步读 `lk_a` 就失败退出。
- 它**自带 Restore 脚本，同样写死 `lk_a`/`lk_b` 且要刷 `preloader_backup`**（cezanne 没有这个分区）
  ⇒ 适配解锁脚本时必须同步适配救砖脚本，否则救援路径是坏的。
- 收尾必发 `fastboot stage signature.bin` + `fastboot oem unlock`，**双清不可避免**（文档也写明了）。
- 依赖安装：`cryptography` + `pyasn1` + `liblk`(GitHub 源码)。这台机器上
  **代理跑 git/uv fetch GitHub 全是 TLS EOF，改 codeload 直连下载 zip 再本地 `uv pip install <dir>` 才成**；
  PyPI 用清华镜像直连。
- 离线可行性验证（零风险，推荐先做）：拿固件包里的 `lk.img`（md5 与包内 `md5sum.xml` 一致）直接
  `lk-unlock.py patch lk.img` —— cezanne 会在偏移 **`0x11ABB0`** 找到小米 RSA-2048 模数并成功打补丁
  （`cert2 957 -> 1047`，产物 +96 B）。这一步能在不碰手机的前提下判定「这条路对本机通不通」。

相关：[[reference-large-file-download-on-this-box]]、[[reference-windows-window-capture-pixelcheck]]、
[[reference-uipi-blocks-elevated-target-testing]]、[[feedback-no-unverified-cause-claims]]、
[[project-k30ultra-root-prep]]
