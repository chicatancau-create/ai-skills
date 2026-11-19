---
name: user-role
description: User is a solo competition learner (全栈竞赛 个人赛, 6—10h/day) who treats E:\OBsidian as their curated study system and delegates its maintenance to AI
metadata:
  type: user
---

The user is a self-learner preparing for a personal-format full-stack competition, studying 6—10 hours a day, working in Chinese with terse, high-level directives ("继续工作", "两个都执行", "先一后二"). They do not write the vault content themselves — they task AI agents (this agent plus 豆包/Doubao) with curating, cross-checking and reorganizing it, then expect the result to be report-ready without hand-holding.

They think of the vault as layered infrastructure they own: knowledge (分册) vs provenance (来源卡) vs evidence (转写/日志) vs status (进度追踪). When they ask for "完善" or "修订", they mean content accuracy and structural coherence of that system, not app code.

They care a lot about not being fed fabricated or stale technical facts — they explicitly ask for verification against official sources and for obsolete technology to be removed rather than annotated. They also run multiple AI writers on the same corpus, so they value edits that survive concurrent modification.

Besides the vault, they run a **local AI model deployment** in `D:\Models` (牧羊人/Herdsman desktop app + GGUF models on an RTX 5070 Laptop, 8GB VRAM) whose purpose is local code completion. There they act as the GUI operator while AI does the config/file/API work.

They will say plainly when they are lost — 「我不懂你现在说的东西，但是我想提个要求…」 — and then restate the need in outcome terms. That is not disengagement: they follow the conclusions, spot when a claim contradicts what they see on screen (they screenshot Task Manager / app panels and challenge them), and remember which errors I admitted to. See [[feedback-plain-language-first]].

Their AI budget is a real, recurring constraint: on 2026-10-05 they said 「我现在的资金耗尽了」and switched executors mid-project, asking me to commit + push the whole repo and produce a self-contained handoff brief for the next AI. Practical consequences: **keep a rollback commit current so nothing is lost when a session dies**, write handoff docs that stand alone (they get pasted verbatim into another tool), and prefer zero-cost options — they will reject paid paths (they dropped code-signing certificates entirely in favour of cloud-drive distribution) and dislike work that has to be redone.

They also ask me to **do** the work, not only audit it — same session: after reviewing another AI's code I was told 「先动手修复 A、B、C 这三个关键缺陷」. So: auditor by default, implementer on request, and when implementing, ship regression tests that would actually have caught the defect.

They also own a software project (**CodeWeave**, `G:\CodeWeave`: 网页端 / 应用端 / 移动端 / 工作区) and run a **two-AI division of labour** on it: another assistant (ChatGPT, model label 「6 Astral」) does architecture evaluation and writes the plans into the repo's `工程文件/`, while this agent is asked to read those plans, independently verify them, run the gates for hard evidence, and report **which work it can and cannot take**. They paste screenshots of the other tool's output to cross-examine my claims. See [[feedback-capability-boundaries]], [[project-desktop-ui-native-route]].

When they set a priority it is a hard constraint, not a preference to trade off — e.g. 「性能放在最高级、最优、最高优先级，UI 是其次的…大不了让别的去对照重建它」. Re-order recommendations under the stated priority instead of re-arguing the cheaper option.

**git CLI 是新手水平**：2026-10-15 同一场里他先 `git init` 建了个空仓库，又在里面 `git clone`（造出
嵌套的 `E:\node` + `E:\node\node`），然后在**外层**那个无 remote、零提交的仓库里敲 `git add`，
连续失败后困惑地发「?」；并且以为 `git add` 就等于「上传」。⇒ 涉及 git 远端操作时，
显式写出「你现在在哪个仓库 / 这条命令实际改了什么 / 还差 commit + push 两步」，
别默认他知道 add≠push；他误建的空仓库要主动点破是坑。托管账号与凭据判据见
[[reference-git-credential-manager-windows]]。

