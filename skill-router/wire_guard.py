# -*- coding: utf-8 -*-
"""Keep the headroom hop in front of cc-switch, even after cc-switch rewrites configs.

WHY THIS EXISTS
---------------
cc-switch's mode controller rewrites the client config on every attach/detach.
Observed 2026-11-15 01:55:56 detach -> 01:56:04 attach: both
  ~/.claude/settings.json  env.ANTHROPIC_BASE_URL
  ~/.codex/config.toml     [model_providers.custom] base_url
were reset from http://127.0.0.1:8787 back to http://127.0.0.1:15721, silently
bypassing headroom (no error anywhere -- tokens just stop being saved).
Re-running the wiring by hand is not a fix; this guard re-asserts it.

RESPECTS THE USER
-----------------
It only rewrites when cc-switch reports mode=proxy AND attached=true for that app,
i.e. cc-switch itself just put 15721 there.  If the user deliberately detaches to
go direct (mode=direct), the guard leaves the config alone.  It also refuses to
point an agent at headroom unless headroom's /health actually answers 200.

USAGE
    python wire_guard.py --status     report only
    python wire_guard.py --once       fix now if needed (used by ops.py)
    python wire_guard.py --watch      loop forever (used by the logon entry)
"""
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request

HOME = r"C:\Users\Admin"
CLAUDE = os.path.join(HOME, ".claude", "settings.json")
CODEX = os.path.join(HOME, ".codex", "config.toml")
LIVE = os.path.join(HOME, ".cc-switch", "live-state.json")
HR = r"D:\uv\bin\headroom.exe"
BACKUP = r"G:\AIrenwu\03_备份\_backup\headroom-wire"
STATE = os.path.join(os.environ.get("AI_SHARED_SKILLS_STATE_DIR", r"D:\AI-Tool-State"),
                     "wire-guard")
LOG = os.path.join(STATE, "guard.log")

WANT_CLAUDE = "http://127.0.0.1:8787"
WANT_CODEX = "http://127.0.0.1:8787/v1"
CC_CLAUDE = "http://127.0.0.1:15721"
CC_CODEX = "http://127.0.0.1:15721/v1"

INTERVAL = 20          # seconds between watch ticks
START_COOLDOWN = 300   # don't try to start headroom more than once per 5 min
_last_start = 0.0


