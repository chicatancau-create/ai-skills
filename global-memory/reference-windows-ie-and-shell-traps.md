---
name: windows-ie-and-shell-traps
description: IE11 capability fully removed on this box (state NotPresent after the 2026-09-28 reboot; only Remove-WindowsCapability works, DISM feature name is dead); %APPDATA%\Microsoft\Internet Explorer holds the shell's Quick Launch/taskbar pins.
metadata:
  type: reference
---

Facts about this Windows box (Build 28000.2704, registry reports "Windows 10 Pro 26H1"), from the 2026-09-21 "uninstall IE cleanly" task.

1. **IE was removed; the user knowingly gave up Edge IE mode.** Initial answer was "保留 IE 模式", so removal was blocked; the user then reversed with 算了，全砍掉 — 碰到老网银再说. So IE mode is **not** a standing requirement on this machine. Restore path if a legacy site ever appears: elevated `Add-WindowsCapability -Online -Name Browser.InternetExplorer~~~~0.0.11.0` + reboot (that is Microsoft's own fix for "uninstalled IE11 and IE mode won't work").

2. **On build 28000 only the Capability form of IE exists — the legacy DISM feature name is a dead end.** `DISM /Disable-Feature /FeatureName:Internet-Explorer-Optional-amd64 /Remove` fails with **0x800f080c** (package not found). `Get-WindowsOptionalFeature -Online -All` also fails on `-All` parameter binding. What worked: elevated `Remove-WindowsCapability -Online -Name 'Browser.InternetExplorer~~~~0.0.11.0'` → `Installed` → `UninstallPending`, `RestartNeeded: True`; after the 2026-09-28 reboot the authoritative state is **`NotPresent`** and `Get-WindowsPackage -Online` lists **no** InternetExplorer package in the component store. Passing `-InputObject` from a `Get-WindowsCapability` pipeline throws a parameter-binding error; give `-Name` as a literal string.

   Still present by design (do NOT hand-delete): `C:\Windows\System32\mshtml.dll`, `ieframe.dll`, `iedkcs32.dll`, and `C:\Program Files\Internet Explorer` (10 entries: `ieinstal.exe`, `iediagcmd.exe`, `IEShims.dll`, `hmmapi.dll`, `ielowutil.exe`, `ExtExport.exe`, locale dirs) — but **no `iexplore.exe` in either Program Files or Program Files (x86)**. The folder belongs to component-store servicing; manual deletion breaks servicing/Windows Update and WCP restores it.

3. **IE user data under `%LOCALAPPDATA%\Microsoft\Internet Explorer` regrows from ordinary use, not from rebooting.** Deleted 2026-09-21, then found again with `LastWriteTime` 2026-09-24 08:40–21:05 (incl. a fresh `DOMStore\<hash>\pan.baidu[1].xml` and a full ESE `CacheStorage`) — i.e. written days later while the IE web platform was touched by some app. Re-deleted 2026-09-28 after a reboot (files were unlocked then; `edb.log` had been locked on 09-21). **Do not conclude "reboot regenerated it" — read LastWriteTime against the boot time first.** Don't chase this folder; its reappearance is not an incomplete uninstall. Only `iexplore.exe` absence + capability `NotPresent` are the real completion signals.

4. **`%APPDATA%\Microsoft\Internet Explorer` is a trap.** The folder name is legacy; it contains `Quick Launch\User Pinned\{TaskBar,StartMenu,ImplicitAppShortcuts}` — i.e. the user's real taskbar and Start pins (observed over time: File Explorer, Google Chrome, 微信, Wallpaper Engine, Steam, ATK HUB, zen.exe, DeskBox). Deleting "IE leftovers" there destroys shell pins. Never write to it; read-only enumeration only.

**How to apply:** before any "clean up / uninstall X" request on this machine, check whether X's leftovers are actually shell- or component-owned, and back up first — a robocopy byte-count mismatch is what surfaced #4. DISM/`*-WindowsCapability` need elevation (unelevated DISM returns error 740); drive them through a UAC-launched `.ps1` that logs to a file, keep the `.ps1` pure ASCII for PS 5.1, and log with `-Encoding utf8` (ascii turns Chinese DISM output into `?`). See [[feedback-backup-and-write-authorization]], [[feedback-no-unverified-cause-claims]], [[feedback-windows-config-json-encoding]].
