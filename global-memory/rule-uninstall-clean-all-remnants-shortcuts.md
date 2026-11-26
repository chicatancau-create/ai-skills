# 卸载/删除软件必须连快捷方式与全部残留一起清干净（用户长期规则）

- 确立：2026-11-26，用户原话（m00065）："以后删除之后，要把所有跟它相关的东西都删干净啊，我还以为那东西活过来了呢，懂吗？以后快捷键要自己处理一下，不要老是出这种问题，删除时要把快捷键也删干净。"
- 事由：2026-11-25 自建搜索服务顶替原版 Everything 时，卸载脚本 `D:\AI-Tool-State\fullindex\optimize.py` 只做了三步（sc delete 服务、HKLM\SOFTWARE\voidtools\Everything 改指自建路径、Remove-Item D:\Everything），**没有任何快捷方式清理步骤，也没做删后残留扫描**。DeskBox「实用小工具」格子里留下死快捷方式 `E:\DeskBox\实用小工具\Everything.lnk`（目标 D:\Everything\Everything.exe 已不存在），用户 11-26 看到图标以为软件"活过来了"。

## 规则（每次卸载/删除软件后强制执行）

1. **快捷方式全清单扫描**（按名字 + 按 lnk 目标双重匹配，WScript.Shell 读 TargetPath）：
   - 开始菜单两根：`%ProgramData%\Microsoft\Windows\Start Menu\Programs`、`%APPDATA%\Microsoft\Windows\Start Menu\Programs`（含 Startup）
   - 桌面：用户桌面 + `C:\Users\Public\Desktop`
   - 任务栏/快速启动：`%APPDATA%\Microsoft\Internet Explorer\Quick Launch`（含 User Pinned\TaskBar）
   - **DeskBox 格子：`E:\DeskBox\<格子名>\*.lnk`**（桌面整理工具会把快捷方式搬进自己的存储目录，"桌面为空"≠没有快捷方式；真身定位可读 `%LOCALAPPDATA%\DeskBox\data\widget-layout.json` 的 `Item:` 路径）
2. **数据目录**：`%APPDATA%\<appname>`、`%LOCALAPPDATA%\<appname>`、`%PROGRAMDATA%\<appname>`、安装目录本体。删前确认不是 Junction（LinkType 为空才直接删）且不被保留组件引用（grep 代码确认）。
3. **注册表**：卸载键三处（HKCU/HKLM/WOW6432Node Uninstall）、Run 键、`HKCU\Software\<vendor>`、`HKLM\SOFTWARE\<vendor>`、App Paths。注意：被自建替代方案**复用**的键（如 voidtools\Everything 改指自建路径）属于新方案的一部分，保留。
4. **服务 / 计划任务 / 进程**：Get-Service、Get-ScheduledTask 的 Actions Execute+Arguments 匹配、运行中进程 Path。
5. **自己建的备份**：用户明确"删干净"时，为该软件建的配置/数据备份一并删除（先例：Super Productivity 备份、Everything-original-backup 均应用户要求删除）；删前在汇报里列明删了什么。
6. **删后复扫验收**：上述清单全部 0 命中才算完；保留组件（自建服务、其自启 vbs、计划任务）单独列明"保留原因"。
7. 失效快捷方式（目标已不存在）直接删，不重建、不留副本（配套 feedback-no-backup-for-junk-deletes）；用户自己删的东西不默认恢复（配套 rule-user-deleted-not-auto-restore）。

## 关联

- 手册：`G:\AIrenwu\本地AI使用手册\03-通用\04-工程规范与安全\规则-卸载删除软件必须连快捷方式与全部残留一起清干净.md`
- 手册：`03-通用\04-工程规范与安全\经验-源码版Electron应用干净卸载三处与DeskBox格子快捷方式真身位置.md`（DeskBox lnk 真身位置与删后即时消失的实测）
- 本次执行记录：`D:\AI-Tool-State\fullindex\使用说明.md`「原版 Everything 的处置」节（2026-11-26 补）。
