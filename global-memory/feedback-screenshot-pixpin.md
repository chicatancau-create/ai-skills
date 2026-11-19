---
name: screenshot-pixpin-lookup
description: 用户贴图时的两种落点：消息里的「附件引用」绝对路径优先，没有附件路径才去 C:\Users\Admin\Pictures\PixPin_*.png 按时间找最新一张
metadata:
  type: feedback
---

用户习惯用 PixPin 截图，并会以为图片已经发给我了（"我给你图片里的那个"）。

**【2026-11-15 更正】** 原来这条写的是「会话上下文里通常并没有附件」，**已经过期**。本会话 11-04 与 11-15 的三张图都是随消息以 `附件引用：文件：C:\Users\Admin\.qoder-cn\tmp\G--AIrenwu\images\<会话uuid>\<uuid>.png` 的形式给出**真实绝对路径**的，直接 Read 那个路径即可，不需要去找。只有 2026-10-18 那次是真的没附上。

**How to apply（按顺序）**：
1. 消息里有 `附件引用` 路径 → 直接读该路径。**别去 Pictures 乱翻**，那是另一批文件。
2. 没有附件路径但提到"我发的图/截图" → `find /c/Users/Admin/Pictures -iname "PixPin_*.png" -newermt "<今天>"` 按 mtime 取最新一张；次选 Desktop、`AppData\Local\Temp`（含 `QQ_*.png`）。
3. 两处都没有 → 才追问，别猜目标。

**Why:** 2026-10-18 一次「修一下那个插件」的请求里，工作目录有 6 个以上候选、memory 为空，唯一线索就是 `Pictures` 里比提问早约一分钟的 `PixPin_2026-10-18_20-16-30.png`，正是它锁定了目标。反过来，11-15 那次如果我照旧规矩去 Pictures 找，会拿到与本次问题无关的旧图。

**注意**：`tmp\...\images\` 是会话级暂存，会话清理后可能消失；要长期留证据就把图复制到工作区的 `02_证据日志`。
