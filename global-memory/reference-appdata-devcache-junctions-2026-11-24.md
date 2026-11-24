# AppData 缓存已联接迁 D 盘（2026-11-24）——D 盘副本是真源不是重复数据

2026-11-24 把一批 AppData 应用数据/缓存用 Junction 迁到 D 盘，**C 盘原路径现在是联接，D 盘目录是唯一真源**。后续任何 AI 看到 D 盘这些目录不要当成「重复数据」清理，也不要再往 C 盘原路径写实体副本（写了会被守护合并回 D）。

## 联接映射

- `C:\Users\Admin\AppData\Local\<名>` → `D:\DevCache\AppData-Local\<名>`
- `C:\Users\Admin\AppData\Roaming\<名>` → `D:\DevCache\AppData-Roaming\<名>`
- 首批名单（以清单文件为准）：local 组 Doubao、Postman、Figma、OpenAI、JetBrains、AzureFunctionsTools、npm-cache、pip、pnpm-cache、pnpm；roaming 组 Code、Trae CN、obsidian、zen、JetBrains、Postman、npm。
- 开机任务 `EmulatorCacheMigrate` 还会补迁 `.android`（home 组）、`Android`、`Huawei`、`CapCut`（local 组），成功后自删。

## 登记与守护

- 清单：`D:\DSH-Guard\migrated_local.json` / `migrated_roaming.json`（键 `migrated`）；home 组仍是 `migrated.json`。
- 守护：`D:\DSH-Guard\migrate_guard_appdata.py`（复用 migrate_guard.main() 按组切换），已接进 `guard_on_logon.ps1` 与 `start_dsh.bat`。回流实体目录会被自动合并回 D 并恢复联接。
- 执行器：`D:\DSH-Guard\migrate_appdata.py local|roaming <名...>`；锁定目录开机脚本 `migrate_emulators.py`。

## 注意

- `AppData\Roaming\npm` 是活 npm 全局前缀（claude/codex/nrm/pi/tokentracker），联接后路径不变照常工作；`D:\node-global` 是另一前缀，两者别混。
- `UV_CACHE_DIR=D:\dev-cache\uv\cache`（小写 dev-cache，与 DevCache 是两个目录）；`AppData\Local\uv\cache` 是 0 MB 空壳，正常。
- 删联接必须用 `cmd /c rmdir`（只删链接），资源管理器删除会跟随联接回收 D 盘真源。
- 详见手册 `03-通用/04-工程规范与安全/经验-AppData缓存迁D盘复用DSH-Guard核心按组包装.md` 与 `G:\AIrenwu\04_磁盘与系统\磁盘整理\迁移防回归守护说明.md` 第十一节。
