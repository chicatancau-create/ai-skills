---
name: reference-local-dns-and-link-verdicts
description: 本机 WLAN 路由器 DNS 会把 chatgpt.com/reuters.com 解析到 Facebook 网段；判链接死活要用 DNS+真实浏览器两层，403/521 多是反爬不是死链
metadata:
  type: reference
---

2026-10-06 实测：本机默认路由走 WLAN，DNS 只有路由器 `192.168.91.113`。

- **DNS 污染**：`chatgpt.com` → `31.13.82.169`、`www.reuters.com` → `31.13.83.2`（都是 Facebook 段）。
  命令行打这两个站得到 401/403，**不是书签失效，是这个网络必须走梯子**。
- **梯子模式**：Clash Verge 是**系统代理**（`127.0.0.1:7897`）+ **TUN 关闭**，所以命令行工具默认不吃它。
  Node 的 fetch 要 `NODE_USE_ENV_PROXY=1` + `HTTPS_PROXY=http://127.0.0.1:7897` 才走代理
  （见 [[reference-skillstore-cli-windows]]、[[reference-git-push-needs-local-proxy]]）；
  Python urllib 会读注册表代理，但 DNS 污染这类问题代理与否都要分开判。

**判链接死活的三层判据（别混用）**：
1. `socket.gethostbyname` —— **解析不了 = 域名真死**（实测死域：mxdm2.com、qqtn.com、xz7.com、
   wallpaperplay.cn、winstepnexus.cn、shop.moiu.net、moids.moiu.cn、52z.com）。
2. HTTP 状态 —— `404` 是"站活着、那一页没了"；`500/502/521/468` 多为服务端或反代问题，需复核。
3. **真实浏览器开页** —— 知乎 403、CSDN 521、`comick.io`/`aigei`/`chatgpt`/一元机场 403、
   Cloudflare 的 `Just a moment...`、百度的"安全验证"**全是反爬，内容在**。
   抽样用浏览器开 2 条知乎确认过标题一致，再按域名规则推广，并写明"同域其余未逐条开页"。

**第四层坑：SPA 站点的前两条判据全部失效**（2026-10-15 在 AtomGit 上踩过）。
`atomgit.com` 对**任意**路径都回 HTTP 200，`curl` 拿到的外壳 HTML 里也不含「页面找不到或无权限」
这类文案（正文由客户端渲染，`docs.gitcode.com` 的文档页甚至 curl 到 0 字节）。
所以「200」和「grep 正文没报错」都**证明不了路由存在**，据此给用户报出的深链接是错的，
害用户白跑一轮。对 SPA 只能：给**可点的菜单路径**（官方文档写的点击入口），
或明确写「此 URL 未验证」，别把状态码当证据。

**第五层坑：解析慢/抖会把上层实验整组污染**（2026-11-02 实测 `gitcode.com`）。
`socket.gethostbyname('gitcode.com')` 花 **11.37 s** 才返回，同一时刻 `github.com`/`baidu.com` 只 0.05 s；
curl 与 git 因此在两次运行里一次成功一次报 `Could not resolve host`（系统 DNS 顺位是
`192.168.0.1` 路由器在前、`223.5.5.5`/`119.29.29.29` 在后）。
⇒ 我做的一组 A/B（验凭据通路）整组作废，误判风险极高。
处置：先用 `curl --resolve <域名>:443:<IP>` 绕开 DNS 把「被测的那一层」和解析分开，
或在结论里明确写「本轮失败发生在 DNS 层，认证结论无效」，别拿污染过的样本下判断。

**顺带**：`file:///G:/…`、`192.168.0.1`、`127.0.0.1:5244` 这类书签不参与死活判定（本地文件/路由器/未启动的面板），
单独归一个目录；带 `sid=`、`token=eyJ…`、`?key=`、`trade_no=` 的 URL 是凭证串，导出前要提醒用户别外传。

相关：[[reference-chrome-bookmarks-and-connector]]、[[feedback-no-unverified-cause-claims]]、
[[reference-git-credential-manager-windows]]
