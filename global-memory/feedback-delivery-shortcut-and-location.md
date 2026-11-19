---
name: feedback-delivery-shortcut-and-location
description: 每次交付软件/项目部署，必须同时给出桌面快捷方式和明确的落点说明；小东西进 G:\AIrenwu 工作区，大文件与软件本体进 D 盘软件盘。复查时桌面 .lnk 不见了要先扫 E:\DeskBox（用户会把快捷方式移进去归档），命中就别重建。
metadata:
  type: feedback
---

做完任何软件部署、工具安装、项目搭建，交付时**必须同时有两样东西**，缺一不算做完：

1. **桌面快捷方式**（.lnk），让用户能直接再打开。
2. **明确的落点说明**——写清每一部分放在哪里，用户不必回头翻聊天记录。

落点默认规则（用户 2026-10-30 原话）：

- **小东西** → 工作区 `G:\AIrenwu`（「AI 任务」文件夹，G 盘），一会话一文件夹。
- **大文件 / 软件本体** → `D:` 软件盘。

**Why:** 用户看不到我的中间过程，交付完只关心「能不能双击打开」和「东西在哪」。缺任一项就等于让他自己做收尾。这与 [[feedback-install-to-d-drive]] 是同一条链：装 D 盘是位置约束，快捷方式是可达性约束。

**How to apply:**
- 建 .lnk 用 PowerShell 的 `WScript.Shell` COM（`CreateShortcut` → 设 `TargetPath`/`WorkingDirectory`/`IconLocation` → `Save`）。
- **脚本必须用 `utf-8-sig`（带 BOM）写盘**：Windows PowerShell 5.1 会把无 BOM 的 UTF-8 当 GBK 读，中文快捷方式名/描述会吃掉字符串结束符，报 `字符串缺少终止符`。见 [[reference-powershell-through-bash-and-recyclebin]]、[[feedback-windows-config-json-encoding]]。
- 快捷方式名用中文显示名，不要用 exe 名。
- 建完**核实两件事**：① 从注册表 `HKCU\...\Explorer\User Shell Folders` 的 `Desktop` 确认这就是用户真看到的桌面（可能被 OneDrive 重定向）；② 重新 `CreateShortcut` 读回 `TargetPath` 并确认目标文件存在。
- **PowerShell 控制台回显中文乱码 ≠ 磁盘上的 .lnk 名字坏了**：2026-11-04 建「影视飓风短视频账号分析.lnk」时 `Write-Output` 打出 `Ӱ쫷...`，实际用 `python -X utf8 + glob` 读目录，文件名完全正确。判据是列目录不是看回显（GBK 控制台码页所致）。
- 报告里逐条列：客户端位置、源码位置、依赖位置、改了什么系统设置及怎么回滚。

## 复查时：桌面没有 .lnk ≠ 被删了，先扫 DeskBox

用户维护「**桌面零快捷方式**」的习惯：交付建好的 `.lnk` 会被他本人移进 `E:\DeskBox\<分类>\`（分类实测有 `VPN`、`刷课软件`、`剪辑工具`、`学习软件`、`实用小工具`、`广告屏蔽`、`性能监控与优化`、`我的桌面`、`新增-AI与开发工具` 等，每个分类旁还配一个同名 `.lnk`）。

**所以复查发现桌面 `.lnk` 计数为 0 时，第一动作是递归扫 DeskBox 确认是否被移动，绝不直接重建。**

```bash
python -X utf8 -c "import glob;[print(p) for p in glob.glob(r'E:\DeskBox\**\*.lnk', recursive=True) if '关键词' in p]"
```

- 扫到 → 什么都不做，汇报里写明「已被移到 `E:\DeskBox\<分类>\`」，这仍算交付有效。
- 扫不到 → 才回落「确认丢失」分支，问用户或重建，并告知重建位置。
- 可以建议某个分类更贴切（如 `广告屏蔽\` vs `实用小工具\`），但**不擅自移动用户整理好的文件**。

**Why:** 2026-10-31 我犯过一次——没查 DeskBox 就重建了 `安卓去广告.lnk`，把用户已归位的东西又变回桌面重复品，用户当场纠正：「不要自己重新搞一个，先看一下是不是我移进去了。因为你把快捷键放在桌面上，我大概率会把它移动走。」

**How to apply:** 因为快捷方式一定会被移走，交付汇报里**必须同时给出程序本体的绝对路径**，不能只说「桌面上有图标」。完整证据与实测数据已归档到手册 `03-通用/02-AI协作与提示词/规则-桌面快捷方式消失先查DeskBox勿重建-Windows.md`（verified，2026-10-31）。
