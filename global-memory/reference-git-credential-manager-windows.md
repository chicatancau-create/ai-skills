---
name: reference-git-credential-manager-windows
description: 本机 git 凭据判据（cmdkey 目标名要带 https://、GCM 无 list、fill 探测会弹窗回显明文、push --dry-run 会删凭据）+ 认证失败伪装相 + 证「写凭据可用」的四步对照法 + gitcode/atomgit 同后端 + Gitee 私有仓库与账号存在性的免凭据判法 + PAT 入口
metadata:
  type: reference
---

2026-10-15 实测，本机（Windows + Qoder 自带 git）的 git 凭据取证要点。

**三个会骗人的判据**

1. **`cmdkey /list:git:<host>` 是假阴性。** GCM 存进 Windows 凭据管理器时目标名是
   `git:https://<host>`（**带 `https://`**）。少写一段会回「* 无 *」，看起来像没存。
   我当时就据此错报了「凭据没有落库」，实际 `目标: LegacyGeneric:target=git:https://gitcode.com` 明明白白在。
   要枚举只能跑全量 `cmdkey /list` 再 grep `git:`；输出是 **GBK**，用 python `decode('gbk')` 处理
   （见 [[reference-windows-python-encoding]]）。
2. **GCM 没有 `list` 子命令**，只有 `get / store / erase / configure / unconfigure / diagnose / azure-repos / github`。
   二进制在 `C:\Users\Admin\.qoder\bin\git\mingw64\bin\git-credential-manager.exe`（`--system` 级 helper）。
3. **`chmod 0600` 在 Windows 上是 no-op**（只影响只读位）。别把 python `os.chmod` 的返回值当权限证据；
   真实保护看 NTFS ACL，用 `icacls <file>` 查（本机 `.gkeys` 下的文件是 `ZHOUMO\Admin:(I)(F)`）。

**不泄露密钥的「有没有凭据」探针**：把 `protocol=https\nhost=<h>\n\n` 喂给 `git credential fill`，
env 设 `GCM_INTERACTIVE=never` + `GIT_TERMINAL_PROMPT=0`。
rc=128 + `Cannot prompt` = 本机没有该主机的凭据；rc=0 = 有（自己 mask 后只打用户名和尾号）。
**2026-11-02 我又踩了一次这条**：漏设那两个 env 跑 `fill`，GCM 当场弹出「Enter your credentials for …」GUI
等用户输入，并把 `username=` / `password=` **明文写进 stdout**（进了工具输出文件）。
判凭据在不在请优先只读 `cmdkey /list`；要让用户重填，就用真 git 命令触发，别让 `fill` 的返回值落地。

**非内置托管站要显式声明 provider**：gitee / atomgit / gitcode 都不是 GCM 内置 provider，
不加 `git config --global credential.https://<host>.provider generic` 它会去猜 OAuth 流程。

**gitcode.com 与 atomgit.com 是同一套后端**：同一个 `zhoujinwei/node` 在两个域名下匿名
`git ls-remote` 都通过、commit 号一致。判「仓库是否公开」要用**匿名 `git ls-remote`（行为测试）**，
别看网页状态码 —— 这俩站是 SPA，任意路径都回 200（见 [[reference-local-dns-and-link-verdicts]]）。
**2026-10-15 复测补一条反向判据**：裸 HTTP 打 `/info/refs?service=git-upload-pack` 两域名各 **200 / 0.4 s 且 HEAD 一致**，
而同一时刻 `git ls-remote` 走 `atomgit.com` **60 s 超时**（根因未定位，疑凭据助手交互）→
**git 侧一次超时不能判「该域名 git 不通」**，要用 smart-HTTP 报文对照，并重跑一次带 `GIT_TERMINAL_PROMPT=0`。
另记：这俩国内站直连就快，**别挂 7897**（代理只留给 GitHub 那条出境链路，见 [[reference-git-push-needs-local-proxy]]）。

