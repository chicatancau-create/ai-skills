---
name: feedback-install-to-d-drive
description: 本机所有软件统一装到「软件盘 D:」，禁止装进 C:；下载的安装包/备份也不要留在 C:，动手前先确认目标盘。
metadata:
  type: feedback
---

# 软件一律装 D:（软件盘），不装 C:

用户 2026-10-06 明确要求：**所有软件统一安装到软件盘（D:），不要装到 C 盘**。这条同时适用于安装器安装包、解压目录、便携版程序目录、以及我为某次安装临时建的备份目录。

**Why:** C: 是系统盘，本机历史上多次做 C 盘空间清理（见 [[feedback-c-drive-hibernate-pagefile-off-limits]]、[[feedback-destructive-file-ops]]）；把软件堆到 C: 是在给用户制造他每月要清理的垃圾。D: 才是这台机器的软件盘——已知既有布局：`D:\Git`、`D:\QoderToolkit`、`D:\DevEco Studio`、`D:\Skills`。

**How to apply:**
1. 任何「装软件 / 装 SDK / 解压绿色版 / 下载安装包」的动作，**先把目标路径写成 D: 下**再执行；默认安装路径是 C: 的安装器要显式改路径或先问。
2. 我自己产生的中间产物（安装包、临时备份、取证目录）也别落在 C:，顺手放 D: 或 `%TEMP%`（`%TEMP%` 属可清理区，可接受）。
3. **MSIX/APPX 例外要主动说明**：包安装位置由系统「新应用保存位置」决定，`Add-AppxPackage` 没有指定安装目录的参数。若它只能落到 C:，把这三条摆给用户选：① 改 Settings → 存储 → 高级存储设置 → 新内容保存位置 → 新应用保存到 D:；② 解包后松散注册（`Add-AppxPackage -Register -DisableDevelopmentMode D:\...\AppxManifest.xml`，需开开发者模式）；③ 接受该应用留在 C:。别默默装到 C: 就当没事。
4. 涉及已有软件（如 Claude 的 MSIX 现装于 `C:\Program Files\WindowsApps`）时，先告知它当前在 C:，再按上面选项推进。

5. **uv / Python 工具的默认落点也在 C:**（2026-11-09 实测）：`uv tool install` 默认写
   `%APPDATA%\uv\tools` 并把可执行文件放 `%USERPROFILE%\.local\bin`。要守 D 盘规矩就先设
   **用户级** `UV_TOOL_DIR`、`UV_TOOL_BIN_DIR`（本次设为 `D:\uv\tools` / `D:\uv\bin`），再把 bin 目录
   追加进用户 PATH（**保持原 `REG_EXPAND_SZ` 类型**，改完回读复验）；模型/缓存同理用 `HF_HOME` 指到 D 盘。
   装完把 C 盘残留的 `uv\tools` 空脚手架清掉。

Related: [[feedback-destructive-file-ops]], [[reference-skill-placement-convention]], [[feedback-toolkit-is-tools-only]], [[reference-c-drive-hibernate-pagefile-off-limits]]
