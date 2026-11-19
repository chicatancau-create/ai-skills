---
name: reference-windows-ghost-drive-letter
description: Windows 多出来的盘符多半是 subst/DefineDosDevice 映射（同一卷所以卷名容量都相同）；判据是 vol 序列号 + QueryDosDevice + 分区表/注册表没有它；摘之前必须先查有没有构建进程在引用该盘
metadata:
  type: reference
---

2026-11-08 在 CodeWeave 上实测：资源管理器出现两个同名同容量的「AI」盘（G: 与 Q:）。
**Q: 不是第二块盘**，是把 `G:\CodeWeave\.local\prep\qt\6.8.3\msvc2022_64` 用 `subst` 映射出来的盘符；
映射目标在 G 盘上，所以标卷名、总容量、可用空间全都一样。

**判据（按这个顺序，30 秒定性）**
1. `vol G:` 与 `vol Q:` 的**卷序列号相同** ⇒ 同一个卷（本次都是 A265-2993）。
2. `Get-Partition | ? DriveLetter` 里**没有 Q**，`Get-Volume` 也没有 ⇒ 不是分区。
3. `HKLM\SYSTEM\MountedDevices` 里**没有 `\DosDevices\Q:`** ⇒ 不是系统级盘符。
4. `QueryDosDeviceW('Q:')` 返回 `\??\G:\...` ⇒ **subst/DefineDosDevice 映射**，目标一目了然。
5. `subst`（无参数）能列出当前会话的映射；若为空但 QueryDosDevice 有值，说明映射在别的会话或由程序直接调用 API 建的。

**摘除**
`subst Q: /D`。注意两点：
- **路径带尾反斜杠时不要加引号**：`subst Q: "G:\a\b\"` 会被 cmd 解析成 `\G:\a\b\` 而报「找不到路径」；没有空格就别加引号。
- **摘之前必须先查有没有进程在用**：本次 `cmake -E env PATH=Q://bin ...` 正在跑测试，我摘早了 30 秒，
  立刻按原路径恢复（`subst Q: G:\CodeWeave\...`）并核对那轮测试全 `Test Passed`、取证截图正常产出，才确认没坏事。

**成因**：CodeWeave 的 `工程文件\工具\构建当前Qt.cmd` 每次构建挑空闲盘符映射 Qt 目录，结束时 `subst %D%: /d`；
**构建被中断（关窗口/被杀）时清理不执行，映射就留在会话里**，直到注销或手动删。
根治要在脚本里做 `:cleanup` 兜底（失败路径也跳过去删），而不是靠人记得。

Related: [[reference-windows-display-topology-probe]], [[reference-qoder-artifact-locations]]

**2026-11-08 补：清理/加固这类幽灵盘时两个必踩的坑。**
- **`subst <盘符>:`（只给盘符）不是合法查询**，本机直接回「无效参数」——原构建脚本那一行一直是失败分支，
  所以已有残留只会被"换个盘符绕开"，永远清不掉。查询只能用**不带参数的 `subst`** 列全表。
- **`findstr` 匹配含反斜杠的路径不可靠**：`/C:"G:\CodeWeave\.local\prep"` 对含该串的行返回 1，`/L` 也一样，
  但 `findstr "qt"` 能命中 ⇒ **别用 findstr 比路径**，改用纯 cmd：按 `>` 拆 `=>` 右侧、`for /f "tokens=* delims= "`
  去前导空格、`if /I "%%C"=="%QT_PHYSICAL%"`。
- 附带：`subst` 输出带 `=>`，`echo %%L` 里的 `>` 会被当重定向，整行要加引号；`%~dp0` 末尾自带 `\`，
  拼 `"%P%.local"` 在盘根会出 `G:\\`。
- 加固落点：CodeWeave 的 `构建当前Qt.cmd` 改为"先列全表认领残留、否则从 Q 起挑空闲"，新增
  `工程文件\工具\清理Qt幽灵盘.cmd`，`qt_setup_tool_path.bat` 改成从自身位置向上找 `.local\prep\...\bin`。

**补：清理脚本必须有"构建中拒绝执行"的守卫。** 我今天就几乎在 `cmake -E env PATH=Q://bin ...` 跑测试时删掉映射。
做法：`tasklist /FI "IMAGENAME eq cmake.exe"`（再加 ninja/ctest/被测 exe）任一命中就打印 [abort] 并 `exit /b 3`，别删。
实测：有假 cmake.exe 在跑时脚本拒绝且映射保留；杀掉后再跑正常删除。
