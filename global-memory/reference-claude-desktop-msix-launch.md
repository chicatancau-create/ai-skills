---
name: reference-claude-desktop-msix-launch
description: Claude desktop on this box is a Developer-signed MSIX; 0x80070020 launch failure (after auto-update OR manual reinstall) is a kernel job/silo leak only logoff/reboot clears; moving it to D: works but InstallLocation lies via Junction; official Simplified Chinese covers the shell layer only.
metadata:
  type: reference
---

# Claude desktop (MSIX) on this machine

**Install shape** — package family `Claude_pzs8sxrjxfjjc`, `SignatureKind = Developer` (side-loaded, not Store),
installed at `C:\Program Files\WindowsApps\Claude_<ver>_x64__pzs8sxrjxfjjc`, AUMID `Claude_pzs8sxrjxfjjc!Claude`.
Launch from CLI: `Start-Process explorer.exe -ArgumentList 'shell:AppsFolder\Claude_pzs8sxrjxfjjc!Claude'`.
User data is **outside** the container at `%LOCALAPPDATA%\Claude-3p` (logs, config.json, window-state.json,
`stealth-relaunch`, vm_bundles) — reinstalling the package does not lose it. Service logs:
`C:\ProgramData\Claude\Logs\cowork-service.log`. Main app log: `%LOCALAPPDATA%\Claude-3p\logs\main.log`.

**Task Manager lies about "running".** The `Claude` group with a `cowork-svc.exe` child is
`CoworkVMService` (SCM service, Type 0x210 = packaged service, LocalSystem, binary inside the package).
It runs whether or not the app does. So "it's in the background but I can't open it" = the app is *not* running;
check for a process named `Claude` and for `Microsoft-Windows-AppModel-Runtime/Admin` events 208/215.

**The 0x80070020 failure mode** (recurs across auto-update cycles):
`main.log` ends with `beforeQuitForUpdate handler fired, going down for update` → app quits to apply a stealth
update → every later activation logs event 215 `Cannot create the Desktop AppX container ... error encountered
converting the job` + event 208 `... configuring runtime [LaunchProcess]`, HRESULT `0x80070020`.
Upstream: anthropics/claude-code issues #89680, #53247, #59934, #84792, #93220.

**Verified dead ends on this box (2026-10-01), do not repeat:**
- `Stop-Service CoworkVMService` (0 cowork processes) → still fails. Its `StartupType` cannot be set to Disabled
  (`Set-Service`/`sc config` → Access denied even elevated; packaged service is config-protected).
- `Add-AppxPackage -Register -DisableDevelopmentMode AppxManifest.xml` → succeeds, changes nothing.
- Control tests: Calculator and Microsoft Store both launch fine, so AppContainer/HCS and the `H:\WpSystem`
  package-data junctions are healthy — do not chase those.
- Token scan proved no process still carries the package SID → the stale silo/job is kernel-side, **nothing is killable**.

**Only cure: log off + log back on, or reboot.**

**Machine-specific traps found alongside it:** package data folders are junctioned to `H:\WpSystem\...` and a batch
of other packages still point at `G:\WpSystem\...` — **G: no longer exists**, so those are dead links
(BaiduNetdisk, PixPin, WeixinShare, UNISUnzip, WinAppRuntime 1.7, 3AD8A913/903DB504 store helpers).
See [[reference-windows-ie-and-shell-traps]] for another shell-folder trap on this box.

## 2026-10-06 补充：把它搬到 D 盘的可行做法（已实测）

`InstallLocation` 报的路径**不能用来判断物理盘** —— Windows 在新卷上放实体，在 `C:\Program Files\WindowsApps\`
留同名 **Junction**。判据：`Get-Item <C路径> -Force` 的 `Attributes` 含 `ReparsePoint`、`LinkType=Junction`、
`Target=D:\WindowsApps\...`，或 `fsutil reparsepoint query <C路径>`。核实物理占用：`Get-ChildItem <D路径> -Recurse -File -Force`
（本次实测 3,816 文件 / 679.4 MB 在 D:）。

- 先让用户在 设置 → 系统 → 存储 → 高级存储设置 → 新内容的保存位置 把「新的应用将保存到」改成 D:，`D:\WindowsApps` 才会建立；
  `Get-AppxVolume` 里 D 卷的 `PackageStorePath = D:\WindowsApps`。
- `Add-AppxVolume -Path 'D:\'` 会报「应存在尾随反斜杠」，写成 `Add-AppxVolume -Path 'D:'` 才通过（本机陷阱，方向反直觉）。
- **只给 `Add-AppxPackage -Volume <D卷>` 不管用**：该版本包内容若已在别的卷以 `Status=Servicing` 暂存，激活会复用旧暂存内容，
  结果仍落在 C:。必须**先 `Remove-AppxPackage` 掉现有注册**（此时 `Get-AppxPackage -AllUsers` 只剩 Servicing 那条，
  删它会报 `0x80073CF1`「当前用户未安装」，属正常），再 `Add-AppxPackage -Path <msix> -Volume <D卷>` → `Register` 事件 400
  显示「以目标 D: 执行的操作 Register 已成功完成」。