**git CLI 是新手水平**：2026-10-15 同一场里他先 `git init` 建了个空仓库，又在里面 `git clone`（造出
嵌套的 `E:\node` + `E:\node\node`），然后在**外层**那个无 remote、零提交的仓库里敲 `git add`，
连续失败后困惑地发「?」；并且以为 `git add` 就等于「上传」。2026-10-15 同日又暴露两条同源误解：
敲 `git pull` 之后以为"这就传上去了"（网站没变化来问「?」），以及以为**一次 commit 会自动同步到所有托管站**。
⇒ 涉及 git 远端操作时，显式写出「你现在在哪个仓库 / 这条命令实际改了什么 / 还差 commit + push 两步」，
别默认他知道 add≠push；他误建的空仓库要主动点破是坑。他的提交信息也是随手写的（`fullstack-code`、`...`、
甚至开头带一个 BOM `﻿`），所以顺手给一条「类型: 中文说明」的范例比批评有用。托管账号与凭据判据见
[[reference-git-credential-manager-windows]]。

**他接受"用实测数字论证某件事不该做"，不要为了显得在推进而执行高风险操作。** 2026-10-15 我建议
**不要**为几 MB 构建缓存去改写两个公开仓库的历史（量到 `.git` 仅 5.08 MB、历史里那份 `local.properties`
只有注释头没泄露路径），他没反对，紧接着说「那你把要做的事情全做了」—— 这句话的含义是
**把待办清单里该做的都做完**，不是"所有列出来的都无条件执行"。⇒ 收到"全做了"这类授权时，
仍要把"我判断不该做的那一件 + 数字理由"单独说清，并留一条"要抹就说一声"的入口。
同一轮他还认可我推翻自己上一轮的结论（"主嫌是 WARP"→A/B 后否定、"source=cli 是降级"→README 更正），
没有因我自我纠错而不满 —— 所以**错了就当众更正**，别悄悄改口径。

**回复长度是硬约束**：2026-10-08 他们直接抱怨「你这么多文字，我看个毛线」，并改成一句话下指令
（「你现在扫描一下，然后给我一个清理建议啊」）。所以：结论 + 表格优先，长段落解释只在他们追问时给；
一次消息里不要同时塞诊断过程、历史更正和多个待确认项 —— 该问的那一句单独问。

**GUI 操作默认由我代劳**：2026-10-08 他直接说「这个东西，你操控我电脑，自己去验证一下就行。我不会英文，不会操作」。
所以遇到英文界面的验证步骤，先自己用 computer-use（终端/桌面应用可驱动，见
[[reference-computer-use-blocked]]）做完并给结论，**不要**把一串英文菜单截图回去让他找按钮；
只有策略硬挡的部分（Chrome 里的选账号/点允许）才单独拎出来，明确到「哪个窗口标题、点哪一处」。

