---
name: reference-windows-network-path-diagnosis
description: 判「谁在接管流量 / 是不是被限速 / 为什么时好时坏」的分层取证法：WARP 分片路由躲过 0.0.0.0/0、网关 ICMP 丢包是限速假象、单流测速分不清服务器按连接封顶、探针会抢带宽、ProxyEnable 被杀软断网修复清零（直连通代理挂）、本机 -State Listen 对 :: 双栈监听假报空、Resolve-DnsName -Timeout 不存在、WLAN 重连要与唤醒时刻对齐才知是否异常
metadata:
  type: reference
---

本机（Win11 + Clash Verge 7897 + Cloudflare WARP + Radmin VPN + VMware）2026-10-15 实测出的四条判据。

**① 判"谁在接管流量"不能只查 `0.0.0.0/0`。** Cloudflare WARP 在 `Mode: Warp` 下装的是
**分片前缀**（`0.0.0.0/5`、`128.0.0.0/3`、`112.0.0.0/4`、`100.0.0.0/10` …，下一跳 `192.0.2.1`），
`Get-NetRoute -DestinationPrefix '0.0.0.0/0'` 里**完全看不到它**，会误判成"没接管"。正确两条：

```powershell
Get-NetRoute -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -like '*WARP*' } | Select DestinationPrefix,NextHop,RouteMetric
Get-DnsClientServerAddress -AddressFamily IPv4 | Where-Object { $_.ServerAddresses }
```
**DNS 被改成 `127.0.2.2 / 127.0.2.3` 是 WARP 在场最快的信号。** 读当前档位用 `warp-cli settings`
（会打印 `Mode: Warp` / `WARP tunnel protocol: MASQUE`；`warp-cli mode` 是**设置**命令不是查询，缺参数直接 rc=2）。

**② 网关 ICMP 高丢包通常是假象。** 实测 `192.168.0.1` 发 15 包丢 **86%**，而**同一条无线链路**出去的
`1.1.1.1` 是 3 ms / **0% 丢包**、`223.5.5.5` 40 ms / 0% → 链路不可能在丢包，是路由器对 ICMP 限速。
判据：**用同一出口路径上的公网目标做对照组**，对照组 0% 丢包即可否定"链路在丢包"，别去重装驱动。

**③ 单流测速分不清"链路慢"和"服务器按连接限速"。** 必须做并发曲线：同一台服务器 1 / 3 / 6 / 8 条流各测一次。
实测 `mirrors.aliyun.com`：单流 ≈5 Mbps、3 流 15.0、6 流 20.2、8 流 20.2 Mbps → **单流被服务器封顶、多流才叠加**。
所以"下载只有 5 Mbps"不能直接归因给链路或代理。国内站 TCP 建连基线是 **<50 ms**，我量到 `gitcode.com:443` 建连
**249 ms** 才是"流量被拐去绕境外"的铁证（同时 `1.1.1.1:443` 只要 5 ms = 隧道对端就近）。
另：`Disable-NetAdapterPowerManagement` 这类查询可能回 `Windows System Error 31`（设备没实现该类），不代表电源管理没关。

**④ 我自己的测速会污染结论，必须主动交代。** 用户跑着 IDM 大文件下载时我连测多轮，
两边各占一半带宽，报出来的绝对值全都偏低；而且我拿同一个镜像站反复拉了 ~60 MB 后它开始回 0 字节（自我限流）。
⇒ 用户报"慢"时先读 `Get-NetAdapterStatistics` 的 6 秒增量看**总占用**，测速换目标或提醒会抢带宽，
并且**A/B 前第一行必须先打印被测组件自己的状态**（我有一次"关之前"的快照其实已经是关闭态，差点把同一条件测两遍当成对照）。

**顺带结论（本机选型）**：WARP 断开前后同一国内镜像 6.0 → 5.3 Mbps，**WARP 不是吞吐低的瓶颈**；
真正限制是 Realtek **2.5GbE 卡只协商到 100 Mbps 全双工**（错误计数 0，`MediaConnectionState=Disconnected` 后换到 WLAN 1.2 Gbps）
+ 源站按 IP 整形。免费 WARP 出口是 Cloudflare 随机节点、不能选地区，连国内站都绕境外，所以本机选型是
**WARP 不参与日常出境，Clash(7897) 是唯一出境口**（详见手册 `03-通用\03-调试与验证\规则-默认路由抢占网卡已换为RadminVPN.md`）。

Related: [[reference-local-dns-and-link-verdicts]], [[reference-git-push-needs-local-proxy]], [[reference-deskbox-zero-fill]], [[reference-codex-desktop-and-ccswitch]]

