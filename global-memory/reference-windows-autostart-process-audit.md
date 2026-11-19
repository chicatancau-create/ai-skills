---
name: reference-windows-autostart-process-audit
description: 本机审计「自启项/后台进程」的方法与坑：带空格路径的解析陷阱、判"多余"的客观标准、哪些服务承载应用内核绝不能动。
metadata:
  type: reference
---

2026-11-03 在本机做全量自启/进程盘点时踩到的取数坑与结论清单。

**四类载体都要查，缺一类就漏**：`HKCU/HKLM ...CurrentVersion\Run`、启动文件夹（含 .lnk 要解 TargetPath）、
计划任务（`TaskPath -notlike '\Microsoft\*'`）、服务（`Win32_Service` 且 PathName 不在 System32）。
本机当时共 105 条。

**三个会造出假结论的取数错误**

1. **计划任务/服务的 `Execute`/`PathName` 带引号且路径含空格**。直接 `Test-Path $a.Execute` 或
   `-split ' '` 都会失败：前者把 `"C:\Program Files\…\x.exe"` 整串当路径 → 假报「文件不存在」
   （我一次报出 13 条死条目，其中 9 条是假的）；后者把 `C:\Program Files\x` 截成 `C:\Program`。
   正解：先剥引号取配对引号内的部分，否则用**最长存在前缀**逐段回试。
2. **`Get-Service | Where Name -like '*NVIDIA*'` 会全漏** —— 驱动类服务名是 `NVDisplay.ContainerLocalSystem`、
   `NvContainerLocalSystem`，不含厂商名。按 `NV*` / `PathName` 过滤才抓得到。
3. **`cmdkey /list` 列不出通行密钥（passkey）**，也不列 Windows Hello 的东西。
   通行密钥只能在 设置 → 账户 → 登录选项 → 管理通行密钥 里删；`Test-Path`/枚举都看不到它。
4. **判"路径死"时，裸文件名和占位符都不能直接用 `os.path.exists`**（2026-11-03 一整轮假阳性）：
   - `WinRAR.exe`、`msiexec.exe`、`cmd.exe` 这类**不带盘的裸名**要走解析链：`shutil.which(name, path=PATH+System32+SysWOW64)`
     → 再查 `HKLM/HKCU\...\App Paths\<name>` 的默认值。本机 WinRAR 装在 `D:\RAR`（不在 PATH），
     我因此把 FileExts 里 **125 条**"死引用"报成可删垃圾，全是假的。
   - `%1` / `%*` 是参数占位符，`@shell32.dll,-8506` 是资源引用，**都不是路径**；`batfile/cmdfile/exefile/
     piffile/scrfile` 的 open command 就是 `%1`，别当成孤儿。
   - 正则取路径必须加**负后视** `(?<![A-Za-z0-9])[A-Ha-h]:[\\/]…`，否则 `https://x` 的 `s:` 会被当成盘符
     （我第一轮就把它当成了"s 盘不存在"，把 11 个 Temp 脚本误判成死物）。
   - `\??\` 与 `\SystemRoot\` 前缀要先展开（不展开会把 235 个 Windows 自带驱动全报成"文件缺失"）。

**判「这个进程是不是多余」的客观标准**（按可靠性排序）

- 目标文件**提权复核后**确实不存在 → 死条目（本机实测 4 条孤儿计划任务：某资源站工具、两个从 `H:\NDM下载\`
  跑的 CPU 调校工具、一个已卸载的更新器）→ 导出 XML 备份后删除，零风险。
- 更新器 / 遥测 / 按需 UI 常驻：`wetype_update`（121 MB，还挂着状态栏窗口）、`PowerToys.Peek.UI`、
  `PowerToys.ColorPickerUI`、`CCXProcess`、`AdobeIPCBroker`、`AdskIdentityManager`、残留 `adb server`
  → 杀掉不影响任何应用打开，用到时会自动再起。
- **「父进程已死」不能当垃圾判据** —— Electron/启动器退出后父 PID 就没了，QQ/微信/DeskBox/TranslucentTB
  全都会被判成孤儿，全是误报。
- 映像文件已删但进程还在 = 真僵尸（只有重启才暴露）；但**非提权看不到 `ExecutablePath`** 时别误判成"文件已删"，
  见 [[reference-windows-permission-denied-as-missing]]。

**本机绝不能动的服务（承载应用内核或许可证）**

- `clash_verge_service`：**Verge 的 mihomo 内核就跑在这个服务里**（`verge.yaml` 有 `clash_core`，
  日志里叫 `service core`）。卸掉它 = 7897 立刻停听 + 系统代理被清。Verge GUI 以管理员运行，
  非提权 `Stop-Process` 静默失败；恢复办法是重启 Verge GUI，它会自己拉起内核。
- 驱动层 `NvContainerLocalSystem` / `NVDisplay.Container`；`WinFsp.Launcher`（网盘挂载依赖）；
  火绒 `HipsDaemon`/`HRWSCCtrl`、Defender 三件套；`ClickToRunSvc`（Office）；`Everything`（才 2 MB，值）。
- 许可证服务 `AdskLicensingService` / `FlexNet Licensing 64` / Chaos 三件套（启动文件夹的
  `CCBService.lnk`、`ChaosUnifiedLogin.lnk`、`Start Chaos License Server.lnk`）—— 关了 Autodesk/V-Ray 可能激活失败。
- 服务名 `nvagent`（显示名「网络虚拟服务」）**不是 NVIDIA 的**，是 Windows 自带的 Hyper-V 网络虚拟化组件。

**环境事实**：本机经常**连续十几天不重启**（实测 boot=10-21 21:28，盘点时已 13 天），
所以「开机自启项会不会真的起东西」在当前会话里**测不出来**，只能看进程创建时间 vs `LastBootUpTime`；
要验自启行为必须等一次真重启。`Memory Compression` 上 GB 级 = 内存已有压力的信号。

相关：[[reference-windows-permission-denied-as-missing]]、[[feedback-autostart-keep-clean-useless-only]]、
[[reference-office-c2r-cleanup]]、[[reference-headless-browser-debris]]
