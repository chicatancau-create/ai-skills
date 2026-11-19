---
name: reference-node-load-measurement
description: 本机 Node 24 做开放负载/CPU 采样的两个实测坑——process.cpuUsage 百分比会算出几万%，DB 测试要 --test-concurrency=1 且显式文件路径
metadata:
  type: reference
---

2026-11-09 在 E12 容量实验中实测的 Node 24 / Windows 行为：

- **不要用 `process.cpuUsage(prev)` 算进程 CPU 百分比来当饱和指标。** 同一轮里它算出 34444% / 78000% 这类不可能值（低负载也几万%）。改用 `os.cpus()` 的 `times` 差分：总时间减 idle，得到 0–100 的**整机**利用率；报告里必须写明“整机 CPU，不是服务进程独占”。
- **`node --test <目录>` 在本机不可用**；要显式列测试文件。跨文件真实 DB 测试必须 `--test-concurrency=1`，否则多个文件同时改同一 schema 会互相踩；单文件内顺序执行不受影响。
- **一键 evidence 脚本要与 npm test 同口径。** 2026-11-09 P03/P04 各踩一次：`package.json` 的 test 带了 `--test-concurrency=1`，但 `scripts/run_project.sh` 直接 `node --test tests/*.test.js`，并行文件互相 TRUNCATE 导致 40P01 死锁 / 登录 401，而单独 `npm test` 全绿。规则：runner 复制同一测试命令；新增测试文件后重跑 runner 本身。
- 开放负载要同时留 `planned`、`sent`、`done` 三个时间戳，才能算 coordinated omission 校正值（`done - planned`）和 dropped；只统计已收到响应会把排队漏掉。
- 被测服务若用 `spawnSync` 启动，超时会返回 `status=null` 且可能没有日志；先检查证据文件是否真的生成，再判断工具/服务是否成功。

**Why:** 这些不是理论问题，都是本轮实际把“全绿”跑成假数字或假失败的原因。

**How to apply:** 写负载/饱和取证时先确认指标来源与单位；报告里区分 raw/corrected、已完成/被拒绝/dropped；测试命令固定写显式文件与并发度。
