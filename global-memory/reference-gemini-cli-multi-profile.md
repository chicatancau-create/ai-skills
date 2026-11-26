---
name: reference-gemini-cli-multi-profile
description: Gemini CLI 个人档已被 Google 停发（改用 Antigravity CLI `agy`）；本机 agy 的登录入口、只存一号的凭据落点、换号壳子 go.cmd/switch.cmd、必须注入 7897 代理，以及权益死因实为 Google 手机验证(VALIDATION_REQUIRED) 而非地区。
metadata:
  type: reference
---

> **⚠️ 2026-10-09 收尾：本机这套已全部删除。** 用户决定弃用 Google 的 AI（"磨太长时间了，算了吧"）。
> `D:\agy`、`D:\npm-global`、`D:\gemini-profiles`、`~\.gemini`、凭据 `gemini:antigravity`、
> PATH 里的 `D:\agy\bin` 与 `D:\npm-global` 均已清除并复核干净。下面记录的是当时的机制，供重装参考。

# Gemini CLI 多账号（本机 2026-10-08 实测）

**装法**：`npm config set prefix D:\npm-global` + 把 `D:\npm-global` 追加进 `HKCU\Environment\Path`，
再 `npm i -g @google/gemini-cli`。装完版本 0.63.0，实体在 `D:\npm-global\node_modules\@google\gemini-cli`。
`node_modules` 里**没有 `@github/keytar`** → OAuth 凭据走 `FileKeychain` 文件回退（`<profile>\.gemini\gemini-credentials.json`），
所以按目录隔离账号是可行的。

**一个账号一个目录**：0.63.0 的 `homedir()` 第一行就是
`const envHome = process.env["GEMINI_CLI_HOME"]; if (envHome) return envHome;`
→ 设 `GEMINI_CLI_HOME=D:\gemini-profiles\accN` 即整份隔离（实测跑一次只生成 `accN\.gemini\*.tmp`，不碰真的 `~\.gemini`）。
**注意官方自己的歧义**：另一处读 settings 的代码是 `baseDir = process.env.GEMINI_CLI_HOME || join(homedir(), ".gemini")`
再 `join(baseDir,"settings.json")` —— 即 settings 落在 `<profile>\settings.json`，而 storage 落在 `<profile>\.gemini\...`。
两处都写一份 `{"security":{"auth":{"selectedType":"oauth-personal"}}}` 才不会踩空。

**`Authentication consent could not be obtained.` 的真因（0.63.0 源码定位，2026-10-08）**
在 `packages/core/src/utils/authConsent.ts`：

```js
if (isHeadlessMode()) return getOauthConsentNonInteractive(...)
else if (coreEvents.listenerCount("consent-request") > 0) return getOauthConsentInteractive(...)
throw new FatalAuthenticationError("Authentication consent could not be obtained...")
```

首次登录发生在主 UI 挂载前 → `listenerCount` 为 0 → 真 TTY 下必抛。**跟网络无关。**
`isHeadlessMode()` 除了「stdin/stdout 不是 TTY」，还把 **`options?.prompt` 为真也算 headless** ——
所以正解是**带 `--prompt=` 跑一次来触发登录**：

```
D:\gemini-profiles\g.cmd acc1 --prompt=hi
```

终端会问 `Opening authentication page in your browser. Do you want to continue? [Y/n]:` → 答 `y`
→ 浏览器开 Google 授权页 → 授权后凭据落进该 profile。（实测已走到这步：答 y 后进程挂在等回调，无人点则超时。）

**`CI=true` 是错招，别再用**：`shouldAttemptBrowserLaunch()` 里有
`if (process.env["CI"] || DEBIAN_FRONTEND === "noninteractive") return false` ——
设 CI 虽绕过 consent，却同时**禁止启动浏览器**，于是改抛
`Manual authorization is required but the current session is non-interactive.`（两个判断共用 CI，方向相反互相拆台。）

**cmd 的 `%*` 不受 `SHIFT` 影响**：切换器里 `shift` 后 `call gemini.cmd %*` 会把账号名一起当位置参数传下去，
报 `Cannot use both a positional prompt and the --prompt flag together`。已改为显式 `%2 %3 ... %9`。

**已排除的两个假因**（别再查）：
- 代理：`HTTPS_PROXY/HTTP_PROXY` 对这一步无关；且实测 Node `fetch` 与裸 `https` 设了这俩变量**照样超时**
  （只有 gaxios/https-proxy-agent 那条路认 env），所以 env 代理不是万能补丁。
