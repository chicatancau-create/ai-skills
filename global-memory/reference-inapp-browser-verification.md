---
name: reference-inapp-browser-verification
description: How to get real-browser UI evidence in this environment — hidden in-app tab limits screenshots, so self-spawn headless Chromium over plain ws/CDP (no Playwright), never attach to a fixed debug port, and set viewports via Emulation not --window-size
metadata:
  type: reference
---

The connected `browser-use` surface in this setup is Qoder's **in-app Browser tab**, which is usually `visibilityState: 'hidden'`. Consequences observed on 2026-09-20:

- `take_screenshot` fails with `NATIVE_BROWSER_VIEWPORT_UNAVAILABLE` while the tab is hidden (structural `take_snapshot` and `evaluate_script` still work).
- There is **no viewport control** in the exposed tool set, so any acceptance criterion phrased as "compare screenshots at 1280×720 / 1440×900 / 768×1024 / 390×844 / 320px" cannot be met silently — record it as not executed and ask the user to open the tab.
- What *is* provable headlessly, and is often stronger evidence than a screenshot: computed styles and geometry via `evaluate_script` (resolved token colors, font-size/line-height/weight/letter-spacing, `getBoundingClientRect` for touch targets, `scrollWidth - innerWidth` for overflow, the set of non-`none` `animationName` values, canvas/WebGL counts), plus a real `press_key` Tab to confirm `:focus-visible` styling.
- `navigate_page` + `fill` + `click` + `take_snapshot` all work on the hidden tab (re-confirmed 2026-09-21 while testing Vue emit/button handlers), so interaction proof does not need a visible window — only pixels do. Pair it with a self-spawned headless Edge `--screenshot` of the same URL for layout.
- **`click` and `press_key` silently no-op on this hidden tab some of the time** (observed twice 2026-09-21: a checkbox click and a filter-button click returned "Successfully clicked" but changed nothing; `press_key` Enter reached the page once then stopped reaching it). A no-op looks exactly like an app bug — before rewriting any handler, re-fire it with `evaluate_script` (`el.click()`, or set `.value` + dispatch `input` then `keyup`). Script dispatch drove every feature correctly, so treat tool-level click failures as harness noise, and note that DOM reads right after a dispatch are pre-render (Vue updates on nextTick).
- Caveat found: `press_key` Enter delivers `keydown` to the focused input but the browser's **implicit form submission does not fire**, while Tab's default action does work. Do not report that as an app bug or as a pass — it needs a human at a visible window.

**How to apply:** for UI verification here, lead with measured computed-style/geometry evidence, list what genuinely requires eyes-on screenshots, and never mark a visual acceptance item as done from jsdom tests alone.

## Escaping the hidden tab: launch your own headless browser (2026-09-20)

The screenshot limitation above applies to the `browser-use` MCP surface only. A self-spawned headless Chromium gives real layout, real `getBoundingClientRect`, and working `Page.captureScreenshot` — use it when layout/visual proof matters.

Hard-won constraints on this box:

- **Never attach to a fixed debug port.** Qoder's own in-app headless Chrome already listens on `127.0.0.1:9333` and holds the app's tabs (Code Canvas previews etc.). A harness that probes a hardcoded port will silently attach to *that* browser and navigate the user's app tabs. Launch with `--remote-debugging-port=0` and read the real port from `<your-temp-user-data-dir>/DevToolsActivePort`.
- **Stable Chrome (137+, here 153) ignores `--load-extension`**, even with `--enable-unsafe-extension-debugging` — the MV3 service worker target never appears. **Edge 153 loads unpacked extensions headlessly** (`--headless=new --load-extension=<dir>`), so prefer Edge for extension E2E and fall back through candidates.
- Node harnesses holding a CDP WebSocket + HTTP server never exit on their own; call `process.exit()` explicitly after cleanup (`taskkill /PID <child> /T /F` for the browser tree).
- Mock an unreachable third-party API at the network layer instead of skipping the test: `Fetch.enable` + `Fetch.fulfillRequest` on the *service worker* session intercepts its `fetch` calls.
- **`--window-size=390,844` does NOT give a 390px viewport.** Headless Edge clamps the window to a ~496px layout width and then crops the PNG to the requested size, so the image looks like mobile but is a clipped desktop render (elements appear "cut off at the right edge" although nothing is overflowing). To prove a narrow layout, screenshot a harness page containing `<iframe width="390" height="844" src="…">` at a legal window size. Verify with `innerWidth` (dump it into the DOM and read it back with `--dump-dom`) before believing any "overflow" you see.
- `--virtual-time-budget=Nms` advances timers deterministically, so one instrumented copy of a page can yield several states (e.g. budget 400 → in-flight/loading frame, budget 1600 → settled/error frame) without a CDP harness.
- **Responsive widths: use `Emulation.setDeviceMetricsOverride`, not `--window-size`.** The window-size trap above only applies to the CLI `--screenshot` path; with a CDP session, overriding device metrics gives honest 1280 / 860 / 375 layouts (re-confirmed 2026-09-24: three widths measured with zero horizontal overflow off a `file://` page).
- **No Playwright needed — `ws` alone drives CDP.** The existing harnesses on this box are plain Node + a ~25-line CDP class over the `ws` WebSocket (JSON-RPC `id`/`sessionId` map, plus an `on(method, fn, sessionId)` hook list for `Fetch.requestPaused` / `Runtime.exceptionThrown`), reusing the already-installed `ws` from the translator project's `test-lab/node_modules`. Prefer copying an existing harness over installing packages — this machine's network to external CDNs/registries is unreliable.
- **本机系统主题是深色**, so a headless browser reports `prefers-color-scheme: dark` by default and screenshots silently differ run-to-run; pin it with `Emulation.setEmulatedMedia` (features `prefers-color-scheme`) before any visual comparison, and measure both themes when asserting contrast.
- Poll for readiness rather than sleeping a fixed time, and expect nulls mid-navigation: right after `Page.navigate` `document.documentElement` can be `null` (return a sentinel like -1 and keep polling), and the MV3 service-worker target only shows up in `/json/list` after the first navigation wakes it.

