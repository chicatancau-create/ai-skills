---
name: local-ai-handbook
description: 本机（这台 Windows）《AI本地使用手册》（G:\AIrenwu\本地AI使用手册，2026-11-16 由 E:\本地AI使用手册 迁入任务区工作区）的**默认前置知识库**。每次任务开始前先检索、任务结束前判断是否回写；任务里出现报错、超时、编码乱码、命令失败、排版异常、插件/技能问题、AI 客户端连不上、或需要本机环境既有结论与取证方法时，必须查证再动手。手册记录的是这台机器上已复现、已验证的踩坑与修复（PowerShell 5.1 编码与传参、沙箱只放行工作区致写 E 盘被拒、虚拟网卡抢默认路由致域名假超时、AI 面板 1ms 连接失败误判、Excel 行高裁字、提权 .cmd 写法、中文注册表导致插件兜底失败、技能发现机制与安装位置、逆向工具箱清单等）。
---

# 本机《AI 使用手册》：默认检索与回写

## 这是什么／为什么默认要用

`G:\AIrenwu\本地AI使用手册` 是本机的 AI 工程知识库（Obsidian 仓库）。
2026-11-16 由 `E:\本地AI使用手册` 迁入 `G:\AIrenwu` 任务区根目录（E 盘已不存在）；旧文档里出现的 E 盘路径按本行理解。
里面是**这台机器特有**的、已复现并验证过的踩坑记录：不是通用编程百科，而是「同一批坑不必再踩第二次」的硬结论。

**默认行为（用户已明确要求）**：
本 skill 是**开工前的前置动作**，不是被点名才用的工具。
拿到一个任务，先按下面的「检索」流程查手册，再动手；任务结束按「回写」流程判断是否留记录。
用户不再需要每次说「查一下手册」。

## 权威边界（必须先读）

1. 系统/开发者/用户当前要求 > 目标项目自己的 `AGENTS.md` / 当前代码 / 实际命令输出 > 手册历史结论。
2. **不因为手册里有类似经验，就跳过当前项目的复现、测试与代码审查。**
3. 手册是辅助记忆，**不是**权限、审批或安全策略的替代品。
4. 网卡名、代理端口、安装路径、版本号这类**易变项**，用前必须实测复核，历史记录可能已过时。

相关文件：

- `~/.dsh/AGENTS.md`（≡ `$DSH_HOME/AGENTS.md` = `D:\DevCache\.dsh\AGENTS.md`）：用户全局规则（第〇节即「默认先查本手册」），是手册里最关键的几条铁律摘要。2026-11-16 曾发现缺失并已重建。
- `G:\AIrenwu\本地AI使用手册\首页.md`、`使用与维护说明.md`、`AI接入规则.md`、`AGENTS.md`：手册自身的规则。
- `G:\AIrenwu\README.md`：任务区总纲（7 类文件夹大纲、脚本库索引、git 双推工作流），手册是其中第 7 类。
- 本 skill 不在 `~/.dsh/skills/` 安装目录里：由 `skill-router`（本机技能总路由）按需读取本文件；旧 `scripts/handbook_search.py` 检索脚本已删除，检索用下面的症状索引 + grep。

## 任务区联动（2026-11-16 起）

手册不再是 E 盘上的独立库，而是 `G:\AIrenwu` 任务区的第 7 类文件夹，与任务区双向联动：

