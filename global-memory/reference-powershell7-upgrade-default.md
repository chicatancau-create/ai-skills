# PowerShell 7 升级并设默认（本机 2026-11-26 已做）

> 候选经验，用前按当前事实复核。完整过程与证据见手册：
> `G:\AIrenwu\本地AI使用手册\03-通用\04-工程规范与安全\经验-PowerShell7升级默认-ZIP装稳定路径与终端默认及注册表只读坑.md`（verified）。

## 核心事实
- **Windows PowerShell 5.1 是系统组件，卸不掉**（`C:\WINDOWS\System32\WindowsPowerShell\v1.0\powershell.exe`）。只能不设默认 + 在 Windows Terminal 里 `hidden:true`，别尝试删。
- **PowerShell 7.7.0 起官方没有 MSI**：winget 装的是 MSIX；GitHub 资产只有 `.msixbundle` + `.zip`。要稳定 exe 路径/重自动化，用官方 win-x64 ZIP 解到 `C:\Program Files\PowerShell\7`，别依赖 MSIX 的版本号路径 + WindowsApps 别名。
- 本机现状：7.7.0 已装 `C:\Program Files\PowerShell\7`，系统 PATH 已前置（保 `REG_EXPAND_SZ`），终端默认 profile 已切到它，5.1 已隐藏，重复 MSIX 已移除。

## 两个真坑（跨任务可复用）
1. **`Get-Item` 打开的注册表键只读，`SetValue` 必报「无法写入到注册表项」**——跟提没提权无关。写注册表用 `[Microsoft.Win32.Registry]::LocalMachine.OpenSubKey($sub,$true)` 拿可写句柄。改 PATH 先 `GetValueKind` + `DoNotExpandEnvironmentNames` 读原始值，写回沿用原 `REG_EXPAND_SZ`，改完广播 `WM_SETTINGCHANGE`；已跑进程仍读旧值，验证按注册表实时 PATH 模拟新进程，别信 `$env:Path`。
2. **Windows Terminal 自动生成 PowershellCore 动态 profile，GUID 固定 `{574e775e-4f2a-5b96-ac1e-a2962a402336}`**。PATH 里有 pwsh 就会出现；手动再加同 GUID 必撞。正解：在自动那条上定制 `name/icon/commandline` 并保留 `source` 字段，别另加。5.1 profile GUID `{61c54bbd-c2c6-5271-96e7-009a87ff44bf}`。

## 静默提权通路（本机 ConsentPromptBehaviorAdmin=0）
`Start-Process powershell -Verb RunAs -WindowStyle Hidden -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File',<worker>` 无 UAC 弹窗；worker ASCII-only、自写日志到 `%LOCALAPPDATA%\Temp`、父进程轮询 `DONE_OK/DONE_FAIL`；`-Verb RunAs` 不能与 `-RedirectStandardOutput` 同用。

## 实物
- 安装包 `H:\下载\PowerShell-7.7.0-win-x64.zip`（sha256 `7c74e03b20a75b59715847439d046a6214b1863ee79b187872980f139bb4a05f`）
- 终端配置备份 `H:\下载\pwsh7-backup\settings.json.bak-20261126-102720`
