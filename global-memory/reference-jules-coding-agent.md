---
name: reference-jules-coding-agent
description: Google Jules 云端编码 agent 的实测机制（Pro 配额硬数字、只能对 GitHub 仓库干活、换 token 不认 HTTPS_PROXY 要开 TUN）—— 2026-10-09 用户决定弃用，本机 Jules CLI 与 Antigravity IDE 已全部卸载删除，此文件留作重装依据。
metadata:
  type: reference
---

> **✅ 2026-10-09 晚更新：CLI 路线废弃，但 REST API + 4 把 key 是当前可用通道。**
> `jules.py`（在 `C:\Users\Admin\.gkeys\`）是只读客户端，`cmd_new` 可派活；
> key 从 DPAPI 保险库取，见 [[feedback-api-key-handling]]。
> **实测校准（重要）**：让 Jules「读一遍代码列问题」产出的审计报告**不可直接采信** ——
> 抽查 5 条断言里 3 条不成立（含两条它自标"严重"的：`空 catch 数十处`、`if 里误用 =`，
> 逐行读源码后均为编造或误读注释文本），2 条成立（`outline: 0` 破坏焦点环、`busy 令牌不解除`）。
> **可靠用法**：让它在云 VM 里真跑 `tsc / eslint / vitest / build` 并贴原始输出（自证，不依赖它的判断），
> 或要求"每条发现必须附一条可运行验证命令"。派活默认用 plan-only（不设 `automationMode`），
> 这样不会往用户 GitHub 推分支/PR，批准权留给人。

> **⚠️ 2026-10-09 收尾状态：本机已全部卸载删除。** 用户决定不用 Google 的 AI 了（"磨太长时间了"），
> `D:\npm-tools`（Jules CLI）、`~\.jules`、`~\.gemini`、`~\.antigravity-ide`、`AppData\Roaming\Antigravity IDE`、
> `D:\Antigravity IDE`（已走 `unins000 /VERYSILENT` 正常卸载）、`D:\agy`、`D:\npm-global`、`D:\gemini-profiles`
> 全部清除，PATH/凭据/注册表/计划任务/自启项均复核为干净，`.npmrc` 的 `prefix` 行也已删。
> **下面这些内容是当时实测到的机制，将来若要重装可直接照做，但当前机器上不存在。**
> 明确**没动**：Gemini 桌面版（`AppData\Local\Google\Gemini`，用户在用）、Clash Verge 及其配置（TUN 从未开启）。

**Jules = Google 的异步云端编码 agent**（`jules.google.com`），任务在云 VM 里 clone 仓库→改代码→开 PR。
2026-10-09 本机实测：**官方 CLI 能装能跑，登录流程能拉起到 Google 授权页**。

```
npm config set prefix D:/npm-tools        # 装到 D 盘，见 [[feedback-install-to-d-drive]]
npm i -g @google/jules                    # v0.1.42, 7 packages
D:\npm-tools\jules.cmd login              # 自动开浏览器；--no-launch-browser 走设备码手输
jules new --repo <owner/repo> "任务描述"   # 派活
jules remote list --session / remote pull --session <id> --apply / teleport <id>
```

**关键点：它的 OAuth scope 是 `https://www.googleapis.com/auth/aida`，不是 code-assist 的
`daily-cloudcode-pa.googleapis.com`** → 理论上不吃 Antigravity CLI 那道 `VALIDATION_REQUIRED` 手机验证。
（截至本次**登录是否最终成功未证实**，用户还在授权。）

**Pro 配额硬数字**（官方 `jules.google/docs/usage-limits/`，2026-10-09 抓的）：

| 计划 | 每日任务(滚动24h) | 并行 | 模型 |
|---|---|---|---|
| Jules 免费 | 15 | 3 | Gemini 2.5 Pro |
| **Jules in Pro** | **100** | **15** | 更高概率拿到 Gemini 3 Pro |
| Jules in Ultra | 300 | 60 | 优先访问 3 Pro |

- 付费档**只对 `@gmail.com` 个人号开放**（官方明写，Workspace/企业号暂不支持）→ 本机 4 个 gmail 号符合。
- 家庭共享方案里**配额不共享**，每人独立算。

**硬前提：Jules 只对 GitHub 仓库干活**，不吃本地文件夹。
`G:\AIrenwu` **不是 git 仓库** → 要用得先 `git init` + 推上 GitHub + 在 Jules 里 Connect GitHub 授权该仓库。
本机 `gh` 已认证账号 `chicatancau-create`（见 Windows 凭据 `gh:github.com:chicatancau-create`）。
仓库根放 `AGENTS.md` 会被 Jules 自动读，用来描述项目约定。