**2026-10-19 追加：网卡 DNS 被写死 1.1.1.1 会让"国内站偶发超时"，且判据是冷解析耗时。** 本机 WLAN/以太网2 的 `NameServer` 注册表值被硬设成 `1.1.1.1,8.8.8.8`（PowerShell 显示 `Dhcp=Enabled` 会误导——接口注册表里写了 NameServer 就是手动值，优先于 DHCP 下发）。后果实测：`www.codebuddy.cn` **冷解析 11.15 秒**（第二次起 0.00s 走缓存，所以只在软件启动瞬间发作，极难复现），而且 1.1.1.1 把它解析到 **43.159.104.94（海外节点）**。改成 `223.5.5.5,119.29.29.29` 后冷解析 **0.13s**、解析到 `112.48.148.210`（国内）。**判据**：测域名慢要分层计 DNS / TCP / TLS / 首字节，只有 DNS 那一段是秒级就是解析器问题，别去查服务器或链路；测之前先 `ipconfig /flushdns`，否则第二次起全是缓存命中，会把 11 秒的问题测成 0 秒。回滚原值：`1.1.1.1,8.8.8.8`（`Set-DnsClientServerAddress -InterfaceAlias WLAN -ServerAddresses ("1.1.1.1","8.8.8.8")`，需管理员）。

**2026-11-06 追加：「直连全通、走代理的全挂」= `ProxyEnable` 被清零，且本机 `-State Listen` 会假报端口死。** 火绒「断网修复」把 `HKCU\...\Internet Settings\ProxyEnable` 从 1 改 0，`ProxyServer` 原样留着，7897 其实一直在监听——它的"修复中"面板不能当"没改坏"的证据。修法只有两条：`ProxyEnable=1` + 广播 `WM_SETTINGCHANGE`（不广播则已开着的程序不重读）；`git` 因为按 URL 单配了 `http.https://github.com.proxy` 反而不受影响，别拿它当"代理没问题"的证据。
两个取证陷阱：① 本机 `Get-NetTCPConnection -LocalPort N -State Listen` 对 `LocalAddress=::` 的双栈监听**恒回 0 条**（`State` 值是空字符串），必须去掉 `-State` 过滤看有没有条目 + `OwningProcess`，我上一轮就是据此误报"内核活着却一个端口都没监听"；② `Resolve-DnsName -Timeout` 在本 build 无此参数，3ms 内抛 `NamedParameterNotFound`，长得和"解析超时"一模一样（同一条坑我已踩第二次），限时解析用 `nslookup -timeout=N -retry=1`。
「网络老出问题」的分层归因：把 `WLAN-AutoConfig/Operational` 的 8001/8002/8011 与 `Microsoft-Windows-Power-Troubleshooter` Id=1（唤醒）逐条对时刻——**贴着唤醒的重连是正常形态**（本机 7 天 18 次唤醒、7 天 385 条 WLAN 事件），不贴唤醒而贴着 `System 10002 WLAN 扩展模块已停止` / `NDIS 10400 硬件停止响应` 的才要查，再看它贴着哪个第三方软件的操作时间。本机 MT7922 高级属性 `LowPowerEnable=Auto`、`RoamIndicateTh=5.中高` 与小米 USB 共享上网（`USB\VID_2717&PID_FF88`）重置 10 次，是两条**未动、待用户定**的候选（关节能会增耗电）。详见手册 `03-通用\03-调试与验证\踩坑-杀软断网修复清零系统代理且StateListen过滤假报端口死.md`。

