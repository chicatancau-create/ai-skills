---
name: reference-harmony-hvigor-cli
description: 本机用 hvigor 命令行编译/取证鸿蒙 ArkTS 工程的方法，以及「编译过了」能证到哪一层（预览器缓存、增量幽灵产物、已废弃的 router 全局 API）。
metadata:
  type: reference
---

鸿蒙工程（DevEco 工程）改完 ArkTS 后可以在本机命令行真编一次，不用开 IDE：

```
cd <工程根>
DEVECO_SDK_HOME="D:/DevEco Studio/sdk" \
  "D:/DevEco Studio/tools/node/node.exe" \
  "D:/DevEco Studio/tools/hvigor/bin/hvigorw.js" \
  --mode module -p module=entry@default -p product=default assembleHap --no-daemon
```

**Why:** 工程的 `local.properties` 里根本没有 `sdk.dir`（IDE 自己注入），所以不能照常规 Go/C++ 那样猜工具链位置；DevEco 装在 `D:\DevEco Studio`（工作区之外，`bin/jbr/sdk/tools` 都在那），`tools/node` 是它自带的 node。一次约 7 s，产物 `entry/build/default/outputs/default/entry-default-unsigned.hap`。没配 `signingConfigs` 会打 `Will skip sign 'hos_hap'` 警告，属正常。

**How to apply:**
- 报错原文比 IDE 面板全：`COMPILE_RESULT:FAIL {ERROR:n}` 会逐条给 `At File: ...:行:列`。用 `grep -viE "^> hvigor (Finished|UP-TO-DATE)"` 滤掉噪声。
- 「BUILD SUCCESSFUL」只证**编译与打包**，不证渲染和点击生效。要在真机/模拟器才算；没跑到就照 [[feedback-skill-routing-table]] 写「未证实」。
- 路由/资源类问题取证到产物层：`build/default/intermediates/res/default/resources/base/profile/main_pages.json` 是编译期路由快照；`build/default/cache/default/default@CompileArkTS/esmodule/debug/**/<Page>.ts` 里应有 `registerNamedRoute(... pagePath: "...")`。
- **增量缓存会留幽灵**：页面文件搬家/改名后，旧路径的 `<Page>.ts`/`.protoBin` 仍躺在 cache 目录里。别拿 `grep` 命中当结论——用同目录 `filesInfo.txt` 计数（0 才算没进本次构建），再 `zipfile` 读 hap 内的 `main_pages.json` 才是打包真相。
- **想要「非增量」证据**：`hvigorw.js clean --no-daemon` + `rm -rf entry/build` 再 assembleHap，看末行 `33 tasks in total: 32 executed, 1 up-to-date`
  ——executed 接近满数才叫从零编过（只跑 15 executed 说明一半是缓存复用，别拿去当「全量验证」）。
- **产物层核对三件套**（`unzip` 出 hap 后）：路由 `resources/base/profile/main_pages.json`；权限在 **`module.json` 的 `d['module']['requestPermissions']`**
  （顶层 `app.modules` 里找不到，我误判过一次「权限没进去」）；代码是否真被编进来看 `ets/modules.abc` 里 `grep -c` 关键类名/`uploadFile` 等符号（命中=没被摇掉）。
- 预览器报 `Could not resolve entry module "entry/src/main/ets/<旧路径>.ets"` 多半不是代码错：`entry/.preview/config/buildConfig.json` 里存着 `previewPagePath` 和一份路由快照，文件搬家后不会自动失效。先看它的 mtime 与快照内容，再让用户点「预览已过期，请重新加载页面」（`.preview` 是可再生缓存，别擅自删）。
- API 选型：本机 SDK 为 `26.0.0`，`@ohos.router` 全局模块自 API 18 起标 `@deprecated`，页面跳转/提示用 `this.getUIContext().getRouter().pushUrl({url})`、`.back()`、`getPromptAction().showToast({message})`（均自 API 10 可用）。判断依据直接查 `D:\DevEco Studio\sdk\default\openharmony\ets\api\@ohos.arkui.UIContext.d.ts` 与 `@ohos.router.d.ts` 里的 `@deprecated/@useinstead/@since`，比搜网页快且不会错版本。组件属性签名同理查 `ets/component/*.d.ts`（`navigation.d.ts` 里同时有 `navDestination(builder: (name: string, param: unknown) => void)` 和 `pushPath(info: NavPathStack 的 NavPathInfo)`）。

- DevEco `tools/` 里**没有独立 codelinter CLI**（只有 `UxTestService/arktsdoc/dumpParser/emulator/hvigor/llvm/node/ohpm/profiler`）⇒ 工程自带的 `code-linter.json5`
  规则集**只能在 IDE 里跑**，别承诺「命令行给你过一遍 lint」；静态自检就用自己的 grep/AST 扫（废弃 API、V1/V2 装饰器混用、未使用具名导入、路由注册与磁盘文件是否一一对应）。
- **本机离线只能验到「编译+打包」这一层，交互验收必然要用户手动（2026-11-01 三条路全实测堵死）**

