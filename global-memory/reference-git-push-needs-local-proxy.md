---
name: reference-git-push-needs-local-proxy
description: 本机 git push 到 GitHub 直连会被连接重置，要走本机代理；端口会漂（7897→2026-11-15 实测 7890），先读 ProxyServer 与 gitconfig，别按记忆填端口、更别用 -c 覆盖掉已配好的正确值
metadata:
  type: reference
---

在这台机器上 `git push` 到 github.com（HTTPS）直连常报：

```
fatal: unable to access 'https://github.com/...': Recv failure: Connection was reset
```

**走本机代理即可**（代理常驻监听 `127.0.0.1:7897`，但环境变量 `HTTP(S)_PROXY` 与 git 的
`http.proxy` 都是**空的** —— 所以 git 默认不走它）：

```
git -c http.proxy=http://127.0.0.1:7897 -c https.proxy=http://127.0.0.1:7897 push origin main
```

**Why**：用 `-c` 内联而不是 `git config`，避免把代理永久写进仓库配置（同一台机器上直连偶尔是通的，
写死后反而会在代理没起时全线失败）。

**How to apply**：判断「是不是网络问题」时**别用 `git fetch` 成功当证据** —— 实测出现过 fetch 正常、
紧接着 push 被重置的组合（小请求过、大请求被断）。推之前先 `python` 试连 `127.0.0.1:7897` 是否在
LISTENING，再决定加不加代理参数。同一个代理此前也用于 raw.githubusercontent.com 被重置的场景，
见 [[reference-skillstore-cli-windows]]。

**2026-11-15 更正（重要）：端口会漂，别按记忆里的端口号写死——连 `-c` 内联也会覆盖掉正确配置。**

本轮实测：`127.0.0.1:7897` **已不通**，系统代理注册表 `ProxyServer = 127.0.0.1:7890`，
而且 `~/.gitconfig` 里**早已配好** `http.https://github.com.proxy http://127.0.0.1:7890`（正确值）。
我按这条记忆里的 7897 手动加 `-c http.https://github.com.proxy=http://127.0.0.1:7897`，
**把本来正确的配置覆盖掉**，第一次 GitHub 推送因此 `Failed to connect to github.com:443 over proxy 127.0.0.1` 失败。
改用 7890 立刻成功。⇒ 上面 2026-10-15 那条「别写进配置、用 `-c` 内联」的建议**在本机已经反过来了**：
按 URL 写进全局配置是对的，**多余的 `-c` 才是风险源**。

**正确顺序（每次都这么走，别凭记忆填端口）**：

```bash
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" //v ProxyServer   # 读真实端口
git config --show-origin --get-regexp proxy                                                    # 看配置里是否已对
# 两者一致就别加任何 -c，直接 git push origin main
python -c "import socket;s=socket.socket();s.settimeout(1.2);print(s.connect_ex(('127.0.0.1',7890)))"  # 0=通
```

判端口存活用**试连 `connect_ex`**，别用 `Get-NetTCPConnection -State Listen`（本机实测会假报端口死）。

本轮两端回读验收：`fdb128c` 同时落在 `gitcode/main` 与 `origin/main`，与本地 HEAD 三方一致。

Related: [[reference-skillstore-cli-windows]], [[reference-windows-batch-entry-encoding]]

**2026-10-15 补充：长期方案是按 URL 挂代理，已实测生效。** 对新手用户（记不住每次都要加 `-c`）
比内联更合适，而且**不会误伤国内站**：

```
git config --global http.https://github.com.proxy http://127.0.0.1:7897
# 撤销： git config --global --unset http.https://github.com.proxy
```
实测：GitHub 直连 `Recv failure: Connection was reset`，配这一条后同一条 push 立刻成功，
而 gitcode/atomgit 仍是直连 0.3–0.5 s。**关键是别写 `http.proxy`（全局）** —— 那会把国内站也拐到境外出口。

**双端一次推送（一个 remote 挂两条 pushurl）配好后，push 会跨进程状态变化**：
`git push origin main` 依次推两条 pushurl，**中途 HEAD 被人 amend 一次就会把两个远端推到不同 SHA**
（实测：AtomGit 收到 amend 前的 `7517080`、GitHub 收到 amend 后的 `526512b`，两边一度分叉；
好在两者文件树完全相同，只差提交信息开头一个 BOM）。⇒ **双推之前先看 `git reflog -3` 的时间戳**，
确认最近几十秒内没人提交/amend；分叉后用 `git push --force-with-lease=main:<旧SHA> <remote> main` 对齐。
另两条实测语义：一边挂了另一边**仍会推成功但整条命令 rc=128**（别把 rc≠0 读成"两边都没上"，
要找那行 `main -> main`）；`git pull` 只走 fetch 那条 URL，不会两边混。