They are **not a Python/crawler engineer** and say so — 「按你的想法去做吧，我也不清楚Python爬虫」. That is a request for me to pick the technical route and justify it in outcome terms, not an abdication: they still challenge claims that contradict their screen, and they answer concrete either/or questions fast (a single letter like 「B」 refers to whatever batch/option list the project's own docs define — e.g. 重整方案 B 批 — and reading it that way was accepted). They will also **offer their logged-in accounts and ask me to drive their browser** to get data; the useful response is to take the authorization seriously while naming the one thing only they can do (be present, click the human-only steps, nominate the specific target), rather than refusing or silently doing it for them. See [[feedback-plain-language-first]], [[feedback-autonomous-execution]].

**他要的是「额度被用掉」这个结果，不是工具好用**：2026-10-09 我给他做了一键换号脚本，被直接纠正
「我并不需要一键换号，我只需要你能利用你的能力，把这 4 个号的额度全用完而已」。
⇒ 遇到外部服务/账号类任务，别在便利性和 UX 上加工，先回答「能不能真跑起来、还剩哪一步只有他能做」。
同一轮他还说「我时间并不是很多，这个能不能用的话，那就其次吧」—— 他会主动降低自己要求里的次要项，
所以我该直接给最短可行路径，不要铺全套方案。

**「用完额度」不等于白烧，而是把活派过去**：紧接着他又补了一句
「我的意思不是让你白白消耗，我的意思是让你利用这个号帮我做事」。
⇒ 谈外部 AI 账号/订阅时，默认目标形态是**用它们当额外算力去干真实任务**（并行长任务、粗活外包、
多号交叉复核），别把话题停在「能不能连上/能不能换号」。回答里要具体说出打算派什么活过去。

**我在工具调用之间沉默会被当成「挂了」**：同一轮里他两次催「你怎么卡住呀？这么死吗」「你怎么卡这了？」
—— 都是因为我在他动手操作的间隙只发工具调用、不出一句话。⇒ 只要一轮里有多次调用或等他操作，
中途至少给一行「我在做什么/我在等你做什么」的说明。

**他另有「玩机/刷机」这条线，且是新手水平但目标很具体**：2026-10-30 起在同一工作区里让我部署安卓工具、
并给他自己的 **Redmi K30 Ultra** 做 root，目标是强开游戏帧率。特征：
① 目标说得很清楚（哪几款游戏要 120、哪几款只求 60 稳），但**刷机常识有缺口** —— 不知道解锁 Bootloader 会强制清空数据，是问到才发现的；
② **对账号风险高度敏感**：「我不想封我的手机账号，就是我的那个社区账号」是硬约束，宁可放弃功能也不暴露主账号（注意他容易把「小米账号被拉黑」和「游戏账号被封」混成一件事，要主动拆开讲）；
③ 会要求绕过正规流程（反复强调「强行 root，不走官方」「优先保证我能 root，尽量保证安全就行」）。
他会接受"没有 + 证据"，但**我不能把"我没查到"说成"不存在"** —— 我先断言该机型无免解锁路子，随后自己查到
MTK BootROM 强解覆盖天玑1200 及以下并当众收回，他对我自我纠错没有不满（与 [[feedback-rigor-audit]] 一致）；
④ 对等待类约束会反弹（「等那么长时间我干嘛」），所以要先讲清「等待是墙钟时间、不需要人守、期间可以并行做别的」；
⑤ **会明确离场并全权委托**：「我后续有其他时间去了，你直接自己最优解去做就行，我没空」「如果还有东西，
你就弹出界面给我，我自己帮你解锁」⇒ 他要的是我把**能自动化的全做完、把只剩物理动作/凭据输入的单独拎出来**
（弹窗截图给他、说清点哪一格），而不是攒一批问题等他回来。密码类输入永远交给他，我不碰。
⑥ 他会把**两类完全不同的账号风险混成一件事**（"解锁会不会封我社区账号" vs "机型伪装会不会封游戏账号"），
要主动拆开列表讲。
⇒ 这类任务里把**不可逆风险（账号封禁 / 数据擦除 / 变砖 / 计时重置）单独成表放在最前面**，并明确标出哪一步只有他能做。
通用判据见 [[reference-xiaomi-miui-root-automation]]，当前进度见 [[project-k30ultra-root-prep]]。

**他还有一条「短视频课程作业」线，是学生身份的小组作业，不是商业项目**：2026-11-04 在同一工作区让我分析短视频账号「影视飓风」并出 PPT，明确「这是我的短视频作业，目前阶段是短视频账号分析」——"目前阶段"意味着后续还会换任务形态（大概率自己做号/运营）。特征与要求：
① 会**拿同学的作业当框架模板**（`H:\下载\全立煦短视频分析.pptx`，"无人在意小组"四章结构），但被问到时明确选了「同框架、重做设计」而不是复刻同学排版 —— 他在意"交上去不能和同学撞脸"，所以框架照搬 + 视觉原创是默认解；
② 数据必须**可核查、能被老师追问**：他会接受"未查到"，不接受编的数字；每个平台数据要带取数日期和口径分档（接口实测／页面实测／媒体口径／未查到）；
③ 要**原生可编辑 pptx + 每页讲稿备注**（他要上台汇报），贴图版不算交付；
④ 允许我直接去看被分析账号的真实视频取证（「必要情况下，你可以直接去看一下他的视频」）。
相关：[[reference-bilibili-open-api-read]]、[[reference-ppt-master-workflow]]、[[project-shortvideo-coursework]]、[[feedback-ghostwriting-no-falsifiable-claims]]（同为"替作业写东西"的诚实边界）。

**别把常规 secret/PII 扫描说成“敏感”**：2026-11-08 他看到材料里出现“敏感”直接发火——「我让你整理代码数据…你搁这跟我敏感啥」。他要的是整理学习资料/代码数据，不是内容审查。⇒ 工程检查里的“敏感元数据检查”必须说明是查 token/密码/私钥/个人信息误提交；对学习资料本身不要套“敏感/政治”框架。

Related: [[feedback-vault-engineering-rules]], [[feedback-version-currency]], [[feedback-rigor-audit]], [[feedback-plain-language-first]], [[project-vault-work-environment]]