**2026-11-06 追加（同日第二次）：网页「第一次打不开、刷新就好」= 非默认网卡上写死的手动 DNS 被系统当默认服务器。** 本机 Radmin VPN(idx8) 注册表 `NameServer=192.168.0.1,192.168.40.187`，两个地址原始 UDP 探测 2.5s 超时，而 Windows 选路就是先用它 —— **每个未缓存域名先白等 12.0 秒**（Dnscache 重试节奏），已缓存的 5~12ms，所以症状看着是"偶发"。清掉后同一测量 **5~29ms**，经代理 github 从 3.3~5.2s 降到 1.24s。
- **判据两条**：① `nslookup` 不带服务器时打印的 `Address:` 行才是"系统实际在用谁"（`ipconfig`/`Get-DnsClientServerAddress` 只按网卡列各自登记值，看不出优先序）；② 一条对照定层：`Resolve-DnsName X` 12,053ms vs `Resolve-DnsName X -Server 192.168.55.131` **5ms**，唯一差别是指不指定服务器 ⇒ 别再往服务器/链路/防火墙上找。
- **只用 `Set-DnsClientServerAddress -InterfaceIndex N -ResetServerAddresses`；`-ServerAddresses @()` 是静默空操作**（我第一遍就这么"修完"了还以为假设错）。三条边界：默认出口网卡的 DNS 不应答也不碰（清了等于一个都不剩）、DHCP 下发的死地址不碰（本机 以太网2 现在就是，要改路由器）、只清注册表 `Interfaces\<GUID>\NameServer` 里真有手动值的。
- **本机 `netstat` 把 mihomo 的监听报成 `CLOSED`**（与 `-State Listen` 恒回空同源）⇒ 判端口死活唯一可靠的是真 `TcpClient.BeginConnect('127.0.0.1',N)` 连一次；用户的 `fix-network.bat` v2.0 长期因此误报"端口没人监听"，已随 v2.1 改掉。
- 那次「网卡节能优化」**没落地**：powercfg 的 GUID/标签解析没匹配上，脚本自己打了"本次不改"，前后 3.42s / 3.63s 无差异 ⇒ `LowPowerEnable=Auto`、`RoamIndicateTh=5.中高` 仍是未动项，别当已优化。
- 详见手册 `03-通用\03-调试与验证\踩坑-非默认网卡写死的手动DNS被系统当默认服务器致冷解析12秒.md`。

**2026-11-11 追加：Clash Verge「主程序退出、系统代理仍开」= 全网 2 秒失败；机场订阅 TLS EOF 时用 DIRECT 规则保底。** 本机实测链路：
- 现象：所有走系统代理的软件全部失败（每个请求约 2s），但直连中转站 200。查进程只剩 `clash-verge-service.exe`，`clash-verge.exe` 已退出，7897 实连 CLOSED，而注册表 `ProxyEnable=1`。**判据：代理坏先看主程序是否在跑，不要只看服务/端口历史状态**；拉起 `D:\Clash Verge\clash-verge.exe` 后端口与代理链路立即恢复。
- 机场：当前订阅 `app.mitce.net` 直连与走代理都 `tls handshake eof`，所有节点延迟测试失败，`25 provider caches were not synced`。此时在**当前订阅的 merge 文件**（`%APPDATA%\io.github.clash-verge-rev.clash-verge-rev\profiles\<uid>.yaml`）加 `prepend-rules: DOMAIN-SUFFIX,moyucccx.top,DIRECT`（Qoder 中转站）与 `qoder.sh`/`qoder.com`，重启主程序后 `curl -x 7897 https://moyucccx.top/` = 200，节点全挂也不影响 Qoder 模型调用（端到端 200、TTFB 3.2s、model 回显正确）。
- **DoH 在 UDP 被限速的热点上会反向劣化**：给 223.5.5.5/223.6.6.6 配 `autoupgrade=yes udpfallback=yes` 后，冷解析一度 27–32s（DoH 引导也要先解析），撤销模板并 `-ResetServerAddresses` 回 DHCP 后恢复 36–74ms。⇒ 先测 UDP，别把 DoH 当默认优化。
- 该网络是手机热点形态：网关 MAC 本地管理（`ea-ac-ad-db-c3-91`）、网关只开 TCP 53、公网 ICMP/UDP 大量丢而 TCP 正常；同时手机 USB 共享网卡报 NDIS 10400 硬件复位 **94 次**并导致重启。此类链路只能改善热点侧/换有线，本机无解。
- `E:\DeskBox\VPN\fix-network.dns.ps1` 曾缺失（bat 的 DNS 选路与代理广播空转），已按 bat 标签协议补回。PowerShell 5.1 坑：`[byte[]]@(($id -shr 8) -band 0xff, $id -band 0xff, ...)` 会按逗号优先解析成 `Object[] -band` 报错，必须逐字节赋值；`VERDICT/NOTE` 要带 `code=` 前缀（bat 里 `!C:~5!` 会切掉 5 字符）。bat 已升 v2.2（GBK+CRLF 保持），新增中转站直连/走代理两项探测。

