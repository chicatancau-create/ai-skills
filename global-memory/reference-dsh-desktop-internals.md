---
name: reference-dsh-desktop-internals
description: DeepSeek Harness 桌面端本机机制：崩溃日志落点、模型卡图片能力字段 input、预设要逐行声明、bundle 会遮蔽内核同名包、overrides 只能写 pnpm-workspace.yaml。
metadata:
  type: reference
---

2026-11-03 在装 `dsh-super-agent` 一路踩出来的 DSH 桌面端（`D:\DeepSeek Harness`，内核 0.2.1-rc.5）机制。

**崩溃/启动日志**：`%APPDATA%\@deepseek-ai\dsh-desktop\logs\crash-<utc>-host.log`（另有 `-renderer.log`）。
host 那份含 `Failed plugins (N)` 全表和 `Plugins waiting for services (43)` 清单，**比 UI 上的错误有用得多**；
判"是否真崩"就看有没有比本次启动更晚的 crash 文件。

**装 bundle 会把应用装死**：bundle 的依赖若含与内核同名的 `@deepseek-ai/*`，pnpm 会把旧版装进
`profiles\desktop\node_modules\`，而 profile 是 **`nodeLinker: hoisted`**（扁平目录）→ **遮蔽内核 asar 里的版本**。
表现是**装的时候一切正常**（`Done in 5s`），只在**下一次冷启动**才炸：
`typert-loader … parameter codec has no create() factory` → `startup failed: 1 required plugin did not activate` →
窗口停在 "DeepSeek Harness is unavailable"。修法是把同名包**钉到内核同版**（registry 上 `next` tag 就是内核版本，
如 `@deepseek-ai/dsh-llm 0.2.1-rc.5`、`cordis 4.0.5`、`schemastery 3.18.5`、`cosmokit 1.8.6`）。

**两处必须记住的写法**：
1. **`pnpm.overrides` 写进 `package.json` 会被 pnpm 11 静默忽略**（警告原文：该字段不再被读取），
   必须写 **`profiles\desktop\pnpm-workspace.yaml` 的 `overrides:` 段**。写错位置时 install 只回
   `Already up to date`、版本一个没变 ⇒ **装完必须回读 `node_modules/@deepseek-ai/*/package.json` 逐个比版本**，别信 rc=0。
2. 用 **DSH 自带的 pnpm 大版本**（本机 11.28.5，`cmd /c corepack pnpm@11.28.5 install`）。
   corepack 默认是 12.5.1，跨大版本可能重写 `lockfileVersion: '9.0'` 让宿主自己的安装路径失配。

**预设（preset）的真实 schema**：内核提供的是 `agent-preset-registry` / `@deepseek-ai/dsh-agent-preset-registry`，
文档明写**注册表不扫描目录、也不接受 preset 路径**（所以 bundle 补丁里的 `roots:` 是无效的，
`@deepseek-ai/dsh-agent-presets` 这个名字在本机 asar 中出现 **0 次**）。
新建预设必须逐行插：

```yaml
- id: preset-solo                    # Loader 编辑地址
  name: '@deepseek-ai/dsh-agent-preset'
  config:
    id: solo                         # 会话保存的预设标识（与行 id 不同）
    name: Solo delivery
    description: …
    order: 10
    plugins: [ …子插件行，可含 !!js 条件… ]
```
声明会**提前加载**，所以加预设会把 plugins 里的插件拉起来。**保留 `!!js` 原文要用追加文本，
不要用 YAML 解析器回写**（一轮就把它抹平了）。

**模型卡与图片能力**：报错「当前模型不支持图片」判据在 `dsh-api-session-controller`：
`if (model.inputModalities !== void 0 && !model.inputModalities.includes("image")) throw … MODEL_DOES_NOT_SUPPORT_IMAGES`；
而 `dsh-llm-pi-ai` 里 `inputModalities: [...resolvedModel.input]` ⇒ **模型卡上的字段名是 `input`**
（`input: [text, image]`）。本机 profile 里 23 条模型卡是从 WorkBuddy 目录**手抄**的，
只抄了 id/name/contextWindow/maxTokens/reasoningEfforts，**能力字段全丢**，所以两条 V4.1-Flash 都收不了图。
改完要**重启内核**才生效（profile 配置在启动时读）。

**读内核版本/源码**：`app.asar`（174 MB）可直接按头解析，无需 asar CLI：
`pickle=uint32@4`、`jsonLen=uint32@12`、JSON 从偏移 16 起（用 `raw_decode` 忽略尾部填充），
**文件数据基址 = 8 + pickle**，再 `seek(base + offset)`。个别 `package.json` 条目没有 `offset`，要跳过。

**其它**：
- 本地网关（实测端口会变，如 9230 / 57000）**要鉴权**：`/` 回 401、`/api/presets` 回 403，
  所以我无法枚举预设名册；「语法正确 + 启动不报错」**不等于**服务已注册（Cordis 对不上号的行静默跳过）。
- 写 `.workbuddy-ai-catalog.json` 的是 `dsh-workbuddy-connect` 插件；它被卸后目录就成了**孤儿缓存**
  （价格/促销字段会停在过期值上，例如促销 11-01 到期但缓存仍写 `x0.00 free=true`），
  且 `/ai/status`、`/plugins/<x>/status` 全部 404 —— 想确认实时价格只能看应用界面或看实际扣费。
- **判会话是真跑还是僵死**：CPU 时间两次采样在涨 ≠ 在推进；要看 `~\.dsh\` 与
  `AppData\Roaming\@deepseek-ai\` 有没有落盘。实测见过「深度求索中 1h20m」但 `~\.dsh` **60 分钟零改动**、
  只有 Electron 的 ShaderCache/GPUCache 在动 = UI 在转圈，turn 已僵。
- `dsh plugin --profile desktop exec` **不是只读**（会触发 pnpm 安装写盘），见项目记忆
  [[project-dsh-agent-teams-deploy]]。

**2026-11-07 补：V4 会话转储格式（只读）。**
`~\.dsh\sessions\<项目slug>\<会话uuid>\session.v4.jsonl.zstd` —— zstd 压缩的 JSONL，Python 3.14 用
`from compression import zstd` 直接解压。事件类型：`session`（id/createdAt/cwd/parentSession/origin）、
`assistant/message`（`data.message.content`、`data.source.model`）、`tool/call|tool/result`、`step/start|end` 等。
**本机实测这些事件里没有结构化的 usage/token 字段**：要统计 token 只能回到
`storages\session_projcache\sessions\*.json` 的 `record.rows.tokenUsage.val.totals`；没有 usage 就标"来源不支持"，
别把消息正文里的数字当 token。

相关：[[project-dsh-agent-teams-deploy]]、[[reference-windows-permission-denied-as-missing]]、
[[feedback-control-test-needs-restart]]、[[reference-gemini-desktop-internals]]（同类 asar 补丁经验）

**2026-11-04 补：上面那套「钉到内核同版」有到期日，内核一升级就反过来炸。**
本机 nightly 从 0.2.1-rc.5 自更新到 **0.2.2-rc.1** 后，profile 里钉着的 `dsh-* 0.2.1-rc.5` /
`cordis 4.0.5` / `schemastery 3.18.5` / `cosmokit 1.8.6` 变成**降级**，崩溃日志里特征是
**只有一个插件的版本号与同批不一致且 `state:"disabled"`**（本次是 `include:session`），
随后 `startup failed: 1 required plugin did not activate` + 56 个插件排队。
⇒ 判据顺序：读 crash 的插件清单找那个"异类版本"，别去读排队表。
修法：从**新内核 asar** 里读它自带的 `node_modules/@deepseek-ai/*/package.json` 版本
（本次 `cordis 4.1.0`、`schemastery 3.19.0`、`cosmokit 1.9.0`、`dsh-* = 0.2.2-rc.1`），
照抄进 `pnpm-workspace.yaml` 的 overrides，再 `corepack pnpm@11.28.5 install --no-frozen-lockfile`，
**装完回读 node_modules 逐个比版本**（本次结果：11 个包到位，`仍是旧版的包 = 无`）。
`dsh-agent-presets` 仍是 super-agent 带的 `0.1.2-rc.1`，本次未致命但属同类隐患。

**装桌面端更新前的三道闸**（本次实测有效）：① `pending` 里包的 SHA512 与 `update-info.json` 声明一致
（「task inspection timed out」多半是 293 MB 大包下得慢，不是源坏——先看 `AppData\Local\@deepseek-aidsh-desktop-updater\pending`）；
② `Get-AuthenticodeSignature` Valid 且**主体序列号与已装 exe 相同**（本机 `91330105MACPN4X08Y`，GlobalSign EV）；
③ 应用确实空闲（ΔCPU≈0 + `~\.dsh` 近期零落盘）。三道过了才 `taskkill /F` + `installer.exe /S`（本次 25 秒，退出码 0）。
更新配置在 `resources\app-update.yml`（provider generic、channel nightly）。
装完用尽的 pending 包可直接删（本次删了 293,425,336 B）。

**2026-11-04 晚：钉版漂移已改成自动对齐（启动守卫）。**
`D:\DSH-Guard\dsh_kernel_sync.py`（纯标准库）+ `D:\DSH-Guard\start_dsh.bat`；
桌面 `DeepSeek Harness（启动自动对齐）.lnk` 与开始菜单 `DeepSeek Harness.lnk` 都指向该 bat
（原 TARGET 留档在 `~\.dsh\guard\原快捷方式目标.txt`，日志 `~\.dsh\guard\sync.log`，改盘前自动备份）。
守卫从 **app.asar 的 `/dsh/node_modules/@deepseek-ai/*/package.json`** 读目标版本、
从 `runtime/versions.json` 读 pnpm 版本，两层校验（YAML + `node_modules` 实装），
rc：0=已对齐(0.1s) / 1=已自动修好 / 2=修失败(包装器 pause 报警)。
**两个语义坑**：①「profile 里没装该包」是正常的（cordis 由内核提供），当故障会导致每次启动白跑安装；
②只比 YAML 会漏「配置对但包旧」。
**盲区**：electron-updater 装完直接重启主 exe，绕过包装器 ⇒ 升级后第一次自启仍可能崩一次。

**2026-11-07：装/卸插件与 provider 的四个动作点（本轮实测）。**
- **装插件**：`dsh plugin --profile desktop add <包名>`（转发 pnpm）。**包名一律不加引号**——`dsh.cmd` 会再包一层，
  cmd 把引号烤进参数，pnpm 收到 `"@dsh-market/plugin"` 就写成垃圾别名（`plugin"` / `memsearch-dsh"`），
  报 `ERR_PNPM_INVALID_DEPENDENCY_NAME` 并整条失败；**但已解析的包已经落盘**，留下「装了仨、坏俩」的混合态。
  `add` 成功后**会自己把包追加进 `dsh.profile.bundles`**（不是只写 dependencies）；bundles 是加载顺序，
  `@local/dsh-preset-switcher` 要留在最后。
- **判包能不能装**：看 `package.json` 有没有 `dsh.bundle.patch`，再比 `@deepseek-ai/*` 依赖区间是否含本机内核 0.2.2-rc.1。
  实测：`billion-context-dsh` 要求 `dsh-llm <0.2.1-0` ⇒ 不能装，`billion-context`（无宿主依赖）才对；
  `dsh-memsearch` 无 `dsh` 字段且依赖旧版 `dsh-agent` ⇒ 用 `@zilliz/memsearch-dsh`。
- **验证**：桌面 profile **不能** `dsh --profile desktop --dump-config`（`profile "desktop" is managed exclusively by the Electron application`），
  `dsh plugin --profile desktop list` 可用；真正的证据是重启 GUI 后「插件 → 已安装插件」列表（可截图留证）。
- **删 provider 插件**：它通常只是 `cordis.patch.yml` 里一段 `@deepseek-ai/dsh-llm-pi-ai` 的 `providers:`；
  删整段 + 把 `agent-default-model` 和 `subagent-model-selection-settings.allowedModels` 指回官方。
  **官方账号 provider id = `deepseek-account`**，模型 `deepseek-flash`（显示名 DeepSeek-V4.1-Flash）/ `deepseek-v4-pro`
  （`deepseek-official` 只出现在 ACP 文档示例里，别拿它当 desktop 的 provider id）。
  改前备份、改后用 SafeLoader（额外注册 `!!js` 构造器）解析、**关应用前后比 SHA256**确认退出不覆盖。

**2026-11-07 晚：插件界面汉化 + 两个会炸启动的写法 + memsearch 依赖链。**
- `@zilliz/memsearch-dsh` 这类插件**没有 i18n**，文案硬编码在 `node_modules/<包>/client.js`；
  逐条换成中文后 `node --check`，重启 GUI 生效。汉化脚本已迁到 **`D:\DSH-Guard\_maintenance\localize_memsearch.py`**
  （同目录 `_rollback\` 放了 5 个原件，`_backup\` 是它的备份目标），幂等，**插件升级覆盖后重跑一次即可**
  （它同时把 `summarizeEnabled: false` 写回该插件自己的 bundle patch）。
- **用户层 `cordis.patch.yml` 只写 `- id: xxx`（不带 `name`）会让应用起不来**：表现是 5 个进程在跑但
  `MainWindowHandle=0`（无窗口），`crash-host.log` 里是 `host exited with 4294967295: 1 entry did not activate`，
  被点名的却是 `experimental-inspector: globalThis.fetch is an accessor...`（**症状指向的插件不是元凶**）。
  要改插件配置就改它自己的 `cordis.patch.yml`（带 id+name），别在用户层写裸 id。
- memsearch 三层依赖：`uv tool install "memsearch[onnx]"`（本机落 `D:\uv\tools` + `D:\uv\bin`，PATH 已加）；
  默认嵌入是 OpenAI 要 key ⇒ `memsearch config set embedding.provider onnx` + `milvus.uri` 指 D 盘；
  摘要走 `dsh headless` 的 **API key 路由**（`deepseek-official`）本机没有 ⇒ 关掉 `summarizeEnabled`，改原文写入。
  面板“打开目录”硬编码 `xdg-open`，Windows 只回显路径。

**2026-11-09 补：memsearch 的实际落点与本机取舍。** CLI 装在 `D:\uv\bin\memsearch.exe`（0.4.23），
工具目录 `D:\uv\tools\memsearch`、HF 模型缓存 `D:\uv\data\huggingface`（bge-m3 int8，约 561 MB）、
向量库 `D:\uv\data\memsearch\milvus.db`；`~\.memsearch\config.toml` 只放 provider/model/uri。
**摘要关闭是写进插件自己的 `cordis.patch.yml`（`summarizeEnabled: false`），不是用户层**——因为
`dsh headless` 走 API key 路由（`deepseek-official`），本机没配 key 时会每轮写「记忆不可用」。
面板文案汉化后需重启 GUI；「打开目录」按钮在 Windows 无效属插件缺陷，不是配置问题。
