---
name: feedback-probing-side-effects-on-user-data
description: 我的探测/取证动作本身会造出真实损害（POST {} 写进用户库、uninstaller 删掉内核、误判服务）——承诺"只读"必须有具体闸门与收尾自证，不能靠启发式或感觉。
metadata:
  type: feedback
---

**对陌生系统做批量探测前，先证明"我这一轮不会产生写副作用"，并在结束时自证。承诺"我不会改你数据"不能靠 URL 关键字之类的启发式来兜。**

**Why**：2026-11-04 一天内三次：

1. 我给一个 Spring Boot 课程后端做"只读"冒烟，用 `READ_HINTS=('list','get','findone',…)` 按 URL 子串分类端点。
   **`register` 里含 `get`** ⇒ `/user/register` 被判成读端点，我对它发了 `POST {}`，
   服务端照单全收并往 `t_users` 插了一行全 NULL（id=77）。那个服务 **16 个端点全是 POST**，
   所以「用 GET 才危险」这条直觉完全失效；而 `@RequestBody Users` 收到 `{}` 就是全 null 实体，`save()` 照样成功。
2. 更早一轮我因为非提权读不到 `C:\ProgramData` 就判服务已坏，重装时**拆掉了正在跑的内核**，断网 5 分钟
   （见 [[reference-windows-permission-denied-as-missing]]）。
3. 同日修 Verge 时我跑的 `clash-verge-service-uninstall.exe` **连带删掉服务 `cores\` 里的两份内核**，
   把"修一个降级"变成"修两个病"，其中第二个是我自己造的。

**How to apply**：

- **闸门三条**（对已有数据的实例做探测时全部要过）：
  ①只打**无必填 body 参数**的端点（从 api-docs 取 `parameters[].required/in`；空 body 打必填参数
  只会得到 500，或更糟——全默认值写入）；
  ②动作型动词显式进黑名单：`register/login/logout/upload/download/pay/send/reset/submit/import/exec`，
  **别只列 add/update/delete**；
  ③**收尾自证清白**：对可能被动过的表复核行数/最大 id，并把结果打出来。
- **误写之后**：先取证留档（id、字段值、表行数），再给出一条收紧的 `DELETE`（带全部 NULL 条件 + 期望影响行数），
  **等用户点头才删** —— 对他数据库的 DELETE 属于不可逆共享状态变更，不因为"是我造的垃圾"就自动动手。
  顺带记录：删行不会回退 auto-increment。
- **跑任何 uninstall/install 型工具前，先假设它会清空自己的数据目录**：先备份那个目录，或改走应用自己的修复按钮。
- **"我差点把没打印当成没问题"是同一族**：报错只进我看不见的地方时，症状是日志缺行，
  见 [[reference-unattended-elevated-scripts]]。
- 报告时**如实区分**哪些损害是我这一轮新造的，别混进"原有故障"。用户明确认可这种披露。

相关：[[feedback-destructive-file-ops]]、[[feedback-rigor-audit]]、[[feedback-capability-boundaries]]、
[[reference-windows-permission-denied-as-missing]]、[[feedback-no-unverified-cause-claims]]