- Windows PowerShell 5.1 的 `Add-AppxPackage` 参数是 **`-Path`**，不是 `-PackagePath`。带中文的 `.ps1` 以 UTF-8 无 BOM 写出会被
  5.1 按 GBK 解析而整段语法失败 —— 这类脚本一律写纯 ASCII（见 [[feedback-windows-config-json-encoding]]）。

## 2026-10-06 补充：0x80070020 不只发生在自动更新

本次是**手动** `Remove-AppxPackage` + `Add-AppxPackage`（v2.19675.1.0）后立即复现：包状态 `Ok`、manifest 与 `app\Claude.exe`
都在、`Register` 成功，但激活 80 s 内 0 进程，事件 215/208 仍是 `0x80070020`（转换作业失败 / `configuring runtime [LaunchProcess]`）。
→ 结论不变：**只有注销或重启能清**，别怀疑包损坏，也别再试停服务与重新注册（上面已记为死路）。

## 用户数据换盘：只能靠目录联接（2026-10-06 实测成功）

`%LOCALAPPDATA%\Claude-3p`（10.4 GB / 494 文件，其中 `vm_bundles` 9.67 GB 是 Cowork 的 VHD）**没有官方换盘开关**：
asar 原话 `CLAUDE_USER_DATA_DIR is set and signed builds ignore it`。可行做法是整目录搬到别的盘再 `mklink /J` 盖回去
（`cowork-svc.exe` 里是硬编码 `%s\vm_bundles\claudevm.bundle` 路径串，联接让路径字符串完全不变）。

本次实测要点（`D:\Claude-zh-20261006\switch.log` / `post-check.log`）：
- 搬之前必须：用户从托盘退出（关窗口无效）+ `Stop-Service CoworkVMService -Force`，否则 VHD 被占、改名会失败。
- 校验用逐文件 SHA-256（robocopy 只比时间戳，不可当校验）；`robocopy` 要加 `/XJ`，且别在 Git Bash 里传 `/MIR`（会被转成 POSIX 路径）。
- `D:\` 根无 EFS 加密属性且 ACL 含 `SYSTEM=FullControl`，LocalSystem 的服务读得到搬过去的文件 —— 换盘前先验这条。
- 结果：`rootfs.vhdx` 透过联接可读、Cowork 服务日志成功 `Created new VM session ... :C:\Users\Admin\AppData\Local\Claude-3p`、
  `SkillsPlugin Delta: 0 to download`（没因找不到数据而重下）。**未证实**：VM 真正挂载引导需用户开一次 Cowork/代理任务。
- C 盘原件按用户要求先改名 `Claude-3p.bak-<date>` 保留，确认无误才删。

## 卸载后残留（2026-10-08 实测）

用户从「设置」卸载 MSIX 后，`Get-AppxPackage -Name Claude`（含 `-AllUsers`）= 0，但 SCM 仍挂着一个
`CoworkVMService`（`TYPE: 210 WIN32_PACKAGED_PROCESS`、`STOPPED`、`PathName` 空）。**它没有注册表键**：
枚举 `HKLM\SYSTEM\CurrentControlSet\Services` 全部 863 个键，`cowork|claude` 匹配 0（`ControlSet001` 同样 0），
`reg query` 报「找不到指定的注册表项或值」，`OpenSubKey(TakeOwnership)` 返回 null，`sc delete` 报「拒绝访问 5」。
→ 打包服务在包消失后变成的 SCM 幽灵条目，**没有正当删除手段**（别再去动注册表或服务 DACL），预期重启后随 SCM 重建消失。
其余残留位置（全部实测在 `C:\Users\Admin\AppData\Local\Claude-3p` 联接之外）：`AppData\Local\Claude`（旧版日志+配置）、
`C:\ProgramData\Claude\Logs\cowork-service.log`、以及 WindowsApps 里**未注册的旧版本目录**（本次是
`Claude_2.2553.1.0_x64__pzs8sxrjxfjjc`，663 MB，2026-09-20 建的）—— 后者可用 takeown + icacls + rd 清掉，父目录 ACL 不受影响。

## 界面语言：官方简中只到壳层

`app\resources\` 内有官方 `zh-Hans.json` / `zh-Hant.json`（41 KB，键与 `en-US.json` 一一对应，如 `+/cwsayrqk` → 「实际大小」），
`app.asar` 语言表也含 `"zh-Hans"`；但在线主界面层 `app\resources\ion-dist\i18n\`（及 `i18n\dynamic\`）只有 11 种语言、**无 zh**，
官方支持页（2026-08-06）的 `Language` 菜单同样 10 种无中文 → 升级到任何版本都不会凭空出现简体中文主界面。
第三方补丁 `claude-desktop-zh-cn` 自报 12,325 条前端 + 355 条壳层翻译，并往包里写 **`zh-CN.json`**（≠ 官方 `zh-Hans.json` 命名）。
`config.json` 的 `"locale"` 键（本次为 `en-US`）是壳层语言入口；改它必须在应用**退出后**改，否则应用退出时会覆写。

Related: [[feedback-install-to-d-drive]], [[reference-powershell-through-bash-and-recyclebin]], [[reference-windows-ie-and-shell-traps]]