- 任务区总纲：`G:\AIrenwu\README.md`（7 类文件夹大纲铁律、脚本库索引、git 双推工作流）。
- 可复用脚本：`G:\AIrenwu\脚本库\`（10 分类；提交双推用 `07_机器修复与clash清理\sync-repo.ps1 -MsgFile <提交信息文件>`）。
- 任务证据：`G:\AIrenwu\01_任务归档\YYYY-MM-DD_任务名\`（01_报告/02_证据日志/03_工具脚本/04_产物）；手册记录的证据路径多指向这里。
- 联动规则记录：`03-通用/04-工程规范与安全/规则-任务区与手册一体化联动.md`。

## 检索（每个任务开始前）

1. 打开 `G:\AIrenwu\本地AI使用手册\首页.md`，扫 `01-前端`、`02-后端`、`03-通用`、`90-模板`、`99-收件箱` 的目录名定位候选。
2. 用**症状关键词**搜索正文（不要只读文件名就下结论）：
   `grep` 模式关键词：`超时`、`乱码`、`裁字`、`提权`、`假忙`、`编码`、`BOM`、`路由`、`网卡`、`沙箱`、`插件`、`技能`、`needs-review`。
   最常用：在 `G:\AIrenwu\本地AI使用手册\03-通用` 下按关键词 grep。
3. 读取命中的记录正文，把结论当作**候选经验**，再用当前项目事实复核。

### 当前正文记录与症状索引

`03-通用` 与 `01-前端` 下已有正文的记录（`02-后端` 目前只有分类 README）。新增记录后**必须**同步本表。

**调试与验证**（`03-通用/03-调试与验证/`）

| 症状 / 场景 | 记录 |
|---|---|
| 内联命令里 `$_`、`$变量`、反斜杠被吞，报错词风马牛不相及 | `踩坑-Bash内联传参吞PowerShell变量与反斜杠.md` |
| 文本里的 Windows 路径"少了反斜杠"、内容莫名断行、肉眼正常但 grep 不中；文件疑似含不可见控制字符 | `踩坑-Bash内联传参吞PowerShell变量与反斜杠.md`（2026-11-15 追加节：反斜杠被压单后 Python 按八进制转义消费 `\202`/`\01`/`\02`、`\n` 当换行 → 静默写出 U+0082/U+0001/U+0002；只有 `repr()` 或按码点正则能发现；**修复用的正确字符串同样会被吃**，改文件须备份 + 匹配数断言 + 写盘后复检） |
| 写文件被拒（`[sandbox: file access denied]` / 拒绝访问），或改写带 BOM 的文件后 BOM 丢失 | `03-通用/03-调试与验证/踩坑-沙箱只放行工作区致写E盘被拒且write会抹掉源码BOM.md`（`verified`：BOM 丢失与沙箱拒写均已实测；拒写不限 E 盘，工作区外一律拒；2026-11-13 由收件箱移入正式分类） |
| 写 OpenRevo（Tauri 宿主）插件页：iframe 里显示的是宿主主界面、`fetch('相对路径')` 报 `Unexpected token '<'`；插件面板整片白底浅字「惨白」；宿主日志刷 `[ERROR] [CONFIG] ... expected value at line 1 column 1` 并停止保存配置 | `03-通用/03-调试与验证/OpenRevo插件页开发三条硬规矩.md`（`verified`：2026-11-20 实机 OpenRevo v0.9.8 复现+修复+验证；三条根因＝未知相对路径兜底回宿主根路由、插件 tab 是独立 WebView2 不继承宿主皮肤、`Set-Content -Encoding UTF8` 写出 BOM 让 Rust serde 拒绝解析。对策＝子页面 base64 内嵌走 iframe `srcdoc`、`html,body` 给实色深底、config 一律用 Python utf-8 无 BOM 读写） |
| 改别的进程窗口样式「看起来成功、其实没生效」：`SetWindowLongW(hwnd,-20,...)` 返回 0、`GetLastError()=5`、`SetLayeredWindowAttributes` 返回 False，exstyle 采多久都不变；面板/状态文件却显示「分层穿透已就位」假绿 | `03-通用/03-调试与验证/踩坑-宿主以管理员运行时外部进程改不了它的窗口样式-穿透要页面自己调宿主接口.md`（`verified`：2026-11-20 实测，目标窗口属于**提权进程**时 UIPI 一律拦截，普通权限写不进去；对策＝函数返回**读回的真实值**而不是计算值，并把动作改成让页面自己调宿主接口 `set_click_through { enable }`；另注意**判断鼠标穿透要看 `WS_EX_TRANSPARENT(0x20)`，不是 `WS_EX_LAYERED(0x80000)`**） |
| 删应用/插件目录时 `Remove-Item -Recurse` 反复报「对路径 xxx 的访问被拒绝」，管理员重试也没用 | `03-通用/03-调试与验证/踩坑-删插件目录被拒是内核驱动与被注入DLL占用-先改父目录名再登记开机删除.md`（`verified`：2026-11-20 实测三层真因＝宿主按 `service.auto_start` 反复拉起伴生 exe、目录内 `.sys` 已被 `sc create` 注册成 **Running 内核驱动服务**（`RTCoreMini64`）、`.dll` 被全局钩子注入到 `svchost.exe` 等进程。修法＝先 `Move-Item` 把父目录整体改名移出应用目录（应用立刻干净）→ `sc.exe stop/delete` 驱动服务 → 剩余锁文件 `MoveFileEx(...,MOVEFILE_DELAY_UNTIL_REBOOT=4)` + `HKCU\...\RunOnce` 兜底；提权 worker 日志必须写 `%LOCALAPPDATA%\Temp`，写项目盘有时静默不生成） |
| 开/关 DeepSeek Harness 弹黑色命令框、停在「请按住任意键继续」必须按键；或自建的启动守卫 bat 在 GUI 起来前卡住不放 | `03-通用/03-调试与验证/踩坑-DSH启动弹黑框等按键-守卫pause叠加遗留中间态目录.md`（`verified`：两层叠加＝守卫脚本对 rc=2 用 `pause` + 可见普通窗口，且它自己 `rmtree(..., ignore_errors=True)` 删不掉的 `.__guard_bak` 被同一脚本判成待人工确认。修法＝删 pause、输出重定向日志、`wscript` 里 `sh.Run bat,0,False` 隐藏启动且快捷方式 `WindowStyle=7`、中间态改「相对路径+大小+小文件 SHA256 全覆盖」判冗余后自动清、`--popup` 只在真有问题时弹中文框。验收：运行中 `Get-Process cmd,powershell` 的 `MainWindowHandle` 全 0） |
| DSH 插件「整体消失」：自己注册的 agent 工具调不到、client slot 按钮不见、profile 依赖与源码都正常，重启也不恢复 | `03-通用/03-调试与验证/踩坑-DSH插件package.json带BOM致整包被内核静默跳过.md`（`verified`：PowerShell 5.1 `Set-Content -Encoding UTF8` 给插件 `package.json` 加了 `EF BB BF`，内核 `loadProfileDirectory` 的 `JSON.parse` 抛 `SyntaxError: Unexpected token '` → 按设计把该 bundle 丢进 `skippedBundles` 且只写 stderr（GUI 启动没人看），bundle patch 整层不入组合。查法：`ELECTRON_RUN_AS_NODE=1` import `app.asar/dsh/node_modules/@deepseek-ai/dsh-app-boot/lib/index.js`，调 `loadProfileDirectory(...,{userLayer:false})` 看 `skippedBundles`／`composeEntries` 条目数；修法：`[System.IO.File]::WriteAllText(..., UTF8Encoding($false))` 去 BOM 并复检首三字节） |
| 预设里明明配了 `tool-subagent`，会话却调不到 `subagent` / `subagent_fork` 工具；或 `plugin_manager list_bundles` 报 `error.code: "incompatible-version"`（profile 里装着旧内核同名包） | `03-通用/03-调试与验证/经验-DSH装插件与删provider的四个动作点.md` 的「2026-11-22 补」节（`verified`：`node_modules` 里 `@deepseek-ai/dsh-tool-subagent@0.2.2-rc.3` 的 peerDeps 把 `dsh-agent/dsh-llm/dsh-session/dsh-subagent/dsh-tools/dsh-system-prompt/dsh-session-projection` 全钉 rc.3，遮蔽 asar 内 rc.5 ⇒ 版本门禁不过、两行插件激活失败。修法＝**先 `remove_bundle` 再 `install_bundle` 并显式带版本**（这些包 npm `latest` 是占位 `0.0.1-rc.1`，真版本在 `next`/`alpha` tag）；装完必须**新开会话**才见新工具） |
| 升级带原生依赖的 DSH 插件时 pnpm 报 `[ERR_PNPM_EPERM] [importPackage ...\@img\sharp-win32-x64] ... rename ..._tmp_ -> ...`，而 `plugin_manager` 说是 `kind: "permission"`「DSH 写不了 profile 目录」 | 同上文件「2026-11-22 补」节第②条（`verified`：**不是权限问题**——同目录 `Rename-Item` 成功、`Remove-Item` 失败，锁的持有者是运行中的 DeepSeek Harness 进程（`libvips-42.dll` / `sharp-win32-x64-0.35.5.node` 已映射）。修法＝把被锁目录**改名挪开**再让 pnpm 往原路径装新份，`.bak-*` 重启 DSH 后删。判真假权限用「能改名但不能删」） |
| DSH 宿主升级后（如 0.2.2-rc.5 → 0.2.3.0 / 内核 `0.2.3-alpha.2`）装插件报 `incompatible-version`，或升级后某个第三方插件界面整块消失 | `03-通用/03-调试与验证/经验-DSH装插件与删provider的四个动作点.md` 第 12 节（`verified` 2026-11-23：①`latest`/`next` tag 都追不上内核，只有显式 `@0.2.3-alpha.2` 能过版本门禁，先 `remove_bundle` 再 `install_bundle` 带全版本；②升级器会把第三方 bundle 留成 `enabled:false, installed:true`（本次 `dsh-better-sidebar`），用 `plugin_manager set_bundle {target, enabled:true}` 一行恢复，不必重装；③`@img/sharp-win32-x64` EPERM 每次升级都会再犯，改名挪开后重装，`.bak` 要关 DSH 才能删） |
| 某域名直连一律超时、走代理秒回 | `踩坑-虚拟网卡空metric抢走默认路由致域名假超时.md` |
| 当前是哪块网卡抢了默认路由 | `规则-默认路由抢占网卡已换为RadminVPN.md` |
| 面板「连接失败 / 耗时 1ms」 | `踩坑-AI面板连接失败耗时1ms是没填密钥而非网络.md` |
| AI 客户端卡「思考中」、切路由无效、用量看不到 | `踩坑-第三方Claude客户端自带服务商配置切全局路由无效.md` |
| 插件报「搜索没跑完」、只在中文 Windows 上失败 | `踩坑-中文注册表值触发PS兜底且param不绑定致插件查不完.md` |
| xlsx 在 Excel 里行高被裁字、文字重叠 | `踩坑-openpyxl写的xlsx在Excel里行高被裁字.md` |
| Excel 打不开整本 xlsx、报 `0x800A03EC` | `踩坑-xlsx字符串以等号开头致Excel打不开簿.md` |
| Windows 新窗口居中、托盘图标取证、DPI-aware | `规则-Windows新窗口默认居中只能常驻监视器.md`、`踩坑-Win11托盘图标在独立溢出窗口且取证须先设DPI-aware.md` |
| 脚本驱动 MSVC / vcvars / qt-cmake | `踩坑-脚本驱动MSVC时vcvars传参与qt-cmake不透传build.md` |
| 缩放/适配后窗口或控件"该缩的没缩"，框比原图大就原样返回 | `踩坑-同一函数既当不放大守卫又当按框缩放致该缩的不缩.md` |
| 休眠/关机收尾窗口里 taskkill /F 杀不掉进程，代理软件残留 | `踩坑-休眠挂起窗口内taskkill子进程杀不掉进程致代理残留.md` |
| 唤醒后没人拉起应用（收尾被休眠冻结、唤醒广播丢失） | `踩坑-休眠冻结收尾致唤醒广播丢失须主动补唤醒.md` |
| 唤醒后代理软件在跑但全机没代理（ProxyEnable 没自动开回） | `踩坑-代理软件重启后不自动恢复系统代理开关唤醒须补开.md` |
| 关机被取消后桌面没代理/应用没了（收尾已提前做） | `踩坑-关机被取消WM_ENDSESSION为假须还原已做的收尾.md` |
| 测试触发真实收尾动作，把系统代理关了/真杀了进程；或 e2e 脚本把用户真实窗口挪了 | `踩坑-测试触发真实收尾动作关掉系统代理.md` |
| 测试断言"日志 mtime/大小不变"偶发失败，其实什么都没坏 | `踩坑-断言活文件mtime大小不变必假失败.md` |
| CTest 全绿但构建树里仍有 LastTestsFailed.log，按它判当前红绿 | `踩坑-CTest全绿后LastTestsFailed残留致红绿误判.md`（`verified`：成功运行不清该文件;判本轮只认 stdout 与 LastTest.log mtime） |
| grep 审查报「未实现/无白名单/死组件/行数少一」，回源码却发现都做了 | `踩坑-静态审查grep四类误报与hex无表头清单统计口径.md`（`verified`：camelCase、前导斜杠、组件自身 id、hex 无表头四类误报） |
| 居中/留白数字假不对称，差 8px/16px 这种干净小数 | `踩坑-可见框与真实矩形差8px致留白数字假不对称.md` |
| 杀软「断网修复」清零系统代理；判代理端口别加 -State Listen | `踩坑-杀软断网修复清零系统代理且StateListen过滤假报端口死.md` |
| GitCode/AtomGit 令牌是否有效（存了≠有效），要零副作用活验 | `规则-GitCode令牌只读活验用api-v5用户端点.md` |
| GitCode 仓库列表抓不到／匿名 API 400 点名 private-token／gitcode.com 直连超时 | `踩坑-GitCode合并AtomGit后repos接口要private-token头且直连超时走7890.md` |
| 两端仓库对齐写操作／GitCode 建仓改简介改公开删仓／gh 改公开被拒或删仓 403／GitHub git push 连接被重置／中文简介变问号 | `规则-两端仓库对齐写操作GitCode增删改UTF8字节body与gh改公开删仓scope.md` |
| 公开仓历史脱敏／清历史手机号邮箱／filter-repo 重写／force-push 被拒 cannot lock ref／历史重写后守护推回旧历史 | `规则-公开仓历史PII清洗用filter-repo镜像克隆法.md` |
| gh api 探活报 404「仓库不见了」、或 422 缺 name | `踩坑-ghapi带-f默认POST致探活404误判仓库已删.md` |
| GitHub 大包推送报 curl 56 / 中途被重置，ls-remote 却正常 | `踩坑-GitHub大包推送被重置需分块推送.md` |
| 设了 VSLANG=1033 但 `cl.exe` 仍输出中文诊断 | `踩坑-VSLANG1033未把MSVC诊断切成英文.md`（`verified`：本机只装中文 2052 语言包、无 1033 资源，VSLANG 只在已装语言间切换；真修复是装英文语言包） |
| 脚本导出 Excel 区域 PNG 是空白（几 KB）、或报 `Unable to find type [System.Drawing.Image]` | `踩坑-Excel区域贴Chart导出空白PNG改用剪贴板或PPT导出.md` |
| 表格中文标点跑行首、KOC/DOU+/18–35 被折行切碎 | `踩坑-Office不守中文禁则且PPT二次折行切词需预断行.md` |
| 强杀 FlClash 后全机断网、端口不监听 | `踩坑-FlClash强杀后停未运行不自动起核心且系统代理悬空致全机断网.md` |
| 关掉 FlClash/开机后全机断网、系统代理开关悬空指死端口 | `修复-FlClash关闭后悬空系统代理的常驻守卫与自动运行.md` |
| 想一键修复网络／想安全关掉 FlClash 又怕断网（脚本写死旧端口与服务） | `工具-网络一键修复v2与安全关闭VPN脚本.md`（`verified`：判端口死活只用真 TCP，`Get-NetTCPConnection` 的 `State` 会有 `空/0` 伪行按它过滤必假报端口死；端口没通时**不许**把 `ProxyEnable` 写 1） |
| FlClash 升级后 sc 报 1060 服务未安装、allow-lan=false 写了但 LAN 仍可连 | `踩坑-FlClash升级0.9.5删helper服务与allow-lan覆写键未生效.md` |
| 防火墙三个 profile 全关想开启、又怕断远程/断局域网 | `修复-Windows防火墙长期全关后安全开启与远程工具放行.md`（`verified`：`state on`+`firewallpolicy blockinbound,allowoutbound`+按程序/接口放行+开丢包日志；`logging blocked` 参数名是错的，正确 `droppedconnections`；杀软在跑≠接管防火墙） |
| Postman「Something went wrong」崩溃屏、网络恢复后仍不复活 | `踩坑-Postman启动瞬间云端断网致崩溃屏且网络自愈后不自恢复须重启.md` |
| 热点上开 DoH 后解析反而 27–32s | `踩坑-DoH在UDP受限手机热点反而劣化须回退DHCP.md` |
| 手机正常电脑断、Wi-Fi 约 6s 硬断 | `踩坑-MediaTek WLAN扩展mtkwlex卸载重载致Wi-Fi硬断手机正常电脑断.md` |
| 导出 QQ 群成员成班级名单 | `规则-QQ群成员名单用无障碍树加滚动采集并拆姓名手机号.md` |
| 抖音聊天 PC 闪退/群消息采集/开群导航/OCR 提取/去重 | `规则-抖音聊天PC群采集GUI事实与启动链.md` |
| npm 报 E404、包名在等宽字体里分不清 `mysq12`/`mysql2`、报错域名与配置的镜像不一致 | `踩坑-npm报404包名肉眼难辨mysq12与mysql2须读debug日志.md`（`verified`：判据只认 `npm-cache\_logs\*-debug-0.log` 的 `http fetch GET 404` 行；一条 install 里一个包 404 会让整条回滚） |
| WebView2/Tauri/Pake 壳应用点了「下载」全盘找不到文件 | `踩坑-壳应用点下载找不到文件先查WebView2的History下载表与真实Downloads目录.md`（`verified`：`downloads` 表 0 行＝从未下载；本机真实 Downloads 是 `G:\NDM下载`，`C:\Users\Admin\Downloads` 不存在） |
| 按截图目视坐标裁原图裁到全黑/无关区域 | `踩坑-Read显示图是缩放版按显示坐标裁原图必裁错.md`（`verified`：Read 显示层等比缩放，定位先像素扫描再裁、最后目视） |
| venv 报 `did not find executable` / `Failed to import encodings` | `踩坑-venv的base解释器被清空致整个venv静默报废.md`（`verified`：查 pyvenv.cfg home 完整性；旧诊断有时效；dev 依赖用 uv pip 补） |
| 命令行 hvigor 报 `00303217 Invalid value of 'DEVECO_SDK_HOME'`；或 BUILD SUCCESSFUL 却 exit 1 | `踩坑-DevEco命令行hvigor两坑-缺SDK环境变量报00303217与unsigned警告致假exit1.md`（`verified`：补 DEVECO_SDK_HOME/hwsdk.dir；红绿只认 stdout 的 SUCCESSFUL/ERROR 行，不认退出码） |
| 安卓模拟器里游戏启动即崩、ApkStart 报「缺少设备原生库…会自动切换兼容镜像重试」 | `99-收件箱/踩坑-易盾加固游戏在非白名单安卓模拟器必崩且缺原生库文案是误判.md`（`needs-review`：真栈 `com.netease.nis.wrapper.MyJni.load` 的 `UnsatisfiedLinkError` 且**无 dlopen/linker 错**＝易盾反作弊白名单拒绝，非缺库；白名单只放行 MuMu/雷电，换镜像/改翻译层/伪装属性/假 MuMu 包名均无效，硬特征 hypervisor CPUID/ranchu 改不动） |

