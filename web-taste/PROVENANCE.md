# web-taste 来源说明

- **目录**：`D:\Skills\web-taste`
- **本机来源**：`D:\QoderToolkit\web-taste`（QoderToolkit 仓库 2026-11-15 02:46:43 +0800 提交 `aa0996f6fec711611886500139cbed314009752d`「QoderToolkit：9 个技能（ppt-master / web-taste / qoder-toolkit 总入口 + 6 个本机取证方法论）」带入）
- **上游仓库**：**未记录**。包内 `README.md` 的安装示例只写占位符 `https://github.com/<your-org>/web-taste-skill`，本地路径示例为 `/Volumes/hai/web-taste-skill`，没有任何真实可访问的上游地址。**没有编造上游 URL。**
- **许可**：**MIT**，`LICENSE` 原文首行 `MIT License`，`Copyright (c) 2026 web-taste-skill contributors`；`README.md` 末尾「License: MIT — tự do dùng/fork/sửa」。许可明示允许使用、复制、修改、合并、发布、再许可与销售，**属于可再分发的许可**。
- **语言**：越南语 + 英语混写（作者母语痕迹），内容为流程与规则，不影响使用。

## 与泄露包 web-kimi 的关系（已实测排除）

- 逐文件 sha256 比对：`web-taste` 20 个文件 vs `D:\QoderToolkit\web-kimi` 175 个文件，**共同路径仅 1 个，字节相同 0 个**；两份 `SKILL.md` 文本相似度 `difflib` 比值 0.213（长度 22136 B vs 2537 B）。
- `web-kimi`（`QvvvvvvQ/skills_leaks` 泄露的 Kimi 产品技能）与本技能**无同源代码**：本技能是对 8 个公开来源的再创作，`design-systems/kimi-style.md` 是对 kimi.com 视觉语言的**自行描述**（文中标注 `Reference: kimi.com (Moonshot)`），不是 Kimi 内部设计文档的拷贝。
- 结论：**不属于泄露内容，MIT 许可成立，正常入 git 远端备份，不进排除清单。**

## 内容来源（作者自述，8 个来源）

| 来源 | 贡献 |
| --- | --- |
| `nexu-io/open-design` | Discovery Form 模式、5 个确定性方向、5 维 critique |
| `Leonxlnx/taste-skill` | bias 修正规则、dial 配置（variance/motion/density）、AI Tells |
| `impeccable.style` | 27 条 anti-pattern、brand vs product 模式 |
| `getdesign.md` | DESIGN.md 集合格式与集成方式 |
| `designmd.ai` | 「DESIGN.md 放项目根」工作流 |
| `styles.refero.design` | 从真实站点提取 DESIGN.md |
| `alchaincyf/huashu-design` | Junior-Designer 工作流、5 流派 × 20 哲学 |
| `op7418/guizang-ppt-skill` | 预检资源读取、P0 自检、主题节奏 |

## 迁移方式

2026-11-25 用 Python `shutil.copytree` 字节级复制，复制后逐文件 sha256 树哈希两端一致（`5b92b30ff3f4940a…`），20 个文件 / 200839 字节。本文件为迁入后新增，包内其它文件未改动。
