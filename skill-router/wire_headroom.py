"""Phase E: point the cc-switch-backed agents at headroom (8787) instead of
cc-switch directly (15721).  headroom already forwards to 15721, so the chain is
    agent -> headroom:8787 -> cc-switch:15721 -> upstream.

Only .claude/settings.json and .codex/config.toml reference 15721 on this box.
DSH is deliberately NOT touched: it does not go through cc-switch and this
session is running on it.

  python wire_headroom.py            dry run
  python wire_headroom.py --apply    write (backs up first)
  python wire_headroom.py --rollback restore the newest backup
"""
import os, sys, json, shutil, time, re, urllib.request, urllib.error

H = r"C:\Users\Admin"
BACKUP = r"G:\AIrenwu\03_备份\_backup\headroom-wire"
STAMP = time.strftime("%Y%m%d-%H%M%S")
OLD, NEW = "15721", "8787"
APPLY = "--apply" in sys.argv
ROLLBACK = "--rollback" in sys.argv

TARGETS = [
    ("claude", os.path.join(H, ".claude", "settings.json"), "json"),
    ("codex", os.path.join(H, ".codex", "config.toml"), "toml"),
]

log = []
def say(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); log.append(s)


def newest_backup(name):
    d = os.path.join(BACKUP, name)
    if not os.path.isdir(d): return None
    fs = sorted(os.listdir(d))
    return os.path.join(d, fs[-1]) if fs else None


if ROLLBACK:
    say("=== ROLLBACK ===")
    for label, path, kind in TARGETS:
        b = newest_backup(label)
        if not b:
            say(f"  {label}: no backup found"); continue
        shutil.copy2(b, path)
        say(f"  restored {path} <- {b}")
        txt = open(path, encoding="utf-8").read()
        say(f"    now references: 15721={txt.count('15721')} 8787={txt.count('8787')}")
    sys.exit(0)

say("=== plan ===")
plans = []
for label, path, kind in TARGETS:
    if not os.path.isfile(path):
        say(f"  {label}: MISSING {path}"); continue
    txt = open(path, encoding="utf-8").read()
    n = txt.count(OLD)
    say(f"  {label}: {path}  ({len(txt)} bytes, {n} occurrence(s) of {OLD})")
    if n == 0:
        say(f"    nothing to do (already {NEW}? {txt.count(NEW)} occurrence(s))")
        continue
    # only rewrite the loopback proxy URL, never anything else
    new = txt.replace(f"127.0.0.1:{OLD}", f"127.0.0.1:{NEW}")
    new = new.replace(f"localhost:{OLD}", f"localhost:{NEW}")
    for line in new.splitlines():
        if NEW in line:
            say(f"    -> {line.strip()}")
    plans.append((label, path, txt, new))

if not APPLY:
    say("\n=== DRY RUN ===")
    sys.exit(0)

os.makedirs(BACKUP, exist_ok=True)
for label, path, old, new in plans:
    d = os.path.join(BACKUP, label)
    os.makedirs(d, exist_ok=True)
    bak = os.path.join(d, f"{STAMP}-{os.path.basename(path)}")
    shutil.copy2(path, bak)
    say(f"  BACKUP {bak}")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(new)
    say(f"  WROTE {path}")
    if path.endswith(".json"):
        json.loads(open(path, encoding="utf-8").read())   # syntax gate
        say("    JSON parses OK")

say("\n=== verify: real completion through the new endpoint ===")
HDRS = {"content-type": "application/json", "x-api-key": "PROXY_MANAGED",
        "authorization": "Bearer PROXY_MANAGED", "anthropic-version": "2023-06-01"}
for model in ("deepseek-v4.1-flash", "claude-sonnet-5"):
    body = {"model": model, "max_tokens": 16,
            "messages": [{"role": "user", "content": "Reply with exactly: OK"}]}
    r = urllib.request.Request(f"http://127.0.0.1:{NEW}/v1/messages",
                               data=json.dumps(body).encode(), headers=HDRS)
    t0 = time.time()
    try:
        with urllib.request.urlopen(r, timeout=90) as resp:
            raw = resp.read().decode("utf-8", "replace"); st = resp.status
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace"); st = e.code
    except Exception as e:
        raw = repr(e); st = None
    ms = round((time.time() - t0) * 1000, 1)
    say(f"  model={model:22s} status={st} {ms}ms  {raw[:220]}")

with open(r"G:\AIrenwu\05_取证扫描\_scan\phaseE_plan.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(log))
say("\n=== APPLIED ===  (rollback: python wire_headroom.py --rollback)")
