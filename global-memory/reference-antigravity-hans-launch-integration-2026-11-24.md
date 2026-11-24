# 反重力汉化与启动整合（2026-11-24）

- 诉求：用户每次启动 Antigravity 都要单跑 H:\下载\antigravity-hans-windows-amd64.exe 才中文；要求启动即汉化。
- 产品身份：D:\Antigravity = **普通版 Antigravity 2.35.0**（非 IDE；%LOCALAPPDATA%\Programs\Antigravity IDE 不存在）。
- 工具：github.com/yuexps/Antigravity-Hans，Go 单文件；SHA256=A1330F1F955515D5024F403C343384F04FEE2D1A4E8FDB58D1C0BEE978C259FA。动态=CDP 会话级注入（随页面关闭消失→每次要单跑的根因）；静态 --patch 仅 IDE 且不含 Swarm 会话页→普通版不可用。
- 整合落地：稳定副本 D:\AI-Tool-State\antigravity-hans\antigravity-hans.exe；官方 `--shortcut --app` 生成桌面「Antigravity 中文.lnk」，目标 `conhost.exe --headless "<exe>" --app --nogui`；开始菜单原 Antigravity.lnk 备份后 repoint 同命令（图标不变）。备份：G:\AIrenwu\01_任务归档\2026-11-24_反重力汉化与启动整合\04_产物\backup\Antigravity.startmenu.lnk.bak。
- 验证：空闲门控脚本按 lnk 同命令启动，应用带 --remote-debugging-port=58321，抓图全中文（新建对话/自动化/自定义/嗨，<已脱敏昵称>…/EN 圆钮），验后 --stop+taskkill 复原。监视器状态目录 %APPDATA%\antigravity-hans\monitor-antigravity.pid。
- 边界：直接双击 D:\Antigravity\Antigravity.exe 仍英文（动态原理）；更新后词库滞后先 --stop；未签名 exe 杀软误报按 SHA256SUMS。
- 手册记录：03-通用/03-调试与验证/经验-反重力汉化每次需单跑工具-动态CDP注入与官方一键快捷方式整合.md（verified）。
- 坑：PS 5.1 `foreach{}|pipe` 非法需 `$()`；Start-Process -RedirectStandardInput 'NUL' 解析成工作目录文件报错→ASCII .cmd `< NUL`；含中文路径 exe 先复制 ASCII 目录。

## 2026-11-24 后续：启动时自动更新汉化工具

- 诉求：每次启动检查 hans 更新并自动更新，免得旧词库配新应用出问题。
- 落地：D:\AI-Tool-State\antigravity-hans\launch.ps1（纯 ASCII 包装器）：Get-FileHash 本地 exe → curl GitHub releases/latest（-m 10，失败回落注册表 ProxyServer）→ 比对 windows 资产 digest（无 digest 回落 SHA256SUMS）→ 不同则下载+哈希校验+Copy 旧 exe 到 backup\antigravity-hans.prev.exe+Move 替换（锁定先 --stop 重试一次）→ 写 version.json → 启动 `--app --nogui`；任何失败记 update.log 并回落旧版启动，不阻塞。-CheckOnly 只检查不启动。
- 两 lnk（桌面「Antigravity 中文」、开始菜单 Antigravity）改指 `conhost.exe --headless powershell.exe -NoProfile -ExecutionPolicy Bypass -File "<稳定目录>\launch.ps1"`；改前备份 *.chain1.bak（同归档 backup）。
- 坑：conhost --headless 控制台码页 OEM936 把 curl stdout 的 UTF-8 中文解出杂散反斜杠致 ConvertFrom-Json 失败（交互 pwsh 正常）→ 改 curl -o 临时文件 + Get-Content -Raw -Encoding UTF8。
- 实测：上游 v0.5.0 digest == 本机哈希（已最新）；隔离假旧 exe 走完整更新分支 5s 通过；headless -CheckOnly 记 up-to-date；坏 ApiUrl 走 catch 记日志 exit 0。
- 回滚：backup\antigravity-hans.prev.exe（更新前 exe）、lnk *.chain1.bak（改链前）。