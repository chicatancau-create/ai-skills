"""One entry point for the whole "two skills + token saver" setup on this box.

  python D:\\Skills\\skill-router\\ops.py status     everything at a glance
  python D:\\Skills\\skill-router\\ops.py verify     real completion, both hops
  python D:\\Skills\\skill-router\\ops.py start      bring the proxy up
  python D:\\Skills\\skill-router\\ops.py stop       take the proxy down
  python D:\\Skills\\skill-router\\ops.py restart    stop + start
  python D:\\Skills\\skill-router\\ops.py wire       point agents at headroom (8787)
  python D:\\Skills\\skill-router\\ops.py unwire     roll agents back to cc-switch (15721)
  python D:\\Skills\\skill-router\\ops.py skills     rebuild the router catalog

Chain:  agent -> headroom:8787 -> cc-switch:15721 -> upstream
"""
import os, sys, json, socket, subprocess, time, urllib.request, urllib.error

# The console here is GBK (Windows PowerShell 5.1).  Subprocess output carries
# UTF-8 Chinese paths that arrive as U+FFFD, which raises UnicodeEncodeError on
# print and kills the whole command.  Never let a display problem abort ops.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(errors="replace")
    except Exception:
        pass

H = r"C:\Users\Admin"
PY = r"C:\Users\Admin\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
HR = r"D:\uv\bin\headroom.exe"
ROUTER = r"D:\Skills\skill-router\router.py"
WIRE = r"D:\Skills\skill-router\wire_headroom.py"
LIB = r"D:\Skills"
ACTIVE = r"D:\Skills-active"
LOG = os.path.join(H, ".headroom", "logs", "proxy-8787.log")

AGENT_ROOTS = {
    "claude": os.path.join(H, ".claude", "skills"),
    "agents/DSH": os.path.join(H, ".agents", "skills"),
    "opencode": os.path.join(H, ".config", "opencode", "skills"),
    "workbuddy": os.path.join(H, ".workbuddy", "skills"),
    "workbuddy-ai": os.path.join(H, ".workbuddy-ai", "skills"),
    "openclaw": os.path.join(H, ".openclaw", "skills"),
    "codex": os.path.join(H, ".codex", "skills"),
    "qoder": os.path.join(H, ".qoder", "skills"),
    "qoder-cn": os.path.join(H, ".qoder-cn", "skills"),
    "herdsman": os.path.join(H, ".herdsman", "work", "skills"),
    "dsh": os.path.join(H, ".dsh", "skills"),
    "cc-switch": os.path.join(H, ".cc-switch", "skills"),
}


def reparse(p):
    try:
        return getattr(os.lstat(p), "st_reparse_tag", 0)
    except OSError:
        return None


def target(p):
    try:
        return os.readlink(p)
    except OSError:
        return ""


def tcp(port, t=3):
    try:
        s = socket.create_connection(("127.0.0.1", port), timeout=t); s.close(); return True
    except Exception:
        return False


def http(url, t=8):
    try:
        with urllib.request.urlopen(url, timeout=t) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def run(cmd, t=180):
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=t,
                       encoding="utf-8", errors="replace")
    return (p.stdout or "") + (p.stderr or "")


def hr(*args, t=240):
    return run([HR, *args], t)


def cmd_status():
    print("=== headroom proxy ===")
    print(f"  8787 listening : {tcp(8787)}")
    st, body = http("http://127.0.0.1:8787/health")
    print(f"  /health        : {st}  {body[:160]}")
    out = hr("install", "status")
    for ln in out.splitlines():
        if ln.strip():
            print("  " + ln.strip())

    print("\n=== cc-switch proxy (upstream hop) ===")
    print(f"  15721 listening: {tcp(15721)}")
    st, body = http("http://127.0.0.1:15721/health")
    print(f"  /health        : {st}  {body[:120]}")

    print("\n=== agent wiring (which port each agent points at) ===")
    for label, path, key in (
        ("claude", os.path.join(H, ".claude", "settings.json"), "ANTHROPIC_BASE_URL"),
        ("codex", os.path.join(H, ".codex", "config.toml"), "base_url"),
    ):
        if not os.path.isfile(path):
            print(f"  {label:8s} MISSING {path}"); continue
        txt = open(path, encoding="utf-8", errors="replace").read()
        port = "8787 (headroom)" if "127.0.0.1:8787" in txt else (
               "15721 (cc-switch direct)" if "127.0.0.1:15721" in txt else "neither")
        print(f"  {label:8s} {port}")

    print("\n=== default-on window (D:\\Skills-active) ===")
    if os.path.isdir(ACTIVE):
        # WorkBuddy writes its own *_migration.json state files into whatever its
        # skills root points at.  They are app state, not skills -- never delete
        # them, and do not count them here.
        for n in sorted(os.listdir(ACTIVE)):
            p = os.path.join(ACTIVE, n)
            if not os.path.isdir(p):
                continue
            ok = os.path.isfile(os.path.join(p, "SKILL.md"))
            print(f"  {n:16s} SKILL.md={ok}  -> {target(p) or '(real dir)'}")
    else:
        print("  MISSING")

    print("\n=== agent skill roots (readable SKILL.md count) ===")
    for label, root in AGENT_ROOTS.items():
        if not os.path.isdir(root):
            print(f"  {label:14s} MISSING"); continue
        kids = [n for n in os.listdir(root) if not n.endswith(".json")]
        ok = sum(os.path.isfile(os.path.join(root, n, "SKILL.md")) for n in kids)
        rp = reparse(root)
        kind = "junction->" + target(root) if rp else "real dir"
        print(f"  {label:14s} {ok}/{len(kids)} readable   {kind}")

    print(f"\n=== library ===\n  {LIB}: "
          f"{sum(os.path.isfile(os.path.join(LIB,n,'SKILL.md')) for n in os.listdir(LIB) if os.path.isdir(os.path.join(LIB,n)))} skills")
    if os.path.isfile(LOG):
        print(f"  proxy log: {LOG} ({os.path.getsize(LOG)} bytes)")


