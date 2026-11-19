---
name: reference-owasp-zap-local
description: 本机 OWASP ZAP 2.17.0 Core 的位置与实测边界——CLI 可启动，但 quick scan（-quickurl）420 秒超时且不产出报告，不能据此声称扫描通过
metadata:
  type: reference
---

本机 ZAP 安装与扫描实测（2026-11-09）：

- 位置：`D:\ZAP\ZAP_2.17.0`（Core zip 从 GitHub release 下载，经 7897 代理，约 103MB）。
- 启动：`zap.bat -version` 可用（系统 Java 25.0.2），输出 `2.17.0`；启动时会提示插件可能过期。
- 失败样本：`zap.bat -cmd -quickurl http://127.0.0.1:<port>/scan -quickout evidence/zap-report.xml -quickprogress`
  运行 420 秒后由 `spawnSync` 超时杀掉（`status=null`），**未生成报告**，工作目录也没有 `zap.log`。
- 因此：ZAP 已安装 ≠ 扫描已执行；没有 `zap-report.*` 时，README/证据只能写“尝试失败/未产出报告”，不能写“ZAP 通过”。

**Why:** E11 的验收要求 ZAP baseline/主动扫描；第一次尝试只证明二进制能启动，不能替代扫描结果。把超时写成通过会伪造验收。

**How to apply:** 下一步优先用 `zap.bat -daemon` 起 API 再分步 spider/ascan，或先检查 Core 包是否缺 quickstart/spider/ascan 插件；仍失败就把 E11 的 ZAP 项保持未闭合，不要用手工 PoC 冒充。相关：[[feedback-rigor-audit]]、[[reference-large-file-download-on-this-box]]。
