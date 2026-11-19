---
name: reference-bilibili-open-api-read
description: B站公开接口匿名读数据的实测边界：card/view/reply/弹幕 XML 可用，space arc/search 与 seasons 被客户端指纹拦；封面 CDN 要 UA+Referer；影视飓风 mid=946974（8019627 是别人）。
metadata:
  type: reference
---

2026-11-04 做「影视飓风」账号分析时逐条实测的 B站**匿名读**通路（curl + 浏览器 UA + `-e https://www.bilibili.com/`，无登录态、无 Cookie）：

**可用（返回 code=0，字段就是页面口径）**
- `x/web-interface/card?mid=<mid>&photo=false` → `fans`、`data.like_num`（账号累计获赞）、`data.archive_count`（主投稿数）、`Official.title`（认证原文，含"2025百大UP主"这类）、`sign`（个性签名原文）、`face`（头像直链）、`attention`。注意 `regtime` 返回 0、`place`/`birthday` 常为空，**注册时间这个接口给不了**。
- `x/web-interface/view?bvid=<BV>` → `title / pubdate / duration / desc / dynamic / owner / stat(view,like,coin,favorite,danmaku,reply,share) / pages`。**无风控**，是逐条取代表作数据最稳的一把。简介 `desc` 里常有固定话术与片尾职员表原文，可做"语言风格"证据。
- `x/v2/reply?type=1&oid=<aid>&sort=2&ps=N&pn=1` → 按点赞排序的高赞评论（含 `member.uname`、`like`、`content.message`）。`sort=2` 是点赞序；`data.upper.top` 是 UP 主置顶。
- `comment.bilibili.com/<cid>.xml` → 弹幕原文，可数词频（实测「无限进步」在 5 条视频里 171–1302 次）。
- 封面：`https://i{0,1,2}.hdslb.com/bfs/archive/<hash>.jpg`，**必须带 `-A` UA 和 `-e https://www.bilibili.com/`**，否则 CDN 拒；返回字节实测全是 JPEG（不是 webp），按真实魔数存扩展名。

**匿名不可用（别浪费时间重试）**
- `x/space/wbi/arc/search`（空间投稿列表）→ curl/Python 一律 `-401 非法访问` / `-352 风控校验失败` / `-403`。即使**自己逆出 wbi 签名并验证 `w_rid` 与浏览器一致**仍然被拒，拦的是客户端 TLS/Header 指纹，不是签名。要拿投稿序列只能走真实浏览器渲染（js_reverse / browser-use MCP 导出页面自己发出的响应）。
- `x/polymer/web-space/home/seasons_archives_list` → 直接回 HTML 403 页。
- `x/web-interface/search/type` 在浏览器里点"最多播放"这类程序化点击会被识别（`dm_img_inter` 里带点击元素 class 的 base64）→ `HTTP 412`。绕行：搜索接口 `order=click` 多页召回 + 逐条 `view` 复核，并在交付里写明这是"已核验的最高播放代表作"而非"官方最多播放榜"。
- `x/player/v2`、`x/player/wbi/v2` 匿名返回 `subtitle.subtitles=[]`；`x/web-interface/view/conclusion/get`（AI 摘要）匿名 `-403`。⇒ **逐字口播台词拿不到，不要编造引号内的话**。
- 空间页 HTML 里「投稿 999+」是上限显示，与接口 `archive_count`（实测 951）并存不矛盾，报告里要分开写。

**账号 ID 备忘**：影视飓风 B站 **mid=946974**（粉丝 1890.9 万、获赞 1.31 亿、951 稿，2026-11-04 实测）；`8019627` 是另一位普通用户「♂星空·传奇♀」，网上/任务书里流传的 8019627 是错的。矩阵子号「亿点点不一样」mid=407054668。对标可用：极客湾 25876945、Linksphotograph 3816626、Thomas看看世界 277329684。

**How to apply:** 需要中文平台公开数据做账号分析/资料核验时，先 `card` + `view` + `reply` + 弹幕 XML 这四把（都能匿名、都是页面口径原值）；投稿序列与字幕必须走浏览器；任何"未取到"照实写未取到。相关：[[reference-bilibili-fav-api]]（写侧接口与 412 配额）、[[reference-chaoxing-mooc-scraping]]（同为"同源/登录态决定成败"的取证教训）、[[feedback-rigor-audit]]。
