---
name: reference-windows-desktop-distribution
description: Windows 桌面应用分发：代码签名各选项的真实条件与 2024+ 变化、MSIX 打包的文件系统硬约束、electron-builder 26 的签名/打包字段
metadata:
  type: reference
---

给 Windows 桌面应用做「正式签名 / 分发」时的已核实事实（2026-10-05 查官方页）。

## 签名选项（微软官方《Code signing options for Windows app developers》，2026-08-29）

- **Microsoft Store 发 MSIX = 免费、不要证书、微软重签、真的不弹 SmartScreen。** 四条路里唯一直接达成「不弹警告」的。注意：走商店发 **MSI/EXE 安装器**仍需自己 Authenticode 签名，只有 MSIX 才免。
- **Store 个人开发者注册现已完全免费**（免除原 $19），官方页称全球近 200 个市场可用，验证方式 = 政府颁发身份证件 + 自拍（AU10TIX/Verified ID），**唯一入口是 `storedeveloper.microsoft.com`**；走合作伙伴中心 / Xbox / Visual Studio 的旧路径仍是收费流程。ms.date 2025-08-07、页面更新 2026-10-04。企业账户另算。

## 不签名、只想「别弹警告」时的现实

- 无签名 + 浏览器下载 = **必弹**「Windows 已保护你的电脑」，**没有合法绕过手段**（那是安全机制本身，别去找）。
- 能真正降低的：走 Store（首选）；**换传输方式** —— U 盘 / 局域网 / 网盘客户端同步不带 Mark-of-the-Web，就不触发下载信誉检查；但**浏览器下载的 zip 解压后 MOTW 会传播给包内文件**，所以必须是「非浏览器下载」。国内网盘对 exe 常有限制，实践中要压成（加密）压缩包。
- 向 Microsoft Security Intelligence 提交误报审查是免费的（`microsoft.com/wdsi/filesubmission`）。
- 给 EXE 填完整版本元数据、不加壳、**不自解压到 temp**（Electron portable 那种自解压是启发式加分项）。
- **企业环境有 AppLocker/WDAC 时，未签名 EXE 是被直接拦死，不是弹一次的问题** —— 「任何机器都不报错」在无签名前提下无法保证。
- **Azure Artifact Signing（原名 Trusted Signing，已改名）** 约 $9.99/月、无 USB token、CI 直连。但 **Public Trust 有地域白名单**：组织限 美/加/EU/英/澳/新/日/韩/新加坡/瑞士/挪威/以色列，**个人限美加** → 中国大陆主体与个人都用不了。不支持 free/trial/sponsored 订阅（须 PAYG 或 EA）。**不签发 EV 且无计划**。CN/O 不可自定义，必须是核验过的法人名。Private Trust 不受地域限制但不解决 SmartScreen。
- **OV 证书** $150–300/年，全球可买（DigiCert/Sectigo/GlobalSign）；2023-06 起 CA/B 强制私钥存 HSM/硬件 token。
- **EV 证书自 2024 起不再即时绕过 SmartScreen**，与 OV 走同样的信誉累积 → 单为「别弹警告」多花 $400+ 已不值。
- **签名 ≠ 不弹 SmartScreen**：官方 FAQ 原文「reputation builds up automatically. The prompt stops appearing once the file hash has sufficient download history」。2026 年 4–7 月有大量微软问答在抱怨此点。
- **SignPath Foundation（开源免费 OV 级）** 硬条件：OSI 许可（禁商业双许可）+ 公开仓库 + **已有一次与目标包对应的公开发布** + 活跃维护历史 + 二进制在 GitHub 官方 runner 上可验证构建（`actions/upload-artifact@v7` + `signpath/github-action-submit-signing-request@v3`）+ 每次发版人工批准 + 贡献者开 MFA + 分支保护 ruleset。**证书主体是 "SignPath Foundation"，不是项目名**。
- 自查命令：`signtool verify /v /pa <exe>`、`Get-AuthenticodeSignature <exe> | Format-List Status,SignerCertificate,TimeSigned`、时间戳健康检查 `curl http://timestamp.acs.microsoft.com`（200 = 健康）。

## MSIX 打包应用的文件系统约束（官方 desktop-to-uwp-behind-the-scenes，2026-01-28）

- **包内只读**：`C:\Program Files\WindowsApps\<pkg>` 不可写 → 任何「EXE 旁边的数据目录 / 便携工作区」设计在 MSIX 下必然失效。
- **包外可写**：「Write outside the package: Allowed if the user has permissions」→ 用户自选的任意目录（非 AppData）在 full-trust 打包桌面应用下可以写。
- **AppData 会被虚拟化**：包内应用新建到 `AppData` 的文件被重定向到 per-user/per-package 私有位置，**卸载时被系统一并清除** → 用户数据默认落 `%LOCALAPPDATA%` 与 MSIX 分发是冲突的。

## electron-builder 26.x（读本地 `app-builder-lib/out/*.d.ts` 比网上文档准）

- `win.target` 有 `nsis` / `nsis-web` / `portable` / **`appx`**，**没有 `msix`**。AppX 只能在 Windows 10 上构建，且强制 sha256。
- `win.azureSignOptions`（`publisherName` / `endpoint` / `codeSigningAccountName` / `certificateProfileName` / 默认 `timestampRfc3161=http://timestamp.acs.microsoft.com`）与 `win.signtoolOptions` **互斥**；两者都不配时默认走 Azure Trusted Signing（内置 `WindowsSignAzureManager`）。
- `signExecutable: false` 是**合法字段**（跳过签名但保留 resedit 资源编辑），不是笔误。
- 证书与口令走环境变量 `CSC_LINK` / `CSC_KEY_PASSWORD`（或 `WIN_` 前缀），别写进 package.json。

Related: [[reference-git-push-needs-local-proxy]], [[reference-windows-batch-entry-encoding]], [[reference-qt-qml-licensing-traps]]