**2026-11-11 再追加：「手机能用、电脑不能用」先查 PC 本地 Wi-Fi 扩展与代理内核，别信“节点全挂”。** 实测：同一机场/同一热点，手机正常、PC 全挂；事后同节点在 PC 上走代理 google/github 均 200 ⇒ 节点没问题，之前 Clash 内核测速的 `tls handshake eof` 是本地状态坏掉时的假象。
- PC 侧硬证据：`WLAN-AutoConfig 10002 WLAN 扩展模块已停止`，模块 `C:\WINDOWS\system32\mtkihvx.dll`，`mtkwlex` 1033/8001 → 约 6 秒后 8000/1030 重载；同时 `11004`/`8003` 断开。一天内发生两次（10:05:47、10:47:43），是 Wi-Fi 硬断而非拥塞。查法：`Get-WinEvent System -ProviderName mtkwlex` + `WLAN-AutoConfig` 10002/11004/8003。
- 同时 Clash 服务内核“端口未绑定”→ 主程序退出后系统代理仍开，所有请求打空端口。两层任一层都能造成“PC 全挂、手机正常”。干净重启让 mtkwlex 与内核重新加载后恢复；别把重启后的恢复误记为“机场恢复了”。
- `UmiTun 4`（UmiVPN TUN）在两次 Wi-Fi 断之前 15 秒/更早出现过一次，只能算时间相关；同时开 Clash+Lantern+UmiVPN+WARP 服务会互踩 TUN/路由/DNS/过滤驱动，排障时保持只开一个。
- 订阅更新返回 **403 Forbidden** 是机场拒绝更新请求（token/UA/风控），与断网无关，节点仍可用；不要拿它当网络故障证据。

**2026-11-11 收尾：网络修复收敛为单文件 `E:\DeskBox\VPN\fix-network.bat` v2.3（自动识别 Clash Verge / FlClash）。** 用户已卸载 Clash Verge，改用 **FlClash**（`D:\FlClash`，端口 7890，配置 `%APPDATA%\com.follow\clash`）。
- 探针以 `rem~` 前缀内嵌在 bat 末尾，运行时用 `findstr /b /c:"rem~"` + `delims=~` 释放到 `%TEMP%\fix-network.dns.ps1`；外部 ps1 已删。**别用 `rem#` + `delims=#`**：会把探针第一行注释的 `#` 也当分隔符吃掉，导致 PowerShell 把注释当命令执行。
- 直连规则：Clash 写「当前订阅 merge + 运行配置 + 全局 Merge」；FlClash 写「config.yaml + 当前 profile」。FlClash 的 profile 规则缩进是 4 空格、config.yaml 是 2 空格，插规则要读 `rules:` 下一行的实际缩进，不能写死。`currentProfileId` 在 shared_preferences.json 里是转义引号，正则用 `currentProfileId\D{0,8}(\d+)`；PowerShell 里别用 `$pid` 变量（只读），改名 `$profId`。
- `:readkey` 遇到空路径必须 `if "%~1"=="" exit /b`，否则 `if not exist  exit /b` 会让 cmd 报 `'/b' 不是内部或外部命令`（FlClash 没有 verge.yaml，必然触发两次）。
- 网关 ICMP 只作参考，不参与「是否重取 IP」；代理探测失败重试一次再下结论；系统代理端口与工具端口不一致时要单独警告。
- FlClash 不重启（脚本只写配置），规则要重启 FlClash 或切订阅才生效；脚本会明说。

**2026-11-11 最终（v2.4，FlClash 专用）：不要 kill FlClash。** 实测 `taskkill /F FlClash.exe/FlClashCore.exe` 后重新启动，FlClash 会停在面板“未运行”，**不会自动拉起核心**，7890 不监听；若系统代理还指着 7890 就整机断网。脚本已改成只写规则、绝不结束 FlClash，规则要用户在 FlClash 里点一次停止/启动（或切订阅）才生效。
- FlClash 结构：`D:\FlClash`（FlClash.exe + FlClashCore.exe + FlClashHelperService.exe）；配置 `%APPDATA%\com.follow\clash`（config.yaml、profiles/*.yaml、shared_preferences.json）。端口/意图读 `config.yaml` 的 `mixed-port` 和 prefs 的 `vpnProps.systemProxy`（本机 true）。FlClashCore 是自研 pipe wrapper（`\\.\pipe\FlClashCore_<hash>`），传 `-t/-f` 会 panic，别拿它当 mihomo CLI 测配置。
- **中转站不要再强制 DIRECT**：本机实测 `moyucccx.top` 直连经常 10s 超时、走节点 200；之前的强制直连规则在 FlClash 下会帮倒忙。只给 qoder.sh/qoder.com 加直连，中转站交给 FlClash 自己路由。
- 直连规则要写三处：运行中的 `config.yaml` + **所有** `profiles/*.yaml`，否则切换订阅就丢；规则缩进读 `rules:` 下一行的实际缩进。
- 脚本探针用 `rem~` 前缀 + `findstr /b /c:"rem~"` + `delims=~`；`rem#` 会把注释行的 `#` 当分隔符吃掉，导致 PowerShell 把注释当命令。