def cmd_verify():
    hdrs = {"content-type": "application/json", "x-api-key": "PROXY_MANAGED",
            "authorization": "Bearer PROXY_MANAGED", "anthropic-version": "2023-06-01"}
    body = {"model": "deepseek-v4.1-flash", "max_tokens": 16,
            "messages": [{"role": "user", "content": "Reply with exactly: OK"}]}
    for port, tag in ((15721, "cc-switch direct"), (8787, "headroom -> cc-switch")):
        r = urllib.request.Request(f"http://127.0.0.1:{port}/v1/messages",
                                   data=json.dumps(body).encode(), headers=hdrs)
        t0 = time.time()
        try:
            with urllib.request.urlopen(r, timeout=45) as resp:
                raw = resp.read().decode("utf-8", "replace"); st = resp.status
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", "replace"); st = e.code
        except Exception as e:
            raw = f"{type(e).__name__}: {e}"; st = None
        ms = round((time.time() - t0) * 1000)
        print(f"  {tag:24s} status={str(st):5s} {ms:6d}ms  {raw[:240]}")
    print("\n  NOTE: if BOTH hops fail the same way, the upstream account/route is")
    print("  the problem, not headroom.  Check the cc-switch log:")
    print(r"    C:\Users\Admin\.cc-switch\logs\cc-switch.log")


def cmd_skills():
    print(run([PY, ROUTER, "sync"]))
    print(run([PY, ROUTER, "doctor"]))


def cmd_savings():
    """The ONLY trustworthy proof that headroom is working.

    Single-shot probes lie: provider prompt-cache can fake a -99.8% "saving"
    (headroom's own ledger showed tok_saved=0, cache_read=64000), and cache mode
    legitimately refuses to compress a cold full history, a read_file result
    (PROTECT_READS=1), or a payload whose ratio trips the strict accuracy guard.
    Real multi-turn traffic is what this ledger counts.
    """
    print(run([HR, "savings"], 180))
    print("=== is the ML compressor (Kompress) actually loaded? ===")
    if os.path.isfile(LOG):
        hits = []
        with open(LOG, encoding="utf-8", errors="replace") as f:
            for line in f:
                if "Kompress" in line:
                    hits.append(line.rstrip())
        for line in hits[-6:]:
            print("  " + line[:230])
        if not any("Kompress ONNX loaded" in x for x in hits):
            print("  WARNING: no 'Kompress ONNX loaded' line -> ML compressor is OFF.")
            print("           Re-seed the model cache with seed_kompress.py (uses hf-mirror;")
            print("           huggingface.co is unreachable here and HEADROOM_OFFLINE=1 blocks fetch).")
    else:
        print("  log not found: %s" % LOG)


def cmd_guard(fix=False):
    """cc-switch rewrites BASE_URL on every attach/detach, silently bypassing
    headroom.  The guard re-asserts the hop (only while cc-switch is in proxy
    mode, and only when headroom is healthy)."""
    g = os.path.join(os.path.dirname(ROUTER), "wire_guard.py")
    print(run([PY, g, "--once" if fix else "--status"], 180))
    import subprocess
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-CimInstance Win32_Process -Filter \"Name='pythonw.exe'\" | "
             "Where-Object { $_.CommandLine -like '*wire_guard*' } | "
             "Select-Object -ExpandProperty ProcessId"],
            capture_output=True, text=True, timeout=60)
        pids = (out.stdout or "").strip()
        print("watchdog process: %s" % (pids if pids else "NOT RUNNING (logon entry will start it; "
                                                        "or run: pythonw wire_guard.py --watch)"))
    except Exception as e:
        print("watchdog process: query failed %s" % e)
    gl = os.path.join(os.environ.get("AI_SHARED_SKILLS_STATE_DIR", r"D:\AI-Tool-State"),
                      "wire-guard", "guard.log")
    if os.path.isfile(gl):
        with open(gl, encoding="utf-8", errors="replace") as f:
            tail = f.readlines()[-5:]
        print("guard log tail:")
        for t in tail:
            print("  " + t.rstrip()[:190])


def cmd_shield(snap=False):
    """The default window is junctions into the library, so a shell delete of the
    window wipes the library (incident 2026-11-15 02:04:06).  The shield keeps a
    real mirror at D:\\Skills-mirror and repairs from it."""
    s = os.path.join(os.path.dirname(ROUTER), "skill_shield.py")
    print(run([PY, s, "--once"] + (["--snapshot"] if snap else []), 180))
    print(run([PY, s, "--status"], 120))


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "status":
        cmd_status()
    elif cmd == "verify":
        cmd_verify()
    elif cmd == "savings":
        cmd_savings()
    elif cmd == "guard":
        cmd_guard("--fix" in sys.argv or "--once" in sys.argv)
    elif cmd == "shield":
        cmd_shield("--snapshot" in sys.argv)
    elif cmd == "skills":
        cmd_skills()
    elif cmd in ("start", "stop", "restart"):
        print(hr("install", cmd))
        time.sleep(3)
        print(f"  8787 listening: {tcp(8787)}")
    elif cmd == "wire":
        print(run([PY, WIRE, "--apply"], 400))
    elif cmd == "unwire":
        print(run([PY, WIRE, "--rollback"], 120))
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