| uni-app H5 下拉刷新判「指示器已停止」用 display/height 恒真；或刷新后分页请求旧页码跳中间页 | `踩坑-uni-appH5刷新指示器绝对定位隐藏与reload未重置pageIndex致分页取证误判.md`（`verified`：uni-page-refresh 绝对定位移出视口，判 rect.bottom>0；reload() 不重置 this.pageIndex → 刷新后触底请求旧索引+1；取证抓 postData 序列，null=预检 OPTIONS） |
| 怀疑「装了两个相同程序」（开始菜单/任务栏出现新旧名两个入口），或应用自更新后改名留旧入口；或想改 Trae CN 默认启动 IDE/Agent 模式 | `踩坑-TraeCN自更新改名留旧快捷方式致开始菜单两个Trae实为同一程序.md`（`verified`：Trae CN 3.4.20 自更新 TraeCode CN→TRAE CN 新增 lnk 不删旧，两 lnk TargetPath 同指一个 exe；判重看进程 Path/卸载注册表/lnk TargetPath 三清单，不看图标数；清理删重复 lnk、保留用户固定/可见的那个（改 lnk 文件名会坏开始菜单磁贴，用户要改名先告知重固定）；默认启动模式用设置 window.startupWindowType=agent/ide，非 CLI 参数；本机已执行：删新留旧→改名 TRAE CN→默认 agent） |
| 要让 AI/脚本剪 CapCut（国际版）视频、生成草稿、加离线字幕；或 pip 装 vosk 挂起不动 | `03-通用/03-调试与验证/经验-CapCut国际版草稿自动化-pycapcut建草稿与vosk离线字幕.md`（`verified`：pycapcut 0.0.4 建草稿文件级断言通过；vosk small-cn + SAPI TTS 自测逐字命中；装库用自带 3.12 别用 3.15；CapCut 首页识别已过，时间线待补；v2 补转场/音频轨/旁白去停顿；v3 整片审查法；v4 转场总时长不变语义 + settb 坑 + 不依赖编辑器的 ffmpeg 成品导出；v8 既有草稿文件级细节优化/黑尾裁剪/首页 Enter 白窗僵尸恢复；v9 纯手写 JSON 造多轨讲解工程（图片须放 materials.videos 且 type=photo、字体用安装包自带 zh-hans.ttf、文字素材 deepcopy 模板改 content、口播留空隙压提示、Path.replace 陷阱）） |
| 微信收到的视频/音频过一阵消失、脚本报找不到文件 | `03-通用/03-调试与验证/经验-微信msg-video临时文件会被自动清理-收到媒体立即备份.md`（`verified`：msg\video 临时缓存自动清理，收到立即备份原件或抽音轨） |
| 给 XD 课件/原型加拖移（drag）跳转，或校验器对 XD 自己存的文件报 `unknown action 'auto-animate'`/symbol 键 `matches NO node` | `03-通用/03-调试与验证/经验-XD拖移auto-animate落盘格式用亲笔样本定案与校验器盲区.md`（`verified`：落盘 drag=`triggerEvent:"drag"`+`action:"auto-animate"`（独立 action，transition 残留 dissolve 被忽略）；无先例用活缓存 `%LOCALAPPDATA%\Packages\Adobe.XD_pc75e8sa7ep4e\LocalState\<hash>\interactions.json` 或用户另存文件的亲笔条目定案；校验器 FAIL 先跑未改动基线区分盲区，修后负例证没放水；xdpatch spec 加 `autoAnimate:true`） |
| 给 XD 组件加「点击切换状态」、克隆 kit 母版做自有组件，或校验器对纯状态文件报 `unknown action 'state-transition'`/母版组 id 误判 | `03-通用/03-调试与验证/经验-XD组件状态与state-transition落盘格式及校验器扩展.md`（`verified`：默认状态=母版 group.children、非默认=meta.ux.states[]+syncMap、实例=syncRef 树+syncMap+localTransform；点击切换=state-transition 双重表示（节点 meta.ux.interactions + interactions.json，guid 一致、destination∈本源 symbol 状态 id）；克隆 kit 母版全量改 id 交付自有组件；validate_proto/inter_probe 已扩展支持状态，未改动基线也 PASS；格式详见 tools\xd\SCHEMA.md §16） |
| CC Switch 报 claude「不是内部或外部命令」、claude/codex/pi「另有 1 处安装」、装了 Antigravity 却显示未安装、顶部「系统环境变量冲突」横幅 | `03-通用/03-调试与验证/踩坑-CCSwitch判claude无法运行且反重力不识别-陈旧npm前缀遮蔽与进程PATH.md`（`verified`：陈旧前缀 D:\node-global+junction C:\node-global 遮蔽 Roaming\npm、自更新中断留 .old 残骸→备份移走九入口三包；Antigravity 条目只认 agy CLI（官方 install.cmd -d D:\agy\bin 装）；安装枚举只用进程 PATH→注册表实时 PATH 重启 GUI；ANTHROPIC* 用户变量 grep 消费方+备份后删消横幅） |
| 反重力每次启动都要单跑汉化工具、想启动即中文 | `03-通用/03-调试与验证/经验-反重力汉化每次需单跑工具-动态CDP注入与官方一键快捷方式整合.md`（`verified`：普通版动态 CDP 会话级注入→官方 `--shortcut --app` 生成 conhost --headless 一键链，备份后 repoint 开始菜单原 lnk；静态 --patch 仅 IDE 不含会话页；直接双击 exe 仍英文） |
| 反重力汉化工具想启动时自动更新／headless 启动链里检查报错或乱码 | `03-通用/03-调试与验证/经验-反重力汉化每次需单跑工具-动态CDP注入与官方一键快捷方式整合.md`（`verified` 后续：launch.ps1 每次启动比对 GitHub release digest 自动更新、失败回落旧版；conhost --headless OEM936 码页须 curl -o 文件+UTF8 读） |
| PixPin（或类似 Qt/原生截图工具）启动即退、退出码 0xC0000409、pixpin.log 截断为 0、无 WER 转储 | `03-通用/03-调试与验证/踩坑-PixPin启动即崩0xC0000409因截图历史索引损坏改名即修复.md`（`verified`：上次截图 UiRegionDetector 超时崩溃写坏 %LOCALAPPDATA%\PixPin\History\_ScreenshotRecord 索引，启动读它即 __fastfail；整目录改名全新数据能跑⇒数据损坏，逐文件改名隔离定位；修复＝_ScreenshotRecord 改名 .off 保留备份，截图本体 Data 与 Config 不丢；0xC0000409 不走 WER，别因无转储排除崩溃） |
| 「GPT」/ChatGPT/Codex 桌面版（MSIX）起不来、事件日志 0x800701C0「配置运行时遇到错误」、重注册报 0x80073D3C「等待删除」、Remove 报 0x80073D02 DynamicDependenciesInUse | `03-通用/03-调试与验证/踩坑-CodexChatGPT桌面版MSIX框架DynamicDependenciesInUse重启无效需重装新版.md`（`verified`：框架卡动态依赖持久损坏态，**重启往往无效**；重装更新版应用换新框架家族最稳；大 MSIX 用 BITS 下载＋提权 Add-AppxPackage -Path；Store 包不能从松散备份重注册） |
| 终端默认还是 Windows PowerShell 5.1，要升最新 7.x 设默认、旧版能删就删；或提权改注册表 PATH 报「无法写入到注册表项」；或 Windows Terminal 加 pwsh profile 撞重复 GUID | `03-通用/04-工程规范与安全/经验-PowerShell7升级默认-ZIP装稳定路径与终端默认及注册表只读坑.md`（`verified`：7.7.0 已无 MSI 只有 MSIX/ZIP，重自动化用官方 ZIP 解到 `C:\Program Files\PowerShell\7`+系统 PATH 前置保 `REG_EXPAND_SZ`；5.1 是系统组件卸不掉只能隐藏；`Get-Item` 注册表键只读→`SetValue` 必失败，须 `[Microsoft.Win32.Registry]::LocalMachine.OpenSubKey($sub,$true)`；WT 自动生成 PowershellCore 动态 profile GUID 固定 `{574e775e-4f2a-5b96-ac1e-a2962a402336}`，在自动那条上定制并留 `source` 别手动撞；验证按注册表实时 PATH 模拟新进程不信 `$env:Path`） |

