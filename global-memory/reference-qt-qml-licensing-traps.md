---
name: reference-qt-qml-licensing-traps
description: 把 C++ 桌面应用迁到 Qt 6 + Qt Quick/QML 时的许可与性能陷阱：QScintilla 是 GPLv3+QWidget、Qt Canvas Painter 列 GPLv3、QQuickWidget 关线程渲染循环、/MT 与 Qt /MD CRT 冲突
metadata:
  type: reference
---

推荐 Qt 作为「高性能 + 可自定义视觉」的桌面 UI 方案之前，先把这几条坑说清（都是被实际纠正过的）：

- **QScintilla 不是白送的编辑器。** 官方许可为 **GPLv3 或商业双许可**，而且它是 **QWidget** 控件，不能当 QML 项直接插进 Qt Quick 场景图；**动态链接不会把 GPL 变成 LGPL**。要用就得先做许可选择、动态链接/源码义务审查，并单独测 QWidget 嵌入 QML 的代价。
- **Qt Canvas Painter 在 Qt 6.11 许可页被列为 GPLv3 模块**（此条由项目内另一会话的工程文档指出，我未独立复核官方页，但「不作为默认依赖」是正确处置）。普通 Qt Quick 场景图已能画黑底/渐变/发光，不需要它。
- **`QQuickWidget` 会关闭 threaded render loop** 并增加离屏 render pass（官方文档明写）→ 性能路径必须用 `QQuickView` / `QQuickWindow`。
- **CRT 冲突**：自研 `CMakeLists.txt` 常用 `/MT`，Qt 官方 MSVC 二进制通常 `/MD`，混链接会出堆/链接问题。Qt 目标及其相连核心要在**独立构建树里统一 `/MD`**。
- **LGPL Qt 的合规不是「动态链接」一个动作就完成**：要逐模块记录确切版本与许可、随包提供许可证与通知、提供实际所用 Qt 库的对应源码及修改、保证用户可替换/重链接，且不得禁止为调试目的的逆向工程。GPL-only 模块不能混进包。自有业务代码不因满足 LGPL 而必须公开。
- **别把 Qt 说成性能冠军或「全 C++」**：QML 含 JavaScript 表达式与运行时；Qt Quick 有布局、绑定、场景图开销。选型可以定，但「最快」必须与既有基线在**同机、同配置、同负载、同内容快照**下实测，且披露样本量（5 次尾部样本不足以支撑 P95 结论）。
- 呈现计时要用 **PresentMon/ETW** 的呈现数据 —— 「动画渲染结束」不等于「屏幕已呈现」；Qt Profiler 只用于定位。
- 核验入口：`doc.qt.io/qt-6/licensing.html`、`doc.qt.io/qt-6/qquickwidget.html`、`doc.qt.io/qt-6/qtquick-visualcanvas-scenegraph.html`、`doc.qt.io/qt-6/windows-deployment.html`、`riverbankcomputing.com/software/qscintilla/intro`、`qt.io/development/open-source-lgpl-obligations`。

Related: [[reference-windows-desktop-distribution]], [[feedback-no-unverified-cause-claims]]
