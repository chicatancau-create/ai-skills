---
name: headless-cdp-visual-acceptance
description: "自起 headless Chromium(Edge/Chrome) 做前端与 MV3 扩展的端到端取证，不装 Playwright，分两条回路：零 CDP 的 msedge --headless 命令行(实拍 + 注入探针取数，适合单文件页面交付后自检)与 spawn+ws/CDP 全量管线(交互、真实视口、扩展、网络 mock)。当需要量布局溢出/几何/计算样式/对比度/键盘焦点顺序/截图、证明「页面真的渲染成了什么样」、复核自己上一轮「看着没问题」、判定「到底修好了没」，或 mock 不可达的第三方接口(在网络层用 Fetch.fulfillRequest 拦 Service Worker 的 fetch)时使用。也在这些症状下使用：实拍命令没报错但目录里零产物、相对路径截图报「拒绝访问」却返回退出码 0、--dump-dom 读不到异步或动效后的状态、对 dump grep 数到的是探针自己的源码、入场动画在 JS 报错后永久不可见、截图宽度与探针量到的 px 对不上、连上了错的浏览器/把用户标签页导航走了、脚本跑完 Node 不退出、稳定版 Chrome 加载不了扩展、窄视口截图出现假性溢出、系统深色主题污染截图。不用于单测与组件测试(用 fs-testing)、需要操作用户已登录的可见浏览器或复用其登录态(用 browser-use MCP)、配色与样式规范本身(qoder-toolkit / web-taste)、某个项目专属的取证批次登记(visual-tool-add-section / codeweave-visual-rebuild-rerun)。"
---

# Headless CDP 视觉与行为取证

## Overview

用 `spawn` 起一个属于自己的 headless Chromium，通过 CDP(纯 `ws`，约 30 行手写客户端)驱动它，把「界面看起来对不对」逼成一组可复跑的数字断言 + 截图证据。适用面：静态页、本地工装页、MV3 扩展的内容脚本/后台。不引 Playwright/Puppeteer，因此不装任何浏览器二进制。

两条前提决定成败：**只连自己启的浏览器**，**只交付会失败断言**。

## 两条回路怎么选

- **零 CDP 命令行回路**(文末那节)：刚交付一个单文件 HTML/静态页，只要一张真图 + 几个数字(溢出、校验态、aria 切换、入场动画是否让内容永久不可见)。三次 `msedge --headless` 调用 + 一段注入脚本，不写 CDP 客户端、不起服务、不开调试端口。
- **CDP 管线**(下面第 0–8 步)：要点击与多步流程、真实窄视口、hover/焦点环、对比度 WCAG、`@keyframes` 中间帧、MV3 扩展、网络层 mock。

线划在「要不要驱动浏览器」上：不需要驱动就用命令行，需要驱动就别省那 30 行 CDP。

## 何时用 / 何时不用

- 用：要量 `scrollWidth - clientWidth`、`getBoundingClientRect`、计算样式与对比度、Tab 焦点顺序、四态(错误/载入/成功/拒绝)、真实渲染截图；要断言扩展后台的请求顺序；第三方 API 在本机不可达但不能因此跳过测试。
- 不用：jsdom/Vitest 就能覆盖的逻辑、需要用户登录态或真实账号的页面(走 browser-use MCP)、CI 里长期维护的 E2E 套件(那是 Playwright 的活，见 fs-testing)、配色与排版怎么写(走 qoder-toolkit / web-taste)。

## 五条硬规则

1. **端口只从自己的 profile 读。** 绝不探固定调试端口。本机 `127.0.0.1:9333` 是 Qoder 内置隐藏 Chrome，持有用户的 Code Canvas 等标签页；探到它就等于在导航用户的页面(2026-09-20 踩过)。启动一律 `--remote-debugging-port=0`，真实端口从 `<临时 user-data-dir>/DevToolsActivePort` 第一行读。
2. **一切端口交给系统分配。** 静态服务用 `srv.listen(0, '127.0.0.1')` 再取 `srv.address().port`，别硬编码 8799 这类数字——撞端口时的失败信息会把你引向错方向。
3. **不可达的外部接口在网络层 mock，不要 skip。** attach 到 Service Worker 的 session，`Fetch.enable` + `Fetch.fulfillRequest`(响应体 base64)。跳过测试等于没有断言。
4. **断言必须被证明会失败。** 全绿不等于有牙齿：把修复临时回滚跑一次，确认相关断言变红，再恢复。见「证明断言有牙齿」。
5. **收尾必须杀进程树 + 显式退出。** 持有 WebSocket 与 HTTP server 的 Node 永远不会自己退出。

