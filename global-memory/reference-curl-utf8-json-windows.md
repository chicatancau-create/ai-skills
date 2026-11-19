---
name: reference-curl-utf8-json-windows
description: Windows Git Bash 下 curl -d 传中文 JSON 会被按本地代码页转码导致服务端 400；用 ASCII 或 UTF-8 文件 --data-binary
metadata:
  type: reference
---

在 Git Bash 里用 `curl -d "{\"name\":\"中文\"}"` 调本地 Spring/Node API，服务端可能返回 **400 invalid_json**：
MSYS 把命令行参数按本地代码页（GBK）转换，发出的字节不是 UTF-8。ASCII 字段（如 `Java Migration`、`contract-task`）
不会触发；纯 JSON 解析测试也可能因此误判为接口 bug。

**Why:** 2026-11-07 Java/MySQL 冒烟脚本两次因此失败（建组织、建任务），而应用内 JUnit 用 UTF-8 字符串完全正常。

**How to apply:**
- 冒烟数据尽量用 ASCII；需要中文时把 JSON 写入 UTF-8 文件，`curl --data-binary @payload.json`。
- 解析响应统一 `python -X utf8`；不要把这类 400 当成服务端校验缺陷。
- 相关：[[reference-windows-python-encoding]]、[[reference-windows-batch-entry-encoding]]。