def log(msg):
    line = "%s %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg)
    try:
        os.makedirs(STATE, exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass
    if "--watch" not in sys.argv:
        print(line)


def healthy(port=8787, t=4):
    try:
        with urllib.request.urlopen("http://127.0.0.1:%d/health" % port, timeout=t) as r:
            return r.status == 200 and b'"healthy"' in r.read()
    except Exception:
        return False


def read_json(p):
    for _ in range(3):
        try:
            with open(p, encoding="utf-8") as f:
                return json.load(f)
        except (PermissionError, OSError):
            time.sleep(0.4)
        except ValueError:
            return None
    return None


def write_text(p, txt):
    """Atomic-ish replace with retry: cc-switch may hold the file briefly."""
    tmp = p + ".guardtmp"
    for attempt in range(4):
        try:
            with open(tmp, "w", encoding="utf-8", newline="") as f:
                f.write(txt)
            os.replace(tmp, p)
            return True
        except (PermissionError, OSError):
            time.sleep(0.5 * (attempt + 1))
    try:
        if os.path.isfile(tmp):
            os.remove(tmp)
    except OSError:
        pass
    return False


def backup(p, tag):
    try:
        d = os.path.join(BACKUP, tag)
        os.makedirs(d, exist_ok=True)
        dst = os.path.join(d, "%s-guard-%s" % (time.strftime("%Y%m%d-%H%M%S"), os.path.basename(p)))
        shutil.copy2(p, dst)
        return dst
    except OSError as e:
        log("backup failed for %s: %s" % (p, e))
        return None


def cc_mode(app):
    L = read_json(LIVE)
    if not isinstance(L, dict):
        return None, None
    a = (L.get("apps") or {}).get(app) or {}
    return a.get("mode"), bool(a.get("attached"))


def maybe_start_headroom():
    global _last_start
    now = time.time()
    if now - _last_start < START_COOLDOWN:
        return
    _last_start = now
    log("headroom unhealthy -> asking the supervisor to start it")
    try:
        subprocess.run([HR, "install", "start"], capture_output=True, text=True, timeout=180,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except Exception as e:
        log("start attempt failed: %s" % e)


def check_claude(apply_):
    mode, attached = cc_mode("claude")
    J = read_json(CLAUDE)
    if J is None:
        return "claude: settings.json unreadable/unparseable"
    env = J.get("env") or {}
    cur = env.get("ANTHROPIC_BASE_URL", "")
    if mode != "proxy" or not attached:
        return "claude: cc-switch mode=%s attached=%s -> leave alone (user chose direct)" % (mode, attached)
    if cur == WANT_CLAUDE:
        return "claude: OK (%s)" % cur
    if CC_CLAUDE not in cur:
        return "claude: unexpected BASE_URL %r -> leave alone (not a cc-switch rewrite)" % cur
    if not apply_:
        return "claude: NEEDS FIX %s -> %s" % (cur, WANT_CLAUDE)
    if not healthy():
        maybe_start_headroom()
        return "claude: headroom not healthy -> NOT wiring (would black-hole the agent)"
    b = backup(CLAUDE, "claude")
    env["ANTHROPIC_BASE_URL"] = WANT_CLAUDE
    J["env"] = env
    if write_text(CLAUDE, json.dumps(J, ensure_ascii=False, indent=2) + "\n"):
        log("claude: rewired %s -> %s (backup %s)" % (cur, WANT_CLAUDE, b))
        return "claude: FIXED -> %s" % WANT_CLAUDE
    return "claude: write FAILED (file locked?)"


def check_codex(apply_):
    mode, attached = cc_mode("codex")
    try:
        with open(CODEX, encoding="utf-8") as f:
            txt = f.read()
    except OSError as e:
        return "codex: config.toml unreadable: %s" % e
    m = re.search(r'base_url\s*=\s*"([^"]+)"', txt)
    cur = m.group(1) if m else ""
    if mode != "proxy" or not attached:
        return "codex: cc-switch mode=%s attached=%s -> leave alone (user chose direct)" % (mode, attached)
    if cur == WANT_CODEX:
        return "codex: OK (%s)" % cur
    if CC_CODEX not in cur:
        return "codex: unexpected base_url %r -> leave alone (not a cc-switch rewrite)" % cur
    if not apply_:
        return "codex: NEEDS FIX %s -> %s" % (cur, WANT_CODEX)
    if not healthy():
        maybe_start_headroom()
        return "codex: headroom not healthy -> NOT wiring (would black-hole the agent)"
    b = backup(CODEX, "codex")
    new = txt[:m.start(1)] + WANT_CODEX + txt[m.end(1):]
    if write_text(CODEX, new):
        log("codex: rewired %s -> %s (backup %s)" % (cur, WANT_CODEX, b))
        return "codex: FIXED -> %s" % WANT_CODEX
    return "codex: write FAILED (file locked?)"


def tick(apply_):
    out = [check_claude(apply_), check_codex(apply_)]
    # The default window is junctions into the library, so a shell delete of the
    # window destroys the library (happened 2026-11-15 02:04:06).  Keep a mirror
    # outside the junction graph and repair from it.
    if apply_:
        try:
            import skill_shield
            for a in skill_shield.tick(verbose=False):
                log("shield: " + a)
                out.append("shield: " + a)
        except Exception as e:
            out.append("shield: error %s: %s" % (type(e).__name__, e))
        # The git remotes are the real backup (user: no local backups).  Keep them
        # current.  Internally debounced to one attempt per 10 min and only when
        # the tree actually changed, so this is a no-op on most ticks.
        try:
            import git_backup
            for p, n in git_backup.REPOS:
                if git_backup.sync(p, n):
                    out.append("backup: %s pushed" % n)
        except Exception as e:
            out.append("backup: error %s: %s" % (type(e).__name__, e))
    return out


def main():
    args = sys.argv[1:]
    if "--watch" in args:
        log("watch started (interval %ds, pid %d)" % (INTERVAL, os.getpid()))
        prev = None
        while True:
            try:
                res = tick(True)
                key = tuple(res)
                if key != prev:
                    for r in res:
                        log(r)
                    prev = key
            except Exception as e:
                log("tick error: %s: %s" % (type(e).__name__, e))
            time.sleep(INTERVAL)
    apply_ = "--once" in args or "--apply" in args
    for r in tick(apply_):
        print(r)
    if not apply_:
        print("(report only; use --once to fix, --watch to keep it fixed)")


if __name__ == "__main__":
    main()
