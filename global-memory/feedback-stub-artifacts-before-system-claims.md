---
name: feedback-stub-artifacts-before-system-claims
description: 用内存桩替代数据库来跑真实服务端时，任何失败先怀疑桩再怀疑被测系统；jest 绕过 Module._load 要用 moduleNameMapper；桩的 WHERE 1=1/列投影/自增 id/数字串类型四个坑会把桩 bug 伪装成服务端 bug。
metadata:
  type: feedback
---

拿内存桩替掉 DB 驱动、去跑别人的真实服务端代码时：**每一条 FAIL 都要先证明不是桩自己的 bug，才能写进对被测系统的结论**；判不出来就标「未定位，归为桩的局限」，不许把桩的失败算成系统的缺陷。

**Why:** 2026-11-01 为绕开「用户没给 MySQL 口令」，把课件 Node 服务端的 `mysql2/promise` 换成内存桩。结果两轮假信号：① 课件自带 jest 测试集里 `login 500` 我一度当成服务端缺陷，后来同一条走真 HTTP 路径实测 200，才确认是桩+环境产物；
② 我自己的桩让 `/api/auth/me` 吐出 `password` 哈希，看起来像「服务端泄露密码」——真实原因是桩没实现 SELECT 列投影，而真库只回 6 列。**这类误报比漏报更贵**，因为它会让用户去改本来没问题的东西。

**How to apply:**
- **jest / vitest 绕过 `Module._load`**：`node --require hook.js` 改 `Module._load` 对普通脚本有效，但 jest 用自己的模块解析器，桩根本没被用上（错误栈直接打进 `node_modules/mysql2/lib/promise/pool.js` 就是证据）。
  正解是 jest 配置里 `moduleNameMapper: {'^mysql2/promise$': '<rootDir>/fake-mysql2.js'}`，并加 `-i`（单进程）+ `--forceExit`（服务端 listen 会让 jest 挂住不退出）。
- 自写 mini-SQL 解释器的四个必踩坑（都修过）：① `WHERE 1=1 AND x=?` —— 别把 `1=1` 当列名解析，要先滤掉常量条件；且 DELETE/UPDATE 得**只取 WHERE 子句**传进解析器，别塞整条 SQL；
  ② **SELECT 列投影**必须实现，否则 `SELECT id,username… FROM users` 会连 `password` 一起回，造出假安全漏洞；③ 自增 `id` 按表内 `max(id)+1`，别拿「参数里第一个数字」当主键（会撞车主键、连锁把后续用例带崩）；
  ④ 纯数字字符串会被我 coerce 成 Number（`phone`），而真 mysql2 对 VARCHAR 回字符串、`DECIMAL` 也回字符串 —— 涉及类型的断言要么放宽并注明，要么交给专职 handler，别当成被测系统的行为。
- **同一进程连跑两轮必出假 FAIL**（桩会改写内存状态）：换配置/换补丁必须换进程和端口，见 [[feedback-control-test-needs-restart]]。
- 更稳的做法是**分层**：先用专职小桩把「客户端请求 ↔ 服务端响应外壳/字段/可空列」逐条断言（可控、易归因），再用通用 mini-SQL 桩跑大范围回归；两者结论分开写，别混成一个「全绿」。
- 桩证永远不等于真证：报告里显式写「这是桩、真库未验」，缺凭据就摆着等用户，见 [[feedback-rigor-audit]]、[[feedback-capability-boundaries]]。
- **验证工具/门禁失败也先自证“工具侧前置条件”**（2026-11-08 托盘门禁三连假失败）：① 读到上一次实例遗留的 `runtime.json`
  （`ready=true` 但 pid/hwnd 已死）→ 启动前必须删状态文件；② 用控制台 `python.exe` 起被测程序，而用户入口是 `pythonw.exe`，
  两者在 Win11 `NotifyIconSettings` 里是不同的提升项 → 起进程的 exe 必须与真实入口一致；③ 把 `GetRect=0` 当“已注册/可见”
  （对股票/自绘/不同 uID 都返回同一块别的图标的槽位）。准则：门禁失败先区分“工具没测到”与“产品坏了”，
  报告写“工具未通过/未定位”，不能反推产品不可用，也不能用另一条路径（常驻实例截图）把失败门禁改判通过。
