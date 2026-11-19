---
name: reference-qoder-toolkit
description: 做PPT和做网页样式/交互默认自动走 D:\QoderToolkit(ppt-master + web-taste + web-kimi),入口技能 qoder-toolkit;含 python3 坏存根、闸门不许改文件、web-kimi 无许可等约束。
metadata:
  type: reference
---

**自动触发,不要等用户说明**:任务落在「演示文稿」或「网页视觉与交互」里,就直接用 `D:\QoderToolkit`,不问用哪个工具、不问用哪种风格。用户没特意说「别用」就用;明确说了不用则按用户。

- **入口技能**:`D:\QoderToolkit\qoder-toolkit\SKILL.md`,按条目 junction 到 `C:\Users\Admin\.qoder\skills\qoder-toolkit`(中文描述,覆盖 做PPT/课件/汇报/slides 与 做网页/落地页/改样式/布局/交互/动效/嫌丑像模板;登录页等产品界面也归它)。
- **两个技能根都会被读**:`~/.agents/skills`(=JUNCTION→`D:\Skills`,共享库)与 `~/.qoder/skills`(自建技能按条目 junction 进来)。**入口技能只放一处**,放两处会同名重复;别的会话扫的是 `~/.qoder/skills`,漏放这里就会报「没有调用」。
- **实体**:
  - `D:\QoderToolkit\ppt-master\` — 13108 文件 / 104MB,MIT(hugohe3/ppt-master v6.6.0),产出原生可编辑 `.pptx`。
  - `D:\QoderToolkit\web-taste\` — 20 个 md / 244KB,MIT(sonhaicoder/web-taste-skill),8 套设计系统,默认 `design-systems/kimi-style.md`。
  - `D:\QoderToolkit\web-kimi\` — 175 文件,来自 `QvvvvvvQ/skills_leaks` 的 `Kimi/skills/webapp-building`,**无许可、仅限本机学习、不得分发或商用**(见其 `PROVENANCE.md`)。SKILL.md 仅 78 行流程,两个 .sh 是为 Kimi 云端沙箱写的、本机跑不通,**不要执行**;只有 `scripts/template/` 那套 Vite+React+TS+shadcn 源码可作脚手架参考。
- 依赖已 `pip install --user` 装齐:PyYAML、python-pptx、XlsxWriter、skia-pathops、uharfbuzz、edge-tts、PyMuPDF(Python 3.14 全有 wheel)。

**How to apply:**
- 一律 `python`;`python3` 在本机是 WindowsApps 坏存根(rc 9009),技能文档里的 `python3 ...` 只是示例。
- **跑 ppt-master 前必看 [[reference-ppt-master-workflow]]** —— init 默认落 `D:\projects`(要 `--dir`)、live preview 因缺 flask 起不来(必须如实报告不能静默)、`import-sources` 会把源 PPTX 图片灌进 `images/`、SVG bounds 与原生表格 JSON 的具体写法、导出后必须用 PowerPoint COM 逐页导 PNG 才算验收。
- 跑 ppt-master 脚本前先 `python D:\QoderToolkit\ppt-master\scripts\attribution_guard.py`,非零即停;**绝不修改 ppt-master 目录下任何文件**(改内容/改名/BOM/CRLF 都会 fail closed)。
- 网页只碰样式与交互,不设计 API/数据库/鉴权/部署;改现有工程沿用它的框架,不引入新依赖。
- web-taste 原文越南语+英语混写:只取流程,输出用中文;小改动不走它的需求问卷。
- `C:\Users\Admin\.agents\skills` 是指向 `D:\Skills` 的 JUNCTION 且**递归扫描**:任何子目录的 `SKILL.md` 都会被登记,名字取目录名。构建产物/临时副本别放 `D:\Skills`。工具实体放在 `D:\QoderToolkit`(扫描根之外),只留一个入口技能在 `D:\Skills` 里。
- **`D:\QoderToolkit` 也是进化技能的实体库,不要当成纯外来件** —— 里面既有 vendored 上游件,也有会话自己写的 `SKILL.md`。放置、联接与 `skill_manage` 的落盘顺序见 [[skill-placement-convention]]。
- **桌面那份 Kimi 原装副本已移交用户另用的 AI 做定制化,不归本工具集管** —— 不要核对、重发、改动或删除 `C:\Users\Admin\Desktop\kimi-webapp-building\`(它甚至可能已不在磁盘上,那是正常的)。需要零改动原装时,从 `D:\QoderToolkit\web-kimi\` 的 174 个原装文件自己重算/重复制(基线聚合 SHA256 前缀 `490f17b0187521e7`,记在 `D:\QoderToolkit\README.md`)。
- 删深层嵌套目录要用 `\\?\` 长路径前缀;摘联接只能 `os.rmdir`,别对联接 rmtree。
- Qoder 插件包限 10000 文件,且本机「上传 Plugin」在 publish 阶段稳定写失败(见下),别再试。

**Why 不装成插件**:本机 Qoder 装本地插件会在 `publish` 报 `EXTENSION_INSTALL_WRITE_FAILED`(6 次、三种归档布局同样失败;文件未被锁、磁盘与 Defender 正常;9/22 装 superpowers 时留过同类失败 `.tmp`)—— 是那个长期运行实例的问题。插件路线还受 10000 文件限制(ppt-master 12994 个,其中 12027 个是 `templates/icons`,`icon_sync.py` 只从本地拷贝不下载)。散装入口技能完全够用。

**Why 用 web-taste 而不是只靠 Kimi 原件**:Kimi 那份泄露件含金量低(78 行流程 + 云端脚本),web-taste 才有成体系的样式/反套路规范;两者互补,前者当脚手架。
