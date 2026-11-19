---
name: reference-windows-longpath-scan
description: Windows 上不带 \\?\ 前缀的 os.walk/open 会「看不见」>260 字符的条目，据此得出的「超限 0 / 文件缺失 / 全绿」结论一律不可信；扫描与读取都要加前缀并复核
metadata:
  type: reference
---

**判「路径是否超限」「文件是否存在」的扫描，必须带 `\\?\` 前缀，否则同一缺陷会反复报「全绿」。**
源码里用 `chr(92)*2 + "?" + chr(92)` 构造，别在 bash heredoc 里写字面反斜杠串（会被吞，见
[[reference-windows-python-encoding]]）。

- 现象：`os.walk('E:\\...')` 走到某个目录时，若目录名本身已把子项推到 260 字符以上，
  **该子目录直接不进枚举**（不报错、不抛异常）；`os.path.exists()` 对同一长路径回 False。
  于是「扫描全库 = 0 个超长路径」「某文件不存在」这类结论是测量盲区，不是事实。
- 实测代价：2026-11-05 在 32 万文件的资料库上，不带前缀数 316,488、带前缀数 316,489，
  差的正是那条 271 字符（`_remote_assets/<host>/<base64>=image/format,png`，URL 查询串被转成目录层级）；
  上一轮据此写下的「路径超限 0」「记账漂移 0」都是假阴性，已公开更正。
- 前缀的副作用：带 `\\?\` 的路径与不带前缀的起点做 `os.path.relpath()` 会抛
  `path is on mount '\\\\?\\E:' ...`；`Path(...).relative_to()` 同样失败。规则：**存盘与比较一律用不带前缀
  的普通路径，只在真正调 os.walk/open/getsize 的瞬间加前缀**；也不要对已带前缀的路径再 `abspath()`。
- 修法优先「展平」而不是留着长名：把文件移到上一层宿主目录并改名 `asset-<md5前12><ext>`，
  **原名→新名 + 字节数 + 整文件 md5 必须落一个映射 JSON**，否则后续按 URL 反推文件名的校验会把它算成缺失
  （我就为此把一处命中判据补成查映射表）。目录名长才是根因时，只删「由 URL 派生的空目录」（basename ≥80 字符），
  上游 tar 里的正常空目录不动。
- 写文件名的上限取 **250**，给后续拼接与 Obsidian 留余量；改名/移动后要复扫一次并把「剩余超长 = 0」当结论输出。

相关：[[feedback-rigor-audit]]、[[reference-windows-python-encoding]]、[[feedback-verify-subagent-file-claims]]