- DNS/回调：`accounts.google.com` 解析到真 Google 段；`ProxyOverride` 已含 `localhost;127.*;<local>`，
  回调不会被系统代理吃掉。（`www.google.com` 仍被污染成 31.13.92.37 = Facebook 段，与本问题无关。）
  本机没开 TUN（适配器只有 Radmin VPN / VMware / WLAN / 蓝牙 / 以太网），7897 由 PID 54760 在听。

**切换器**：`D:\gemini-profiles\g.cmd <acc1..acc4> [gemini 参数]`，内部设 `GEMINI_CLI_HOME` + 上面那组代理 env。
非交互调用用 `g.cmd acc2 -p "..." -o json`。

**CC Switch 管不了这件事**（实测其二进制）：它只**读** `~/.gemini/oauth_creds.json`
（读不到提示 "Refresh ~/.gemini/oauth_creds.json via the gemini CLI"），写的是 `settings.json` 的
`env` / `security.auth.selectedType`；「应用配置 → Gemini CLI 配置目录」只能指**一个**目录，
「路由」页要先把凭据喂给它才有意义。所以 4 账号轮换只能靠 `GEMINI_CLI_HOME`，CC Switch 不参与。

## 后续：Gemini CLI 个人档已死，改用 Antigravity CLI（2026-10-08 实测）

Google 服务端停发「Gemini Code Assist for individuals」：`0.63.0`、`0.64.0-preview.0`、`0.65.0-nightly.20261008`
**三个版本一律返回** `IneligibleTierError`，诊断里 `tierId: 'free-tier'`。官方公告 2026-05-19 迁移到 Antigravity CLI，
弃用页更新 2026-09-02；论坛 2026-09-26 有活跃 Google AI Pro 账号仍被判 not eligible 的报告。
**但本机实测相反**：用户这 4 个 Google 账号都开了 PRO，登进 Antigravity 后 `agy models` 能列出真模型表
（`gemini-3.8-flash-high/medium/low`、`gemini-3.1-pro-high/low`、`claude-sonnet-4-6`、`claude-opus-4-6-thinking`、`gpt-oss-120b`）
→ 权益在 Antigravity 侧是活的，Gemini CLI 那条死路不用再救。

**Antigravity CLI 装法（已装到 D 盘）**：
```
curl -fsSL https://antigravity.google/cli/install.cmd -o install.cmd
install.cmd -d D:\agy\bin        # 默认 %LOCALAPPDATA%\agy\bin，用 -d/--dir 改盘
```
脚本自带 **certutil SHA-512 校验**；装完 181 MB 的 `agy.exe`（版本 1.3.1），并自动把 `D:\agy\bin` 写进用户 PATH
（当前终端不生效，要重开）。npm 上**没有**官方 `@google/antigravity-cli`，只有 `antigravity-cli@0.0.1` 占位包。
安装器最后会打印「placed successfully at C:\Users\Admin\AppData\Local\agy\bin\agy.exe」—— 那是它自己的文案，
**实测 C 盘没有第二份**，只有 D 盘那一个 181 MB 文件。

**登录必须给代理，否则死在 token 交换（这是真正的根因）**：直接敲 `agy` 会走 IPv6 直连
`token exchange failed: Post "https://oauth2.googleapis.com/token": dial tcp [2404:6800:4008:c19::5f]:443: connectex …`
（浏览器侧是成功的，设备码页都出来了，只死在 CLI 换 token）。Go 程序认 `HTTPS_PROXY/HTTP_PROXY`，所以：
```
D:\agy\ag.cmd -          # 内部设 HTTPS_PROXY/HTTP_PROXY=http://127.0.0.1:7897 + NO_PROXY=localhost,127.0.0.1 再裸跑 agy
```
代理一给，立刻进到 `Welcome to Antigravity CLI! Choose your color scheme:` 的 onboarding。
注意与上面 Gemini 那条区分：**Gemini 的 consent 报错与网络无关，Antigravity 的 token 报错就是网络**。

**多账号是原生的，不用目录隔离**：二进制里有
`AGY_ACCOUNT=%q matches no signed-in account; available accounts: %s` → 同时登多个号，按次用 `AGY_ACCOUNT=<邮箱>` 选。
另有 `ANTIGRAVITY_APP_DATA_DIR`、`ANTIGRAVITY_EXECUTABLE_DATA_DIR`、`ANTIGRAVITY_BROWSER`。
登录入口：**不带参数直接跑 `agy`**（原文提示 `Please sign in to view available models. Launch the CLI without arguments to sign in.`），
走 `https://accounts.google.com/o/oauth2/auth` + device code 流。
壳子：`D:\agy\ag.cmd <账号邮箱|-> [agy 参数...]`（内部设 `AGY_ACCOUNT` + 代理；同样避开 `%*` 不受 shift 影响的坑）。