**同一个 AtomGit 账号有两个命名空间，都指向同一个仓库**（2026-10-15 实测）：
`gitcode.com/zhoumoyukuai/fullstack-code.git` 与 `gitcode.com/zhoujinwei/fullstack-code.git`
匿名 `ls-remote` 返回**同一个 HEAD**，网页 title 也一致 → handle 与显示名都能当路径用，别据此以为有两个账号。
**Gitee 的判存在性方式不同**：不存在的仓库回 **401 `[session-xxxx] Unauthorized`**（私有/不存在不区分），
而 AtomGit 回 403「could not be found」+ 网页 404 ⇒ **在 Gitee 上不能靠匿名 HTTP 状态码判仓库是否存在**。
**2026-11-02 补一条可判的方法**（免凭据两步，实测有效）：
① 抓 `https://gitee.com/<属主>/projects` 的公开仓库列表看目标名在不在（本轮 `lzy_syx` 列表里有
`harmonyMall`/`testStore` 而**无** `mymall`，私有仓库页回 403）；② `GIT_TERMINAL_PROMPT=0 git ls-remote` 匿名试取。
两步交叉才能判「私有/不存在」，单看仓库页状态码不行（403 与反爬同码）。
本轮的教训是：`Incorrect username or password` 出现时**先做这两步再动凭据**——我先前让用户重填了一遍，
其实那个仓库根本不在他权限范围内，同名的 `harmonyMall` 才是能匿名直取的那个。

**判"某个桌面 App 装在哪"要读卸载注册表的 `DisplayIcon`，别看 `InstallLocation`、也别猜目录名**
（2026-10-19 实测）：NSIS 类安装器常把 `InstallLocation` 写成**空**，而 `DisplayIcon` 是
`<exe 路径>,0`（去掉 `,0` 即真路径）。同一轮还证实**应用自动升级会换目录**：
WorkBuddy 国内版从 `D:\WorkBuddyAIguonei\` 搬进 `D:\WorkBuddyAIgouji\`（旧目录只剩 debug.log+version），
于是此前写死的 `WORKBUDDY_ELECTRON_BIN` 变成死路径 —— **凡"给插件写死可执行路径"都有这个到期日**，
处理顺序见 [[reference-windows-process-env-inheritance]]。

**访问令牌（PAT）入口与用法**：右上角头像 → 个人设置（左侧「API 密钥」/「访问令牌」）→ 新建。
用户自己的 handle 是 `zhoujinwei`，AtomGit 显示名是 `zhoumoyukuai`（最早那条
`gitee ... zhoumoyukuai: Incorrect username or password` 报错里的名字就是它；
**2026-11-02 更正**：gitee 上那个仓库页回的是 **403** 不是 404 —— 私有页与反爬同码，所以状态码本身判不了存在性，
判法见上面「属主 /projects 列表 + 匿名 ls-remote」两步）。
文档列出的 scope 只有 `project` / `Issue`，**没有 GitLab 式的 `write_repository`**，别照抄别家的权限名；
git over HTTPS 用 PAT 当密码、用户名就是 `@` 后面那个 handle。

**两个认证失败的伪装相（都别当成「令牌过期」）**

1. **GCM 弹窗的用户名默认填 `git config user.name`。** 本机当时是 `zhoumo`，而 GitCode 要 handle
   `zhoujinwei` → `HTTP Basic: Access denied`，且远端回的是
   `The password-based authentication of Git has been removed. Please use your personal access token instead.`
   —— 这句是**误导性通用文案**，实际是用户名错，不是平台禁了密码登录。
   **2026-11-02 更新**：`E:\fullstack-code` 的 `git user.name` 现在已经是 `zhoujinwei`（弹窗默认值不再错），
   同一句「password-based removed」这轮出现时真因是**令牌过期** ⇒ 这句文案两种成因都会套它，别据此归因。
2. **认证失败后 git 会调 `credential reject`，把那条凭据直接删掉。** 所以 push 失败一次之后
   `cmdkey /list` 里那个 `git:https://<host>` target 会消失。别据此判断「我没存过」，
   要看的是失败当时的报错行。

排查凭据内容时用 `git credential fill` 取出来**只看形状**：长度、有无空格/反斜杠、前 12 与后 20 字符。
有一次实际存进去的是整条 `python "…\store-atomgit-credential.py" --prompt`（97 字符、含空格），
是用户把命令本身当令牌粘进了密码框。据此给脚本加了 `^[A-Za-z0-9_\-]{16,64}$` 形状闸门。

**`git push --dry-run` 不是无副作用的探测（2026-11-02 实测，我造成的）**
它不写 ref，但**会真走一次认证**；认证一失败 git 照样调 `credential reject`，
把 Windows 凭据管理器里那条 `git:https://<host>` **删掉**（我为了验双推通路跑了一次 dry-run，
用户的 gitcode 凭据就这么没了，只能让他重填）。而且**多 `pushurl` 时 git 撞第一个失败就中止**，
后面的 URL 根本轮不到 ⇒ 「一次落两端」的结构决定了**一端凭据坏 = 两端都推不上**。