| CrossDesk `--unattended-enable` 永远 exit 1 且重定向输出全空；便携版开不了登录前无人值守；安装版 GUI 开着时 enable 也失败 | `03-通用/03-调试与验证/踩坑-CrossDesk便携版开不了登录前无人值守-三层门禁与CLI输出只上控制台.md`（`verified`：三层＝便携编译门禁 kAutostartRequiresElevation=false（autostart_task.h:10-15）、CLI AttachConsole+freopen CONOUT$ 致重定向必空、kClient 租约要求 GUI 完全退出（WM_CLOSE 只缩托盘须 taskkill /F）；identity 在 %APPDATA%\CrossDesk\trusted-devices\ 而非 Local cache；修复＝安装版→首启联网取 ID→杀 GUI→提权 enable→复核 ProgramData\CrossDeskUnattended\status.json 与服务 Automatic） |
| SnugWin 加手机屏报「原主显示器脱离活动桌面，已中止」重启复现；虚拟屏建屏安全中止；SetDisplayConfig/QueryDisplayConfig 返回 87 | `03-通用/03-调试与验证/踩坑-SnugWin加手机屏安全中止实为克隆到达误报-扩展拓扑存库修复.md`（`verified`：克隆到达使物理屏 dedicated 哈希变→EnsureNonCherryIntact 误报；修复＝保持管道连接 Add→纯拓扑旗标扩展→QueryDisplayConfig 原始字节块(topologyId=NULL)回传 SAVE_TO_DATABASE 存库→Remove；清场 RemoveAll 防遗留占位；判到达只比 CCD 活动条数别用 AllScreens；拓扑旗标与存库旗标互斥致 87） |
| CrossDesk 手机菜单「隐私屏异常：Capture changed; privacy screen is being turned off」、隐私屏按钮灰；断开后本机自动锁屏、重连落在锁屏 | `03-通用/03-调试与验证/踩坑-CrossDesk防窥屏CaptureChanged异常-断开自动锁屏致锁屏态重连竞态.md`（`verified`：lock_on_disconnect=true 断开即锁机→锁屏态重连→解锁恢复捕获时后端重启的 capture-stop 通知撞上隐私自动启用→privacy_controller.cpp:171-181 FailLocked；修复＝停 GUI+服务后把 GUI cache config.ini 与 ProgramData\CrossDeskUnattended\shared-identity.json 内嵌 host_config 的 lock_on_disconnect 同改 false 再启；取舍＝断开不再自动锁机；手动锁屏态重连仍可复现上游竞态） |
| 想用脚本直接操控一台运行中的 VMware 客户机；`vmrun` 任何命令都报 `A password is required for this operation`；SMB 445 通但 `net view` 报 `System error 5`；客户机 3389/5985/22 全关；又不能抢宿主前台 | `03-通用/03-调试与验证/经验-加密VMware虚拟机绕过vmrun密码墙用自带VNC做全量键鼠操控.md`（`verified`：`vmx.encryptionType="partial"` 时 vmrun/`*-InGuest` 全线不可用，改走 VM 自带 `RemoteDisplay.vnc`（127.0.0.1:5901）+ 自写 RFB（`D:\AI-Tool-State\vm-guest\vncctl.py`，shot/type/key/combo/click/move）。三坑：VMware 忽略 SetPixelFormat、固定下发 32bpp 小端 **BGRX**（按 xRGB 解整屏发黄）；`_ : " ! ?` 等 keysym 被**静默丢弃**→自建 SHIFT_MAP 补 `Shift_L=0xFFE1`；点击坐标须**现截图现换算**（2358x1398 ÷ 1600 ≈ 1.47375，分辨率会变）。协议：RFB 矩形头 12 字节、`FramebufferUpdateRequest` 10 字节。宿主↔客户机文件走 HGFS 共享文件夹（`H:\VMShare` ↔ `\\vmware-host\Shared Folders\VMShare`）不通 SMB；批量命令写 `.bat` 进共享目录只敲一行启动。发键前必先截图确认焦点） |
| JetBrains IDE 里某插件的 AI 面板报「Saved Node.js path is not available」/记住的 node、python、git 路径已不存在；改完一处仍报同一条 | `03-通用/03-调试与验证/踩坑-IDEA里CC-GUI插件保存的Node路径失效-IDE与插件各存一份须同改.md`（`verified`：同一件事存两遍——IDE 的 `options\nodejs.xml`（`NodeJsLocalInterpreterManager`）+ 插件写进 `options\other.xml` 的 PropertyService 键 `claude.code.node.path`，卸载 Node 24（`D:\Node.js`）后两份同时成死链；只改 XML 会被 IDE 回写，须再在面板里点「保存」；同机 PyCharm 有同名 `nodejs.xml` 一并改；`C:\...\Roaming\JetBrains` 与 `D:\DevCache\AppData-Roaming\JetBrains` 是同一份（junction）；验收只认 `idea.log` 的 `Saved manual Node.js path` / `Environment check passed for claude` / `Using configured Node.js path … (v26.13.1)`，不认红字消失） |