## 2026-10-08 更新（无 ws 依赖、裁切判据、以及"让用户手点"的场景）

- **不需要 `ws` 包了**：本机 `node_modules/ws` 找不到，而 **Node 24 有全局 `WebSocket`**（undici），25 行 CDP 类直接 `new WebSocket(url)` 即可。旧记录里指向 `E:\插件（ai）\test-lab\…` 的现成 harness **随工作区迁移已不存在**，别再去找。
- **`scrollWidth == clientWidth` 证明不了"没被裁"**：SPA 根节点常带 `overflow-hidden`，超宽元素是被**静默剪掉**而不是产生滚动条，于是"无横向溢出"的断言会假绿。要逐个元素量 `getBoundingClientRect().right > clientWidth`，并区分"处在 `overflow-x:auto/scroll` 容器里"（可滚到 = 可达，不算缺陷）与"在 overflow-hidden 里"（真丢失）。
- 断言的测量目标写歪比不测更糟：一次 selector 停留在旧类名（`.text-lg` 已改 `.text-xl`）表现为"该控件=无元素"，看着像通过其实没量。凡是"缺席/无元素"都要当成探针故障去查，不是当成通过。
- **需要人在可见窗口里操作（扫码、发消息、撤回、翻页）时，别用连接器那个浏览器**：它是独立上下文，与项目自己的 Chrome profile 不共享 cookie，用户在那边登录对脚本毫无用处。正确做法是用项目那个 profile 起**可见** Chrome（`--user-data-dir=<profile>`），并先释放 profile 独占。。
- 长跑脚本用 `node x.js > log 2>&1` 或 `python -u`，别 `| tail`——管道会缓冲到你什么都看不到（与 [[reference-powershell-through-bash-and-recyclebin]] 同一族坑）。

## 2026-11-04 又踩一次同一条：按像素"数元素"会造出假故障

上面第 29 行那条 `--window-size` 陷阱我又中招并**据此报了错结论**：uni-app 的 tabBar 明明有 3 个 tab，
我用 `--window-size=390,844` 截图后**目视 + 像素列簇都只数出 2 个**，差点交付"第三个 tab 没渲染"。
实际 CSS 视口是 **496×751**，第三个条目 `x=331..496` 被切在 390 px 画面之外。

- **数元素只能用 DOM + `getBoundingClientRect`**：`document.querySelectorAll('.uni-tabbar__item').length`
  + 每项 `x/width` + `img.complete && naturalWidth>0` + `getComputedStyle` 的色值，才是可交付判据。
- **像素列簇连"计数"都做不了**：整条底栏有背景/边框时，非白列会连成一片（实测 `runs=[(0,389)]`），
  分不出几个图标；别拿它当"数个数"的手段。
- 要真图就用 CDP 的 **`Page.captureScreenshot`**（配合 `--window-size=496,844` 这类合法窗口尺寸），
  别用 CLI 的 `--screenshot`（那条路会裁图）。
- `msedge --dump-dom` 能拿到渲染后 DOM（本次靠它先确认 3 个 item），但**进程会 segfault**——
  文件仍然写出来了，所以别把 segfault 读成"取证失败"，先看产物。
- 结论层面：**"我截图里看不到" ≠ "它没渲染"**，这是 [[feedback-no-unverified-cause-claims]] 的又一实例。

## 2026-11-07 Playwright + `vite preview` 的两个假故障

- **`vite preview` 默认只绑 `localhost` 的 IPv6（::1）**：`curl 127.0.0.1:4179` 回 000，Playwright 的
  `webServer.url=http://127.0.0.1:4179` 就等满 60s 超时。要么命令加 `--host 127.0.0.1`，要么 url 写
  `http://localhost:4179`。
- **同名按钮会点错**：顶部范围胶囊和会话筛选都有"全部"，`getByRole('button',{name:'全部'})` 在 web-first
  断言里会 strict-mode 冲突或点到另一个。用 `.seg`、`within(grid)` 之类限定区域再取。
- **Vite 6 + Vitest 2 的 `defineConfig` 类型不兼容**（vitest 自带旧 Vite 类型），换 vitest 3，或从
  `vitest/config` 导入 `defineConfig`。
- 无头/桌面验收都要**每次全新的浏览器 profile**：`file://` 下 WebView2 会缓存旧 bundle，改完前端仍看到旧界面时先换
  `storage_path`，别急着怀疑 CSS。

