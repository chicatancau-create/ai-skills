---
name: reference-qt-qml-build-traps
description: 安装/构建/部署/验收 Qt 6 Quick 应用的实测硬坑：中文路径废 qmlimportscanner、junction 深度改坏 ../../、QT_FORCE_STDERR_LOGGING、offscreen 豆腐块、CTest 全绿后 LastTestsFailed.log 残留、QQmlEngine::warnings 只覆盖创建期、中文 SDK 用 subst 盘符
metadata:
  type: reference
---

给 Qt 6 + Qt Quick/QML 项目**装环境、构建、部署**时的已实测坑（2026-10-05 在本机走通「配置→编译→链接→部署→启动→像素验证」全过程踩出来的）。选型与许可方面的坑见 [[reference-qt-qml-licensing-traps]]。

## 中文路径会直接废掉 QML 构建链

`qmlimportscanner`（CMake 的 `qt_add_qml_module` 会调它）拿到中文路径时收到的是**乱码**并失败（实测报 `G:/CodeWeave/搴旂绔?/native/ui-qt`，正是 UTF-8 字节被按 GBK 解读），同一次输出里还出现两种不同乱码 —— 说明 Qt 工具链各组件对路径编码处理不一致。**被扫描的是源码目录，所以构建目录放 ASCII 救不了它，源码路径本身必须纯 ASCII。** 与 [[reference-windows-batch-entry-encoding]] 的 936 代码页问题是同一类根因。

## 用 junction 绕开时，深度会静默改坏相对路径

Qt 工程常用 `${CMAKE_SOURCE_DIR}/../../content` 这类**相对**路径找资源包。把 ASCII junction 建在错误的层级，这条相对路径就指到别处（实测指到 `G:/content`），报错表现为**测试断言失败**（`publishedTitles().size() > 1`），看起来像代码 bug，其实是 harness 问题。CodeWeave 仓库自带的 `app-native-ascii` junction 指向 `应用端`（不是 `应用端/native`），深度刚好让 `<junction>/native/../../content` 命中仓库根的 `content/` —— 借现成 junction 而不是自己新建。junction 只能用 `os.rmdir` 摘除，递归删会连目标一起毁；删完要数一遍目标条目确认没受影响。

## 先怀疑自己的验证脚手架，再怀疑工具链

同一句 `qmlimportscanner: No such file or directory` 我复现了两种**假阳性**：① 把中文路径当参数传进 `.bat`（`%~1`）→ cmd 按 OEM 代码页转一道就烂了；② `cmd /c 'call "C:\Program Files (x86)\..." && set'` 抓 vcvars 环境，引号被 cmd 吞掉，只解析出 1 个变量，cmake 随即报「找不到 Ninja」。两次我都差点据此对工具线下结论。**正确做法**：Python 直接以 Unicode argv 调 cmake（CreateProcessW 走宽字符），vcvars 环境用一份纯 ASCII `.bat` 执行 `call vcvars64.bat && set > env.txt`，再按 **gbk** 解码解析（实测 150 个变量）。据此我还一度把自己的正确结论「中文路径致命」误改成「写重了」—— 脚手架修好后它又成立了。

## 两个「静默失败」，没有任何报错

1. **不设 `qt_policy(SET QTP0001 NEW)`** → QML 不嵌进资源（exe 里连 `Main.qml`/`qt/qml` 字符串都没有），`engine.loadFromModule()` 找不到东西，进程**以退出码 -1 结束，零控制台输出**。`qt_policy` 由 `find_package(Qt6)` 提供，必须写在它**之后**（写前面报 `Unknown CMake command "qt_policy"`）。
2. **`windeployqt` 不带 `--qmldir <含 qml 源码的目录>`** → 生成**空的 `qml/` 目录** → 部署版 `import QtQuick` 失败 → 同样是静默 -1 退出。

两条共同点：**GUI 子系统 exe 默认不写 stderr**，`subprocess` 管道和 `> log 2>&1` 都抓不到东西。判定方法：先看退出码（4294967295 = -1；3221225781 = 0xC0000135 = DLL 没找到），再看 `dist/qml/` 是否为空、exe 二进制里有没有 QML 资源串。

**但这是可以强制打开的**：设 `QT_FORCE_STDERR_LOGGING=1` 后，`QQuickView` 的 QML 编译错误就能从管道里拿到
（实测抓到 `qrc:/qt/qml/CodeWeave/Ui/qml/Main.qml:3530:56: Cannot assign to non-existent property "style"`）。
`QT_LOGGING_TO_CONSOLE` 也能用但会先打一行 deprecation 警告。要更细的模块解析过程加 `QT_LOGGING_RULES="qt.qml.import=true"`。
**别一上来就断言"GUI exe 抓不到输出"** —— 先试这个开关。

