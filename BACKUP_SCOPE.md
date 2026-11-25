# 备份范围与许可边界（推送前必读）

本仓库是**个人备份**，不是再分发。推送前逐技能核对了许可，**有 7 个技能被排除在远端之外**。
它们仍在本地磁盘上、仍然可用，只是永远不会被 push。`.gitignore` 里已按目录排除。

## 一、被排除的技能与原因（全部有原文依据，不是猜测）

| 技能 | 排除原因 | 原文依据 |
| --- | --- | --- |
| `docx` | Anthropic 专有，禁止在 Services 之外保留副本、禁止转移给第三方 | `LICENSE.txt`：「© 2025 Anthropic, PBC. All rights reserved.」+「may not … Extract these materials from the Services or **retain copies of these materials outside the Services**」+「may not … **Distribute, sublicense, or transfer these materials to any third party**」 |
| `pdf` | 同上 | 同上 |
| `pptx` | 同上 | 同上 |
| `xlsx` | 同上 | 同上 |
| `reverse-trace` | 包内无 LICENSE，上游许可未知；自带 PROVENANCE 限定仅本机自用 | `PROVENANCE.md`：「许可证：**包内没有 LICENSE / LICENSE.txt**，上游许可状态未知」「用途限定：**仅本机学习与自用**。不二次分发、不对外交付」 |
| `reverse-wechat-miniapp` | 同上 | 同上 |
| `webapp-building` | **泄露的 Kimi 产品技能，没有任何使用许可** | 与 `D:\QoderToolkit\web-kimi` 逐文件 sha256 比对：**175 个文件中 173 个字节相同**；web-kimi 的 `PROVENANCE.md` 记来源为 `QvvvvvvQ/skills_leaks`，上游 README 声明「版权及知识产权归属原公司，**没有任何使用许可**」「不要二次分发、不要公开传播」 |

QoderToolkit 仓库另排除 **`web-kimi`**（同一条泄露来源）。2026-11-25 起，QoderToolkit 的其余 **9 个技能**（含 MIT 的 `ppt-master`、`web-taste`）已字节级迁入本库并纳入远端备份；**只有 `web-kimi` 留在原库 `D:\QoderToolkit\web-kimi`，不进本仓库**。

**把仓库设成 private 也不能解决这一条**：上传到托管平台本身就是「转移给第三方」，
而且 Anthropic 那条明确禁止「在 Services 之外保留副本」。所以是排除，不是「私有就行」。

## 二、本次审计顺手修掉的一个真问题

`D:\Skills\webapp-building` 被复制进统一库时**丢掉了 web-kimi 的 PROVENANCE.md**，
限制条款随之消失，它一度看起来像普通开源技能。本次已把 `PROVENANCE.md` 补回该目录，
写明同源证据、许可状态与本机可用性限制。**限制条款必须跟着内容走。**

## 三、被排除的技能怎么重新取得

| 技能 | 重新取得方式 |
| --- | --- |
| `docx` / `pdf` / `pptx` / `xlsx` | 由 Anthropic 官方服务 / OpenClaw 预装渠道重新安装（本机记录：`.clawx-preinstalled.json`，slug 同名，装入时间 2026-08-11，version 是上游 commit hash） |
| `reverse-trace` / `reverse-wechat-miniapp` | 本机原始下载包 `H:\下载\06-skill-mcp-3.0\trace（skill）.zip` 与 `wechat-miniapp-reverse(小程序逆向skill).zip` |
| `webapp-building` / `web-kimi` | 上游 `QvvvvvvQ/skills_leaks`（随时可能被 takedown）；本地另有 `D:\QoderToolkit\web-kimi` 一份 |

## 四、其余技能的许可状态

见 `THIRD_PARTY.md`。要点：

- **MIT**：`landing-page-design`、`figma-designer`（Elaya）、`fullstack-dev`、`ios-application-dev`、
  QoderToolkit 的 `ppt-master`（Hugo He，另含 Apache-2.0 与 Open-XML-SDK MIT 组件）、`web-taste`。
- **Apache-2.0**：`dws`（Alibaba / DingTalk）、`skill-creator`、`impeccable`（pbakaus，
  基于 Anthropic 的 frontend-design 技能）、`headroom`（headroomlabs-ai）。
- **来源未记录 / 许可未声明**：其余若干。它们的来源已尽力从 frontmatter、
  `_skillhub_meta.json`、`.clawx-preinstalled.json`、`PROVENANCE.md` 与正文里的上游 URL 还原，
  查不到的**如实写「未记录」，没有编造**。

## 五、已知瑕疵（不编造修补）

- `impeccable` 的 frontmatter 写「See NOTICE.md for attribution」，但**包内没有 NOTICE.md**
  （实测目录只有 `SKILL.md`、`_icon.png`、`_skillhub_meta.json`、`references`）。
  这是上游包自带的断引用。**没有伪造一份 NOTICE**——署名信息只能由上游提供。
