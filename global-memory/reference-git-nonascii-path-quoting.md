---
name: reference-git-nonascii-path-quoting
description: git 文本模式输出会把非 ASCII 路径转成八进制转义串，导致「本地 vs 远端」文件集比对得出全不匹配的假结论；正确取法是 ls-tree -z + bytes，且比哈希前要先归一化 CRLF
metadata:
  type: reference
---

2026-11-02 实测（Windows + git 2.52.0.windows.1，仓库含中文目录名）。
写「拿 git 输出和文件系统做比对」的取证脚本时的三条硬规则。

**1. 文本模式的路径清单对非 ASCII 不可用。**
`git ls-tree -r --name-only` / `git diff --name-only` 会把中文路径输出成
`"\350\267\250\345\271\263...\345\217\221/.gitignore"` 这种**带引号的八进制转义串**（`core.quotePath` 默认 true），
与 `os.walk` 拿到的原始 UTF-8 路径交集恒为 0。
后果不是报错而是**静默得出「两边完全不一样」的假结论**——我据此差点报「本地是另一套代码」，
同一轮内换了命令又复发一次（`git diff --name-only` 算「远端新增 ∩ 本地未跟踪」得 0，真值是 56/56 全撞）。

**2. 用 `-z`，但注意 `-z` 在 diff 上行为不符文档。**
`git ls-tree -r -z` 正常（NUL 分隔、不转义），实测可用。
`git diff -z --name-only` 与 `git diff -z --raw` 实测**输出里没有 NUL**（整段被当成 1 条），
所以求「两个 rev 之间的文件集差」宁可改成：对两个 rev 各跑 `ls-tree -r -z` 拿字典，自己做集合差。
接收一律用 subprocess 的 **bytes**，自己按 `b'\0'` 切、`decode('utf-8')`。

**3. 判「两份代码是否同一版本」，比哈希前必须先归一化行尾。**
本机 `core.autocrlf=true` 且仓库有 `.gitattributes` ⇒ 远端 blob 是 LF、Windows 工作区落 CRLF。
直接比 `sha1(b"blob %d\0" + data)` 会把行尾差异读成内容改动。
实测某目录：原始比 → 10 个「有差异」；`data.replace(b'\r\n', b'\n')` 后再比 → **真实内容差异 0**。

**4. 别把 `--name-only` 的输出再手工加引号喂给 `git commit --only`.**
2026-11-09 用 `sed 's/^/"/;s/$/"/'` 给 `git diff --cached --name-only` 的八进制转义路径再包一层引号，
得到 `""06-\345...""`，`git commit --only` 直接报 pathspec 不匹配。索引里确认只有目标目录时用普通
`git commit`（或先 `git add` 显式路径）更稳；要脚本化就传原始路径，别再加工。

**结论要分四类报，别只报一个「不同」**：同名同哈希 / 仅 CRLF 差异 / 真实内容差异 / 单边独有。
一次比对出现「全部不匹配」这种极端值时，**先怀疑取数方式，再怀疑被测对象**
（同 [[feedback-stub-artifacts-before-system-claims]]、[[feedback-no-unverified-cause-claims]]）。

相关：[[reference-windows-python-encoding]]、[[reference-powershell-through-bash-and-recyclebin]]、
[[reference-git-credential-manager-windows]]