## QML 语法/属性错误的最快探测：`qmllint`（随 Qt 一起装）

`<Qt>/bin/qmllint.exe qml/Main.qml`（配 `QML2_IMPORT_PATH=<Qt>/qml`）静态扫全文，秒级。
实测一个 4600 行的 `Main.qml`：`missing-property` 只 1 条（就是让程序启动即死的那条），
`unqualified` 风格告警 946 条。**做门禁只把 `missing-property` 当错误**，`--warnings-as-errors` 全开会被风格告警淹死。
比它更强的是让程序自己加载一次（见下条），qmllint 只能查编译期，查不出运行期绑定错误。

## offscreen QPA 会让中文全变豆腐块 —— 视觉取证必须用真实 `windows` 平台

`QT_QPA_PLATFORM=offscreen` 下 `QQuickView` 能正常编译加载、`grabWindow()` 也出图，但 **CJK 字形全是方框**
（伴随 `QFontDatabase: Cannot find font directory <Qt>/lib/fonts`）。这是 offscreen 的字体回退问题，
**不是产品缺陷**，据此报"你的界面显示成方块"是错的。要出可对比的视觉证据就别设 `QT_QPA_PLATFORM`，
用真实 `windows` 平台跑（窗口一闪而过，2 s 内退出），中文渲染与已安装版一致。

## `-DCMAKE_CXX_FLAGS=...` 会**整串替换**掉 CMake 给 MSVC 的默认值

CMake 对 MSVC 的 `CMAKE_CXX_FLAGS` 初始值是 `/DWIN32 /D_WINDOWS /EHsc`。命令行传
`-DCMAKE_CXX_FLAGS=/analyze`（或 `=/W4`）会把它**全部覆盖掉**，`/EHsc` 就没了，
于是 `<chrono>` 之类头文件刷出几十条 `C4530 未启用展开语义`，看起来像项目的重大缺陷。
**正确写法是追加**：`-DCMAKE_CXX_FLAGS="/DWIN32 /D_WINDOWS /EHsc /analyze /W4"`。
判据：改配置前后各跑一次，若某条警告从 32 条变 0 条而源码没动，那是脚手架变了。
（2026-10-10 我据此误报过一次"core 没有 /EHsc"，实测 9 个目标全都有。）

## 想知道某个 flag 到底加没加：读 `build.ninja`，别看日志

Ninja 默认不回显编译命令，`-v` 才有。真正的逐目标 flag 在 `<build>/build.ninja` 里：
只取 `build **/*.obj:` 语句后面那条 `  FLAGS = `，**别把 `build xxx.exe: CXX_EXECUTABLE_LINKER...`
的 FLAGS 混进来**（链接规则没有编译 flag，会把统计彻底带偏 —— 我第一次读出来一张全错的表）。
CMake 生成的 cl 命令行里 `/DWIN32` 这类是写在 FLAGS 开头的，所以覆盖与否一眼可辨。

## MSVC `/analyze` 输出的两个解析坑

1. 诊断行格式是 `path(230) : warning C6031: ...` —— **括号和冒号之间有一个空格**，
   按 gcc 风格写 `path(230): warning` 的正则会**静默匹配 0 条**，看起来像"分析器什么都没报"。
2. 中文诊断是 **GBK**，用 UTF-8 读会得到乱码但结构还在；正则能过但消息不可读。
   先 `raw.decode("gbk", errors="replace")` 再解析。
3. `/analyze` 有真误报：`C6001 使用未初始化内存` 会打在**成员数与初始值个数刚好相等的聚合初始化**上
   （实测 `EvidenceRecord` 13 成员 / 13 初始值仍报 C6001）。报之前先数结构体成员，别直接采信。


## MSVC 的 `std::filesystem::is_symlink()` 把 junction 也算成 symlink

`symlink_status()` 对 Windows **目录联接**返回的 reparse point 会被 MSVC STL 判为 symlink。
后果：任何"防逃逸 → 拒绝 symlink 路径"的应用层守卫，会连带拒掉 **junction、OneDrive/Dropbox 同步占位目录、
`已知文件夹` 重定向**这些完全正常的部署形态，而且往往只是**静默返回空结果**（错误串进了一个没人显示的状态字段）。
实测：把一个拒绝 symlink 根目录的内容加载器指向 junction 后的 `content/`，10 s 超时、条目数为 0；
换成真实目录 0.5 s 全绿 —— 唯一变量是联接。**排查顺序**：先怀疑自己搭的 ASCII junction，再怀疑产品代码；
真要修产品，判据应是"解析后的真实路径是否越界"，不是"是不是 reparse point"。


## aqtinstall（命令行装 Qt）的边界