## 流程

### 0. 先找现成 harness，别从零写

本机已有两份可抄的实现：`E:\插件（ai）\test-lab\browser-test.js`(MV3 扩展 + 网络层 mock + 滚动位置)、`E:\插件（ai）\login\verify.js`(纯页面 + 对比度/主题)。按当前项目改常量，比新写一份省事且少踩坑。`ws` 依赖可以指到已装好的 `node_modules/ws`。

### 1. 本地静态服务

```js
const srv = http.createServer(handler);
await new Promise(r => srv.listen(0, '127.0.0.1', r));
const BASE = `http://127.0.0.1:${srv.address().port}`;
```

静态文件路径要 `path.normalize` 后校验仍在 root 目录内，别把工装服务开成任意文件读。被测页面如果需要两份互不干扰的文本(后台常按文本缓存，会污染请求顺序断言)，就生成两份措辞不同的长页。

### 2. 启浏览器：Edge → Chrome

```js
const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'verify-profile-'));
const child = spawn(bin, [
  '--headless=new', '--remote-debugging-port=0', `--user-data-dir=${profile}`,
  '--no-first-run', '--no-default-browser-check', '--window-size=1280,900'
], { stdio: 'ignore' });
```

要测扩展再加 `--disable-extensions-except=<abs-dir>` 与 `--load-extension=<abs-dir>`，并加 `--disable-backgrounding-occluded-windows --disable-renderer-backgrounding`(否则后台标签被节流，断言会超时)。候选顺序固定 **Edge → Chrome**：稳定版 Chrome 137+(本机 153)直接忽略 `--load-extension`，加 `--enable-unsafe-extension-debugging` 也没用，MV3 SW target 永远不出现；Edge 153 能 headless 加载未打包扩展。

### 3. 只认自己的端口

```js
const ownPort = async () => {
  for (let i = 0; i < 60; i++) {
    if (child.exitCode !== null) throw new Error('浏览器进程已退出 code=' + child.exitCode);
    try {
      const p = Number(fs.readFileSync(path.join(profile, 'DevToolsActivePort'), 'utf8').split('\n')[0].trim());
      if (p > 0) return p;
    } catch (e) { /* 文件还没写出来 */ }
    await sleep(500);
  }
  throw new Error('未能在自己的 profile 里读到 DevToolsActivePort');
};
const version = await getJSON(`http://127.0.0.1:${await ownPort()}/json/version`);
const cdp = new CDP(version.webSocketDebuggerUrl);
```

先检查 `child.exitCode`：启动失败的浏览器会留下一个永远不出现的端口文件，不检查就只会看到 30 秒超时。

### 4. 最小 CDP 客户端

```js
class CDP {
  constructor(url) { this.url = url; this.id = 0; this.pending = new Map(); this.handlers = []; }
  connect() { return new Promise((res, rej) => {
    this.ws = new WebSocket(this.url, { perMessageDeflate: false });
    this.ws.on('open', res); this.ws.on('error', rej);
    this.ws.on('message', raw => {
      const m = JSON.parse(raw.toString());
      if (m.id && this.pending.has(m.id)) {
        const { resolve, reject } = this.pending.get(m.id); this.pending.delete(m.id);
        m.error ? reject(new Error(m.error.message)) : resolve(m.result);
      } else if (m.method) for (const h of this.handlers)
        if (h.method === m.method && (!h.sessionId || h.sessionId === m.sessionId)) h.fn(m.params);
    });
  }); }
  send(method, params = {}, sessionId) { const id = ++this.id; const p = { id, method, params };
    if (sessionId) p.sessionId = sessionId;
    return new Promise((res, rej) => { this.pending.set(id, { resolve: res, reject: rej }); this.ws.send(JSON.stringify(p)); }); }
  on(method, fn, sessionId) { this.handlers.push({ method, fn, sessionId }); }
}
```

挂页面：`Target.createTarget`(或从 `/json/list` 找 `type==='page'`) → `Target.attachToTarget {flatten:true}` 拿 `sessionId` → `Page.enable` + `Runtime.enable`。之后所有 `Runtime.evaluate` 都带这个 sessionId，并固定 `returnByValue: true, awaitPromise: true`；`r.exceptionDetails` 存在就抛，否则页面里的异常会被静默吞成 `undefined`，你会误判成「选择器没匹配到」。

注册 `cdp.on('Runtime.exceptionThrown', ...)`：页内异步脚本的错误不会进 evaluate 的返回值。

### 5. 页面取证断言

用 `Emulation.setDeviceMetricsOverride` 换视口(比 `--window-size` 可靠)，用 `Page.captureScreenshot {captureBeyondViewport:true}` 出整页图。典型测量：

- 溢出：`scrollWidth - clientWidth <= 0`
- 对比度：读 `getComputedStyle` 的前景色与有效背景色，本地按 WCAG 公式算，两套主题各量一遍
- 焦点顺序：真发 `Input.dispatchKeyEvent` 或直接读 `document.activeElement` 链，并量 `outlineStyle/outlineWidth`
- 状态：`requestSubmit()` 触发，再轮询 DOM 计数

**把断言改成量真实控件。** 曾有一条「焦点环可见」量到 `none 3px` 却靠别的元素蒙过——测量目标写歪了比不测更糟。

### 6. MV3 扩展 + 网络层 mock

```js
await cdp.send('Page.navigate', { url: `${BASE}/` }, PG);   // 先导航一次唤醒后台 SW
let swTarget;
for (let i = 0; i < 40; i++) {
  const targets = await getJSON(`http://127.0.0.1:${CDP_PORT}/json/list`);
  swTarget = targets.find(t => t.type === 'service_worker' && /\/background\.js$/.test(t.url));
  if (swTarget) break;
  await sleep(500);
}
if (!swTarget) throw new Error('NO_SW');                    // 上层据此换下一个候选浏览器
const SW = (await cdp.send('Target.attachToTarget', { targetId: swTarget.id, flatten: true })).sessionId;
const requestLog = [];
cdp.on('Fetch.requestPaused', async p => {
  requestLog.push(new URL(p.request.url).searchParams.getAll('q'));
  await cdp.send('Fetch.fulfillRequest', { requestId: p.requestId, responseCode: 200,
    responseHeaders: [{ name: 'Content-Type', value: 'application/json' }], body: mockBody(p.request.url)
  }, SW);
}, SW);
await cdp.send('Fetch.enable', { patterns: [{ urlPattern: '*translate.googleapis.com/*' }] }, SW);
await cdp.send('Page.reload', {}, PG);
```

要点：拦截挂在 **SW session** 上，不是页面 session；`Fetch.enable` 要在被拦请求发出前(所以先导航唤醒、装好拦截、再 reload)。计数 `mocked` 并在结尾打印——**为 0 说明走了真实网络**，测试绿了也是假绿。

### 7. 证明断言有牙齿

每条关键断言过一遍：临时回滚对应修复 → 跑 → 确认它变红 → 恢复 → 再跑确认全绿。回滚改动单独 `git stash` 或用 sed 临时反转，跑完 `git diff` 确认干净。没做这一步的断言，在报告里标「未证明会失败」。

**结论单位要和实现单位对齐。** 断言「首批请求不含远端段落」时，先确认后台是不是把内容批次再按固定字符数(实测 1800 字符)拆成多个网络包——按包下结论会连红两次，而代码其实没问题。这类粒度写进注释，别只留在对话里。

### 8. 收尾清理

```js
} finally {
  try { if (cdp && cdp.ws) cdp.ws.close(); } catch (e) {}
  try { execFileSync('taskkill', ['/PID', String(child.pid), '/T', '/F'], { stdio: 'ignore' }); } catch (e) {}
  try { fs.rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 300 }); } catch (e) {}
}
console.log(failed ? `\n${failed} 项失败` : '\nVERIFIED');
process.exit(failed ? 1 : 0);   // ws / server 会让事件循环挂住, 必须显式退出
```

多浏览器候选轮转时，每个候选在自己的 finally 里清，别留到最外层。残留排查(本机踩过一次 22 进程 / 796MB)：只按**命令行里含自己 profile 前缀**筛目标，逐条判僵尸——父链已 GONE + CDP 端口无人连 + 命令行是 `--headless=new --user-data-dir=...Temp\...` 三条都满足才杀。**别用一条 PowerShell 查询的自匹配结果当作残留证据**(它会把自己列进去)。

不要顺手杀：`127.0.0.1:4173`、`127.0.0.1:5173`，以及父进程是 `Qoder.exe` 的 node/bash。杀完后 Alt+Tab 里的全白卡片是 explorer 缓存幽灵，不代表进程还在。

## 症状对照表

| 症状 | 根因 | 处置 |
|---|---|---|
| 用户说「我的页面被你跳走了」 | 探了固定端口, 连上 Qoder 内置隐藏 Chrome(9333) | 端口只从自有 profile 的 `DevToolsActivePort` 读 |
| `node xxx.js` 不返回, 被超时杀掉 | ws + http server 挂着事件循环 | 清理后显式 `process.exit()` |
| Chrome 下 SW target 永不出现 | 稳定版 Chrome 137+ 忽略 `--load-extension` | Edge 优先；以 SW target 出现判加载成功, 否则换候选 |
| 390px 截图右侧元素被切 | `--window-size=390,844` 实际给 ~496px 桌面渲染再裁切 | 用 `DeviceMetricsOverride`；或含 390px iframe 的工装页, 并回读 `innerWidth` 自证 |
| 截图与用户看到的色调不一致 | 本机系统主题为深色, 浏览器默认报 dark | `Emulation.setEmulatedMedia` 钉成 light |
| 刚导航就报读不到 `documentElement` | 提交瞬间文档尚未替换 | 取不到返回哨兵值继续轮询, 别当成断言失败 |
| 断言两次都红, 代码看着没问题 | 按网络包边界判断了内容批次 | 先确认拆包粒度(实测 1800 字符/包), 再定断言粒度 |
| evaluate 返回 undefined 被当成 0 | 页面抛异常被吞 | 检查 `exceptionDetails` 并注册 `Runtime.exceptionThrown` |

## 报告口径

交付时逐项写明：

- 浏览器与版本(打印 `/json/version` 的 `Browser`)、被测 URL、断言总数与通过数、截图落盘目录。
- mock 拦截请求数；**明确列出被 mock 掉的外部依赖**，不许把 mock 跑绿说成端到端已验证。
- 做过回滚验证的断言才算「有牙齿」；没做的标注出来。
- 临时 profile 与进程已清理；未清理的说清残留位置。
- 结论只写量到的。本机特定事实带日期(如 9333 归属、Chrome 153 忽略 `--load-extension` 均记于 2026-09-20)，环境会变，引用旧事实前先重新确认。

## 零 CDP 快速回路（实拍 + 注入探针取数）

> 本节自 `verify-page-in-headless-edge` 合并而来(合并与删除发生于 2026-09-25，节内实测数据记于 2026-09-24)。全程只有 `msedge --headless` 的三次调用 + 一段注入脚本：不写 CDP 客户端、不起静态服务、不开调试端口，因此不可能连到用户的浏览器。

### 本回路的五条硬规则(实测于 Edge 153 / 2026-09-24)

1. **输出路径必须绝对，判据是文件而不是退出码。** 相对路径的实测后果：

   ```
   [ERROR:components\headless\command_handler\headless_command_handler.cc:266] Failed to write file desk.png: 拒绝访问。 (0x5)
   ```

   命令**返回码仍是 0**，`ls *.png` 只会告诉你没有这个文件。`--screenshot`、`--user-data-dir`、以及 `--dump-dom` 的重定向目标全部写绝对路径；判据永远是 `os.path.exists(p) and os.path.getsize(p) > 0`。
   配套坑：Git Bash 的 `/tmp/xxx` 与 Windows 原生 `python` 不是一套路径，会出现 `FileNotFoundError: '/tmp/kw_dump.html'`(bash 刚写完它)。运行目录用 `C:\Users\<user>\AppData\Local\Temp\<run>\`，一次一个新目录，别复用。

2. **`--dump-dom` 在 load 那一刻就序列化。** 不带 `--virtual-time-budget` 时探针实测在 `T=13ms` 出结果——异步回调、`setTimeout` 兜底、动效结束后的状态**全都读不到**；加了 budget 才读到 `T=2014ms`。所以取数必须放在延时之后，并且**每个读数自报 `T=` 和一个 rAF 帧计数**。探针节点抽出来是空串 = 你的读取时刻还没到，不是「页面没问题」。

3. **读数只走带唯一 id 的 PROBE 节点，按 id 正则取回。** 直接对 dump grep 关键字是错的：实测一份 dump 里含 `aria-invalid` 的有 7 行，**第一行是探针自己写的 `querySelectorAll('[aria-invalid="true"]')` 源码**，与 DOM 里真实的 `aria-invalid="true"` 属性长得一样。固定做法：页面里放 `<div id="PROBE" hidden></div>`，探针把 `key=value | key=value` 写进它的 `textContent`，取回时按 id 正则切出来再 `html.unescape`(dump 里 `->` 会变成 `-&gt;`)。

4. **入场动画必须 fail-open，且回显选择器的特异性要够。** CSS **默认必须可见**，只有加上 `.js` 网关后才隐藏：`.reveal{opacity:1}` + `.js .reveal{opacity:0}` + 一条能把显示态赢回来的规则；兜底定时器要注册在**任何可能抛错的代码之前**。
   第三条**不能写成裸单类**。`.revealed{opacity:1}` / `.force{opacity:1}` 的特异性只有 (0,1,0)，干不过 `.js .reveal` 的 (0,2,0) —— 照这么写等于网关没生效，一个完全正常的页面会被判成「永久不可见」。实测(同一份 fail-open 页、已中和 transition/animation)：

   | 回显选择器写法 | 类加在哪 | `INVISIBLE` |
   |---|---|---|
   | `.force{opacity:1}` 裸单类 | `html` | **3/3** 假报警 |
   | `.force .reveal{opacity:1}` 后代 | `html` | 0/3 正确 |
   | `.reveal.revealed{opacity:1}` 复合 | 每个 `.reveal` 元素 | 0/3 正确 |

   即：回显选择器的特异性必须 **≥** `.js .reveal`，且加类的位置要和选择器对得上。另外 `web-taste/references/motion-recipes.md` 第 2 节 Entrance Reveal 是裸写法 `.reveal{opacity:0;transform:translateY(20px)}`，无 no-JS 守卫、无兜底 —— 绑定该设计系统时必须补上 fail-open。

5. **实拍与取数共用同一组 flag，并钉死 `--force-device-scale-factor=1`。** 截图像素宽 = window-size × devicePixelRatio。实测：传 `=2` 会把 500×800 的窗口拍成 **1000×1600** —— 这个参数是真生效的，别假设命令行会忽略它。本机默认 DPR=1，所以**不传与传 `=1` 的截图逐字节相同**(两张 500×800 PNG md5 均为 `ea29f4eb…`)；这条 no-op 只在本机当前缩放下成立。
   但 `=1` **并非零副作用**：实测 window-size=500 下不传时 `innerWidth=496`，传 `=1` 后变 **492**。所以 `--screenshot` 与 `--dump-dom` 必须带**同一组** flag，否则量到的溢出宽度对应的不是截图里那一屏；结论里要写清带了哪组参数。影响分两类：**显隐类判据不受影响**(同一对照组两种参数逐项相同)，**凡是从 `clientWidth` 减出来的像素量会整体平移**(见下面 `OVER` 基线)。

### 命令

先把被测页面**复制**到运行目录，只在副本 `</body>` 前追加探针块——交付文件本身保持干净。

```bash
EDGE="/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"   # 路径有空格，整条加引号
RUN="C:\\Users\\Admin\\AppData\\Local\\Temp\\page-verify-1"
"$EDGE" --headless --disable-gpu --user-data-dir="$RUN\\ud" \
  --window-size=1280,900 --force-device-scale-factor=1 --hide-scrollbars \
  --screenshot="$RUN\\desktop.png" "file:///$RUN/page.html"
