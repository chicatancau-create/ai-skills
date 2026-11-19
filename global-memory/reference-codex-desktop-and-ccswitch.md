---
name: reference-codex-desktop-and-ccswitch
description: Where the OpenAI Codex desktop app keeps config/logs on this box, that its model traffic is routed through the PatewayAI relay via cc-switch, and how to tell a local rejection from a relay-side one.
metadata:
  type: reference
---

本机跑 **OpenAI Codex 桌面端**（进程名 `ChatGPT.exe`，包 `OpenAI.Codex_*`，与 Qoder 并存），
模型流量由 **cc-switch**（`D:\CC Switch`，托盘常驻）切到第三方中转 **PatewayAI `https://api.pateway.ai/v1`**。

取证入口（2026-10-01 实测可用）：
- **配置**: `C:\Users\Admin\.codex\config.toml` —— `model` / `model_reasoning_effort` / `[model_providers.custom]`
  （`experimental_bearer_token` 是**明文**中转站 key，截图/贴日志前先脱敏）。`config.toml.bak.*`、
  `config.toml.provider_backup` 是历史值。
- **谁改的**: cc-switch 把每个服务商的完整 config 文本存在 `C:\Users\Admin\.cc-switch\cc-switch.db`
  表 `providers`(`app_type='codex'`) 的 `settings_config` 里；**切服务商时它整段覆写 config.toml**。
  所以只改 config.toml 不够，界面选完还要回 cc-switch 同步，否则下次切换被打回。
  当前 codex 服务商看 `~\.cc-switch\settings.json` 的 `currentProviderCodex`。
- **每次请求的真实模型/档位/报错**: `~\.codex\logs_2.sqlite` 表 `logs`，
  读只读: `sqlite3.connect('file:logs_2.sqlite?mode=ro&immutable=1', uri=True)`，
  grep `feedback_log_body like '%Turn error%'`；span 里带 `model=... codex.turn.reasoning_effort=...`。
  会话原文在 `~\.codex\sessions\YYYY\MM\DD\rollout-*.jsonl`。
- **中转站真实支持的模型**: `GET /v1/models`（带 Bearer）直接列出来，比猜可靠。

**判据：报错来自哪一侧**（别只看中文措辞就下结论）。用同一个 key 打 `/v1/responses` 做对照组：
- `The model \`x\` does not exist` ⇒ 中转站没这个模型。
- `该模式不支持当前模型 / not available in this service mode` ⇒ **模型在中转站存在，但当前 key 的线路/套餐不带它**
  （2026-10-01 `gpt-6.1-sol` 就是这种：`/v1/responses` 与 `/v1/chat/completions` 两条路都拒，
  而编造的 `gpt-6.1-luna` 报的是 does not exist）。这类问题在客户端怎么切模式都没救。
- `Invalid value: 'ultra'. Supported values are: none, minimal, low, medium, high, xhigh, max`
  ⇒ 推理档位被中转站拒（Codex 新版选择器会放出 `ultra`/`max`，`[desktop] enabled-reasoning-efforts` 控制）。

**Claude 侧同理，且两处 token 会不一致**（2026-10-06 实测）：`~\.claude\settings.json` 的
`ANTHROPIC_AUTH_TOKEN` 被中转站判 `401 Invalid token`，而 cc-switch.db 表 `providers` 里同一家（Micu）
存的是**另一个 token，能通过鉴权**。所以"key 失效"先别下结论，两处都试一遍再说。
另：New API 类网关的 503 有两种含义，别混为一谈 ——
`No available channel for the current group` = 该模型别名**没有线路**；
`No credentials available. Please add or enable credentials via Admin API or config.json` =
**运营方自己没配上游密钥**（用户侧无解，换节点也没用）。
用 node/undici 打这类网关可以绕过 Cloudflare 对 python urllib 的 403 error 1010 指纹拦截。

## 删供应商删不掉 = 它是「当前供应商」(2026-10-08 实测)

CC Switch 二进制里有写死的提示串 **「无法删除当前正在使用的供应商」**。所以界面上点删除没反应时,
先看 `~\.cc-switch\cc-switch.db` 表 `providers` 里那行的 `is_current`:等于 1 就是被这条规则挡住。

- **界面显示与实际标记会不一致**:开着「路由」时,`live-state.json` 里 `proxy_route` 指向路由用的服务商
  (本机 claude 是 `openoxclaude-…`),但 `providers.is_current` 可能还留在另一个服务商上
  (本次是 `myclaude-1791388650968`)。所以「看着在用 A、其实当前标记是 B」。