- **不需要注册 Qt 账号**（别误以为必须走官方在线安装器的登录墙）。
  本机实测（2026-10-09）：`uvx --from aqtinstall aqt install-qt windows desktop 6.8.3 win64_msvc2022_64 -O D:\Qt`
  配 `HTTPS_PROXY=http://127.0.0.1:7897` → 125 s、2.0 GB、退出码 0。**现在本机有 `D:\Qt\6.8.3\msvc2022_64`**，
  配套：cmake/ninja 用 `C:\mingw64\bin\cmake.exe`，MSVC 环境靠 `dumpenv.cmd` 调 vcvars64.bat 再解析 `set`。
- 但 **aqtinstall 3.3.0（PyPI 最新）不支持 Qt 6.11+ 的新仓库布局**：新版把组件挪到嵌套的 `qt.qt6.<ver>.<arch>/`，aqt 仍按老结构请求 `qt6_6120/qt6_6120/Updates.xml` → 404。实测 `qt6_683/` 老结构 HTTP 200 可装，`qt6_6113/`、`qt6_6120/` 全 404。要 6.11+ 只能官方在线安装器或等 aqt 适配。
- **`--modules` 里写不存在的模块名会让整个安装中止**（不是跳过）。Qt 6 里 **`qtsvg` 不是模块名**（SVG 已并入 qtbase）。先 `aqt list-qt windows desktop --modules <版本> <arch>` 拿真实清单。
- aqt 装出来的 Qt **没有 `LICENSES/` 目录**（只有 `doc/` 和 `sbom/`）→ LGPL 随包义务要自己补，别以为装完就齐。

## windeployqt 的体积与行为（实测，替换掉「60–120 MB」这类估计）

- 带 `--qmldir` 的最小 Qt Quick 交付：**59.4 MB**。
- 在 **vcvars 环境里**跑 windeployqt 会自动多带 `vc_redist.x64.exe` **24.4 MB** → 合计约 **84 MB**；不在 vcvars 里则报 `Cannot find Visual Studio installation directory, VCINSTALLDIR is not set` 并跳过它。报体积时必须说明这一差别。
- **`--dir` 只搬运行库和插件，不复制主程序 exe** —— 要自己拷过去再启动。

## 版本事实（2026-10-05 核）

`aqt list-qt windows desktop` → `6.7.3 6.8.3 6.9.3 6.10.3 6.11.3 6.12.0`。**Qt 6.12 是 LTS**（官方博客标题即「Qt 6.12 LTS Released!」），6.8 也仍是受支持的 LTS 线。别把 6.11 当最新。

## CTest 全绿后 `LastTestsFailed.log` 仍在 —— 残留文件，不是本轮结论

CTest **不会在全绿运行后删除** `<build>/Testing/Temporary/LastTestsFailed.log`。2026-11-11 与 11-12 两次：该文件存在且内容写着 `8:qt-qml-load`，但 mtime 是前一天某次中间态失败；本轮 11/11 全绿、#8 实际通过。我据此误判过「当前是红的」。**判本轮结果只看 `LastTest.log` 的 mtime + ctest stdout 的 `tests passed` 行**，或先比对两个文件 mtime；看到失败日志存在不等于红。

## `QQmlEngine::warnings` 只覆盖创建期 —— 「QML warnings 0」证明不了无未定义绑定

只连接 `QQmlEngine::warnings` 信号收集警告时，**窗口 resize 后绑定重新求值产生的警告走 Qt 消息处理器，不进该信号**。实测缺陷：`anchors.topMargin: root.width <= 1200 ? ds.s84 : ds.s20` 中 `s84` 未声明，1440×900 的验收截图走另一分支照不到，1100×720 窄窗 smoke 又报「warnings 0」——两者都不矛盾，因为采集面有盲区。要覆盖运行期绑定警告必须 `qInstallMessageHandler` 收 `QtWarningMsg`（并说明过滤口径）。**推广：任何「0 警告/0 错误」的清洁声明都要先声明观察面**；条件分支里的缺陷只在触发该分支的状态下可见，验收状态选错了就永远绿。

## 中文 SDK 物理路径：用 `subst` 映射盘符，别改源码路径

Ninja 无法枚举物理路径含非 ASCII 段的 SDK（junction 也救不了，因为 junction 目标仍是中文）。CodeWeave 的 `构建当前Qt.cmd` 做法：`subst` 一个**固定盘符（Q:）**指向 SDK，构建结束在 cleanup 里摘除；中断的构建会留下残留映射，脚本会认领指向自家 SDK 的旧映射。看到「多出一个同容量盘符」先查 `subst`/`QueryDosDevice`，见 [[reference-windows-ghost-drive-letter]]。

Related: [[reference-qt-prep-environment]], [[reference-qt-qml-licensing-traps]], [[reference-windows-batch-entry-encoding]], [[reference-windows-window-capture-pixelcheck]]
