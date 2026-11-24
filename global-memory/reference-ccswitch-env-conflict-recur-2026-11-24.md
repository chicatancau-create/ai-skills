# CC Switch「系统环境变量冲突」复发：真因是 headroom manifest 被整批写进注册表（2026-11-24 22:16）

> 追加条目，不改写旧条目。是对 reference-ccswitch-detection-and-agy-reinstall-2026-11-24.md 第 14 行「ANTHROPIC_TARGET_API_URL 已删除、无消费方」的现状更正与补全。

## 症状

CC Switch 4.0.40 主窗口顶部黄色横幅「检测到系统环境变量冲突 / 发现 2 个环境变量可能会覆盖您的配置」：
`ANTHROPIC_TARGET_API_URL=http://127.0.0.1:15721`、`OPENAI_TARGET_API_URL=http://127.0.0.1:15721/v1`，来源均为「用户环境变量（注册表）」。

## 真因（关键，避免误判为 CC Switch bug）

- 这俩变量**不是 CC Switch 写的**，是 **headroom 部署 manifest 被整批同步进 `HKCU\Environment`** 的副产品。
- 证据：注册表现存 27 个 `HEADROOM_*` 变量与 `C:\Users\Admin\.headroom\deploy\default\manifest.json` 的 `base_env` **逐项同名同值**（唯一缺 `HF_HOME`）；`ANTHROPIC_TARGET_API_URL`/`OPENAI_TARGET_API_URL` 只是这批里的两条。
- 所以「删了就再也不弹」是错的：只要有脚本再按 manifest 全量写注册表，横幅必然复发。**判据是看注册表里有没有整批 HEADROOM_*，而不是只看那两条。**
- 消费方事实更正：全局变量**没有**消费方，但 headroom 启动链**自己注入**同名变量，三处齐备，全在 `C:\Users\Admin\.headroom\deploy\default\`：
  - `run-headroom.ps1` L7-L9（`$env:HEADROOM_OFFLINE='1'` / `$env:ANTHROPIC_TARGET_API_URL` / `$env:OPENAI_TARGET_API_URL`）
  - `ensure-headroom.ps1` L7-L9（同上）
  - `manifest.json` `base_env`（L22 起，含全部 HEADROOM_* 与两条 TARGET_API_URL）
  ⇒ 删注册表变量**不影响** headroom 上游，符合 `D:\Skills\headroom\SKILL.md` L127-133 的 2026-11-20 修正。

## 处置步骤（实测有效）

1. 备份：`$snap | ConvertTo-Json | Set-Content D:\DevCache\.cc-switch\backups\env-manual-backup-<yyyyMMdd_HHmmss>.json`
2. `reg delete "HKCU\Environment" /v ANTHROPIC_TARGET_API_URL /f`；同法删 `OPENAI_TARGET_API_URL`（保留 `CODEX_HOME=D:\DevCache\.codex`）
3. 广播：`SendMessageTimeout(HWND_BROADCAST=0xffff, WM_SETTINGCHANGE=0x1A, 0, "Environment", SMTO_ABORTIFHUNG=2, 3000, out r)`；reg delete 本身不发通知，不广播则新进程读不到
4. **必须重启 CC Switch**：横幅读的是**启动时快照**，删完变量横幅仍在（本次实测删完再截图，横幅照旧）。`Stop-Process -Id <pid> -Force` → `Start-Process 'D:\CC Switch\cc-switch.exe'` → 约 10 s 后日志出现 `[SRV-001] 代理服务器启动于 127.0.0.1:15721` + `claude attach`/`codex attach`
5. 验证：横幅消失；`15721/health` 与 `8787/health` 均 200；重启后**没有**新增 `env-backup-*.json`（有新增＝它又检测到冲突）

## 重启 CC Switch 的副作用（重要）

- 重启会重写客户端配置，哈希必变：`C:\Users\Admin\.claude\settings.json`、`D:\DevCache\.codex\config.toml`。**变哈希 ≠ 变目标**，本次重启后仍是 `ANTHROPIC_BASE_URL=http://127.0.0.1:8787`、`base_url="http://127.0.0.1:8787/v1"`（即 headroom 仍在前、没被静默绕过）。复核要看 URL，不要看 hash。
- 强杀不走 detach 路径，但客户端配置本来就指向 8787（headroom 活着），15721 只断几秒，无感。

## 现网链路（本次实测，22:20）

`Agent → headroom 127.0.0.1:8787 → cc-switch 127.0.0.1:15721 → api.aruhub / 摸鱼 CodingPlan → deepseek-v4.1-flash`

- 8787 `POST /v1/messages`（model=claude-sonnet-5）→ HTTP 200，回 `"OK"`，`model` 字段被映射成 `deepseek-v4.1-flash`
- 15721 同一请求 → HTTP 200
- 进程：cc-switch PID 37936；headroom `python -m headroom.cli proxy --port 8787 ... --openai-api-url http://127.0.0.1:15721/v1`（PID 35048/35320 双壳）

## 取证小坑

- `Get-NetTCPConnection -LocalPort 15721 -State Listen` 会**查不到**监听（本次为空，但 curl `/health` 返 200）⇒ **判端口死活只能用 curl/HTTP 探测，不要信 netstat/Get-NetTCPConnection 的空结果**。
- CC Switch 静默启动后主窗口 14×14 且在托盘：枚举 `EnumWindows` 按 PID 找，真实内容窗是 1326×751/1536×904 那个隐藏窗；`ShowWindow(h,5)`+`ShowWindow(h,9)` 后 `PrintWindow(h, hdc, 2)` 可抓（14×14 那个抓到纯黑）；抓完 `ShowWindow(h,0)` 收回托盘还原用户原状。
- `Invoke-WebRequest` 对本地端口可能报 `(404) 未找到` 而非连接失败，容易误判「有人在响应」；用 `curl.exe -w "%{http_code}"` 判定。
- `curl.exe --data-binary` 传 PowerShell 里 `Set-Content -Encoding utf8` 生成的文件会带 BOM → 上游报 `malformed JSON`/`expected value at line 1 column 1`；必须 `[System.IO.File]::WriteAllText(path, json, [System.Text.UTF8Encoding]::new($false))`。

## 遗留（未做，等决策）

- 注册表仍有 27 个 `HEADROOM_*`（含 `HEADROOM_OFFLINE=1`、`HEADROOM_SAVINGS_TARGET=0.50`）。它们**不触发** CC Switch 横幅（横幅只扫 ANTHROPIC/OPENAI/GEMINI/GOOGLE_GEMINI/XAI 前缀），但违反 headroom SKILL.md 的 2026-11-20 约定；manifest 已含全量，删除理论安全，本次为降低风险**未动**。
- 没有任何 skill 脚本在写 `HKCU\Environment`（grep `D:\Skills` 无命中）⇒ 本次同步是一次性人工/会话操作，暂无自动复发源；但根因未封堵（无「禁止把 manifest 写注册表」的守门脚本）。

## 关联

- 旧条目：`D:\Skills\global-memory\reference-ccswitch-detection-and-agy-reinstall-2026-11-24.md`（检测三坑、agy 重装、npm 前缀）
- 架构：`D:\Skills\headroom\SKILL.md` L110-140；`D:\Skills\skill-router\SKILL.md`「链路 Agent→headroom:8787→cc-switch:15721」
- 回滚：把备份 JSON 里的两个值 `reg add "HKCU\Environment" /v <名> /t REG_SZ /d <值> /f` 写回，再重启 CC Switch 与 headroom。