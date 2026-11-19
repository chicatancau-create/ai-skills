---
name: feedback-skill-routing-table
description: 本机自建技能家族的「谁该触发」默认路由表 —— 做/验/装三条线各只有一个入口,防止多个技能抢同一句话或全部空转。
metadata:
  type: feedback
---

任务一进来就按下表选**唯一一个**入口技能,不要同时加载多个,也不要因为"不确定"就跳过。

| 用户说的话 | 触发 | 明确不触发 |
|---|---|---|
| 做 PPT / 做页面 / 改样式 / 调布局 / 加交互 / 动效 / 嫌丑像模板 | `qoder-toolkit` | 三个取证类、三个安装类 |
| 交付后「它真渲染成什么样」(单文件 HTML/CSS, 实拍 + 探针取数) | `headless-cdp-visual-acceptance` 的「零 CDP 快速回路」一节 | 只跑 `qoder-toolkit`(它只管产出, 不取证) |
| 需要交互流 / 真窄视口 / hover 焦点环 / 对比度 / MV3 扩展 / mock 接口 | `headless-cdp-visual-acceptance` 的 CDP 管线(第 0–8 步) | 命令行回路(`--window-size` 有 496 下限, 给不出手机态) |
| 这句安全/隔离声称成不成立 | `verify-app-security-claims` | `fs-security`(静态审查)、`security-scan` |
| 打包上传前判断收不收、超在哪项限制 | 暂无入口(2026-09-24 两个安装类自建技能 `diagnose-qoder-plugin-install`、`qoder-extension-install-diagnosis` 均已删除) | 别顺手调 `install-github-skill-on-windows-qoder`(那是第三方包落位) |
| 装第三方 GitHub 技能包到本机 | `install-github-skill-on-windows-qoder` | `skill-creator`(从零写)、`qoder-find-extensions`(官方市场) |
| 页面必须有数据才可测 | `localstorage-data-shape-seeding` | 直接下结论说"空态即通过" |
| CodeWeave 换构建后重测 / 改取证工具代码 | `codeweave-visual-rebuild-rerun` / `visual-tool-add-section` | 通用取证类技能 |

**Why:** 2026-09-24 一天之内自建技能涨到 10 个,会抢同一句话的是「生产 vs 取证」与「事前预判 vs 事后取证」两对;抢错的代价是要么白跑一套管线,要么把"没量到"写成"已验证"。用户明确要求把这些划界写进**默认规则**而不是靠当场判断。2026-09-25 `verify-page-in-headless-edge` 已整体并入 `headless-cdp-visual-acceptance`(作为「零 CDP 快速回路」一节)并删除,所以「验」这一类现在**只有一个入口**,内部再按要不要驱动浏览器分两条回路。

**How to apply:**
- 生产与取证是**接力**不是并行:先 `qoder-toolkit` 产出,再按上表挑一个取证技能证明它;两者不要同时加载。
- 判据必须有牙齿:测量前先造一个"必须报红"的对照组(探针两次都不红 = 探针是死的);没量到的写「未证实」并带日期,绝不写成「已验证」或「不成立」。
- 窄视口结论不能由 `--window-size` 给出(实测 390→innerWidth 496);要真窄视口必须走 CDP 设备模拟。
- 家族路由的完整版(含每个技能的实体位置与许可)在 `D:\QoderToolkit\README.md`;两处若冲突以本表为准并去更新 README。
  查「本机到底有什么」时 `D:\Skills\README.md` 是第二本账,先读两份 README 再 `ls`。
- **取证入口可能指向已不在本机的跑器**:2026-10-03 核点时 `codeweave-visual-rebuild-rerun` 与
  `visual-tool-add-section` 里写的 `tools/visual/*.mjs` 在 D/E/G 五层内都找不到(`E:\CodeWeave` 现只剩
  应用端/移动端/网页端)。调这两个技能前先确认 runner 在当前工作区,找不到就直说「工具不在本机」,
  不要照 SKILL.md 硬跑再报「全绿」。
- 改已归案技能的 description: junction 挂着的时候 `skill_manage patch`/`delete` 一律 `SKILL_PATH_INVALID`(2026-09-25 实测三个技能)。摘掉 junction 之后能不能 patch **未验证**,别再照旧写「先摘联接再 patch」;当下可行的做法是直接改 `D:\QoderToolkit\<name>\SKILL.md`(需用户授权)+ 自己补等价校验,见 [[skill-placement-convention]]。
