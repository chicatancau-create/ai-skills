---
name: reference-chrome-bookmarks-and-connector
description: Chrome 新版书签存在 AccountBookmarks（带 checksum，不可外部改写）；Qoder 浏览器连接器有三个坑——evaluate 返回值被吞、导航失败会回报上一个 URL、tab id 会变
metadata:
  type: reference
---

**找书签数据**：Chrome 12x+ 的账号书签不在传统 `Bookmarks` 文件里，而在
`%LOCALAPPDATA%\Google\Chrome\User Data\<profile>\AccountBookmarks`（明文 JSON，含 `roots` 树）
加一份 `EncryptedAccountBookmarks2`（`v20` OS-crypt 头）。**profile 下没有 `Bookmarks` 不等于没书签** ——
先列目录找 `AccountBookmarks`，别据此断定用户"书签丢了"。本机 4 个 profile 里只有 Default 有数据。

**改写这个文件不生效（2026-10-06 已用探针证伪，别再试）**：Chromium 按同步协议的 `EntitySpecifics`
算 `checksum`，我用 9 种序列化都复现不出文件里的现值。于是做了个可回滚实验：优雅关闭 Chrome（会存会话）→
往 `AccountBookmarks` 加一个测试目录 → 带 `--restore-last-session` 重启 →
**Chrome 自己重写了该文件、丢弃测试目录、并把 checksum 换成它的新值**（`a02164ce…`→`5057adba…`）。
说明明文 `AccountBookmarks` **不是权威源**（加密库/云端才是），外部写入会被无声回滚，
而不是"算错校验和才回滚"。加上连接器 `navigate` 只支持 http(s)（进不去 `chrome://bookmarks`）、
导入要点的原生文件选择框也驱动不了 ——
**结论：替用户"直接替换收藏夹"这件事我没有安全实现路径**，只能交付 Netscape 格式 HTML +
两下点击（`Ctrl+Shift+O` → `⋮` → 导入书签）。做这类任务前先把这条边界讲清，别承诺"我帮你导进去"。

**标签分组不是书签**：侧边栏里带 `×` 和"新标签页"的那组（常用 / AI中转站 / 编程教学）在任何 profile 的
书签树里都搜不到 —— 它们是标签页分组。分组数据在 `Sessions\Session_*`/`Tabs_*`，格式是 `SNSS` 魔数 +
version 3 头 + **压缩 body**（我两次帧偏移假设都错，别再啃）。可行的替代：把侧边栏可见标题抄下来，
去 Chrome 的 `History`（SQLite，表 `urls(title,url)`；运行中要先 `shutil.copy` 一份再 `mode=ro` 打开）
里按标题匹配反推 URL。用户真实窗口的标签页连接器看不到。

**批量抓正文的三个坑**：① **GBK 站**（52pojie、中关村在线、太平洋电脑、西西软件园、pc6）按 UTF-8 解会出
乱码并被误判成"标题不符"，必须读 HTTP 头与 `<meta charset>` 再解码；② **B 站等返回压缩体**，
不解压得到的是乱码，别当"抓到正文"；③ **平台域名不决定主题**（zhihu / csdn / bilibili / weixin / bing
只是托管方，按它们分类会把数学、英语、HTML 全抹平），主题要靠标题+关键词；
主机匹配必须用注册域后缀（`host == h or host.endswith('.'+h)`），否则 `x.com` 会误咬别的域。
`take_snapshot` 默认只给交互节点，要全文得 `verbose:true` + `filePath`。

**Qoder 浏览器连接器（mcp__user-browser-use）的三个实测坑**：

1. `evaluate_script` 的返回值取不回来 —— 不带 `filePath` 时只回 `{}`，带 `filePath` 时文件里也是 `{}`。
   想让脚本产出数据，只能让它**写进 DOM**（`document.title` / `<pre>`）再 `take_snapshot`，
   或者把结果 POST 回一个本地服务。
2. `navigate_page` **导航失败时会把上一个页面的 URL 当结果回传**（实测：qqtn.com 失败后返回
   "redirected from qqtn.com" 却指向知乎）。判据：返回 URL ≠ 请求 URL 即为加载失败；
   标题只剩主机名 + `take_snapshot` 报 "Accessibility tree not available" 也是失败签名。
3. `list_pages` 只看到连接器自己那个标签页（用户真实窗口的标签页看不到），且 tab id/groupId 会变，
   报 `No tab with id: ...` 时要重新 `list_pages` 取新 id。

**How to apply:** 要批量读网页内容，优先在服务端并发抓取 + 解析 `<title>`/`meta description`/正文；
只对 JS 空壳页（正文 <220 字符或含 "enable JavaScript"）走浏览器。注意 **B 站等站点会返回 brotli/gzip
压缩体，不解压会得到乱码**，别把乱码当"抓到了正文"。`take_snapshot` 默认只给交互节点，
要全文得 `verbose:true` + `filePath`。

Related: [[reference-inapp-browser-verification]], [[reference-windows-batch-entry-encoding]], [[feedback-rigor-audit]]