**凭据不在文件里，在 Windows 凭据管理器**：`cmdkey /list` 里有
`LegacyGeneric:target=gemini:antigravity`（用户名 `antigravity`）和另一条 `target=EOxaH1L9QA`。
明面目录 `~\.antigravity`、`%LOCALAPPDATA%\agy` 都不存在；数据目录是 **`~\.gemini\antigravity-cli\`**
（实测 13.7 MB，其中 `bin\webm_encoder.exe` 就占 13.4 MB；还有 `jetski_state.pbtxt`、`conversation_summaries.db`、
`cache\onboarding.json`、`cache\default_project_id.txt`、`log\cli-YYYYMMDD_HHMMSS.log`）。
→ 以后要清/迁凭据得走 `cmdkey /delete:`，删目录没用。

**加账号就在 onboarding 里**（2026-10-08 实测，**推翻我先前「入口在 Plugins Manager」的推断**）：
用 computer-use 往 Windows Terminal 发一个 `Return` 跳过「Choose your color scheme」后，
界面直接进到连账号页，原文是
`Your browser should open automatically. If not:` + 一整条 `https://accounts.google.com/o/oauth2/auth?...redirect_uri=https%3A%2F%2Fantigravity.google%2Foauth-callback...`
+ `→ Click here to authenticate` + `If you aren't automatically redirected, paste the authorization code below:`。
Chrome 标题随即变成「登录 - Google 账号」= 浏览器确实被拉起。**剩下的选账号/点允许只能用户做**
（computer-use 对 Chrome 会触发 `browser_url_policy` 并终止整轮控制，见 [[reference-computer-use-blocked]]）。
另外 `AGY_ACCOUNT=nosuch@example.com` 在只有一个号登录时**不报错也不列 available accounts**（直接忽略），
所以「用假邮箱枚举账号」这招至少要两个号之后才可能有效。
`agy` 无 TTY 时直接退出且零输出 → 登录链路没法在我这边无头复现，只能用户真终端跑。

用户侧资源（2026-10-08）：4 个 Google 账号都有 PRO，分别登录在 4 个 Chrome 资料里
（Chica Tancau 及另外 3 个账号，昵称已脱敏），授权时按资料窗口区分账号。

## 2026-10-09 复核：1.3.2 自己承认了死因，且 CLI 只存一个号

- **自动升到 1.3.2 后，报错文案改对了**：`Eligibility check failed: Your current account is not eligible for Antigravity. Verify your account to continue.`
  + `Alternatively, try signing in with another personal Google account.` + 直接甩出 `https://accounts.google.com/signin/continue?sarp=1&...&flowName=GlifWebSignIn`。
  → 1.3.1 那句「not currently available in your location」**是错的兜底文案**，别再按地区去查。
- **第 2 个号（<已脱敏用户名>）登录后吃的是同一个 403**，说明这是**账号级风控**（多号+代理），不是某个号坏了。
- **`/login` 在 1.3.1/1.3.2 都不存在**（实测终端回 `Unknown command: /login`）。二进制里那句
  `Please log out (/logout) and log back in (/login).` 误导，别照它做。唯一的登录入口是**没有任何已登录账号时**跑 `agy`，
  它会出 `Select login method: 1. Google OAuth / 2. Use a Google Cloud project`。
- **确认只存一个号**：Windows 凭据管理器里永远只有 1 条 `gemini:antigravity`（`user=antigravity`，明文 JSON：
  `token.{access_token,refresh_token,expiry,token_type}` + `auth_method` + `id_token`）。登第 2 个会顶掉第 1 个。
  查是哪个号：解 `id_token` 的 JWT payload 取 `email`（脚本 `C:\Users\Admin\AppData\Local\Temp\agywho.ps1`，
  依赖同目录 `agycred_src.txt` 里的 `CR2::Raw`）。
- **一键换号**：`D:\agy\switch.cmd` = `taskkill /IM agy.exe /F` + `cmdkey /delete:gemini:antigravity` + `call D:\agy\ag.cmd`。
  换号前要先在 Chrome 切到对应的**个人资料**（本机 4 个资料：Chica 及其余 3 个已脱敏账号，
  邮箱分别是 chicatancau 及其余 3 个已脱敏用户名 @gmail.com），否则授权页会顺着默认资料又登回旧号。
- `D:\agy\ag.cmd` 已改成**不带参数也能直接跑**（内部用 `shift` + `%1..%9`，仍不能用 `%*`）。
  要带参数又不指定账号时写 `ag.cmd - -p "..."`。
