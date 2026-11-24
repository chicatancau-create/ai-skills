# CC Switch 检测三坑与 agy 重装现状（2026-11-24）

> 追加条目，不改写旧条目。对 reference-gemini-cli-multi-profile.md 的两处现状更正见下。

## 现状更正（相对 2026-10-09 旧记忆）

- `D:\agy` 并非永久删除：2026-11-24 已按官方脚本重装 CLI：`curl -fsSL https://antigravity.google/cli/install.cmd` → `install.cmd -d D:\agy\bin`；agy.exe 239,256,728 B、v1.5.15；用户 PATH 已含 `D:\agy\bin`。CLI 尚未登录（凭据目录未生成），登录含手机验证只能用户本人过。
- 代理端口以实测监听为准：现 **127.0.0.1:7890**（FlClash），旧记忆里的 7897 已不监听。curl 认 HTTP(S)_PROXY 环境变量。

## CC Switch 检测机制（4.0.40 实测）

- 「Antigravity」条目管的是 **agy CLI**，桌面 IDE（D:\Antigravity\Antigravity.exe）不算；4.0.40 起 IDE 走独立 agy-desktop 探测（PR #9893）。「装了 IDE 却显示未安装」不是 bug。
- 安装枚举 `enumerate_tool_installations()` 只用**进程继承的 PATH**（issue #9810）：从老父进程拉起的 GUI 看不到新加 PATH；修法=taskkill 后用注册表 Machine+User 拼接 PATH 重启。
- 「检测到系统环境变量冲突」横幅：ANTHROPIC/OPENAI/GEMINI/GOOGLE_GEMINI/XAI 前缀的**用户注册表变量**一律告警（docs/user-manual/zh/5-faq/5.4-env-conflict.md）。本次冗余源 `ANTHROPIC_TARGET_API_URL=http://127.0.0.1:15721` 已备份后删除（~/.claude 与 cc-switch.db 均无消费方）。

## 本机 npm 前缀现状

- 单一健康全局前缀 = `C:\Users\Admin\AppData\Roaming\npm`（npm prefix 一致）：claude 2.1.331 / codex 0.172.0 / pi 1.6.0。
- 陈旧前缀 D:\node-global（C:\node-global 为其 junction）的 claude/codex/pi 九入口+三包已备份移走到 `G:\AIrenwu\01_任务归档\2026-11-24_CC-Switch重复安装与反重力识别\04_产物\backup\node-global`；目录里 npm/npx/nodemon/motrix 等未动，PATH 条目保留。
- Claude Code 自更新中断特征：bin 目录只剩 `claude.exe.old.<毫秒时间戳>`，cmd 包装指向不存在的 exe → 报「不是内部或外部命令」。

## 执行壳教训

- 工具名 pwsh 实为 PowerShell 5.1，**内层再调 `pwsh` 会 CommandNotFound**；后台 job 直接 `& '脚本.ps1'`。
- install.cmd 参数 sanitize 禁 CMDCMDLINE 含 `&|;<>^` → 不能 `cmd /c "set …&&…install.cmd"` 包装，环境变量在调用壳里设。
- 用户活跃时取证不抢前台：ShowWindow(hwnd, SW_SHOWNOACTIVATE=4) + PrintWindow 后台抓图（gui-control\pwcap.py）。

## 关联

- 手册记录：`G:\AIrenwu\本地AI使用手册\03-通用\03-调试与验证\踩坑-CCSwitch判claude无法运行且反重力不识别-陈旧npm前缀遮蔽与进程PATH.md`（verified）。
- 归档：`G:\AIrenwu\01_任务归档\2026-11-24_CC-Switch重复安装与反重力识别\`（脚本+备份+前后截图）。

## 2026-11-24 后续（用户授权清理 + 复查）

- 用户说「将垃圾清理，然后再检查一遍」：已删 `backup\node-global`（1,375,634,939 B，G 盘释放约 1.30 GB）与 `D:\AI-Tool-State\agy-install`（install.cmd/run_install.ps1 先归档到 03_工具脚本）；env 备份 JSON 保留。回滚改走 npm 重装旧版。
- 复查全绿：注册表 PATH 下 where 四命令单一入口、版本 2.1.331/0.172.0/1.6.0/1.5.15、*.old.* 扫描空、ANTHROPIC_TARGET_API_URL 空、CC Switch 日志 attach 正常；ccswitch_recheck.png 与 final2 逐字节一致。
- 取证补充：show_noactivate.py 支持 argv[3] 强制 hwnd（最大面积候选会误选 tray_icon_app 透明覆盖窗，抓出纯黑图）；用户 09:54 把主窗口关到托盘后，抓图完毕应 SW_HIDE 还原托盘状态。