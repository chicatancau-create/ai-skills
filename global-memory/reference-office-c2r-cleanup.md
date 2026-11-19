---
name: reference-office-c2r-cleanup
description: This PC's Office Click-to-Run layout — which folders are live engine vs real junk, store apps need provisioned-package removal, and how to get silent elevation.
metadata:
  type: reference
---

Windows box `ZHOUMO` (built-in `Admin`), Office is installed via Office Tool Plus at
`D:\全新office安装——Office_Tool\Office Tool\` (config dropped in
`%LOCALAPPDATA%\Office Tool Plus\Temp_XXXX\Configuration.xml`). SKU seen: ProPlus2024Retail,
x64, zh-cn, Current Channel, KMS-style activation tooling also on D:.

**Do not treat as junk** (they are the live C2R machinery; deleting them breaks future Office
updates even when no Office app is installed):

- `C:\Program Files\Common Files\Microsoft Shared\ClickToRun` (~98 MB) + `ClickToRunSvc` service
- `C:\Program Files\Microsoft Office 15\ClientX64` (~9 MB) — Office15 bootstrap for C2R updates
- `AppvStrm/AppvVemgr/AppvVfs` drivers, `C:\Windows\System32\OffFilt.dll`,
  CLSID `{f07f3920-…}` / `{98de59a0-…}` "Microsoft Office Filter/Persistent Handler" — all Windows inbox
- `Common Files\Microsoft Shared\ink`, `VBA`, `VC`, `XNA`, `VGX`, `DAO` — not Office-only

**Real junk signals** read from registry: `HKLM\SOFTWARE\Microsoft\Office\ClickToRun` →
`LastScenario` / `LastScenarioResult`, and `Scenario\INSTALL\TasksState` values
(`REMOVEINSTALLATION=TASKSTATE_FAILED` = half-finished uninstall). `Configuration\ProductReleaseIds`
empty while `ProPlus2024Retail.*` sub-values remain = install/uninstall aborted midway, apps already gone.

**Gotchas learned:**

- A failed/ongoing C2R install resets `HKLM\SOFTWARE\Microsoft\Office` itself (observed 8508 → 23
  subkeys in ~9 min). Never delete Office hives while `setup.exe` / `OfficeC2RClient` /
  `OfficeClickToRun` are running — that is what produces the `INSTALL / Failure` shell in the first place.
- Store apps (`Microsoft.MicrosoftOfficeHub` 328 MB, `Microsoft.OutlookForWindows`, `MSTeams`) are
  installed **and** provisioned: `Remove-AppxPackage` alone lets Windows re-add them — also run
  `Remove-AppxProvisionedPackage -Online`. Their *user data* can be 0 MB while the package is huge,
  so judge size by `C:\Program Files\WindowsApps\<pkg>`, not by `%LOCALAPPDATA%\Packages`.
- `ConsentPromptBehaviorAdmin=0` with `EnableLUA=1` here → `Start-Process -Verb RunAs` elevates
  with **no UAC dialog**, so an elevated run is cheap. A plain bash→powershell shell starts unelevated.
- `reg load` has no `/ro` switch (fails "Invalid syntax"); `reg save <hive> out.hiv` is the good backup,
  restorable with `reg load`. Backups from the 2026-09-22 cleanup: `C:\Office_Cleanup_Backup_2026-09-22`.
- Dangling `HKCR\.xlsx` → `Excel.Sheet.12` (ProgID gone) is what a half-removed Office leaves behind;
  a completed install re-registers it, so leave associations alone mid-install.

See also [[reference-windows-ie-and-shell-traps]], [[reference-powershell-through-bash-and-recyclebin]],
[[feedback-no-unverified-cause-claims]].