- **验证链接是一次性的、几分钟就废**，浏览器打开后报 `400 That's an error` 基本都是过期/已被用，重新跑一次 agy 取新链即可。
  服务端可先自查：`curl -x http://127.0.0.1:7897 -o /dev/null -w "%{http_code}" -L "<url>"` 返 200 才算活着。
- 本机梯子会**瞬断**：`token exchange failed: Post "https://oauth2.googleapis.com/token": EOF` 出现过一次，
  连测 6 次又全通 → 先重试，别急着改配置。
- **`agy models` 能列全 ≠ 这个号能用**：模型表走 `fetchAvailableModels`，权益走 `loadCodeAssist`，
  两个端点互相独立。实测被 403 挡住的号照样能把 14 个模型全列出来。判死活只能跑一次真 `-p` 请求。
- **OAuth 授权链接不在 CLI 日志里**（`antigravity-cli\log\cli-*.log` grep `oauth2/auth` = 0 命中，日志只记
  `daily-cloudcode-pa.googleapis.com` 那批后端调用）。⇒ 想「从日志抓 URL → 用指定 Chrome 资料打开」这条路**不成立**，
  只能靠先把目标资料的窗口顶到最前，赌 Chrome 把新标签开在最前窗口里。
- 换号壳子 `D:\agy\go.cmd [1|2|3|4]`：杀 agy → `cmdkey /delete` → `chrome.exe --profile-directory="..."` 顶到前面
  → `call ag.cmd`。资料目录对应关系（读 `Google\Chrome\User Data\Local State` 的 `profile.info_cache`）：
  `Default`=Chica/chicatancau，`Profile 1`/`Profile 2`/`Profile 3` 为其余 3 个账号（昵称与邮箱均已脱敏）。
- **Gemini 桌面版不是替代品**：它是网页套壳，不能读写本地文件、不能跑命令，我驱动它也榨不出可用于工作的额度；
  换号还得在它的界面里切账号，比 CLI 更麻烦。
- 用户 2026-10-09 明确的目标是**「把这 4 个号的额度全用完」**，并直接否掉了我做的「一键换号」方向
  （「我并不需要一键换号」）。⇒ 别在 UX 便利性上继续加工，先解决「能不能真跑起来」。
  当前状态：4 个号里实测 2 个（Chica 与 Profile 1 那个已脱敏账号）全卡在同一道手机扫码验证，**未证实**另外 2 个已脱敏账号是否也卡。

## 2026-10-08 晚实测：agy 登录通了，真正卡点是「Google 要求验证账号」不是地区

用 `D:\agy\ag.cmd -`（注好 `HTTPS_PROXY=7897`）+ computer-use 驱动终端，onboarding 一路走完
（配色 → ToS 页的 `[x] 数据收集` 保持默认 → 信任工作区），**登录成功**：界面显示 `chicatancau@gmail.com`、
`Gemini 3.8 Flash (High)`，说明 token 有效、代理是根因（之前裸跑 `agy` 没代理 → 直连 IPv6 `oauth2.googleapis.com` 超时）。

**我先前把根因写成「出口 IP 地区判定」，那是错的，已推翻**。界面那句
`not currently available in your location` 只是 CLI 的兜底文案（`server_oauth.go:114`）；
日志里后端真正返回的是：
```
403 PERMISSION_DENIED  reason=VALIDATION_REQUIRED  "Verify your account to continue."
validation_url=https://accounts.google.com/signin/continue?sarp=1&scc=1&continue=...&flowName=GlifWebSignIn
```
（`retrieveUserQuotaSummary` 与 `loadCodeAssist` 同一个后端、同一个 token，都吃这个 403。）
把 `validation_url` 在浏览器里打开 = 中文页「**验证您的信息后才能继续**」+ **手机扫二维码**（sarp=1）。
→ **只有用户本人用手机扫码能过，程序侧无解**；换 Clash 节点跟这件事无关。
旁证：`agy models` 走 `fetchAvailableModels` 是成功的（模型表能列全），说明不是网络也不是地区。

其它实测到的机制（2026-10-08 晚）：
- ~~**`/login` 和 `/logout` 是真斜杠命令**~~ **错**：1.3.1 实测 `/login` 回 `Unknown command: /login`，只有 `/logout` 存在。
  二进制原文 `Please log out (/logout) and log back in (/login).` 是误导（见上面 2026-10-09 复核段）。
