---
name: feedback-api-key-handling
description: 用户明确要求：处理 Google API key 时不得触发泄露检测（org policy 默认 DISABLE_KEY + Jules/AI Studio 的 abuse auto-detection 会自动删 key）。key 一律走本机 DPAPI 保险库，只显后 6 位，并定期脱敏对话日志。
metadata:
  type: feedback
---

持有第三方 API key 时，一律走本机 DPAPI 保险库，**不再存明文文件**。

**保险库（2026-10-09 建好，4 把 Jules key 已入库）**

```
C:\Users\Admin\.gkeys\securevault.py     # DPAPI(CRYPTPROTECT_CURRENT_USER) 加解密 + CLI
C:\Users\Admin\.gkeys\vault\<label>.bin  # 密文；label = key 后 6 位
C:\Users\Admin\.gkeys\scan-exposure.py   # 全盘搜明文 key（只报路径与次数，绝不打印 key）
C:\Users\Admin\.gkeys\scrub-exposure.py  # 把明文 key 换成 [REDACTED-API-KEY-*]
                                         # 自动跳过最近 300 秒内被写过的文件（=当前会话记录）
python -X utf8 securevault.py list | verify | get <label>
```

现存 4 把 label：`5HbD4g`、`13gWhA`、`QzZsA`、`0AJzYw`。用户 2026-10-09 确认**一把 key = 一个 Google 号**；
但四把调 `/v1alpha/sources` 看到的 GitHub owner 全是 `chicatancau-create`（四个号授权了同一个 GitHub 账号）。

**规则**

1. **只存在仓库之外**：`%USERPROFILE%\.gkeys\`。**绝不**写进 `G:\AIrenwu`、`G:\CodeWeave` 或任何 git 工作树，
   也不写进 `.env`、脚本常量、README、注释、commit message。
2. **脚本一律从保险库取**（`securevault.unprotect(...)`，或 `get <label>` 走管道传给子进程），
   **不要把 key 当命令行参数传** —— 命令行会进 shell 历史、进程列表和 CI 日志。
3. **任何输出/日志/报错只打印后 6 位**；区分多把 key 也用后缀，不用前缀。
4. **不往任何网页表单、第三方诊断服务、粘贴站提交 key**。
5. **对话记录会落明文**：实测 key 出现在 `~\.qoder\projects\**\*.jsonl` 与 `~\.qoder\logs\**`。
   处置 = 跑 `scrub-exposure.py --apply`；它会自动跳过正在运行的这场会话的记录，
   **会话结束后再跑一次**才能清掉最后那份。这不属于 Google 的扫描面（扫描器只看公开源），
   真正的风险是"别人拿到这台机器"或"你把对话导出/截图外传"。
6. 新增 key 用 `securevault.py add <label>`（从 stdin 读），不要先落成明文文件再转。
7. **DPAPI 的代价**：密文与"这个 Windows 账户"绑定 —— 重装系统、换 Windows 用户、把 `.bin` 拷到别的机器，
   都**解不出来**。要跨机器就得另外做一份口令加密的备份，别指望复制 `.gkeys`。
8. **别把「让用户粘贴密钥」设计成需要他自己敲命令行的流程**。2026-10-15 我给了个 `getpass` 隐藏输入的脚本，
   用户却把令牌**直接粘在 PowerShell 提示符**上当命令执行（报 CommandNotFoundException），令牌于是明文进了
   `%APPDATA%\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt`（实测命中 1 行）+ 他发来的截图。
   ⇒ 给隐藏输入流程时必须写清「先回车跑命令、**等出现提示语**再粘」；事后主动查那个历史文件
   （只报命中行数与路径，绝不打印内容），并建议**吊销重发**。清历史要先备份再改。
9. **git 的 PAT 不进 `.gkeys` 明文文件**，走 Windows 凭据管理器（`git credential approve` → GCM）。
   `.gkeys/<host>.txt` 只作临时中转；优先用 `--prompt`/getpass 直取不落盘。判「用户到底写没写这个文件」
   要看 **mtime + 内容**，别听转述 —— 同一轮里用户两次说「已填」，实测 mtime 没动、值仍是空。
   凭据是否真落库的判据见 [[reference-git-credential-manager-windows]]。

10. **用户发来的截图里可能带明文密码/验证码**。2026-11-10 他拍屏给我看小米账号登录框，密码整串可见
    （`2007914zjwZJW…`）。处理方式：**不复述、不记录、不写进任何文件**；一句话提醒"这张图里密码是明文，
    如果截图会外传/同步云建议改密并开两步验证"，然后继续干活，别反复说教。
    他自己是接受这种风险的，提醒到位即可，不要因此拒绝继续。

**Why:** 用户 2026-10-09 主动发来 Google Cloud 组织政策文档，要求「避免触发警报把 key 封了」。
两处独立机制都会自动处置泄露密钥：

- `iam.serviceAccountKeyExposureResponse` —— **自 2024-06-16 起不设置也默认 `DISABLE_KEY`**，
  检测到公开泄露（如公共代码库）即自动停用；受监控对象含「长期服务账号密钥 + 绑定到服务账号的 API 密钥」。
- Jules / AI Studio 的 key 页面自己写着 `Abuse auto-detection on — any API keys found to be publicly exposed will be automatically disabled`。

Google 同时声明**不保证能检测到泄露**，所以不能指望"没被抓到就没事"。

**How to apply:** 任何涉及这些 key 的脚本、派发给 Jules 的任务、日志与交付物。
相关：[[reference-jules-coding-agent]]、[[feedback-no-unverified-cause-claims]]
