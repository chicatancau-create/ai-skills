# gh 删仓 delete_repo 授权：device flow 必须走代理，码 15 分钟过期

> 2026-11-26 实测验证（verified）。配套 `reference-two-platform-repo-align-write-ops.md`。

## 结论
- `gh repo delete {owner}/{name} --yes` 需要令牌含 `delete_repo` scope；缺它返回 HTTP 403 `Must have admin rights to Repository...needs delete_repo scope`。
- 授权命令：`gh auth refresh -h github.com -s delete_repo`（OAuth device flow，必须用户在浏览器打开 https://github.com/login/device 输入一次性码并点 Authorize，非交互拿不到）。

## 网络坑（关键）
- `github.com` 首页 GET **直连可达（200）**，但 device flow 的 `POST https://github.com/login/device/code` **直连超时**：`read tcp ...->20.247.166.64:443: wsarecv: A connection attempt failed...`。即「首页通」不代表「OAuth 端点通」。
- 必须挂代理：`$env:HTTPS_PROXY='http://127.0.0.1:7890'; $env:HTTP_PROXY='http://127.0.0.1:7890'` 后再 `gh auth refresh`，取码成功。
- 代理端口用 `Get-NetTCPConnection -LocalPort 7890 -State Listen` 可能查不到 LISTEN，但 `curl.exe -x http://127.0.0.1:7890 https://github.com` 实测 200——以 curl 实测为准，别被端口枚举误导。
- 直连失败/代理 overnight 不稳时会出现 `HTTP 503`、`Post .../login/oauth/access_token: unexpected EOF`；网络恢复后走代理即成。

## 时序坑
- 一次性码约 **15 分钟过期**，无人点授权则 `context deadline exceeded`、REFRESH_EXIT=1。
- 最优解：先 `ask_user_question` 确认用户「现在就点」，**再生成码**并立刻贴出，避免码白白过期。生成后后台 job 轮询，用户授权完成会通知，再执行删除。

## 删仓流程
1. 删前 `git clone --mirror` 备份并 `git rev-parse HEAD` 验 refs（备份落 `G:\数据备份\仓库删除备份_<日期>\{name}.git`）。
2. 授权后 `gh repo delete chicatancau-create/{name} --yes`（rc=0）。
3. `gh repo list --json name,visibility` 复核数量与可见性；`git ls-remote <两端URL> HEAD` 复核保留仓两端对齐。
- 注意：删 GitHub Pages 构建产物仓（如 learning-blog-demo）会让对应 Pages 站下线，源码若在别仓则不丢，删前知会用户。