- 凭据落点已确认：Windows 凭据管理器 `target=gemini:antigravity`、`user=antigravity`，
  blob 是**明文 JSON**（1667 B，键只有 `token.{access_token,token_type,expiry,refresh_token}`、`auth_method`、`id_token`），
  **一次只存一个号**。`~\.gemini\` 下没有任何含邮箱的文件（只在 `antigravity-cli\log\` 的日志里出现）。
- 核对当前登了哪几个号：新开 cmd 跑 `set AGY_ACCOUNT=zzz` 然后 `D:\agy\ag.cmd - -p hi`，
  若多号已存会报 `AGY_ACCOUNT="zzz" matches no signed-in account; available accounts: <列表>`。
- **mihomo 外部控制器确实没开**：`clash-verge.yaml` 里 `external-controller: ''`，只留
  `external-controller-pipe: \\.\pipe\verge-mihomo-sidecar-<hash>`，所以 TCP 9090/9097 连不上，
  换节点只能用户在 Clash Verge 界面点。（当前订阅「娱乐办公好帮手」组已选 `🇯🇵 JP 01`，
  经 7897 打 ipinfo 实测出口 `23.146.72.122 / Tokyo / JP`。）
- Chrome 里选哪个 Google 账号这步**我做不了**：computer-use 一碰 Chrome 就触发 `browser_url_policy`
  并终止整轮控制；但 `user-browser-use`（浏览器连接器）能开页、截图、读无障碍树 —— 用它打开
  `validation_url` 取证成功（页面已是简体中文）。

## 2026-11-03 复核：两个号卡在「我们无法验证您的身份」

用户问「我有 4 个 PRO 号，能不能反代 Gemini」时顺带查到的状态：

- 两个号（邮箱均已脱敏）打开就是中文页
  「我们**无法验证您的身份**」+ 三条建议（用以前登录过的设备/浏览器、用家里或单位的 Wi-Fi、
  改辅助电话号码）。这是 **Google 账号自己的登录风控挑战页**，不是封号，也不是 Antigravity 的资格检查页
  （后者文案是 `We couldn't verify your info` / `not eligible`，官方论坛确认那是 OAuth 过了但资格检查失败）。
- 判据分层：① 匿名读得到 ≠ 凭据有效；② 这类挑战页意味着**当前设备+网络下所有需要重认证的操作被锁**
  （新登录、OAuth 授权、改密码、改手机号），已登录会话能撑到 token 过期；③ 长期过不去 → 走恢复表单 →
  表单也过不了就是限制乃至停用，**Pro 订阅绑在号上，号废权益废**。
- 本机 Windows 里存着两条 `google.com` **通行密钥**（弹窗标题「选择通行密钥」），涉及账号身份已脱敏。
  `cmdkey /list` **看不到 passkey**，只能在
  设置 → 账户 → 登录选项 → 管理通行密钥 里删；删之前要提醒：这类批量注册的号往往**没有恢复手机、
  通行密钥就是唯一登录凭据**，删了就彻底进不去。用户当时的决定是「号不要了」。
- 这两个号就是批量注册号，
  正是最容易被这个页面困死的一类 —— 没有历史登录设备、没有恢复手机，Google 拿不到任何"是你"的证据。

## 「PRO 版密钥」不存在（官方 2026-08-18 口径，别再找）

`https://ai.google.dev/gemini-api/docs/google-ai-plans` 的 Limitations and compatibility 原文：
> **AI Studio UI only**: Google AI plan benefits for developer usage apply **only within the Google AI Studio web interface**.
> Direct use of the Gemini API (such as using API keys or external applications) is billed and managed separately.

- Google AI **Pro / Ultra 只抬高 AI Studio 网页界面**（Playground + Build mode）的日配额，
  **不落**到 API key，也**不落**到 agy / Gemini CLI 的 OAuth 通道。
- API key 的档位是 **Free / Tier 1 / 2 / 3**，按 **Cloud Billing 消费历史**升档
  （`/gemini-api/docs/rate-limits` 那张表全文不提 Pro）。想要大额度 key 只能绑云账单花钱。
- 同页还写明：**AI Studio 里的 Antigravity Preview / Deep Research 代理不含在 Pro 套餐内，需要 paid API key**。
- ⇒ 用户问「Pro 密钥在哪」的正确答案是**没有这个东西**，不是他没找到。
- 本机抓这类官方页要用 `curl -x http://127.0.0.1:7897`（WebFetch 在这台机器上对 google 域名直接 `fetch failed`），
  读出来记得 `python -X utf8`，否则 GBK stdout 会炸。


相关：[[feedback-install-to-d-drive]], [[reference-windows-batch-entry-encoding]],
[[reference-codex-desktop-and-ccswitch]], [[reference-local-dns-and-link-verdicts]],
