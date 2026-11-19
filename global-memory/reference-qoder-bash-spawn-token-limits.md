---
name: reference-qoder-bash-spawn-token-limits
description: 本会话 Bash 工具派生的进程令牌受限——GUI 报「No usable temporary directory」、%APPDATA% 首次建目录 WinError 5；要真验桌面应用必须经 explorer.exe 启动
metadata:
  type: reference
---

2026-10-30 部署一个 PyInstaller 桌面客户端时撞到的两类**假故障**，都源于从本会话 Bash 直接 spawn 的进程带着受限令牌。

## 症状一：GUI 起来就弹「缺少 WebView2」，真错在别处

由 bash 直接 `Popen(exe)` 启动时，客户端弹出「这台电脑缺少微软 Edge WebView2 运行时，界面没法显示」，
但同一段错误详情里写的是：

```
[Errno 2] No usable temporary directory found in
['C:\\Users\\Admin\\AppData\\Local\\Temp', ..., 'C:\\WINDOWS\\Temp', 'c:\\temp', 'c:\\tmp', ...]
```

即 **TEMP 不可写**，不是缺 WebView2（`C:\Program Files (x86)\Microsoft\EdgeWebView\Application` 实测存在）。

**判据**：同一个 shell 里 `python -c` 往 `AppData\Local\Temp` 和 `Roaming` 写文件都成功 —— 所以别拿"我的 shell 能写"去否定 GUI 的报错，两者令牌不同。

**解法**：改用 `explorer.exe "<exe 绝对路径>"` 启动。Explorer 用自己的令牌 CreateProcess，**等价于用户在资源管理器里双击**。改完后主窗口正常出现（类名 `WindowsForms10.Window.8.app...`，pywebview 的 WinForms 宿主）。

## 症状二：首次创建 %APPDATA% 下新目录返回 WinError 5

`os.makedirs(r'...\AppData\Roaming\<新目录>', exist_ok=True)` 报 `PermissionError [WinError 5] 拒绝访问`，
而同一天 bash 的 `mkdir -p` 建同一个目录**成功**；目录一旦存在后，python 再在里面建子目录也正常。
排查过并**排除**的：Controlled Folder Access（`Get-MpPreference` 返回 0）、ACL（`ZHOUMO\Admin` 是 FullControl）。
**根因未证实**，但可操作结论是：**跑测试/装工具前先把应用要用的数据目录建好**，别把"首次创建失败"当成程序 bug 报出去。

## 副作用

- 由 bash spawn 的 GUI 进程可能弹**Windows 防火墙**询问（本机 adb 绑 `127.0.0.1:5037`，`netstat` 可证只有回环，点「取消」不影响插线使用）。这类安全弹窗**不要替用户点**，报给他决定。
- 环境变量（PATH / 用户级变量）改动对**已存在的 bash 会话无效**，测的时候要么显式注入，要么读注册表 `HKCU\Environment` 复核。见 [[reference-windows-process-env-inheritance]]。

相关：[[reference-windows-window-capture-pixelcheck]]、[[reference-computer-use-blocked]]、
[[feedback-delivery-shortcut-and-location]]、[[feedback-no-unverified-cause-claims]]