test -s "$RUN/desktop.png" && echo OK || echo "零产物 = 失败(别看退出码)"

"$EDGE" --headless --disable-gpu --user-data-dir="$RUN\\ud" \
  --window-size=1280,900 --force-device-scale-factor=1 --virtual-time-budget=5000 \
  --dump-dom "file:///$RUN/page.probe.html" > "$RUN/dump.html"
```

```python
import re, html
d = open(r"C:\Users\Admin\AppData\Local\Temp\page-verify-1\dump.html", encoding="utf-8", errors="replace").read()
m = re.search(r'<div id="PROBE"[^>]*>([\s\S]*?)</div>', d)
print(html.unescape(m.group(1)) if m else "EMPTY -> 读取时刻没到, 加大 --virtual-time-budget")
```

### 探针块(实测可跑)

```html
<div id="PROBE" hidden></div>
<script>
window.__frames = 0; (function f(){ window.__frames++; requestAnimationFrame(f); })();
setTimeout(function (){
  var L = [], de = document.documentElement;
  L.push('T=' + Math.round(performance.now()) + ' FRAME=' + window.__frames);
  L.push('VW=' + innerWidth + ' CLIENTW=' + de.clientWidth + ' SCROLLW=' + de.scrollWidth + ' OVER=' + (de.scrollWidth - de.clientWidth));
  var wide = [], all = document.querySelectorAll('*');
  for (var i = 0; i < all.length; i++){ var r = all[i].getBoundingClientRect();
    if (r.right > de.clientWidth + 1) wide.push(all[i].tagName + '.' + all[i].className + '@' + Math.round(r.right)); }
  L.push('WIDE=' + wide.slice(0, 3).join(','));
  var f = document.querySelector('form');
  if (f) f.dispatchEvent(new SubmitEvent('submit', {cancelable: true, bubbles: true}));
  L.push('INVALID=' + document.querySelectorAll('[aria-invalid="true"]').length + ' ERRON=' + document.querySelectorAll('.err.on').length);
  var t = document.querySelector('button[type="button"]');
  if (t){ t.click(); L.push('PRESSED=' + t.getAttribute('aria-pressed') + ' TYPE=' + (document.getElementById('pw') || {}).type); }
  var els = document.querySelectorAll('.reveal'), inv = 0;
  for (var j = 0; j < els.length; j++){ if (parseFloat(getComputedStyle(els[j]).opacity) < 0.05) inv++; }
  L.push('INVISIBLE=' + inv + '/' + els.length + ' JSCLASS=' + (document.documentElement.className || '-'));
  document.getElementById('PROBE').textContent = L.join(' | ');
}, 2000);
</script>
```

校验态必须**程序化触发**才读得到：空提交用 `dispatchEvent(new SubmitEvent(...))`(或 `form.requestSubmit()`)，别指望 dump 里天然有 `aria-invalid`。

### 对照组：这条回路的断言同样要证明会失败

同一套探针，四种页面(均为 `--virtual-time-budget=5000` 下 `T≈2013ms` 取的数)：

| 页面 | INVISIBLE | 判读 |
|---|---|---|
| 裸 `opacity:0` + JS 先抛错 | **3/3** | 真缺陷：内容永久不可见 |
| fail-open 网关 + JS 先抛错 | 0/3 | 正确：没加 `.js` 就一直可见 |
| fail-open 网关 + 正常 | 0/3 | 健康对照 |
| fail-open + 正常 + `transition:opacity 700ms` | **3/3** | **测量假象** |

最后一行是这张表存在的理由：虚线时间预算下 rAF 只推进 **1 帧**(`FRAME=1`)，基于 `transition` 的显隐永远停在起始值 `opacity:0` —— 一个完全正确的页面会被判成「全隐藏」。**测显隐前先把动效中和**，在副本 `</head>` 前追加：

```html
<style>*,*::before,*::after{transition:none!important;animation:none!important}</style>
```

加上它之后四行结果变成 3/3、0/3、0/3、**0/3** —— 真缺陷与测量假象这才分得开。要看动效本身跑到哪一帧，就别用这条回路，走上面的 CDP 管线。

溢出探针同理要有正向对照：塞一个 `width:600px` 的元素在 500 宽下必须报红，实测 `OVER=104 WIDE=DIV.x@600`；正常页报 `OVER=0 WIDE=`。探针两次都不红 = 探针是死的。`OVER` 是从 `clientWidth` 减出来的，所以它跟着硬规则 5 那组 flag 漂移：同一个 600px 元素在 window-size=500 下，不传 `--force-device-scale-factor` 量到 `CW=496 OVER=104`，传 `=1` 量到 `CW=492 OVER=108`(`WIDE` 两种参数一致)。**判溢出只看 `OVER>0` 与 `WIDE` 有没有内容，不要拿 104 当基线比对**。

### 本回路特有的静默失败

| 症状 | 根因 | 处置 |
|---|---|---|
| 命令没报错，目录里没有 png | 相对路径被 Edge 自己解析，`拒绝访问 (0x5)`，**rc 仍为 0** | 绝对路径 + `test -s` 判产物 |
| python 说 `/tmp/xxx` 不存在 | bash 与 Windows 原生 python 不是一套路径 | 全用 `C:\...\AppData\Local\Temp\` |
| PROBE 抽出来是空串 | 读取时刻还没到(load 即序列化) | 探针延时 + 加大 `--virtual-time-budget` |
| grep 计数比预期大 | 命中的是注入脚本源码 | 只按 `id="PROBE"` 正则取回 |
| 读数是 `-&gt;` 这种 | dump 里是 HTML 实体 | `html.unescape` |
| 明明修好了仍报 3/3 不可见 | 虚线下 transition 时钟冻住 | 测显隐前中和 transition/animation |
| 校验态永远全绿 | 没人触发提交 | 探针里 `dispatchEvent(SubmitEvent)` |
| 截图看着对但数字不对(或反之) | 只信了一样 | 截图 + 断言双轨，以数字为准 |
| 截图宽度 ≠ `--window-size`，或与探针量到的 px 对不上 | 截图像素 = window-size × devicePixelRatio；`=1` 本身也会挪动 `innerWidth` | 实拍与取数共用同一组 flag，结论里注明带了哪组 |

### 本回路测不到的(交给上面的 CDP 管线)

- **真窄视口**：`--window-size` 有下限且被裁，实测 `390→innerWidth 496`、`500→496`、`768→742`、`1440→1414`。任何「390px 手机态」结论都不能由这条回路给出——用 `Emulation.setDeviceMetricsOverride`。
- **`screen.width` / `screen.availWidth` 在 headless 下恒为 800**(2026-09-24 实测，与 `--window-size` 取 390/500/1440 都无关)。它既不是视口宽也不是设备宽，别拿它做设备判定或响应式断点依据——只有 `innerWidth` / `documentElement.clientWidth` 是真的。
- 上面那组 `innerWidth` 还随 flag 漂移且**差值不等比**：`500` 宽下不传 496、传 `=1` 是 492(差 4)，而 `1440` 宽下两种参数都是 1414(差 0)。别记「固定少 4px」，只记「两组参数各量一遍，引用时说明带的哪组」。
- 折叠以下内容(单次 dump 不滚动)、hover/focus 态、`@keyframes` 中间帧、对比度、扩展与后端联动。

运行目录只放在 `Temp\page-verify-*` 下，交付结论给出后即删；截图要留就明确写它是给人看的、不是判据。**别把页面副本和证据留在被测项目的源码目录里**——技能扫描根里的杂物会被登记成幽灵条目。`--force-device-scale-factor` 那三条实测结论**换机器或改系统缩放后要重测**。