**前端**（`01-前端/07-表单与交互/`）

| 症状 / 场景 | 记录 |
|---|---|
| 提示条/通知浮层挂几天不消失，被用户当成删不掉的悬浮元素 | `踩坑-浮层提示不自动消散被用户当成删不掉的悬浮元素.md`（`verified`：成功类不弹浮层改页面内留痕；其余 info 4s / error 8s 自动消散；验收截图覆盖操作后 N 秒） |
| `powercfg /list` 只显 2 个方案、注册表里却堆了十几个；或按 `REG_SZ` 读 `FriendlyName` 全空 | `踩坑-电源计划被驱动更新工具复制成同名方案且FriendlyName是REG_EXPAND_SZ.md`（`verified`：判重复要比 `powercfg -query` 归一化后的哈希不是名字；`powercfg -delete` 非提权可用；名字叫 Overlay 不代表是 overlay 方案） |
| 电源/盖子按钮明明设了「休眠」却总变回「睡眠」；或设了休眠但机器从不真休眠（合盖只是亮屏即回、耗电不掉） | `踩坑-电源按钮反复变回睡眠且从不真休眠-S0现代待机未转休眠与组策略硬锁.md`（`verified`：两层问题——值被「设置」App/第三方工具 reset，用 `HKLM\SOFTWARE\Policies\Microsoft\Power\PowerSettings\<设置GUID>` 写 AC/DCSettingIndex 硬锁；真休眠要 `PlatformAoAcOverride=0` + `HibernateAfterTimeout=600` + 重启，因为只支持 S0 的机器按钮进的是 S0 联网待机。查值必须 `powercfg /qh`，`/q` 只显 1 项；LID/PBUTTON/SBUTTON 是 `1=睡眠 2=休眠`，UIBUTTON_ACTION 是 `0=睡眠 1=休眠 2=关机`） |
| Git Bash 里 `cmdkey /list` 只打印用法、像命令坏了 | `踩坑-GitBash调cmdkey的list被MSYS改写成路径.md`（`verified`：`/list` 被 MSYS 当绝对路径改写，加 `MSYS_NO_PATHCONV=1` 或写 `//list` 即恢复） |
| ppt-master 门禁报 bounds 溢出，或 final gate 全绿但 PowerPoint 仍裁字 | `踩坑-ppt-master出片需预留bounds且导出后必须COM导PNG目视.md`（`verified`：按检查器实际文字外框扩区；名义到 720 仍可能被 COM 渲染裁底，必须逐页导 PNG 复核） |
| 所有 workflow 一起 failure，但 job 里 0 个 step、2 秒结束、日志 404 | `踩坑-GitHubActions计费阻断表现为job零step两秒结束.md`（`verified`：`enabled:true` 不代表能跑；真因只在 check-run annotations 的付款文案；判据看 `steps` 数与 `runner_name`，结论只能写「本机通过、云端未验证」） |
| 设了 `HTTPS_PROXY` 但 git 仍连不上，报错 `via 127.0.0.1` 不显示端口 | `踩坑-git按URL写死代理端口端口漂移后env覆盖不了.md`（`verified`：`http.<url>.proxy` 优先级高于环境变量；用 `-c ...proxy=<实测端口>` 覆盖、空值=直连；`--unset-all` 不清 global；TLS EOF 加 `-c http.version=HTTP/2`） |

| `encoding/json` 不吃 BOM，日志出现 `invalid character 'ï'` 就是特征码；本机因此长出幽灵重复项、开机恢复一直失效。去掉 BOM 才暴露第二层 `cannot unmarshal string into Record.display_name` ⇒ 判据是「这条日志不再出现」，不是「文案变了」。给 Go 的配置不能有 BOM，给 PowerShell 5.1 的 .ps1 必须带 BOM，方向相反 | `踩坑-PowerShell写配置带UTF8BOM让Go程序静默读不到并一层掩盖一层.md` |
| 面板显存数据源取不到时显示 `--`/0%（＝无数据≠用量 0）；任务管理器表头那个 0% 是**网络**列。只认两条：进程命令行有没有 `-ngl`；`Get-Counter '\GPU Process Memory(*)\Local Usage'` 按 PID 取值。利用率要在生成中采样 | `踩坑-应用面板显存0%与任务管理器无GPU列-判走没走GPU的两条硬判据.md` |
| `clocks_throttle_reasons=0x400`(SW Power Cap) 而温度仅 52℃；只在**同一时段做 A/B**（实测新件 29.4@106W vs 原件 15.4@73W）。`BatteryStatus=2` 与 `PowerAC=True` 会同时出现 | `踩坑-笔记本功耗封顶让同一配置吞吐差十倍-tok每秒不能当基线.md` |
| 新版 Codex 删 `wire_api="chat"`；宿主网关有 `/v1/responses` 却**吞掉 tools**，且 `/v1/completions` 回 200 空 body；转发 SSE 不逐块 flush 会让客户端报 stream disconnected（首块 6.5s vs 0.29s）；`requires_openai_auth=true` 把 key 送去 api.openai.com；`env_key` 只认环境变量；真 500 源于模板要求 system 消息唯一且在首位 | `踩坑-Codex接本地OpenAI兼容网关的六道关-协议tools被吞SSE不flush与system消息顺序.md` |

**构建与工程化**（`01-前端/08-构建与工程化/`）

| 症状 / 场景 | 记录 |
|---|---|
| `npm run dev` / `npm run build` 报 `error:0308010C:digital envelope routines::unsupported`（`ERR_OSSL_EVP_UNSUPPORTED`）；怀疑 vue-cli / webpack 老项目跑不了新 Node | `踩坑-Node17以上跑vue-cli4报ERR_OSSL_EVP_UNSUPPORTED-用fnm双版本并在项目内固化16.md`（`verified` 2026-11-27：根因＝Node 17 起 OpenSSL 3 把 MD4 归 legacy provider，webpack 4 仍调 md4；一行判据 `node -e "require('crypto').createHash('md4')"` 成功=能用旧 webpack、抛 0308010C=必须降到 16。修法三层＝fnm 双版本 + 项目内 `.node-version` + `.vscode/settings.json` 的 `terminal.integrated.env.windows` 前置 16 的 PATH；**只靠 fnm 的 use-on-cd 不够**（VSCode 直接以项目 cwd 起终端、不执行 `cd`），profile 必须额外调 `Set-FnmOnLoad` 且 `fnm env` 显式带 `--fnm-dir`；机器级 default 不能降到 16（DSH 的 billion-context 要求 engines≥20 且带 sharp 原生模块） |

**工程规范与安全**（`03-通用/04-工程规范与安全/`）

