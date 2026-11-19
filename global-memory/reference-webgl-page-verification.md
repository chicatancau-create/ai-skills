---
name: reference-webgl-page-verification
description: How to actually verify a WebGL/Three.js page on this box — the browser-use tab blocks rAF, headless Edge needs --enable-unsafe-swiftshader, PNG byte size is not a black-frame test, and Chromium import maps reject fallback arrays
metadata:
  type: reference
---

验证本机写的 WebGL / 动画页面（2026-10-19 做单文件 three.js 沙盘时实测）：

- **连接器那个 tab 是 hidden，`requestAnimationFrame` 直接挂起**：页面初始化代码会跑完，但 `setAnimationLoop`/rAF 一帧都不出，看起来像"卡死在 loading"。判据：`document.visibilityState==='hidden'` + 一个 2.5s 超时的 rAF 探针。结构类断言（DOM、evaluate、snapshot）在那个 tab 仍然可用，像素不行。
- **要像素就自起 headless Edge**：`--headless=new --remote-debugging-port=0 --user-data-dir=<tmp> --enable-unsafe-swiftshader`，从 `<profile>/DevToolsActivePort` 读端口，Node 24 全局 `WebSocket` 裸写 CDP 即可（不需要 ws 包）。`Emulation.setDeviceMetricsOverride` 控制视口。本机有独显，headless 会走真 GPU（我的重场景 3 遍全场景渲染仍能跑到几百 fps），别默认它是软件光栅。收尾 `taskkill /PID <pid> /T /F` + 删 profile 目录。
- **PNG 文件大小不能当"是不是黑屏"的判据**：截图里含 DOM 覆盖层（面板/文字），纯黑画面也能有 380KB。要判黑就在页内 `gl.readPixels` 求均值（headless 可见页可用；hidden tab 里恒为 0，会得到假结论），或者直接看图。
- **Chromium 不支持 importmap 的 fallback 数组**：`"three": ["urlA","urlB"]` 会让整条规则失效，报 `Failed to resolve module specifier`。字符串映射正常。
- **模块 URL 失败会被负缓存**：同一个 specifier 重试必然再失败。兜底只能换 URL；但 addon 内部的 `import 'three'` 走 importmap，所以只有 addon 可以换镜像，**核心库换源会得到两份 three 实例**。核心失败的正当兜底是"自动重载一次"（sessionStorage 打标记，成功后清掉）。
- **同步 XHR 探测镜像在本机是反效果**：unpkg / npmmirror 的 DNS 直接超时，同步阻塞十几秒；HEAD 探测在浏览器里也可能全灭（curl 却 200）。要么别探测，要么异步。
- **GLSL 反向 smoothstep（edge0 > edge1）是 undefined**：ANGLE 上会吐 NaN，单个像素没事，但进 UnrealBloomPass 的模糊链就整帧变黑——表现为"关掉 bloom 就有画面"。写降值一律用 `1.0 - smoothstep(小, 大, x)`。同类雷：`1.0/length(...)` 与 `sin(x)/k` 的 0/0。

相关：[[reference-inapp-browser-verification]]、[[feedback-screenshot-pixpin]]、[[reference-local-dns-and-link-verdicts]]
