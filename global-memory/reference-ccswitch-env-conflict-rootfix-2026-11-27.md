# CC Switch「系统环境变量冲突」第二次复发 → 根因封堵（2026-11-27 08:32）

> 追加条目，不改写旧条目。更正 `reference-ccswitch-env-conflict-recur-2026-11-24.md` 末尾「根因未封堵…暂无自动复发源」的判断：**那条判断是错的，有自动复发源，本次已封堵。**

## 症状（与 11-24 完全相同）

CC Switch 4.0.42 主窗口顶部黄色横幅「检测到系统环境变量冲突 / 发现 2 个环境变量可能会覆盖您的配置」，`HKCU:\Environment` 里又出现：

- `ANTHROPIC_TARGET_API_URL = http://127.0.0.1:15721`
- `OPENAI_TARGET_API_URL = http://127.0.0.1:15721/v1`

## 真因（源码级证据）

- 计划任务 **`headroom-default-health`**（State=Ready，动作 `wscript.exe //B //Nologo "C:\Users\Admin\.headroom\deploy\default\ensure-headroom.vbs"`）周期性跑 `ensure-headroom.ps1`。
- `ensure-headroom.ps1` L8-9：`$env:ANTHROPIC_TARGET_API_URL='http://127.0.0.1:15721'` / `$env:OPENAI_TARGET_API_URL='http://127.0.0.1:15721/v1'`，L30 `headroom.EXE install agent ensure --profile default`。
- `headroom/install/providers.py` **L185-189** `apply_mutations()`：`if manifest.scope in {ConfigScope.USER.value, ConfigScope.SYSTEM.value}` → `_apply_windows_env_scope(manifest)`。
- 同文件 **L113-152** `_apply_windows_env_scope()`：把 `_unix_scope_values(manifest)`（= `manifest.base_env` + `manifest.tool_envs` 合并）**逐个** `[Environment]::SetEnvironmentVariable(name, value, 'User')` 写进注册表。
- `handler` 链：`install_agent_ensure()`（`headroom/cli/install.py` L1289-1319）在部署不健康时 `_deactivate_deployment_mutations()` → 停 → 起 → `_activate_deployment_mutations()`（L356-374）→ `manifest.mutations = apply_mutations(manifest)` ⇒ 全量重写注册表。
- 结论：**`scope=user` + `base_env` 里含 ANTHROPIC/OPENAI 前缀键 = 每次重启 headroom 代理就往注册表写一次横幅触发源**。删变量只是治一次。

## 根治做法（改 manifest，不动 headroom 源码）

上游 URL 改用 **CLI 参数** 承载，绕过环境变量与注册表：

1. 备份 `C:\Users\Admin\.headroom\deploy\default\manifest.json` → `G:\AIrenwu\_tmp\headroom-manifest-backup-<ts>.json`
2. `proxy_args` 追加 `--anthropic-api-url http://127.0.0.1:15721`（`--openai-api-url http://127.0.0.1:15721/v1` 原本就在）。依据：`headroom/cli/proxy.py` L1092-1101 这两个是 `headroom proxy` 的 click option，与环境变量同效。
3. 从 `base_env` 删除 `ANTHROPIC_TARGET_API_URL`、`OPENAI_TARGET_API_URL`（28 → 26 条）
4. **同时从 `mutations` 删除对应的两条 `target=env` 记录**（28 → 26 条）。不能省：`_remove_windows_env_scope()` 还原时按 `mutations[].data.previous` 回写，旧记录 `previous` 为空串，留着会被写回空值。
5. 注册表删值 → 广播 `WM_SETTINGCHANGE`（`SendMessageTimeout(0xffff, 0x1A, 0, "Environment", 2, 3000)`）→ 重启 CC Switch（横幅读启动快照）。
6. 验证：`http://127.0.0.1:8787/readyz` 的 `checks.upstream.url` 应为 `http://127.0.0.1:15721`、`status=healthy`；`15721` 直连返 404（正常，根路径无路由）；`~/.claude/settings.json` 的 `ANTHROPIC_BASE_URL` 仍是 `http://127.0.0.1:8787`。

## 执行结果（2026-11-26 23:32 - 11-27 08:32 复核，跨 8 小时仍成立）

- 注册表两个变量：空。
- CC Switch：PID 37144（23:32:54 重启后启动），15721 监听正常；横幅应已消失（读的是重启时快照）。
- headroom：`8787/readyz` 200，`upstream.url=http://127.0.0.1:15721` healthy；`runner.pid=38748`。
- manifest mtime 08:05:29（健康检查又跑过），但 `base_env` 已无这两个键、`proxy_args` 仍带 `--anthropic-api-url` ⇒ 自动复发链已断。

## 可复用规则

- **判断「一次性人工同步」还是「程序自动回写」：看目标文件 mtime 与哪个计划任务/常驻进程活动时间对齐。** 对齐了就是自动源，光删变量必复发。
- **给代理链排除冲突变量需同时改三处**：启动脚本、manifest 的 `base_env`、manifest 的 `mutations` 历史。少改 `mutations` 会在下次 detach/attach 被写回空值。
- **优先用 CLI 参数承载上游 URL，而不是全局环境变量**：不经过注册表、不污染其它客户端、不被第三方切换器扫描。
- **manifest 的 mtime 会被健康检查不断刷新，不能拿 mtime 判「有没有被改回去」**，要读 `base_env`/`proxy_args`/`mutations` 实际内容。
- 沙箱为 workspace-write 时，`HKCU:\Environment` 写入与 `C:\Users\Admin\.cc-switch\backups\` 写入都会被拒（`Requested registry access is not allowed` / `Access to the path ... is denied`）；备份改落 `G:\AIrenwu\_tmp`。

## 关联

- 前序：`D:\Skills\global-memory\reference-ccswitch-env-conflict-recur-2026-11-24.md`、`reference-ccswitch-detection-and-agy-reinstall-2026-11-24.md`
- 手册：`G:\AIrenwu\本地AI使用手册\03-通用\03-调试与验证\踩坑-CCSwitch环境变量冲突复发-headroom-manifest整批进注册表与横幅需重启才消.md`（已追加「2026-11-27 第二次复发与根治」节）
- 架构：`D:\Skills\headroom\SKILL.md` L110-140
