---
name: reference-uipi-blocks-elevated-target-testing
description: 目标是提权进程时，中等完整性的测试脚本会被 UIPI 静默挡掉——SendInput 返回成功但事件丢弃、PostMessage 失败不报错，会误判成「功能没做出来」
metadata:
  type: reference
---

在这台机上给**已提权（High IL）**的桌面窗口做自动化验证时，从默认（Medium IL）的 Bash/PowerShell 发出的输入会被 UIPI 过滤：

- `SendInput` 返回「注入了 1 个事件」，但目标窗口**根本收不到**——返回值不代表送达。
- `PostMessageW` 直接失败且不抛异常，除非显式检查返回值/`GetLastWin32Error`。
- `Stop-Process` 报「拒绝访问」；`Get-Process .Path` 返回空（这条反过来可以当「目标是提权进程」的判据）。
- 写进 `C:\Windows\Temp` 的文件，中等完整性连 `Test-Path` 都会抛「拒绝访问」而不是返回 False —— 别把它误读成「文件不存在」。

**How to apply:** 一旦怀疑目标提权，先把**整个测试脚本**用 `Start-Process -Verb RunAs` 跑起来、结果写到 D 盘日志再回读（本机 `ConsentPromptBehaviorAdmin=0`，静默无弹窗）。在证明「注入通路本身可用」之前，不要对功能下任何结论——我这次就是拿失败的正对照去怀疑已经生效的功能，白绕了好几轮。

顺带两个本机事实：`HKCU\SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers` 的 `~ RUNASADMIN` 在这台机确实生效（PixPin 就挂在这上面）；系统双击间隔只有 **340 ms**，做单击/双击判别时别按 500 ms 估。

判据尽量找**不依赖输入注入**的硬信号：目标窗口的 `GetWindowRect` 几何变化、它自己写出的日志行、或进程可读性差异，都比「我发了输入所以它应该动了」可靠——后者要先单独证明通路本身是通的。
