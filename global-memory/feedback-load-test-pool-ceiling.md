---
name: feedback-load-test-pool-ceiling
description: 压测并发要压过连接池上限；Prisma 默认池在 50 并发下会 500/长尾，URL 加 connection_limit=20 后归零；事务内辅助查询必须复用当前 client。
metadata:
  type: feedback
---

压测的并发数必须**大于**连接池上限，并记录错误状态分布；否则池饥饿会被低并发单测完全掩盖。

**Why:** 两起同类事故。① 项目 03 下单接口 15/15 单测全绿，20 并发 × 240 请求全挂起，根因是事务 `connect()` 后又 `pool.query()` 申请第二条连接，形成互等。② 2026-11-08 P02 压测：50 并发、默认 Prisma 池时出现 4 个 500、P99 2.2s；把 `DATABASE_URL` 加 `connection_limit=20` 后 2000 请求 0 错误、QPS 575、P99 120ms。低并发测试两起都发现不了。

**How to apply:** 事务内辅助查询显式传当前 `client`；提交前 grep 事务块里是否还有 `pool.query`。压测脚本并发要超过池上限，`fetch` 加超时，输出 P50/P95/P99、错误数/错误状态码、DB 连接数，并同时断言业务不变量（成功数、库存/席位、持久化行数）。Prisma 项目在测试/压测 URL 里显式写 `connection_limit`，并在 README/证据里记录池大小，别把默认池当无限。
