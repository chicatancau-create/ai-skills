---
name: reference-ppt-master-workflow
description: D:\QoderToolkit\ppt-master 在本机出可编辑 PPTX 的实测边界：init 默认落 D:\projects、live preview 缺 flask、import-sources 会把源 PPTX 图片灌进 images/、SVG bounds 与 class 的硬规则、原生表格 row_heights 含表头、锁里一资源一行、python-pptx 不递归、PowerPoint COM 逐页导 PNG 才算目视验收。
metadata:
  type: reference
---

2026-11-04 用 ppt-master（Default Generate 路线，23 页中文 deck）跑通「素材→规划→SVG→门禁→导出→取证」全流程后实测到的本机边界。技能文档只讲流程，以下都是文档里没写或写法与本机不同的部分。

**项目落位与素材灌入**
- `project_manager.py init <name>` **默认把工程建到 `D:\projects\<name>_<format>_<date>`**，不是当前目录。要留在工作区必须加 `--dir "G:\AIrenwu\<会话文件夹>\ppt"`。
- `import-sources` 会把源 PPTX 抽出来的图片**复制进 `<project>/images/` 并用 `copy2` 保留原 mtime**（本轮 26 张同学 PPT 的截图混进我的 15 张素材里，mtime 还是转换时刻，容易被误判成"别的东西写进来的"）。删之前先与 `sources/<stem>_files/` 逐文件 md5 比对确认是重复副本，再删，然后重跑 `analyze_images.py`。
- `analyze_images.py` 认得 webp/png/jpg 真实字节；B站封面 CDN 下来的**全是 JPEG 不是 webp**。

**live preview 起不来**
- `svg_editor/server.py` 第 39 行 `from flask import ...` → 本机 Python（`D:\PyCharm\Python`）**没有 flask**，直接 ModuleNotFoundError。技能规则要求「起不来就在设计参数确认里如实说」，不要静默跳过；也不要擅自 pip 装依赖。
- 替代目视手段见下面「COM 导 PNG」。

**SVG 手写阶段的四条硬规则（踩过三轮门禁）**
- root `<g>` 的 `data-pptx-bounds` 是**模块区不是文字框**：检查器按「baseline − 0.85×size ～ baseline + 0.35×size」量文字，超出 5% 就是 error。先跑 `text_measure.py calibrate <project> --outline` 拿每角色「每 100px 几个 CJK / Latin / 数字 / CAPS」，再按率写区，横向至少留 24px 余量。
- `class` 属性是禁用项（structural blacklist）。想让检查器认出网格线，用 `id="grid-1"`，**不要** `class="grid"`。
- 原生图表/表格标记（`data-pptx-replace-with`）的 `row_heights` **必须含表头行**：`columns` 占一行，N 行正文要写 N+1 个权重。JSON 无效时 `stamp_native_fallbacks.py` 会跳过该对象，下一轮就报「缺 data-pptx-fallback-sha256」——看着像两个问题，其实是一个，先修 JSON 再 stamp。
- `spec_lock.md images` **一个资源一行**（键是资源不是页面）；同一张图跨页复用只写一行，写两行报 `appears in multiple spec_lock.md image rows`。§VIII 里最终没落位的行要删掉，否则报「locked file is not referenced by any svg_output」。
- 原生 chart 的 carrier group 里**只放 fallback**：说明文字/截图放进去会在 `--native-charts-and-tables` 分支被丢弃，且触发「marker text 需要 companion entry」警告。
- 原生 chart 的 metadata frame **必须包含类目标签与刻度标签带**，不能只等于 plot，否则 PowerPoint 会压缩绘图区；caption 要写进 payload，categories 必须与画面文字一致。若柱图数据标签贴顶线，调大轴 max，而不是靠移动 fallback 文字遮掩。

**导出后的验收（关键，别只信 `[OK]`）**
- `python-pptx` 的 `slide.shapes` **不递归 group**，导出把每个 root `<g>` 编成组合形状，顶层遍历会数出「0 图片」的假阴性。必须遇 `MSO_SHAPE_TYPE.GROUP` 下钻。图片/图表数可与 checker 对表；文字数必须注明口径——`has_text_frame` 会包含空文本形状，是否去空白也会改变字数，不能拿原始总数与 checker 的 text carrier 数硬对齐。
- 真目视取证用 PowerPoint COM：`Presentations.Open($src,$true,$false,$false)` → `Slides.Item($i).Export($f,'PNG',1280,720)`，逐页 PNG 再拼 contact sheet 看。PowerPoint 是 ClickToRun 已装，可用；`.ps1` 要 `utf-8-sig` 写。最终还要对**交付路径上的副本**重跑结构、署名与 md5 检查，不能只验 exports 原件。
- headless Edge 截网页做「数据页截图」时，`--screenshot=` **必须是绝对 Windows 路径**，相对路径报「系统找不到指定的路径」（Edge 不继承 bash 的 CWD）；B站空间页匿名可截，但右上角会弹登录浮层，要按坐标裁掉（实测浮层约 x 978–1312 / y 78–292）。

**Why:** 这些坑各花了一轮返工（门禁三轮才归零），而且全是"工具回显成功但产物不对"的类型 —— 与 [[feedback-rigor-audit]] 的「已通过必须挂本轮自产证据」直接冲突。
**How to apply:** 下次做 PPT 时：init 加 `--dir`、预览失败就如实报、bounds 先 calibrate 再写、表格 JSON 行数含表头、锁一资源一行、导出后递归数形状 + COM 导 PNG 逐页看。相关：[[reference-qoder-toolkit]]、[[reference-docx-layout-verification]]（Word 侧同源教训：别用字体度量算分页，要让 Office 自己渲染）、[[feedback-skill-routing-table]]。