- **改法**:退出 CC Switch → 备份 `cc-switch.db`(SHA-256 比对) → `UPDATE providers SET is_current=…`
  把标记挪到别家 → `DELETE FROM providers WHERE id=…` → `PRAGMA integrity_check` / `foreign_key_check` 复核 → 重启。
  `stream_check_logs.provider_id` 会有该服务商的日志行,一并删掉即可;`skill_repos.name` 里出现 `myclaude`
  是**另一个东西**(GitHub 仓库 `cexll/myclaude`),别误伤。
- **托盘不退**:`taskkill /IM cc-switch.exe`(不带 `/F`)只会缩进托盘,20 s 无变化才需要 `/F`。
  强杀前先备份、杀完先跑 `PRAGMA integrity_check` 再动写操作。
- **杀进程不会改 live 配置**:本次 `~\.claude\settings.json` 前后 SHA-256 一致(仍指向 `http://127.0.0.1:15721`
  代理托管),说明改 `is_current` 不会顺带覆写客户端配置。
- 红字「额度没查到 / 解析响应 JSON 失败」与删除无关:那是 `providers.meta.usage_script` 去请求
  `{{baseUrl}}/user/balance`,对方返回非 JSON。

## cc-haha(Claude Code Haha 桌面端)不走 cc-switch 路由 (2026-10-09 实测)

`D:\Claude Code Haha`(Electron + `claude-sidecar-*.exe server --port <随机>`,数据在 `%APPDATA%\claude-code-desktop`)
**有自己独立的服务商库**,与 cc-switch 完全无关:

- `~\.claude\cc-haha\providers.json`(activeId + baseUrl + apiKey)和 `~\.claude\cc-haha\settings.json`(`env.ANTHROPIC_BASE_URL`)
  写死了它要打的地址(本次 `https://openox.tech`)。cc-switch 在 `~\.claude\settings.json` 里写的
  `127.0.0.1:15721` **对它无效** —— 所以在 CC Switch 里切 claude 路由,这个窗口一点反应没有。
  **但这两个文件不是「界面上选了就算」的落点**:2026-10-09 20:54 用户在 app 内把服务商改成 aruhub 后,
  `providers.json` mtime 仍停在 10-08 00:56、`activeId` 仍是 OpenOx,而 netstat 实测主进程
  (`Claude Code Haha.exe`,不是 sidecar)已 ESTABLISHED 到 `165.140.240.229:443`(= api.aruhub.com)。
  ⇒ **生效态在 app 内存/别处,别去手改这两个 json 来切线路**(会和内存态打架);要切就在 UI 里切。
- **判据**: `~\.cc-switch\logs\cc-switch.log` 里转发行按 `[Codex] >>> 请求目标:` / `[Claude] ...` 打标签;
  本次全库 2129 条全是 `[Codex]`、`[Claude]` 零条,且 15721 只有 LISTENING 无 ESTABLISHED ⇒ Claude 流量从未进代理。
- 「界面显示正常 ≠ key 能用」:健康检查/`/v1/models` 不看余额,`/v1/messages` 才看。本次 openox 的 key
  `models` 返回 200、`messages` 返回 **402 `insufficient balance, please top up`**(1 s 内),
  而 CC Switch 列表里它仍显示「正常」。**一发 max_tokens=8 的最小 `/v1/messages` 才是死活判据。**
- 402 之后 sidecar 的表现:GUI 一直转「思考中 N 分 N 秒」,但 sidecar **零外网连接 + CPU 增量 0**、
  工程目录零文件写入 ⇒ 假忙,不是慢。要停当前轮并重启 app 才能再发消息。
- 备用线路 `https://api.aruhub.com` 的 key 可用(200 + 正常回复),但**直连 10.7 s `UND_ERR_CONNECT_TIMEOUT`**
  (DNS 给 165.140.240.229),必须 `NODE_USE_ENV_PROXY=1 HTTPS_PROXY=http://127.0.0.1:7897` 走 clash 才通
  (3.1 s)。给任何客户端填 aruhub 都要顺带配代理或开 TUN。见 [[reference-local-dns-and-link-verdicts]]。
  **2026-10-09 21:25 网络层定位**:TUN 在运行时配置 `clash-verge.yaml` 里已是 `tun: enable: true`,但
  `Get-NetAdapter` 无任何 TUN/Mihomo 网卡、`Get-Service` 查不到 clash-verge 服务、
  `C:\Program Files\Clash Verge\clash-verge-service.exe` 不存在 ⇒ **服务模式没装所以网卡建不出来**
  (内核原始报错未取到,属强推断)。`ProxyEnable` 开成 1 也没用:cc-haha 实测仍直连
  `本机IP → 165.140.240.229:443`,**它的 sidecar 不读系统代理**。
