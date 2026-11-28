# 剪辑不装剪映装 CapCut：本机路径与草稿实况

- 核实时间：2026-11-28。
- **本机没有剪映 JianyingPro**。注册表三处 Uninstall 键无「剪映/Jianying/CapCut」条目，开始菜单只有 `CapCut\CapCut.lnk`，全盘 depth 4 只找到 `D:\CapCut\CapCut.exe` 与 `D:\CapCut\9.8.0.4213\CapCut.exe`（国际版 9.8.0.4213）。
- **CapCut 关键路径**（配置在 `C:\Users\Admin\AppData\Local\CapCut\User Data\Config\globalSetting`）：
  - 草稿库 `currentCustomDraftPath` = `E:\CopCut\草稿\CapCut Drafts`（810 文件 24MB）
  - 素材 `customMaterialPath` = `E:\剪影\素材\CapCut Materials`
  - 预存 `customPresetPath` = `E:\剪影\预存\JianyingPro Presets`
  - 缓存全在 `C:\Users\Admin\AppData\Local\CapCut\User Data\Cache`（remux/agency/prerender）
  - `fpsNumerator=60 / fpsDenominator=1`、`needWaterMark=false`、`lastLoginPlatform=google`
- **导出成片落点**：历史习惯是 `H:\视频\CopCut\`（现存两个历史成片可作证据：`平凡的一天_精剪v6.mp4`、`网店商品短视频（1202 周金炜）.mp4`）；**2026-11-28 起正式成品目录改为 `H:\视频\成品\<内容名>\`**（用户新建，按内容单独成册）。导出目录本身 CapCut 不写进配置（`Export.ini` 只有一个 `userFirstVideoEnhanceExport=false`），是导出对话框里手选的。
- `C:\Users\Admin\AppData\Local\JianyingHubMCP`（v0.8.87 / node 22.23.2 / 端口 19877）是剪映 Hub 的 MCP 通道，**不代表本机装了剪映**——用户可能在手机端/云端用剪映。
- 排查法：`Get-ItemProperty HKLM/HKCU 的 Uninstall\* | Where DisplayName -match '剪映|Jianying|CapCut'` + 全盘找 exe；**不要只按文件夹名猜**（`E:\剪影\预存\JianyingPro Presets` 只是 CapCut 沿用了剪映的预设目录名）。
- 关联：[[规则：剪辑工具/素材放 D 盘，成品视频放 H 盘]]。
