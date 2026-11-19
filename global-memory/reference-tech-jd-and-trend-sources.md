---
name: reference-tech-jd-and-trend-sources
description: 判断「技术是否主流/岗位是否达标」时的可用检索源与其口径限制：官方调查可用，公司招聘官网 SPA 检索不到，WebFetch 失败判不了死活
metadata:
  type: reference
---

2026-11-04 做「全栈计划是否主流、是否达到企业/字节要求」时实测的检索通路：

## 能直接拿到数的官方口径

- `https://survey.stackoverflow.co/<年>/technology` —— 语言/数据库使用率（当年给到 JavaScript 62%、SQL 58%、Python 58%、TypeScript 44%、PostgreSQL 58%）。
  **注意**：正文里不一定有 Node.js / React / Vue / Docker / K8s 的分项，别假装量到了。
- `https://github.blog/news-insights/octoverse/...` —— 语言排行按 **GitHub 月度贡献者数**，与搜索热度口径完全不同（Octoverse 2026：TypeScript > Python > JavaScript）。
- `https://www.tiobe.com/tiobe-index/` —— 搜索热度口径。**2026-10 起官方加入中文搜索词（权重为英文的 44.2%）**，所以 2026-10 前后的名次不能直接纵向比。
- `https://top10.owasp.org/2025/...` —— OWASP Top 10:2025 正式版入口；`owasp.org/Top10/2025/zh-Hant` 会 308 跳到这个域，要按提示重取。

## 公司 JD 检索

- **`jobs.bytedance.com` 这类 SPA 招聘站在 WebSearch 的 `allowed_domains` 里检索返回零结果**（页面不被索引）。
  可行路子：搜「公司名 + 岗位名 + 职位要求」，命中牛客、高校就业网、国家大学生就业服务平台上**转发的 JD 全文**，再明确标注「第三方转载的 JD 样本」而不是官方口径。
- 官方可直取的前端 JD 例子：`jobs.bytedance.com/campus/position/7471101478682413319/detail...`（搜索结果里能直接拿到正文）。
- 样本只代表个别团队：字节不同 BU 的栈差异很大（后端大量 Go，也收 C++/Java/Python；前端 React 与 Vue 都有岗；AI 岗要 RAG/Agent/评测/成本）。
  结论要按维度拆开给，别把一份 JD 当全公司标准。

## 取数失败不等于死链

同一轮里 `docs.github.com/copilot`、`docs.cursor.com`、`code.claude.com` 三个官方文档 WebFetch 全部 `fetch failed`。
按 [[reference-local-dns-and-link-verdicts]] 的分层判据，这只算「本通道没取到」，**不能写进交付物里称链接已验证**；要写官方入口就写清「未复核」。