- **【2026-10-11 更正上面那条「aruhub 必须走 7897」的因果】**:真因不是 aruhub 或线路丢包,而是
  一块叫 **`Meta`(Meta Tunnel, Wintun)** 的虚拟网卡 `InterfaceMetric` 为**空** + `AutomaticMetric=Disabled`,
  以最高优先级抢走默认路由,把直连流量灌进隧道 → 表现为「直连一律 `CONNECT_TIMEOUT`、走 7897 秒回」。
  `Set-NetIPInterface -InterfaceIndex 4 -InterfaceMetric 5000`(需管理员)后,**同一命令直连 3/3 HTTP 200(2.0–3.5s)**,
  出口变为 RNDIS 网卡 `192.168.134.34`(它才是当时真正的 uplink,**别禁用它**)。
  所以「aruhub 要配代理」只在 Meta 隧道劫持路由时成立;以后判这类问题先看 `Find-NetRoute` 的出口网卡。
  另:判「网关可达」不能只看 TCP 能连——隧道会替你应答,本机曾因此误判路由器 80/443「可连」。
  **各线路 443 裸握手**:`openox.tech` OK、`api.pateway.ai` OK、`api.aruhub.com` 超时(3 次里 1 次 8 s 才通,丢包级抖动)。
  DNS 无污染 —— Google DoH 与系统解析同为 165.140.240.229,别再猜污染。
- **无需 TUN 就能用的线(2026-10-09 实测)**:cc-switch 里叫 `Claude Official` 的那条其实是中转
  `https://api.pateway.ai/v1`,它的 key 直连出真内容:`claude-opus-5-5` 200、带 `context-1m` beta 头也 200;
  **`claude-sonnet-5-5` 被拒**(「该模式不支持当前模型」= 套餐线路不带它)。该网关对路径拼接极宽松
  (`/v1/messages`、`/messages`、`/v1/v1/messages` 全 200),所以 cc-haha 填 base 带不带 `/v1` 都能跑;
  但它的「获取模型」按钮会 404(拼成 `/v1/v1/models`),**模型名必须手填**。

相关：[[reference-qoder-app-internals]]、[[feedback-no-unverified-cause-claims]]、[[reference-computer-use-blocked]]、
[[reference-local-dns-and-link-verdicts]]

## Skills 页(2026-10-08 实测)

- **技能库是 CC Switch 自己的**: `C:\Users\Admin\.cc-switch\skills`(`settings.json` 里
  `skillStorageLocation: "cc_switch"`)。官方 README 明确该位置**可改为 `~/.agents/skills`**;
  本机 `~\.agents\skills` 是 junction → `D:\Skills`,所以切过去就等于让公共库成为 CC Switch 的库。
- **同步方式**: 官方口径「自动 / 只用软链接 / 只用复制,默认软链接,失败时改为复制」。
  `skillSyncMethod` 当前是 `symlink`。
- **1314 是权限,不是 CC Switch 的 bug**: 2026-10-08 之前本机没有 `SeCreateSymbolicLinkPrivilege`
  也没开开发者模式,`os.symlink` 一律 `winerror 1314`;写
  `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock\AllowDevelopmentWithoutDevLicense=1`
  (提权 `Start-Process reg -Verb RunAs`)后**新进程**建符号链接立刻成功,不用重启。
  注意 `reg query` 经 bash 可能什么都不输出,别据此判断键不存在 —— 用实测建链接来判。
- **Claude 侧走插件路径**: 导入时它会建 `~\.claude\plugins\marketplaces`(空目录)与 `~\.claude\cache`,
  不是直接往 `~\.claude\skills` 里放东西。日志里 Claude/OpenCode 报 `os error 183 当文件已存在`
  而 Codex 报 1314 —— **183 的确切调用点未证实**(2026-10-08),别当结论用。
- 「发现」页拉 GitHub 技能仓库会 60s `DOWNLOAD_TIMEOUT`(本机直连被污染/重置),
  要拉仓库得走 `127.0.0.1:7897` 代理,见 [[reference-git-push-needs-local-proxy]]。
