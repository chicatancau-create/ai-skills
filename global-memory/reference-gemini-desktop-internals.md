---
name: gemini-desktop-internals
description: Gemini 桌面版(Windows/Electron)主界面语言 —— 账号语言改了无效，必须给 asar 里 /src/main.js 打两处 ?hl= 补丁；含日志骗人和带参数秒退的坑
metadata:
  type: reference
---

Gemini 桌面版 (`%LOCALAPPDATA%\Google\Gemini\app-<ver>\`, Electron + `resources\app.asar`) 的界面语言分布是**两套机制**，排查时不要混：

- **外壳窗口**（设置弹窗、加载页、顶栏/返回栏）= asar 里的本地 HTML + `_locales/` 翻译，跟随 `app.getLocale()`（= Windows 显示语言）。系统改中文后这部分自动变中文。
- **主内容区** = 远端网页，URL 在 bundle 里硬编码为 `https://gemini.google.com/app`（变量 `de`，无 env / 无 CLI 开关可覆盖）。语言由 Google 服务端判定。

**已确认的事实**：
- 应用设置项里**没有任何语言开关**（`settings_*` i18n key 全集里没有 language），所以「在界面里改成中文」不可能。
- 实测 Google `/app` 的语言优先级：`?hl=zh-CN` 参数 > `Accept-Language` 头 > `HL` cookie（cookie 在匿名请求里几乎不起作用）。
- Electron 会话**认** `%APPDATA%\Gemini\Preferences` 里的 `intl.accept_languages`：写入后应用会读进去并在退出时保留该 key（同时自己补 `browser`/`spellcheck` 字段）。**但实测改这个不能把主界面变成中文**（2026-09-21 验证：写 `zh-CN,zh` 后界面仍英文）—— 已登录会话的语言不看 Accept-Language，只有 `?hl=` 参数这条路有效。
- **不要用自定义参数启动它验证东西**：`Gemini.exe <任意额外参数>` 或给启动器传 `--remote-debugging-port` 都会让进程**立刻自行退出**（0 个进程存活），所以 CDP 这条路是死的。只能用无参数的 `Start-Process ...\Google\Gemini\Gemini.exe` 启动。
- **它的日志会骗你**：`window_manager` 那行 `Loading Gemini shell: <url>` 经过 `Z()` 处理，而 `Z()` 只输出 `protocol//host/pathname`，**查询串被抹掉**。所以日志里看到不带参数的 `https://gemini.google.com/app` 并不代表没加参数 —— 别据此判定补丁失败。
- 主界面 URL 的真实取值顺序：`_n()` 里 `n = zi(V("lastAccountUrl","")) ?? de`，然后 `loadURL(loading.html)` 完再 `loadURL(n)`。`lastAccountUrl` 为空时用硬编码常量 `de`（在 `/src/main.js`，整个 asar 里只出现 1 次）。

**根因（2026-09-21 实测确认，别再往账号语言上找）**：用户的全部 4 个 Google 账号首选语言**都已经是简体中文**，桌面应用照样英文 —— 所以账号语言对这个应用无效。真正决定它的是 `%APPDATA%\Gemini` 这份**独立会话档案**（多账号在应用里共用同一个 cookie 库，切账号也不变），而它那份状态是英文。浏览器里同一个账号是中文，因为浏览器是另一套档案。⇒ 只有 URL 层的 `?hl=` 能压过它。

**生效的补丁（两处，都在 `/src/main.js`）**：
1. `de="https://gemini.google.com/app"` → 末尾加 `?hl=zh-CN`。只管第一次启动。
2. `zi()` 里 `t.search=""` → `t.search="?hl=zh-CN"`。**必须一起改**：`zi()` 会把查询串剥掉并存进 `lastAccountUrl`，之后（尤其切账号后）加载走的是这条缓存地址，只打补丁 1 会出现「第一个账号中文、换账号变英文」。改完连已经存歪的 `lastAccountUrl` 也会在下次读取时被补回参数，不用清数据。
补丁 1 单独用 = 半生效，别只打一半。
- asar 可以**手工按二进制改写**而不必重打包：头是 `[u32=4][u32 H][u32 S][u32 jsonLen][json+补零]`，数据区起点 `8+H`；改完一个 entry 的 size 后按 offset 升序重排后续 offset 即可。此包 25 个内嵌 entry + 147 个 unpacked（字体/`_locales`/`gemini_native.node`/`package.json`），unpacked 的不进数据区所以不受影响。**没有 asar 完整性 fuse** —— 打完补丁应用照常启动。
- 用户数据目录是 `%APPDATA%\Gemini`（不是 `Default\` 子目录结构）；日志在 `%LOCALAPPDATA%\Google\Gemini\logs\gemini.log*`，里面**没有** locale / 请求头信息。

**这台机器上的坑**：读 `Network\Cookies` 会被权限分类器直接拦（含登录令牌），别试；PowerShell `CopyFromScreen` 截屏也拿不到桌面（`InvokeMethodOnNull`），和 [[computer-use-blocked]] 同源。⇒ 验证 GUI 结果只能让用户自己看。

相关：[[feedback-plain-language-first]]、[[reference-qoder-app-internals]]
