---
name: reference-qoder-taskstop-orphan-process
description: TaskStop on a background Bash task kills only the npm/cmd wrapper; the node grandchild keeps holding the port — verify with Get-NetTCPConnection and Stop-Process the real PID.
metadata:
  type: reference
---

`TaskStop` reports `status: killed` while the actual server is still alive. When the background command was `npx vite preview ...`, the harness stops the `npx`/cmd wrapper, but `node.exe .../vite/bin/vite.js preview --port 4173 --strictPort` survives and keeps answering (it returned HTTP 404 only because I had deleted its `dist/` — an easy miss, since "404" looks like "nothing there").

**How to apply:** After stopping a self-started dev/preview server, always re-probe the port (`curl --max-time 2 http://localhost:<port>/`). A non-refused answer means an orphan. Find the owner with `Get-NetTCPConnection -LocalPort <port> -State Listen` → `Win32_Process -Filter "ProcessId=..."` and read `CommandLine` + `CreationDate` to prove it is yours, then `Stop-Process -Id <pid> -Force`. Write that lookup as a `.ps1` file, not an inline `-Command` string — bash swallows `$conn`/`$_` (see [[powershell-through-bash-and-recyclebin]]). Only kill a process whose command line you have confirmed as self-started; ports 4173/5173 can also belong to the user's own servers ([[reference-headless-browser-debris]]).