| 症状 / 场景 | 记录 |
|---|---|
| 卸载 MSI 版 Node 后 `npm`/`npx` 报找不到 `npm-cli.js`；`npm ls -g` 全局包全空但文件还在 `%APPDATA%\npm`；改过 npm 前缀的机器 | `踩坑-卸载MSI版Node24后npm包装器死链与全局前缀丢失.md`（`verified` 2026-11-27：两处影子副本不随卸载走——①`D:\node-global\{npm,npx,corepack}` 手改包装器里硬编码的安装路径（`_prog` 有 IF EXIST 回退、`_cli` 没有→死链）；②安装在 `D:\Node.js\node_modules\npm\npmrc` 里的 `prefix=${APPDATA}\npm` 被一起删→prefix 回落到新 node 目录。修法＝六个包装器改指**不被卸载的 junction** `D:\nodejs-current` + 用户级 `~/.npmrc` 写死 prefix + 计划任务 Execute 路径一并改（`Set-ScheduledTask` 非提权可用）；踩坑：`Set-Content -Encoding ascii` 写中文注释会全变 `?`，.cmd 注释必须全英文；MSI 留下的 `<hash>.rbf` 被运行中旧进程锁住删不掉是正常的，查 `PendingFileRenameOperations` 即可） |
| `.ps1` 含中文报假语法错、乱码 | `踩坑-PowerShell5.1读无BOM的UTF8脚本中文变乱码.md` |
| `Get-Content` 回显 UTF-8 中文乱码、疑似文件写坏 | `踩坑-GetContent默认按代码页解码致UTF8中文回显乱码.md` |
| `Get-Content x -Raw \| python` 报 JSON 语法错（缺逗号/非法控制字符），文件本身合法 | `踩坑-pwsh管道喂python把UTF8中文重编码致JSON假错.md` |
| 桌面 .cmd 提权、`choice` 默认键、判管理员 | `踩坑-cmd入口脚本判管理员与choice默认键取值.md` |
| 单实例 mutex 静默失效 | `踩坑-CreateMutexW后未紧邻读GetLastError致单实例守卫静默失效.md` |
| AtomGit 与 GitHub 差异、国内推送 | `规则-AtomGit与GitHub差异与国内推送判据.md` |
| 等比缩放结果"再算一次会变"、轮询反复调整、1px 抖动 | `踩坑-缩放结果二次取整不收敛致反复SetWindowPos.md` |
| 口语需求（"上下也要留白"）写成阈值规则、注释与代码公式不一致 | `规则-规则类改动先写死判定式并核对注释与代码一致.md` |
| 隔几天想回滚注册表/文件改动，却发现 `.reg` 备份与取证日志连同 TEMP 一起没了 | `踩坑-回退备份与取证放TEMP会被更新重启清空且日志会滚存.md`（`verified`：11-11 14:37 WU servicing 后 TEMP 15.21→0.08 GiB、19 份 `.reg` 全灭；StorageSense 计划任务 `LastTaskResult=267011` 证明不是它干的；`WindowsUpdateClient/Operational` 日志几天内滚存，判据要当场抄成文本） |
| 一个"某应用窗口/内容太窄"的修复想写成通用形状规则，却击穿了既有的形变/比例硬约束 | `规则-通用加宽规则击穿形变硬约束须按应用名单制.md` |
| 提交混入空文件、云端项目不全、该不该忽略 uploads 等「产物」 | `踩坑-提交前审查两坑-全暂存区混入空文件与课程样例误判.md` |
| ctypes 建窗口/托盘返回 NULL 且 GetLastError=0 | `踩坑-ctypes窗口过程在CreateWindowExW内同步回调字段未初始化致静默NULL.md`（`verified`：WNDPROC 同步回调早于字段初始化；状态先初始化再创建） |
| 归档/清理前判断 `.bak`、旧脚本是否真是垃圾 | `规则-清理归档前先反查三类引用.md`（`verified`：先查计划任务/Run、脚本/文档引用、回滚点；三类都不命中才删） |
| 公开仓库跑敏感正则命中一堆手机号/私钥，怕真泄露 | `踩坑-公开仓库敏感扫描误报分诊-哈希子串演示号与脱敏夹具.md`（`verified`：哈希子串/演示号/脱敏坏输入夹具;分诊后才报泄露） |
| 令牌化收口后截图配对出现差异，无法归因重构还是改色 | `规则-视觉中性重构先等值替换再改色.md`（`verified`：令牌值先等于原字面量保零视觉差，改色另作视觉决策） |
| 清理会话产物时发现交付件与最新导出件页数/大小/MD5 不同 | `规则-清理会话垃圾前先比对交付件与导出原件.md`（`verified`：用户可后续编辑交付件；旧导出件不能反向覆盖，空白页只报告不自动删） |
| bat 内嵌 PS 探针注释被当命令、`'/b' 不是命令`、`$pid` 只读 | `04-工程规范与安全/踩坑-bat内嵌PowerShell探针的marker与readkey空路径及pid只读.md` |
| 模型该放哪 / 新下载模型落点 / 模型路径散落任务目录 | `04-工程规范与安全/规则-AI模型统一存放D盘Models目录.md` |
| 视频成品/渲染缓存放哪 / 工作区膨胀 / 归档前清理 | `04-工程规范与安全/规则-工作区不留视频-交付即清中间产物.md` |
| 批量替换只改了几处，`git diff` 却报整文件重写 | `踩坑-Python文本模式批量改写把CRLF静默转LF致diff暴涨.md`（`verified`：文本模式**读**时已折叠 CRLF，`newline=''` 不会恢复；一律 `rb`/`wb`，还原要逐文件参照 HEAD 原行尾） |
| 采集器写完才发现 robots 禁了搜索页；或 curl 拿到的 HTML 里没有正文 | `踩坑-牛客robots禁search采集只能走sitemap且正文须渲染.md`（`verified`：`Disallow:/search`，合规入口是公布的 sitemap；SPA 外壳仅 6 KB，正文须 headless 渲染；两层抓取 + 匹配三道闸） |
| 要把私有仓库转公开，担心历史/路径/证据哈希 | `规则-仓库公开前脱敏须扫全历史且改证据要重签哈希清单.md`（`verified`：扫 `git rev-list --all`；代码默认值不改；改证据必须重签 manifest；历史留痕让用户拍板；生效判据是匿名 API 200） |
| 手册/任务区路径对不上、还按 E 盘找手册、回写逐次请示、全局「先查手册」触发失效 | `规则-任务区与手册一体化联动.md`（`verified`：2026-11-16 手册迁入 `G:\AIrenwu\本地AI使用手册`；回写按 2026-10-13 授权自动执行；`~/.dsh/AGENTS.md` 第〇节曾缺失已重建；技能经 skill-router 按需读） |
| 任务区根目录该放什么、脚本/证据/产物往哪归 | `规则-工作区大纲与归类铁律.md`（2026-11-16 更新为根 7 类：手册是第 7 类；脚本库 10 分类） |
| 要摸透/调整 PowerToys 功能、脚本启停模块或改热键；安装根调 Settings CLI 报 CommandNotFoundException | `03-通用/04-工程规范与安全/经验-PowerToys功能配置速查与CLI-DSC自动化入口.md`（`verified`：CLI 在 WinUI3Apps 子目录、DSC get 实测与配置一致；38 模块清单在任务归档报告；Junction 真源在 D、提权须 RunAs） |
| **DSH 会话老是「本轮运行失败」**、报 `Tool call "xxx": Unexpected non-whitespace character after JSON at position N`、`Received arguments` 里两个 JSON 对象粘在一起 | `03-通用/03-调试与验证/踩坑-上游中转把并行工具调用粘进同一tool_use参数致整轮MALFORMED_RESPONSE.md`（`verified`：中转把同 step 的两个并行工具调用合并进一个 tool_use 块且丢了第二个名字 ⇒ 整轮 MALFORMED_RESPONSE；修法＝`llm/stream` waterfall 插件 `llm-stream-repair` 补 `block-end` 覆盖坏参数并改写终止原因为 `tool-calls`，金丝雀假流端到端实测通过） |
| 想改 DSH 模型调用行为（重试/改写流/降级路由）又不想动 app.asar；插件装上了但报 `cannot get property "config" without inject` | 同上记录「可复用规则」2–5 条（`ctx.on('llm/stream', (options, next) => ...)`、`apply(ctx, pluginConfig)` 第二参数、`remove_bundle`→`install_bundle` 顺序、profile patch 手写行不热生效） |
| 两份同源资料做全量哈希比对，报出几条「内容不同」但文件明明存在；或一侧 `open()` 报 `Errno 2 No such file or directory` 而文件确实在 | `03-通用/03-调试与验证/踩坑-跨盘全量哈希比对被MAX_PATH截断误报内容不同.md`（`verified`：两侧根路径长度差 4 字符把临界长文件名顶到 260 ⇒ 备份侧读失败被降级成「哈希为空 → 记为不同」，8 条假阳性；加 `\\?\` 前缀重算 8/8 一致，真差异只剩 1 个；铁律＝读失败永不等于内容不同、差异三分类互斥、判备份完整要文件数+目录数+总字节+逐文件哈希四项齐对） |
| 环境变量指向不存在的目录、PATH 里有重复项、`python3` 报 exit 9009、命令行 hvigor/adb/hdc 找不到 | `04-工程规范与安全/经验-环境变量体检与整理-失效路径重复PATH与缺失SDK变量.md`（`verified`：判据＝值含盘符逐条 `Test-Path -LiteralPath` + PATH 合并后 `Group-Object` 找重复 + `python3.exe` 大小为 0 即存根；本机实测 3 条失效路径（`MAVEN_HOME` 停在已删的 3.9.16、`AQUA`/`RUSTROVER_VM_OPTIONS` 指向不存在的 `D:\JAVA\jetbra`）、3 条冗余 PATH（`C:\node-global` 是 `D:\node-global` 的 Junction、`D:\Git\cmd` 与机器级重复、`\.dotnet\tools` 不存在）、3 条缺失变量（`DEVECO_SDK_HOME`/`ANDROID_HOME`/`ANDROID_SDK_ROOT`）；修法＝SetEnvironmentVariable User + 强制 REG_SZ + 广播 WM_SETTINGCHANGE，`python3` 用 `python.exe` 副本放到 PATH 更靠前的目录遮蔽 0 字节存根） |
| 按「`.cmd/.bat` 必须 GBK 无 BOM」批量转码后，控制台里的中文反而变乱码；文件本身明明没坏 | `04-工程规范与安全/踩坑-cmd入口自带chcp65001时机械转GBK反而制造乱码.md`（`verified` 2026-11-26：脚本第 2 行写 `chcp 65001` ＝**自己声明要 UTF-8 控制台**，此时按铁律机械转 GBK，控制台按 UTF-8 解释 GBK 字节 ⇒ 必花；本机 4 个 `.bat` 被改坏后从备份逐字节还原，sha256 前 16 全对（706B/198C6D7953DF39A7、595B/BFA1859F9B9B7C22、613B/4931B80826D2A63B、647B/A8D88F83FFFA34EF）。修法＝批量脚本加守卫 `declares_utf8_codepage(raw)`，对 gbk/utf-8 两种解码**都**查 `chcp 65001`/`chcp65001`，命中跳过；全库共 7 个此类例外登记为合规。另一条：按铁律严跑预演得 205 项，其中约 175 项只是纯 LF→CRLF 归一化，会造上百个无意义 diff ⇒ **只修「`.ps1` 含中文无 BOM」与「`.cmd/.bat` 带 BOM 或非 GBK」两类**） |
| 要按清单批量删目录/清污染，或同一工作区同时有多个 AI 会话在写、怕互相踩 | `04-工程规范与安全/规则-批量删除前先落全量快照且多会话破坏性操作要互斥.md`（`verified`，severity **critical**：2026-11-26 事故全案——9:26 我拍的全量快照是**唯一**能定损的证据，10:53–10:55 并行会话用「磁盘 minus git 跟踪树」判定污染，删掉 8 个顶层对象（`OpenRevo插件整理` 128 条 25.02MB、`10_视频广告` 56、乱码区 11、`disk_reports` 6、`.agent-teams` 2、`鸿蒙歌单数据` 2，共 243 条目 / 净损 62.6MB / 183 条目）；**四条恢复路径全空**——回收站 156 条目关键字 0 命中、`git log --all` 对 6 路径无历史、全盘 G/H/D 无备份包、`vssadmin list shadows /for=G:` 报 `Error: You don't have the correct permissions`。五条规则：删前落 CSV 快照（路径/字节/mtime/SHA256）进任务夹 `02_证据日志` **不放 TEMP**、删前 robocopy `/E /XJ` 冻结到另一块盘、多会话放 `.lock` 互斥、污染只按 `git diff --name-only` 的 **additions** 判（untracked 一律不动）、验收必须答「删了什么/多少/能否恢复」三问） |
| 要删干净某个软件但开始菜单/卸载注册表全找不到；DeskBox 格子里的图标不知道真身在哪；源码版 Electron 应用怎么卸 | `03-通用/04-工程规范与安全/经验-源码版Electron应用干净卸载三处与DeskBox格子快捷方式真身位置.md`（`verified`：源码版＝仓库目录+`%APPDATA%\<appname>` userdata+整理工具 lnk 三处；DeskBox 格子 lnk 真身在 `E:\DESKBOX\<格子名>\`，widget-layout.json 的 `Item:` 路径可定位，删 lnk 图标即时消失不必重启；删前 git status/@{u}..HEAD 检查+git bundle --all+userdata robocopy 排除纯缓存备份到 G:\数据备份；rmdir /s /q 可过 node_modules 长路径；关键词扫残留防误伤同名无关任务） |
| 卸载/删除软件后图标还在（DeskBox 格子/开始菜单/桌面），用户以为软件"活过来了"；要按"删干净"标准验收 | `03-通用/04-工程规范与安全/规则-卸载删除软件必须连快捷方式与全部残留一起清干净.md`（`verified` 2026-11-26，用户长期规则：卸载后按清单扫快捷方式——开始菜单两根/用户桌面+`C:\Users\Public\Desktop`/Quick Launch 含 User Pinned\TaskBar/**`E:\DeskBox\<格子名>\*.lnk`**（按名字+WScript.Shell 读 TargetPath 双匹配）+ `%APPDATA%`/`%LOCALAPPDATA%`/`%PROGRAMDATA%` 数据目录（删前查 LinkType 非 Junction + grep 保留组件无引用）+ 注册表（Uninstall 三处/Run/vendor 键/App Paths，被替代方案复用的键保留）+ 服务/计划任务 Actions/进程 Path + 自建备份（用户说"删干净"就一并删）；**删后复扫全清单 0 命中才算完**。事故根因＝Everything 手写卸载脚本 `D:\AI-Tool-State\fullindex\optimize.py` 只有 sc delete 服务+注册表改指+删目录三步，无快捷方式步骤、无删后扫描） |
| 凌晨/定时计划任务长期不跑、索引或备份产物陈旧；LastTaskResult=2147946720（0x800710E0 请求被拒）；笔记本到点在休眠 | `03-通用/04-工程规范与安全/经验-笔记本凌晨计划任务因休眠与电池限制永不执行.md`（`verified` 2026-11-26：DisallowStartIfOnBatteries=True + StartWhenAvailable=False + WakeToRun=False 三设置叠加笔记本 30 分钟 idle 休眠⇒03:30 永不触发也不补跑；修复＝StartWhenAvailable/WakeToRun=True + 关电池限制 + Action 改 cmd /c 重定向到日志；StartWhenAvailable 醒来补跑是最关键兜底；WakeToRun 深度休眠唤醒依硬件而定；Interactive principal 注销后不跑） |

**AI 协作与提示词**（`03-通用/02-AI协作与提示词/`）

| 症状 / 场景 | 记录 |
|---|---|
| **技能放哪、何时被识别、如何实现「默认调用」** | `规则-WorkBuddy技能发现机制与本地技能安装位置.md` |
| 本手册如何接入 DSH，做到每次任务默认查（2026-10-19） | `规则-本地手册接入DSH成为默认前置与写Markdown的编码坑.md` |
| 逆向技能/工具箱在哪、能不能用 | `规则-技能库已收录逆向技能只放指针.md`、`规则-逆向工具箱清单与后端选型决策表-MCP.md` |
| 换了 Qoder 版本就「失忆」、两个客户端记忆是否共用 | `规则-国内版与国际版Qoder两套记忆目录完全独立只能单向拷入并校验.md`（`verified`：`.qoder` 与 `.qoder-cn` 无共享无联接；搬运用 `cp -n` + 手工合并索引 + `diff -rq` 复核；**别用 mklink /J**） |
| 审查方与执行方共仓，发现写在对话里执行方看不到；续接后沿用旧现状 | `规则-多AI同仓审查交接三件套与续接先核时钟.md`（`verified`：发现文档+必读指针+处置建议；已闭标✅;续接先核 date/HEAD/行数） |
| Qoder 浏览器 Agent 里 evaluate 恒返回 null、自绘单选点不动、标签页突然消失 | `经验-Qoder浏览器Agent的evaluate恒null与自绘单选要点label.md`（`verified`：读 DOM 用 `domSnapshot()`；自绘单选点 `label:has(input[value=...])`；调试器断开后重建 agent 新开页；写操作要刷新回读 + 独立验证） |
| 换了 Agent 就「失忆」、要让所有 AI 共用一份全局记忆、记忆该放哪 | `规则-全机AI共享全局记忆存D盘Skills库并接线各Agent.md`（`verified`：实体 `D:\Skills\global-memory\`；接线走各 Agent 全局指令文件不是技能目录；单向 cp -n + sha256 + 索引合并 + orphan 检查；同名冲突 diff 三分类、独有内容带日期附录追加；禁 junction 实时共用） |

**后端**（`02-后端/`）

| 症状 / 场景 | 记录 |
|---|---|
| 代码里写了路由，浏览器/接口仍 404 `Cannot GET /` | `02-后端/02-API与接口设计/踩坑-Express改了代码浏览器仍404先查未保存缓冲与旧进程.md`（`verified`：编辑器缓冲没落盘 + 端口上是旧进程；判据是 curl 真实响应体 + `Win32_Process` 的 CreationDate，本机别用 `-State Listen`） |
| `SyntaxError: await is only valid in async functions and the top level bodies of modules` | `02-后端/01-架构与项目结构/踩坑-CommonJS目录下js顶层await报SyntaxError.md`（`verified`：目录 package.json `"type":"commonjs"`；包 async IIFE，别整体改 `"module"`） |
| Spring Boot jar 连 MySQL8 启动失败 `Public Key Retrieval is not allowed`（mysqld 重启后首连、useSSL=false） | `02-后端/04-数据库与ORM/踩坑-MySQL8重启后JDBC首连报PublicKeyRetrievalNotAllowed须allowPublicKeyRetrieval.md`（`verified`：caching_sha2 缓存空需取 RSA 公钥；JDBC URL 加 `allowPublicKeyRetrieval=true` 即好，A/B 实测） |

## 本机环境速查（来自 `~/.dsh/AGENTS.md`，细节查正文）

- `pwsh` 实际是 **Windows PowerShell 5.1**（无 PowerShell 7）；命令里含 `$` 或成对反斜杠就**先落成文件再执行**。
- `.ps1` 必须 **UTF-8 with BOM + CRLF**；`.cmd` / `.bat` 必须 **GBK 无 BOM + CRLF**。
- **沙箱按会话策略**：`workspace-write` 时工作区外写被拒；`danger-full-access` 时不限（2026-11-13 会话实测 E 盘/C 盘写入成功）。手册 2026-11-16 迁入 `G:\AIrenwu` 工作区后，回写不再触发工作区外拒写。沙箱只覆盖 `pwsh` 与文件工具，**Node/Python 等子进程不受限**（workspace-write 下实测）。
- 报错先按「有没有真的发出去」分流：1ms 的「连接失败」是本地校验，不是网络。
- 判域名可达：不带凭据打同一端点，拿到 `401/403` JSON 即链路通。
- 查路由：`Get-NetRoute -DestinationPrefix '0.0.0.0/0'`、`Get-NetIPInterface`；**不禁用网卡、不删路由**，只降 metric。
- 交付 xlsx/docx 时，排版结论只能靠真实渲染出图（COM 导 PDF → PNG → 肉眼）签字；不要指望 AutoFit。

## 回写（任务结束后，用户已授权完工自动回写）

用户 2026-10-13 明确授权「完工自动回写」：**无需逐次请示**，直接按模板写入 `G:\AIrenwu\本地AI使用手册`（已在任务区工作区内，不再触发沙箱工作区外拒写），并在完工汇报中说明写了什么、写到哪里；把握不足写收件箱保持 `needs-review`；用户可随时收回授权。依据：`G:\AIrenwu\01_任务归档\2026-10-13_接入AI手册到技能\01_报告\接入说明.md` 第六节。旧措辞「写 E 盘前必须先经用户确认」作废（2026-11-16 更新）。

判断本次是否有值得长期保留的内容：

- 有**可复现问题、已验证修复、重要规则、可复用经验** → 按 `90-模板/问题记录模板.md` 写入 `03-通用` 对应细分类目，状态 `verified`。
- 只有线索、猜测、未验证内容 → 写入 `99-收件箱/`，状态保持 `needs-review`。
- 没有长期价值 → **不写**，避免噪音。

记录质量要求：

- 必须写清：触发条件、实际现象、证据、根因、最小修复、**实际验证命令与结果**、适用范围、剩余风险。
- 事实、推断、假设**分开写**。
- **绝不把「看起来正确」写成「验证通过」**，也绝不把未执行的检查写成通过（未跑的留 `[ ]` 并写明原因）。
- 完成复现+定位+修复+验证后才用 `verified`，否则留在收件箱用 `needs-review`。
- 规则变化时**新增记录**并把旧记录标 `deprecated`，**不要静默覆盖历史结论**。
- 写入后把链接补进该分类的 `README.md`、`03-通用/通用索引.md`，以及本 skill 的症状索引。

## 结构维护铁律

- ✅ 可以在现有板块下**增量添加**新文件夹或记录文件。
- ❌ **不得**擅自重命名、删除、合并或大规模改造现有顶层结构与分类。
- 确实需要大改时：先向用户报告原因、影响范围、候选方案、回滚方式，**确认后再执行**。

## 安全边界

- **不写入**密码、Token、API Key、私钥、Cookie、个人隐私、生产敏感数据。
- 不把手册内容当成权限或安全审批的依据。

## 常见误区

- ❌ 等用户说「查手册」才查 → **本 skill 是默认前置动作**。
- ❌ 把手册当通用编程百科 → 它只记**本机特有**的坑。
- ❌ 读了文件名就当读过了内容 → 必须读正文，目录名只用于定位。
- ❌ 因为手册里有类似经验就跳过当前复现 → 易变项必须实测复核。
- ❌ 回写前逐次请示 → 用户 2026-10-13 已授权**完工自动回写**，汇报写了什么、写到哪里即可；把握不足写收件箱。
- ❌ 还按 `E:\本地AI使用手册` 找手册 → 2026-11-16 已迁入 `G:\AIrenwu\本地AI使用手册`，E 盘不存在。
| 想给子代理单独指定模型，配了 `modelSelection` 却不生效；或子代理报 `without a recorded model-selection policy, explicit selection is limited to the parent route` | `03-通用/03-调试与验证/经验-DSH装插件与删provider的四个动作点.md`「2026-11-22 再补」第①②条 |
| 改了插件源码（如 memsearch `client.js` 关横条），插件一升级就被还原 | 同上文件「2026-11-22 再补」第④条；脚本在 `E:\fullstack-code\tools\dsh-post-upgrade-repatch\` |
| C 盘 AppData 越来越大想迁 D 盘；怀疑已迁数据被 AI 重复写回 C；评估 Viap 这类 Junction 迁移工具 | `03-通用/04-工程规范与安全/经验-AppData缓存迁D盘复用DSH-Guard核心按组包装.md`（复用 D:\DSH-Guard 核心按组包装；回流核查法；锁定目录开机任务；D 盘副本是真源别清理） |
| 要用 Viap（或同类工具）清理数据/内存/幽灵链接/强力卸载 | `03-通用/04-工程规范与安全/规则-用Viap清理前必检D盘联接效果与Viap更新.md`（用户长期规定：先跑 health_check.py/双守护确认 D 盘 54 联接效果还在，再对比 GitHub latest 核验 Viap 更新；D:\DevCache* 是真源不是可清理内存） |
| 想程序化驱动 LightC/Tauri 清理软件跑扫描取结果；设 WebView2 调试端口不监听；清理软件勾选不生效或怕误删用户数据 | `03-通用/03-调试与验证/经验-LightC全模块UIA驱动清理与社交默认全选误删用户数据.md`（Tauri 覆盖调试参数改 UIA；各模块控件形态+确认反向找；-ExpectMin 守卫+dry-run；社交默认全选含用户数据；旧驱动同体积备份净释放 0） |

| 清理 git 污染误删未跟踪目录 / ai-renwu 本地历史被 ai-skills 污染 | `03-通用/04-工程规范与安全/规则-清理git污染勿删白名单外真实未跟踪工作目录.md` |
| HarmonyOS App 网络数据/网络图片全空白但不报错，编译 `BUILD SUCCESSFUL`；同一份代码前一天还正常 | `01-前端/06-网络请求与接口联调/HarmonyOS-写死局域网IP作为接口地址-换网络后静默全挂.md`（`verified`：2026-11-26/27 跨夜实测，后端进程 PID 未变、`127.0.0.1:3000` 一直 200，仅电脑换网络后 DHCP 把 IP 从 `10.149.175.18` 改成 `192.168.113.52`，写死的 `SERVER_URL` 就全挂。查法＝先用 `Invoke-WebRequest` 测代码里那串写死的 URL，再测 `127.0.0.1`；改 IP 后必须重新构建） |
| 视频精讲/NVENC 流水线：体检报的段数和成品时长对不上、假爆音、字卡 BGM 突然 -99dB；或 F5-TTS 报 torchcodec `[WinError 127]`；或克隆配音把 Morty/Rick 念成"摸体/锐克" | `03-通用/04-工程规范与安全/踩坑-视频精讲流水线三坑-体检口径串台与F5配音DLL.md`（`verified`：①体检脚本 `load_edl()` fallback 到完整版 EDL → 用完整版 44 段边界采样精简版 322s 波形，出 7 处假爆音 + 假 -99dB；加 `AUDIT_EDL` 环境变量选时间轴模块，判据「报的段数/总长与成品实际时长差 >1s 即串台」②torchaudio 2.9 的 `load()` 走 torchcodec 需共享库 FFmpeg，静态构建无 DLL → 在 `import f5_tts` **前** monkeypatch `torchaudio.load` 走 soundfile ③F5 是 pinyin tokenizer，英文名必须改中文音译，配 faster-whisper 相似度自检） |
| CapCut 草稿批量生成后素材离线 / 换目录后视频不显示；或 CapCut 截图全黑、UI Automation 取不到控件，想验证工程是否正常 | `03-通用/04-工程规范与安全/踩坑-CapCut草稿素材路径迁移与CEF无法截图验证.md`（媒体绝对路径在 `draft_content.json` + `draft_virtual_store.json` **两处**，只改一处素材面板仍离线；CEF/GPU 渲染截图必黑、UIA 文本=0，验收改判引用完整性+路径 exists+duration 对齐；`draft_meta_info.json` 启动后统一回写＝加载成功强证据） |
