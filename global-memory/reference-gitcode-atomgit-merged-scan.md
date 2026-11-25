---
name: reference-gitcode-atomgit-merged-scan
description: GitCode 与 AtomGit 已合并为同一平台；扫 GitCode 仓库清单走活口代理+private-token 头打 api/v5/user/repos；gh 当轮未手动挂代理即可用
metadata:
  type: reference
---

2026-11-25 实测（盘点用户在两个托管平台各有哪些仓库时踩出）：

- **GitCode 与 AtomGit 已合并**：2025-10-28 起深度整合、2025-11 新一代 AtomGit 上线，账号体系打通、仓库数据互相同步（官方公告 gitcode.com/org/gitcode/discussions/11）。gitcode.com 网页标题已是「AtomGit」。本机旁证：`E:\fullstack-code` 的 `atomgit` remote 实际 URL 就是 `https://gitcode.com/zhoumoyukuai/fullstack-code.git` ⇒ 旧「GitHub/GitCode/AtomGit」拓扑实为两个平台（补充 [[feedback-round-then-push-both-remotes]]；该旧条的「多端」表述已按用户 2026-11-25 要求纠正为两端）。
- **扫 GitCode 仓库清单**：网页是 SPA 空壳，web_fetch/静态抓取拿不到数据；匿名 `GET https://gitcode.com/api/v5/users/<login>/repos` → 400 `Orchestration error: Invalid header parameter: private-token, required` ＝网关点名缺头，**不是令牌失效**。正路：`curl.exe -sS -m 25 -x http://127.0.0.1:7890 -H "private-token: <令牌>" "https://gitcode.com/api/v5/user/repos?type=all&per_page=100&page=1"`。令牌取凭据管理器 `git:https://gitcode.com`（UserName=zhoujinwei，规范 login=zhoumoyukuai），只留内存绝不回显；7890 是当轮活口（7897 已死、gitcode.com 直连超时），端口会漂每轮试连。
- **GitHub 侧**：gh 当轮未手动挂代理即可用；`gh repo list <login> --limit 300 --json ...` 与 `gh api 'user/repos?affiliation=owner,collaborator,organization_member&per_page=100'` 双查互证，防漏协作/组织仓库。PowerShell 里 --jq 表达式内嵌双引号会被剥掉致 jq 报 `function not defined: private/0`，jq 参数整体用单引号。
- 手册详记：`G:\AIrenwu\本地AI使用手册\03-通用\03-调试与验证\踩坑-GitCode合并AtomGit后repos接口要private-token头且直连超时走7890.md`（verified）。
