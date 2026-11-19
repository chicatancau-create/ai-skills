---
name: reference-windows-process-env-inheritance
description: 改了 HKCU/HKLM 环境变量却不生效时，真凶通常是长寿命启动器进程的旧环境块 —— 附读他人进程环境块的纯 ctypes 方法（PEB+0x20→params、params+0x80→Environment）与 DeskBox 实案
metadata:
  type: reference
---

**规则**：`HKCU\Environment` / `HKLM\...\Session Manager\Environment` 里**已经删掉或改对**的变量，
仍然可能在应用里生效 —— 因为环境变量只在**进程创建时**复制一份。凡是「由长寿命启动器拉起来」的桌面应用，
只重启那个应用**没用**，它每次都从启动器继承旧环境。

**实案（2026-10-19，本机）**：DSH 插件 `dsh-workbuddy-connect` 一直报
`the configured WorkBuddy Electron binary is not available at D:\WorkBuddyAIguonei\WorkBuddy.exe`，
而注册表两处都已无 `WORKBUDDY_*`（我已删除并广播 `WM_SETTINGCHANGE`）。逐层查下来：

```
DeepSeek Harness (42296)  ← 父 DeskBox.exe (39360)  ← 父 11616（已退出）
DeskBox.exe        环境块含 WORKBUDDY_ELECTRON_BIN=D:\WorkBuddyAIguonei\WorkBuddy.exe   ← 旧值
DeepSeek Harness   同一份旧值（继承）
```

⇒ 修法只有两条：**重启那个启动器**，或**改从 Explorer（开始菜单 / 快捷方式 / Win+R）启动目标应用**。
本机 DSH 是 `DeskBox.exe` 拉起来的（DeskBox 见 [[reference-deskbox-zero-fill]]）。
另注：国际版一直正常，只是因为它继承的 `WORKBUDDY_AI_ELECTRON_BIN` 恰好指向存在的路径 ——
**同一份旧环境不一定表现为故障，可能只是"碰巧对"，别拿"另一个能用"当排除证据。**

**How to apply**：凡"我改了环境变量/PATH 但应用里还是旧值"，按这个顺序查，别反复重启目标应用：
① 注册表两处现读（HKCU + HKLM 机器级）；② 目标应用的**父进程链**（`Get-CimInstance Win32_Process -Filter "ProcessId=X"`，
一路取 `ParentProcessId`，父可能已退出 → 链会断，断本身就是线索）；③ 直接读启动器与目标进程的**环境块**比对。
还有一条同源判据：我自己这个 shell 也带着已删除的旧值（Qoder 启动时快照的），
所以**我跑的子进程测试默认继承脏环境** —— 测"没有这个变量会怎样"必须显式 `delete process.env[k]`，
否则测的是旧值。

**读他人进程环境块（纯 stdlib ctypes，同用户无需管理员）**：

```python
h = kernel32.OpenProcess(0x0400|0x0010, False, pid)          # QUERY_INFORMATION | VM_READ
NtQueryInformationProcess(h, 0, byref(PBI), ...) -> PBI.PebBaseAddress
params    = read_ptr(Peb + 0x20)                              # x64 RTL_USER_PROCESS_PARAMETERS
envaddr   = read_ptr(params + 0x80)                           # Environment
raw       = read(envaddr, 0x8000)                             # 见下：别信 EnvironmentSize
entries   = raw.decode('utf-16-le','ignore').split('\0')
```

⚠ 实测坑：`EnvironmentSize` 我按 `params+0x90` 读回 **0**（偏移不对），所以**别依赖它** ——
直接读固定 32 KB 再按 `\0` 切、只保留含 `=` 的条目即可。打印时**只按名字前缀过滤**（如 `WORKBUDDY`），
别整块输出 —— 环境块里常有令牌类变量。

Related: [[reference-git-credential-manager-windows]], [[project-dsh-agent-teams-deploy]], [[reference-deskbox-zero-fill]]