**2026-10-18 补充：失败是阵发性的，一次失败什么都证明不了**。同一台机器同一个仓库，走代理连推 4 次都
`RPC failed; curl 55 Send failure: Connection was reset`（POST git-receive-pack 842286 字节，第 2 次还
换过 `http.version=HTTP/1.1`、`http.postBuffer=524288000`，都无效），第 5 次原样重跑就
`3321abd..1331f81 main -> main` 成功。期间 `git ls-remote` 也会随机报
`schannel: failed to receive handshake, SSL/TLS connection failed`（走不走代理都会），所以：

- 判"推没推上去"只认两样证据：push 自己打的 `旧sha..新sha main -> main`，以及重试后 `ls-remote` 打出的远端 sha；
  `git status -sb` 的 `ahead 1` 只是本地缓存的 remote-tracking，不能当结论。
- 别为这种失败改产品代码或 git 配置，**带退避重试 3~5 次**即可；`curl -x http://127.0.0.1:7897 <repo>/info/refs?service=git-receive-pack`
  回 401 就说明代理隧道本身是通的。

**2026-11-08 再证：代理本身也会阵发 TLS EOF，且会持续几分钟。** 同一条 `git push origin HEAD:main` 前两次报
`TLS connect error: error:0A000126:SSL routines::unexpected eof while reading`；期间 `curl -x 7897 https://github.com`
与直连都返回 000（schannel 握手失败 / connection reset），几分钟后原样重跑成功。别因连续两次失败就改配置或宣布
推不上去；先 `git ls-remote` 看远端 SHA，过一会儿再试。另：`git push origin HEAD:main` 可在不切分支的情况下
把工作分支同步到 main。

**2026-11-09 再证：GitHub 可长时间 TLS EOF，而国内两端不受影响。** 同一提交推 `origin`(GitHub) 连续 4 次
`TLS connect error: error:0A000126:SSL routines::unexpected eof while reading`（含 `http.version=HTTP/1.1`），
同一时刻 `domestic`(GitCode) 与 `atomgit` 推送成功、`ls-remote` 均返回新 SHA。结论：不要因 GitHub 单端失败
反复改配置或宣布“没推上去”；按端分别核对 SHA，GitHub 留待网络恢复后补推。

**2026-11-08 补充：`gh` CLI / GitHub API / Actions 也常需要显式代理。** 直连 `gh run list/view/watch`
或 `git push` 会出现 `TLS connect error: unexpected eof while reading`；同一条命令前加
`HTTPS_PROXY=http://127.0.0.1:7897` 即可成功。私有仓库的 Actions 运行、日志下载同样走该代理。
判断顺序：先看 `git push` 是否打出 `old..new -> main`，再用 `gh run view <id> --json jobs` 看每个 job 的
`conclusion`，不要用“命令没报错”当 CI 通过。


---

## 国内版补充（2026-11-19 并入）

> 来源：Qoder 国内版 `C:\Users\Admin\.qoder-cn\memory\reference-git-push-needs-local-proxy.md`（本地修改日期 2026-11-05），国际版没有的内容，逐字保留；只追加，不改写上文。
> 注意：下文端口 7897 是 2026-11-05 当时值；本机代理端口会漂（见上文 2026-11-15 节，实测 7890），以先读 ProxyServer 与 gitconfig 为准。

**2026-11-05 补充：代理也会是坏的那一条路，别把它当默认**

同一分钟内实测：走 7897 `git push` 报 `TLS connect error: error:0A000126 SSL routines::unexpected eof`，
`curl -x 127.0.0.1:7897 https://api.github.com/zen` 回 **HTTP 000**（5 s 超时）；而**不带代理直连**
`curl https://github.com/<owner>/<repo>/info/refs?service=git-upload-pack` 回 **401 = 端点可达、只是要鉴权**，
随后 `git -c http.sslBackend=openssl -c credential.interactive=false push origin main` 一次成功。
所以顺序是：**两条路各试一次再判网络**，而不是「GitHub 必须走 7897」。
`netstat -ano | grep -c 127.0.0.1:7897` 只证明端口有人听，证明不了出口能通（代理节点挂了照样在 LISTENING）。
加 `credential.interactive=false` 让它在拿不到凭据时快速失败，而不是弹 GCM 窗挂住。
私有仓库匿名 `info/refs` 回 401 属正常，**不能当「仓库不存在」或「网络断了」的证据**。
国内站（GitCode/AtomGit）反过来：直连就通，别挂代理。
