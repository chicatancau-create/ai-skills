---
name: reference-qoder-app-internals
description: Where the Qoder desktop app keeps its own runtime state on this machine — main log, plugin registry (tmp+rename), plugin cache, search daemon process — for diagnosing app-level failures.
metadata:
  type: reference
---

诊断 Qoder 桌面端自身故障（不是项目代码）时的定位入口：

- **主进程日志**: `C:\Users\Admin\AppData\Roaming\com.qoder.app.stable\logs\<启动时间戳>-<pid>-<hash>\main.log`
  （国际版是 `com.qoder.app.stable`，CN 版是 `com.qodercn.app.stable`；目录名里的 pid 要和
  `~\.qoder\mcp-router.json` 的 pid 对上才是当前实例）。同目录还有 `renderer.log`、`app-plugin/`、`qodercli/`。
  CLI 侧日志在 `C:\Users\Admin\.qoder\logs\`（`qoder-context.log`、`qoder-search-indexing.log`、`sessions/`）。
- **插件状态**: 注册表 `C:\Users\Admin\.qoder\plugins\installed_plugins_v2.json` + 开关
  `C:\Users\Admin\.qoder\settings.json` 的 `enabledPlugins`；解包内容在 `plugins\cache\<market>\<id>\<version>\`。
  安装走「写 `installed_plugins_v2.json.<uuid>.tmp` → rename 覆盖」的原子替换，所以**残留的 .tmp 文件 = 失败的写入尝试**，
  数一下就能知道失败了几次、每次想把哪个插件写进去。
- **常驻进程**: 主进程会派生 `qoder-search.bundle.mjs mcp-bridge` → `... daemon-server`（知识中心/搜索索引），
  它加载 Rust 原生模块 `.../runtime/native/mtree/mtree.win32-x64-msvc.node` 遍历文件。
  插件注册表每次变化都会触发主进程 `PluginInventory` 重新读取 + 索引重载。
- **取证只能认 `.qoder-versions\<运行中版本>\resources\app.asar`（2026-10-20 踩实）**: 国际版运行体是
  `D:\Qoder\.qoder-versions\0.4.8\resources\app.asar`（157,775,573 B），CN 是 `D:\Qoder CN\.qoder-versions\0.4.8\...`（157,772,655 B）。
  而 `D:\Qoder\resources\app.asar`（138,460,165 B）与 `D:\Qoder CN\resources\app.asar`（139,525,650 B）**是旧版残留壳**，
  界面文案完全不同（子代理拿它取证就把成立的功能判成不存在，来回返工一轮）。
  版本目录会堆 `0.4.4 / 0.4.7 / 0.4.8`（各带 `.qoder-update-ready.json`），判"哪个在跑"用进程路径：
  `Get-Process | Where-Object Name -match 'Qoder'` 的 `Path` 里那段版本号才算，别按文件存在与否推断。

**How to apply**: 用户报「Qoder 装不上/扩展配置写不进去/插件状态不对」时，先 grep `main.log` 里的
`Extension install stage failed` 拿 `stage` 和 `errorCode`，再对照 `plugins\` 下的 .tmp 残留，
比在 UI 上反复重试有效得多。判断文件是否被锁：用 ctypes `CreateFileW(..., DELETE, FILE_SHARE_ALL, ...)`
探测比盲目改文件安全（Rust `std::fs` 默认不带 `FILE_SHARE_DELETE`，会挡住 rename）。

相关：[[feedback-windows-config-json-encoding]]、[[feedback-rigor-audit]]
