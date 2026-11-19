---
name: plain-language-first
description: When the user says 我不懂你现在说的东西, stop explaining internals — restate as visible behavior and copy-paste commands, then answer the outcome they asked for
metadata:
  type: feedback
---

当用户说「我不懂你现在说的东西，但是我想提个要求…」时，**不要换个说法再解释一遍技术细节**。他把需求转成了结果描述，我要回答的是那个结果。

**Why**：2026-09-20 在本地模型部署任务里，我连着讲 GGUF 元数据、mmproj、CLIP 架构、Job Object。用户直接说看不懂，然后提出真正想要的：「我发图片给它的时候，它能自动开启这个功能去识别图片」。正确答案不是再解释一遍视觉塔，而是「已经是这样了，你贴图它就能看见，我刚实测过」+ 一条自查命令。同理，他在导入对话框里问「选项应该怎么选」，要的是「点取消，别导入」这一句，不是一堂多模态课。

**How to apply**：
- 先给**结论 + 他该做什么**（点哪个按钮 / 粘哪条命令 / 什么都不用做），技术原因放在后面且尽量短。
- 用他能观察到的现象做证据（「我发了一张蓝底圆圈，它回答『这是一个蓝色的圆形』」），不要用架构名词做证据。
- 他看不到也不需要看到的中间产物，明确说「不会在列表里出现，这是正常的」，否则他会去找那个东西并误操作。
- 每次给一个**失败时怎么办**的自查命令（例如 `curl http://127.0.0.1:8080/v1/models` 看 running 还是 stopped），让他在我不在的时候能自己判断。
- 涉及安全/费用的点要翻译成人话：不是「lan_accessible: true」，而是「局域网里别人也能免密用你的显卡」。
- **他看不懂英文界面**（2026-10-08：「我不会英文，不会操作」）。所以：能自己用 computer-use 点掉的就别让他点；
  非要他点时，写成「切到标题为『登录 - Google 账号』的那个 Chrome 窗口 → 选 <已脱敏昵称> → 一路允许」这种带可见锚点的句子，
  不要贴英文菜单原文或术语。

相关：[[user-role]]、[[feedback-autonomous-execution]]、[[reference-computer-use-blocked]]
