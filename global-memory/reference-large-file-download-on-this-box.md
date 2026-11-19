---
name: reference-large-file-download-on-this-box
description: 本机大文件下载必须用 curl 子进程而不是 Python urllib（TLS 被重置），以及测速/进度测量的会给出假结论的坑；含 GitHub 在本机「代理反而挂、codeload 直连能过」的实测取址策略
metadata:
  type: reference
---

2026-10-31 下一次 5.67 GB 固件、2026-11-10 下几个 GitHub 仓库时连踩出来的，全部有 A/B 数字。

## 核心：urllib 在这台机器上下大文件会被重置

同一主机、同一 40 MB Range 区间，同时刻对照：

- `curl` 单连接：**7.05 MB/s**（41,943,040 B / 5.95 s）
- Python `urllib.request.urlopen`：**TLS 握手直接失败** → `ssl.SSLEOFError: [SSL: UNEXPECTED_EOF_WHILE_READING]`

所以用纯 Python（urllib）写的下载器只会得到 **0.5–0.7 MB/s**，那点吞吐是「握手失败 → sleep → 重试」间隙里蹭到的。
**做法**：批量下载一律 `subprocess.run(["curl", ...])`；要并发就分段队列（一段一条 curl 进程），
12 并发实测聚合 **50 MB/s**，5.67 GB 两分钟下完。

## GitHub 在本机：代理反而挂，codeload 直连能过（2026-11-10 实测）

本机 7897 代理对 **GitHub 的 release/仓库下载**经常直接失败：

- `curl -x http://127.0.0.1:7897 https://codeload.github.com/...` → `schannel: failed to receive handshake, SSL/TLS connection failed`
- `git clone` 走代理 → `fatal: unable to access ...: TLS connect error: error:0A000126:SSL routines::unexpected eof while reading`
- **同一时刻去掉 `-x` 直连 `https://codeload.github.com/<owner>/<repo>/zip/refs/heads/<branch>` 成功**（5 MB zip 一次拿到）

⇒ 取 GitHub 仓库的可靠顺序：**① `codeload.github.com/.../zip/refs/heads/<branch>` 直连**（先试 main，404 再试 master）
→ ② `raw.githubusercontent.com` 直连（读单个文件、不吃 API 限流）→ ③ 才考虑代理。
`api.github.com` 有速率限制，未认证时会直接回 `API rate limit exceeded` —— 别把限流当成"仓库不存在"。
PyPI 走清华镜像直连可用：`-i https://pypi.tuna.tsinghua.edu.cn/simple`。
（`git push` 仍需代理，见 [[reference-git-push-needs-local-proxy]]；下载与推送是两条不同的通路。）

## 我在这次里连续给出的三个错根因（顺序都是「看起来合理」）

1. 「bigota 被限速，换 OSS 镜像就好」→ 半对，bigota/hugeota 确实只有 9 KB/s。
2. 「8 个 worker 里 5 个被派到慢镜像」→ 改成全部走快镜像，仍然 0.6 MB/s。
3. 「长连接被降速，改短连接分段」→ Python 分段队列仍然 0.6 MB/s。
4. 真因是**客户端**（urllib TLS 被重置），直到拿同一区间做 curl vs urllib 的 A/B 才暴露。

⇒ 规则：**怀疑"服务器限速"之前，先用另一个客户端打同一段字节做 A/B。** 同一 URL 换镜像/换连接数都不动，说明问题在自己这侧。

## 三个会让测量说谎的坑

- **测速公式别只看数字**：我用 `awk` 算 `30/(耗时)`，四个不同镜像全部报 **0.7 MB/s** —— 那不是限速一致，是四次都撞满了 `curl -m 40` 超时。凡是多个来源给出**完全相同**的速率，先怀疑测量被超时截断。正确写法：`curl -w "%{speed_download} B/s http=%{http_code} got=%{size_download}"`，或按固定间隔量文件字节增量。
- **写盘不 flush 就看不到进度**：worker 里只在请求结束时 `f.flush()`，于是磁盘上的大小滞后真实下载量（观测值全是 1 MB 的整数倍），据此算的 ETA 完全错。**每块写完就 flush**，否则进度不可观测。
- **`.part` 中间态会被 glob 计入**：`glob("[0-9]*")` 把 `00012.part` 也算进"已完成"，虚报进度；进程被杀时这些未 rename 的中间态直接作废。统计只算正式名，清理时单独删 `.part`/`.dl`。

## 小米 CDN 的取址细节

- **小米固件**：`bigota.d.miui.com` / `hugeota.d.miui.com` 在本机被限到 **9 KB/s**；同一个文件在阿里云新加坡 OSS（`bkt-sgp-miui-ota-update-alisgp.oss-ap-southeast-1.aliyuncs.com`）上**直连**最快（走 7897 代理反而掉到 637 KB/s）。
- 小米 CDN **必须同时带 `-A` UA 和 `-e` Referer**，否则 Range GET 回 **403 + HTML 壳**；`bn.d.miui.com`、`cdnorg.d.miui.com` 恒 403。CDN 的 `ETag` **不等于** md5，别拿它当校验值。
- **有官方 md5 时，多连接/多源拼包是安全的**：拼完算一次 md5 对上就是对的，与它由几条连接提供无关。
- **GitHub Release 资源必须 `curl -L`**：`curl -O <release-url>` 不带 `-L` 会把 302 的空响应存成 0 字节文件，看起来"下载成功"。

相关：[[reference-local-dns-and-link-verdicts]]、[[reference-git-push-needs-local-proxy]]、
[[reference-windows-network-path-diagnosis]]、[[reference-windows-python-encoding]]
