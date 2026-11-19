---
name: feedback-toolkit-is-tools-only
description: D:\QoderToolkit 只放工具与技能本体,任何工作产物(页面、报告、截图、证据、临时件)一律不许落在里面。
metadata:
  type: feedback
---

`D:\QoderToolkit\` 是**工作机**,不是仓库、不是输出目录。里面只允许有:技能实体(`ppt-master`、`web-taste`、`web-kimi`)、自建技能目录、以及那本台账 `README.md`。

**Why:** 2026-09-24 我为了"怕工作区被并发会话清掉",把重建的落地页与登录页放进了 `D:\QoderToolkit\demos\`,用户当场否掉并要我迁回工作区 —— 工具目录混进产物会让它不再可移植、不再可备份,也让"哪些是能力、哪些是一次性输出"分不清。

**How to apply:**
- 交付物回到当前工作区(如 `E:\AIrenwu\<项目名>\`);取证中间件(截图、探针副本、dump)只放 `%TEMP%\<用途>\`,跑完即删。
- 担心产物被别的会话当垃圾扫掉,正确做法是**告知用户位置**或按用户指定归档,而不是塞进工具目录。
- 页面丢了可以靠技能重跑再生,不必为"保命"把产物寄存在工具集里。
- 相关:[[skill-placement-convention]]、[[qoder-toolkit]]。
