---
name: reference-chaoxing-mooc-scraping
description: 用 Qoder 内置浏览器（browser-use MCP）抓学习通 mooc1.chaoxing.com 课程内容的可复用机制：切章节、读 iframe 正文、拿附件 objectid 与真实下载地址、会话极易失效。
metadata:
  type: reference
---

学习通课程页主要靠 browser-use（内置浏览器带登录态）。**fetch 能不能通用要看具体路径，别再一刀切**：
2026-11-01 在 `studentstudy` 顶层页里 `fetch('/mycourse/studentcourse?courseId=&clazzid=&cpi=&enc=&mooc2=1', {credentials:'include'})` **成功**（200、188 KB，拿到全课目录）；
`fetch('/mooc-ans/knowledge/cards?...')` 同源也通；**但换成跨域主机 `https://mooc-ans.chaoxing.com/...` 就是 `Failed to fetch`** —— 必须走**当前页同源的 `mooc1.chaoxing.com`** 前缀。
顶层页 `GET studentcourse`（无参数/不同上下文时）仍会被 CSP 挡。2026-11-01 实测有效的手法：

- **取全课目录（结构/节数/哪节叫「作业」）**：fetch `studentcourse` 后 `DOMParser`，**`.chapter .head` 选择器在这份 DOM 里取不到标题**（返回 1 个空条目，我白跑两轮）；
  能用的是 `[...doc.querySelectorAll('a[href*="studentstudy"]')]` 取 `textContent` 去重（62 节全出来），章标题再对**原始 HTML** 正则 `/第\d+章[^<]{0,30}/g`。
  单节正文用 `fetch('/mooc-ans/knowledge/cards?clazzid=&courseid=&knowledgeid=<chapterId>&num=1&cpi=')`，`body.textContent` 前段就是任务原文（后半是页面脚本 `mArg` JSON，`attachments` 在里面）。

- **切章节**：目录条目不是 `<a href>`（`querySelectorAll('a')` 匹配 `chapterId` 会得到 0 条），而是
  `<span class="posCatalog_name" onclick="getTeacherAjax('<courseId>','<clazzid>','<knowledgeid>')">`。
  直接在顶层页 `window.getTeacherAjax(...)` 调用即可切内容，比点目录稳。
- **读正文**：内容在 `document.querySelector('iframe').contentDocument`（同源）。取 `body.innerText` + 附件节点。
- **附件**：正文里每个附件是一个 `.ans-attach-ct` 节点，内含一个 `iframe[module=downloadfile]`，
  它的 `data` 属性（HTML 实体转义的 JSON）直接给出 `objectid / name / size` —— **不用点开就能拿到文件名和 id**。
  视频类附件另有 `mid`，走 `richvideo/initdatawithviewerV2`。
- **真实下载地址**：别猜 `/ananas/attachment/{id}?enc=`。用 `list_network_requests`（`includePreservedRequests`，类型给 xhr+document）
  回看浏览器自己发出的请求，签名直链在 `https://dN.cldisk.com/download/{objectid}?at_=&ak_=&ad_=&fn=` 上，
  由 `/ananas/status/{objectid}` 返回。**自己主动取**：只要顶层页 origin 还是 `mooc1.chaoxing.com`，同源
  `new XMLHttpRequest()` GET `/ananas/status/<objectid>` 直接回 `{download, filename, crc, length}`（`fetch` 在部分页面被 CSP 挡，XHR 可用；
  iframe 内的模块页也能用 `inner.contentWindow.XMLHttpRequest` 绕开顶层 CSP）。签名有时效，拿到就下。
- **curl 下 cldisk 必须带 UA + Referer**：裸 curl 拿签名直链回 403（我误判成「链接失效」）；加
  `-A "Mozilla/5.0 ... Chrome/131" -e "https://mooc1.chaoxing.com/"` 后 200，字节数与 `length` 完全一致。返回体先 `head -c` 看一眼，403 时是 HTML 错误页。
- **其他任务点的正文与附件**：顶层页 `fetch('/mooc-ans/knowledge/cards?...&num=N')`（N=1/2/3…）是**可用**的，
  用 `DOMParser` 取 `#pageDiv.textContent` 就是图文全文（比 iframe 稳）。但 `num>=2` 的附件**不在解析后的 DOM 里**，
  是页面脚本 `mArg` 的 JSON —— 对原始 HTML 正则 `"objectid"` / `"name"` 才能捞到文件名和 id。
- **目录取 ID**：条目是 `div.posCatalog_select`，`id="cur<knowledgeid>"`（`querySelectorAll('a')` 匹配 chapterId 得 0 条）。
  一级标题是 `div.posCatalog_select.firstLayer`。
- **别用 grep 扫课程目录找接口**：SVG 资源里全是 `xmlns="http://www.w3.org/2000/svg"`，`grep -r "http"` 会被几十 KB 图形 XML 淹没；
  限定 `--include=*.ets --exclude-dir=.git`，或只 grep `createHttp|rcp|:3000|localhost`。
- **致命副作用**：在 iframe 里 `dispatchEvent(click)` 触发下载会把**顶层页导航走**，返回 `Inspected target navigated or closed`；
  之后 evaluate 的相对 URL 会解析到 `d0.cldisk.com` 而不是 mooc1，取到的 `/ananas/status/` 一律 403（我据此误判过一次）。
  而且**这一下就把学习通登录态整站打回 `passport2.chaoxing.com/login`**，我这边无法恢复，只能让用户重新扫码（本轮实测：扫码后恢复，
  但隔天/隔天级会话也会自己死，`enc` 参数换页即失效，别把旧 URL 当长期入口）。

**Why:** 学习通的会话和 `enc` 参数都短命，一个多余的导航就前功尽弃；而资料（服务端安装包、验收演示）只挂在附件里，本地磁盘和课件仓库都没有。

**How to apply:** 按「先读清单、再取 objectid、最后一次性下载」的顺序做，全程只用 `getTeacherAjax` + 读 iframe + 看网络请求，**不要点附件**；
需要真下载时把 objectid 交给用户，或在自己有把握的独立回合里做。取到章节 ID 后先 `evaluate` 抓 body 文本存下来，
再考虑动任何会改页面状态的元素。鸿蒙课程那套的 ID 与附件见 [[project-harmony-course-status]]。
相关：[[reference-inapp-browser-verification]]、[[reference-computer-use-blocked]]、[[reference-chrome-bookmarks-and-connector]]。