**本机坑**：
- npm 的全局包是「node 壳 + 解出的 Go 二进制」，二进制落在 `%TEMP%\jules_tmp\jules.exe`，
  **两个实例同时跑会 ENOENT 抢同一个目录** → 别并行开两个 login。
- 在 Git Bash 里 `taskkill /IM` 会被转成 `D:/Git/IM`（同 robocopy `/MIR` 那类坑），
  杀进程改用 `powershell Stop-Process -Id`。
- `npm` 的 PowerShell 版被执行策略挡（`无法加载文件 D:\Node.js\npm.ps1`），
  bash 里要调 `/d/Node.js/npm.cmd`，别用 `cmd.exe /c "npm ..."`（会变成交互式 cmd）。

## 2026-10-09 实测：`jules login` 不认 HTTPS_PROXY，卡在换 token

**两次登录都失败在同一处**（Chica 号，浏览器侧授权**成功**，回调也打到了 `127.0.0.1:52799` / `127.0.0.1:61674`）：
```
Error: failed to login failed to exchange code for token:
Post "https://oauth2.googleapis.com/token": dial tcp [2404:6800:4008:c19::5f]:443: connectex: ...
```
→ 它解析到 Google **中国 IPv6 段**直连，超时。
**关键结论：注入 `HTTPS_PROXY/HTTP_PROXY` 环境变量救不了它** —— 同一个二进制里
「自更新」请求 `storage.googleapis.com/jules-cli/latest/metadata.yaml` 是**走了代理**的（报的是 `EOF` 而不是 dial 超时），
但 OAuth 换 token 那条请求**用的是不带 `ProxyFromEnvironment` 的自定义 transport**。
⇒ 想登录成功只有两条：
1. **开 Clash Verge 的 TUN / 虚拟网卡（服务模式）**，让不认 env 代理的程序也被接管；
2. 在一个能直连 Google 的网络下完成一次 `jules login`（之后 token 落盘，日常调用是认代理的那条路，能继续用）。

凭据落点：`~\.jules\`（登录失败时里面只有 `cache\`，没有凭据文件）；Windows 凭据管理器里 `jules*` 条目数 = 0。
所以「登录到底成没成」用 `jules remote list --repo` 判最可靠 —— 没登录时报
`Trying to make a GET request without a valid client (did you forget to login?)`。

带代理的壳子：`D:\npm-tools\julp.cmd <jules 参数>`（设 `HTTPS_PROXY/HTTP_PROXY=7897`、
`NO_PROXY=localhost,127.0.0.1,[::1]` —— **localhost 必须绕过代理**，否则 `127.0.0.1:<port>/oauth2callback` 回调会被吃掉）。

## Antigravity **桌面 IDE** 是另一个产品，别和 CLI 混
- 官方下载页 `antigravity.google/download` 上有**两个** Windows 包：
  **Antigravity IDE (Standalone) v2.5.5**（`edgedl.me.gvt1.com/.../antigravity/stable/.../windows-x64/Antigravity IDE.exe`，就是 Pro 权益里那个）
  和 **Antigravity 2.0 hub v2.21.1**（`storage.googleapis.com/antigravity-public/antigravity-hub/...`）。
- 是 **Inno Setup** 包 → **支持 `/DIR=`，能装 D 盘**（不像 MSIX 只能认命）：
  `AntigravityIDE-x64.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /DIR="D:\Antigravity IDE"`，
  实测 `/VERYSILENT` 仍会弹进度窗（不阻塞，自己走完）。装完 1.2 GB。
  本机 SHA-256 `a8c25631fd5e43bf217a6cf510ca796441817f4ad9c50b1d892282c7366edc4a`。
- **IDE 认 `HTTPS_PROXY`**（它的换 token 是 axios，读 env）→ 用 `D:\Antigravity-IDE.cmd` 启动就能过认证，
  之后停在 `Sorry, this account is ineligible to use Antigravity IDE ... not currently available in your location`。
  ⚠️ 这句 location 文案**与 CLI 同款、不可信**；CLI 侧已证实真因是 403 `VALIDATION_REQUIRED`（见
  [[reference-gemini-cli-multi-profile]]）。IDE 自己的日志当时没落盘（`Roaming\Antigravity IDE\logs\<session>\` 为空），
  所以 IDE 侧的 VALIDATION_REQUIRED **未直接取证**，属同账号同接口的推断。

