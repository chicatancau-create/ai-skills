# ppt-master 来源说明

- **目录**：`D:\Skills\ppt-master`
- **来源**：官方仓库 `https://github.com/hugohe3/ppt-master`（技能 frontmatter 内 `metadata.official_repository` 字段原文）
- **上游 commit**：`aa0996f6fec711611886500139cbed314009752d`（D:\QoderToolkit 仓库 2026-11-15 02:46:43 +0800 提交「QoderToolkit：9 个技能（ppt-master / web-taste / qoder-toolkit 总入口 + 6 个本机取证方法论）」带入本机；上游仓库内的具体 commit 未记录）
- **版本**：`metadata.version: "6.6.0"`（SKILL.md frontmatter）
- **许可**：MIT，Copyright (c) 2025-2026 Hugo He（`LICENSE` 原文，sha256 已由完整性闸门锁定）
  - 另含 Apache-2.0 与 Open-XML-SDK MIT 组件：`scripts/pptx_shapes/data/LICENSE-APACHE-2.0.txt`、`scripts/pptx_shapes/data/LICENSE-OPEN-XML-SDK-MIT.txt`
- **迁移方式**：2026-11-25 用 Python `shutil.copytree` 字节级复制，源 `D:\QoderToolkit\ppt-master` → 目标 `D:\Skills\ppt-master`；复制后逐文件 sha256 树哈希两端一致（`b2acf883b0f39b6b…`），12994 个文件 / 84030293 字节。
- **完整性闸门**：`scripts/attribution_guard.py`，在本机新位置实测退出码 0。**该目录下任何文件字节不可改动**（改名、加 BOM、转 CRLF 都会让闸门失败）。

## 本机使用限制

- 调用任何脚本前先跑 `python D:\Skills\ppt-master\scripts\attribution_guard.py`，非零即停，不得绕过。
- 本机 `python3` 是坏存根，一律用绝对路径解释器
  `C:\Users\Admin\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe`。