- 探通路：用 `git ls-remote`（纯 fetch，不触发 reject），或显式**单个** URL。
- 反过来，「只为弹认证窗并把凭据落盘、又不发布任何东西」的安全写法：
  `git push --dry-run https://<host>/<owner>/<repo>.git main:refs/heads/cred-check`
  （临时 ref 名 + 显式单 URL；dry-run 不创建 ref，但认证真实完成并已存进凭据管理器）。

**证「推送凭据真的可用」要凑齐四步对照，缺一步都下不了结论（2026-11-02，被用户追问「真的通了吗」后补做）**

```
① GET /info/refs?service=git-upload-pack   -> 200   匿名可读 ⇒ 读操作（含 ls-remote）不能当凭据证据
② GET /info/refs?service=git-receive-pack  -> 401   匿名写协商被拒 ⇒ 该端点真校验
③ 带明显错的凭据打 receive-pack            -> 401   不是「给什么都放行」
④ GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never git push --dry-run <单URL> main:refs/heads/x -> rc 0
   禁掉一切弹窗 ⇒ 能用的只能是"已落盘"的那条，不是弹窗当场输入的内存凭据
⑤ 收尾断言：git ls-remote --heads 里没有那个临时 ref 名（证明确实没发布）
```
我最初拿「`ls-remote` 拿得到 refs」当凭据通了，被用户一句质疑问倒——公开仓库匿名就能读，那是假证据。
另记：`gitcode.com` 解析当时要 **11.4 s** 且偶发 `Could not resolve host`，一次 A/B 整组因此作废
⇒ **网络层失败会污染认证实验**，先 `curl --resolve <域名>:443:<IP>` 绕开 DNS 再测（见 [[reference-local-dns-and-link-verdicts]]）。

**gitee 与 AtomGit/GitCode 是两套独立账号体系**（2026-11-02）：课件给 `gitee.com/<owner>/<repo>.git` 时，
拿 AtomGit 的账号密码去填 gitee 弹窗必然失败；同一仓库路径在 `atomgit.com` / `gitcode.com` 下回
`<CH.00905403> The project you were looking for could not be found` + 403，可据此判「该仓库只在 gitee」。
**判某个 gitee 账号存不存在要用对照**：`gitee.com/<user>` 存在回 **200**、不存在回 **404**；
但标题是 `Privacy (<user>) - Gitee.com` 且 `/projects` 列表为空 = **该用户开了主页隐私**，
不代表账号不存在 ⇒ 「目标仓库不在属主公开列表里」这条判据**只对公开列表非空的属主成立**，
碰到 Privacy 用户只能退回「问仓库主人」或「让用户在已登录浏览器里打开该仓库页」。

**2026-11-09：本机只剩两个 git 站点（用户定的规矩），且 `ag` 这个命令不存在。**
- 凭据管理器里实际只有两条：`git:https://gitcode.com`（用户 `zhoujinwei`）与 `gh:github.com`；
  **atomgit.com / gitee.com 既没有凭据，也已把它们的全局 `credential.<host>.provider` 行删掉**。
- `.gkeys\atomgit.txt` 里的 `T-...` 令牌**名字叫 atomgit、实际是 GitCode 的，而且已失效**：
  对 `atomgit.com` 与 `gitcode.com` 都回 `HTTP Basic: Access denied`。它的存在感是"每次自动登录失败"的来源，
  已移到 `_maintenance\_rollback`。
- 别信 AI 编的命令：`ag auth login --with-token`（照 gh 语法造出来的）在本机不存在；AtomGit/GitCode
  没有命令行登录，认证只有「网站生成 PAT + 凭据管理器」这一条路。
- 仓库自述：`E:\fullstack-code` 的 README 写**私有**；另 `gh` 账号 `chicatancau-create` 与 git 作者
  `zhoujinwei` 不是同一个名字，`gh api repos/<owner>/...` 404 不能当"仓库不存在"的证据。

相关：[[feedback-api-key-handling]]、[[reference-git-push-needs-local-proxy]]、[[project-dsh-agent-teams-deploy]]、
[[reference-git-nonascii-path-quoting]]