- `~/.ohos` 不存在 → 从没做过 DevEco 自动签名；工程 `build-profile.json5` 的 `signingConfigs: []`，产物只有 `entry-default-unsigned.hap`，装不进任何设备。
- DevEco 自带 `tools/emulator/Emulator.exe` + `sdk/default/openharmony/toolchains/hdc.exe` 都在，但 `%LOCALAPPDATA%\Huawei\Emulator\deployed` **总共 43 KB**，只有 5 个机型的 `.ini` 桩，系统镜像没下载；`hdc list targets` 回 `[Empty]`。
- ⇒ 别承诺「我给你跑一遍验收」。给用户的是一份**点击顺序清单**（在哪个页、做什么动作、应该看到什么变化），并且明说哪几步风险最高（我这边是 `Scroll` 里套 `Swiper`+`Grid` 的高度、`Navigation` 传参）。

**「编译绿灯」之下的三类运行时陷阱（2026-11-01 全靠静态核对抓出来，构建一次都没报）**

- **响应外壳猜错**：服务端统一包是 `{code,message,data}`，但 `data` 的内部结构各接口不同 —— `/api/products` 的 `data` 是
  `{products:[], pagination:{}}`，而 `/api/products/featured` 的 `data` 是裸数组。按数组写 `payload.data` 会拿到 undefined，列表空白但编译过。
  做法：读服务端 model/controller 的 `return` 语句，别信接口清单和 Postman 集。
- **可空列**：mysql2 把 `DECIMAL` 回成 **string**、`text`/可为 NULL 的列回成 **null**，所以 `phone/avatar/images/description` 要声明成
  `string | null` 再兜底；`price` 直接当字符串显示别做算术。
- **`$rawfile(变量)` 的名字检查扫不到**：文件名藏在数据数组里（`bannerList`、`icon: '01.png'`），逐一对目录时要把**数据数组的字面量**一起算进去。
  另一半证据是 `unzip -l *.hap | grep -c resources/rawfile/` —— 素材真进了包才算。

**ArkTS 写法坑（本轮实测）**

- `AppStorageV2` 不是全局，必须 `import { AppStorageV2 } from '@kit.ArkUI'`；`@ObservedV2`/`@Trace` 才是全局免 import。
- `AppStorageV2.connect<T>(T, () => new T())` 的工厂箭头函数会撞 `10605090 arkts-no-implicit-return-types`，写成 `(): T => new T()`。
- `catch (err)` 里不要引用 `err.message` 之外的字段；`JSON.parse` 出来的对象按 `Record<string, object>` 再 `as` 目标接口，别直接 `as` 带索引的 `any`。
- 预览器/真机之外的**唯一真验证手段**：把课件服务端 `node app.js` 起来（不需要数据库），探 `404→{"code":404,"message":"路由不存在"}`、
  `400→"邮箱和密码不能为空"`、静态 `GET /public/uploads/x.jpeg→200 image/jpeg`。这一层能实证端口、响应外壳、失败文案、图片 URL 拼法；
  只有真实数据行才需要数据库。用完 `TaskStop` 后必须再探一次端口（见 [[reference-qoder-taskstop-orphan-process]]）。

**资源名拼错**：`$r('app.media.X')` 写错名字编译照样 SUCCESSFUL，预览器里只是空白图。做法：把代码里出现的名字集合与 `resources/base/media/*` 逐一对
（扩展名 svg/png/json 都要试），`$rawfile` 见上一条。

- `navDestination` 的 @Builder 参数写成 `param: unknown` 会触发 `10605008 arkts-no-any-unknown`；写 `param: object` 才编得过（d.ts 注明 unknown 可换成用户自定义类型）。
- **`@Styles` 里只能写通用属性**：塞 `.fontSize()`/`.fontColor()` 会报 `10505001 Property 'fontSize' does not exist on type 'CommonAttribute'`（一次可炸 9 条），浅灰底/描边/圆角这类可以进去，字号与文字色必须回到调用点。
- **`modules.abc` 符号计数证明不了某些写法**：`stateStyles`、`linearGradient`、`shadow`、`@Styles` 都被编译期内联，`$r('app.media.x')` 的资源名进的是 `resources.index` 而非 abc 字面量 —— abc 查不到 ≠ 没生效，只能说静态层面无证据。「有没有真的渲染出来」仍然只有预览器/真机能判。
- **`@Styles` 里只能写通用属性**：把 `.fontSize()`、`.fontColor()` 放进 @Styles 会报 `10505001 Property 'fontSize' does not exist on type 'CommonAttribute'`（一次能炸 9 条）。@Styles 只留 height/width/border/borderRadius/backgroundColor/linearGradient，字号与文字色回到调用点。
- **abc 符号计数对部分 API 无意义**：`stateStyles`/`animation`/`linearGradient`/`shadow` 在编译期被内联，`$r('app.media.x')` 的资源名进的是 `resources.index` 而不是 abc 字面量 —— 这几类在 `ets/modules.abc` 里恒为 0，「查不到」既不能证明用了、也不能证明生效；
  反过来 `DotIndicator`/`LoadingProgress`/中文文案字面量**查得到**，所以只适合用来证明「已经删干净了」。「某 API 还在不在代码里」这种结论只能靠源码 grep。
