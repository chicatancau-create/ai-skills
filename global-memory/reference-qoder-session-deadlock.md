---
name: qoder-session-deadlock
description: 诊断「某个 Qoder 对话卡住、发消息没反应」：EXECUTION_TURN_ALREADY_ACTIVE 执行槽死锁的判据、后台代理仍在写盘的取证法、以及唯一解法与转接入口。
metadata:
  type: reference
---

用户报「这个工作区有个对话卡那里了」时，按这条查，别看 UI 猜。

**症状签名**（`list_chat_sessions` + 主进程日志 `AppData\Roaming\com.qoder.app.stable\logs\<启动戳>-<pid>-<hash>\main.log`）：
- 会话 `runtimeState:"error"`，每条新消息 **0.4 秒内**失败，`read_chat_session` 里 assistant 消息 `status:"failed"` 且正文为空；
- `main.log` 里 `ChatSession message delivery failed` / `ChatSession goal delivery failed` 的 error.message 恒为 **`EXECUTION_TURN_ALREADY_ACTIVE`**；查上下文用量会另报 `QODER_EXECUTION_CONTROL_FAILED`；
- 触发点通常是某一轮派了后台代理（`backgroundAgentCount>=1`），那一轮的执行槽一直没释放。

**最反直觉的一点：输入死了，执行还活着。** `messageCount` 继续涨、hook-activity 继续成对出现、目标文件的 mtime 还在往前推。**动同一个文件前先连测两次 mtime**（隔 50s 左右），确认那个代理真的停了手，否则两边互相覆盖。日志里出现 `Background subagent stop requested` **不等于**解锁——实测点了两次停止，锁仍在，代理照写。

**别做的尝试**：从别的会话用 `send_message_to_chat_session` 探测同样会撞上这条锁（可当一次性确诊探针，代价是一条 failed 记录）；`wait_chat_sessions` 对 error 态会话立刻返回 `outcome:"failed"`，等不到它的后台代理，要等只能轮询文件 mtime / grep main.log。

**唯一解法**：重启 Qoder —— 锁在进程内存的执行句柄里，会话历史落盘，重启后大概率可继续用。代价是当场杀掉那个还在干活的后台代理并打断同机其他 running 会话，属用户决策，别替他按。

**转接入口**：用户在原对话里发的图片**不用他重发**，落在 `C:\Users\Admin\<用户>\.qoder\tmp\chat-attachment-staging\<uuid>.png`，按 mtime 对上 `ChatSession turn starting` 的 `attachmentCount` 时刻即可取到。转接前把产物目录整体快照到 `%TEMP%`（`md5sum` 核过再算数），交接文档里写清「哪几条需求已完成、哪几条没做」，逐条挂本轮自产证据。

相关：[[reference-qoder-app-internals]]、[[reference-qoder-artifact-locations]]、[[feedback-verify-subagent-file-claims]]、[[feedback-rigor-audit]]
