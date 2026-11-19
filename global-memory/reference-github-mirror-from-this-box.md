---
name: reference-github-mirror-from-this-box
description: 本机批量取 GitHub 公开仓库的可用通路：codeload 直连可用、7897 代理与 github.com 网页域不通、git 走 schannel 与代理握手失败，以及压缩包静默截断的判据
metadata:
  type: reference
---

2026-11-04 实测（要给用户做「公开题库/知识库离线镜像」时直接照这页走，别再从头试）。**通路状态是按域名分片的、且会漂，每轮先花 30 秒重测再决定路线。**

## 分域可达性（当轮实测）

| 端点 | 直连 | 走 127.0.0.1:7897 |
| --- | --- | --- |
| `codeload.github.com`（tar.gz） | ✅ 可用 | ❌ 000 |
| `raw.githubusercontent.com` | ✅ 200 | ❌ 000 |
| `api.github.com` | ✅ 200 | ❌ 403（代理出口被 GitHub 拦） |
| `github.com`（网页/`/archive`） | ❌ 超时 000（但同轮 `git ls-remote` 偶尔通） | ✅ curl 200 |
| `git clone`（direct 或 `-c http.proxy=`） | ❌ TLS EOF | ❌ `TLS connect error`（git 用 schannel，和代理握手就是过不去；curl 同代理却正常） |

⇒ **`git clone` 这条路在本机不可靠，别死磕。** 批量取正文改用：`https://codeload.github.com/<owner>/<repo>/tar.gz/refs/heads/<branch>`，
按 `main → master → gh-pages → develop` 顺序试（HEAD 探不到就用 GET 读首块判断）。代理对 GitHub 无用且会挡 API，
这条与 [[reference-git-push-needs-local-proxy]] 不冲突（那条讲 push），也和 [[reference-skillstore-cli-windows]]
里「raw 直连必被重置」的旧结论相反 —— 当轮 raw 直连是通的，说明结论要按轮重测。

## 三个会静默骗人的坑

1. **压缩包会半截。** 连接被中间设备掐掉时 `resp.read(n)` 返回 `b''`，和「正常读完」一模一样，于是截断的 tar 被记成 `ok`。
   实测一轮里 8 个包有 5 个是坏的（`Compressed file ended before the end-of-stream marker`），而日志全绿。
   唯一可靠的判据是**下载完再整包验一遍**：`gzip.decompress(open(p,'rb').read())`（截断会抛 EOFError）+ `tarfile.open(...).getmembers()` 非空；
   验不过就删文件重下（我最后用 4 次重试、并发降到 2 才稳）。只测首块、只看 status code、只看文件大小都判不出来。
2. **别用一个 `last` 变量收集多次异常。** 按分支循环试 `main/master/...` 时，最后一次 404 会把真正的「中途 SSL 断流」覆盖掉，
   日志显示 `FAIL ... 404 Not Found`，把我误导到去怀疑 URL 格式（其实 curl HEAD 全 200）。每个分支/每次尝试的错都要独立留档。
3. **匿名配额按小时算。** `api.github.com` core = 60 次/小时（不是每分钟），`search` = 10 次/分。
   一轮 `repos/{owner}/{name}` 批量核验就能把 core 打空、后续全 403。核验尽量省着用（只给最终入选的仓库查 sha 和 license），
   体积/文件数改用 tar 或 `search` 拿。`search` 还常整批抛 SSL EOF，要带重试。

## 交付形态

给学习库做镜像时，只抽 `.md/.txt/.csv`，`.png/.jpg/.svg/.pdf/.mp4/.zip` 一律跳过（一个 900 MB 的题解仓库正文只有几十 MB）；
`raw` 压缩包落工作区暂存、抽完即删，见 [[feedback-no-c-drive-scratch]]。
