# 备份归口与合并规则（2026-11-25 确立）

## 事实

本机备份/回滚/历史快照统一归口到 `G:\数据备份\`，不再散落在业务工作区。

- `G:\CodeWeave\工作区\data\迁移回滚` 已于 2026-11-25 整体移入 `G:\数据备份\`，
  随后与 `全栈工程师学习资料库_20261120_单盘数据备份` 全量比对后合并，
  最终归档为 `G:\数据备份\全栈工程师学习资料库_20261120_合并版`。
- 两个原始快照（迁移回滚版、单盘数据备份版）在合并版被证明为完整超集后删除。
  合并版含完整 `.git`（HEAD `76f143f1a241bd83f3f0d70bb75d0e497238fc29`，344 提交，
  origin/domestic/atomgit 三远端）+ B 独有的 20 条 CodeWeave 内容。

## 规则

1. **不要在 `G:\CodeWeave\工作区\data\` 下重建 `迁移回滚`**。该目录已迁出，
   备份类内容一律放 `G:\数据备份\`。该目录下已有 `README-迁移回滚已迁出.md` 说明。
2. 旧路径 `G:\CodeWeave\工作区\data\迁移回滚\...` 出现在历史日志/审计 JSON 里时，
   **按历史证据保留原样，不要据此恢复目录**。需要真实路径时用 `G:\数据备份\` 下的合并版。
3. 合并/去重前必须先做**全量内容比对**，不能只看文件数或目录名：
   - 同大小文件要逐个算 SHA-256（本次 378,110 个全部一致，才敢判定 B ⊂ A）。
   - 差异要分类：A 独有 6,397 条全是 `.git`（不可替代）；B 独有 20 条是新知识（必须并入）。
   - 冲突文件逐行 diff 判定优劣，败方另存 `*.superseded-by-A` 留档，**不直接丢弃**。
4. 用户强调过「不要把里面的知识搞丢了」——合并等于**并集**，永不做「取一边丢一边」。

## 合并结论摘要

| 项 | 结果 |
| --- | --- |
| 两边共有文件 | 378,110 个，SHA-256 **100% 一致** |
| A（迁移回滚）独有 | 6,397 条，**全部 .git 内部对象** |
| B（单盘数据备份）独有 | 20 条（8 目录 + 12 文件），CodeWeave 发布适配层 |
| 内容冲突 | 仅 2 个文件，均判 B 优 |
| 合并版 | 466,302 条 / 384,240 文件 / 13.73 GB，A+B 完整超集 |

冲突判定：
- `scripts/verify_archive.sh`：A 硬编码旧盘符 `/e/OBsidian`；B 按脚本位置推导 + 新增 `SKIP_PRACTICE`。取 B。
- `.workbuddy/memory/MEMORY.md`：A 写「2026-11-06 起 `E:\OBsidian\...`」；B 写「2026-11-20 起 `G:\CodeWeave\工作区\...`」。取 B（新事实）。

## 踩坑

- `SHFileOperationW` + `FOF_ALLOWUNDO` 在本机 G 盘**并没有真的把 13.7GB 目录放进回收站**
  （G 盘 `$RECYCLE.BIN` 近乎空，空间直接释放）。想真正可回滚，应先用 `robocopy` 保留副本，
  或先确认 `$RECYCLE.BIN` 配额策略，不要假定 `FOF_ALLOWUNDO` 一定生效。
- `Get-ChildItem -Recurse` 在 20 万+ 文件的树上极慢且不加 `-Force` 会漏数隐藏 `.git`；
  核对规模必须用 `os.scandir`。

## 关联

- `D:\AI-Tool-State\fullindex\merge_scan.py`（全量扫描 + 哈希比对）
- `D:\AI-Tool-State\fullindex\merge_apply.py`（补齐 B 独有 + 冲突择优 + 写合并说明）
- `D:\AI-Tool-State\fullindex\merge_verify.py`（超集核验）
- `D:\AI-Tool-State\fullindex\merge_verify_git.py`（.git 逐字节核验）
- `D:\AI-Tool-State\fullindex\merge_notes.py`（防误建说明）
