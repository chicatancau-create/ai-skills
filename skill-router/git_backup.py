"""Keep the git backup current. Called by wire_guard's watch loop (debounced) or
by hand:  ops.py backup

Design rules:
  * Never pushes secrets: the licence exclusions live in .gitignore, and a final
    staged-path check refuses to commit anything under an excluded directory.
  * Never force-pushes, never rewrites history, never deletes a remote branch.
  * A failed push is logged and retried next cycle; it never blocks the guard.
  * Debounce: at most one attempt per MIN_INTERVAL seconds, and only when the
    working tree actually differs from HEAD.
"""
import json
import os
import subprocess
import sys
import time

for _s in (sys.stdout, sys.stderr):
    if _s is not None:
        try:
            _s.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
GIT = r"D:\Git\cmd\git.exe"
# 子进程一律不创建控制台窗口：本模块由无窗口的 pythonw 调用，
# 不隐藏时每个 git 命令都会闪一个黑色 cmd 窗口（开机时会连弹数个）。
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
REPOS = [(r"D:\Skills", "ai-skills"), (r"D:\QoderToolkit", "qoder-toolkit")]
REMOTES = ["origin", "gitcode"]
STATE = r"D:\AI-Tool-State\git-backup"
LOG = os.path.join(STATE, "backup.log")
MIN_INTERVAL = 600          # seconds between automatic attempts
EXCLUDED = {
    "ai-skills": {"docx", "pdf", "pptx", "xlsx", "reverse-trace",
                  "reverse-wechat-miniapp", "webapp-building"},
    "qoder-toolkit": {"web-kimi"},
}
env = dict(os.environ, GIT_TERMINAL_PROMPT="0")


def log(msg):
    os.makedirs(STATE, exist_ok=True)
    line = "%s %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg)
    if sys.stdout is not None:
        try:
            print(line)
        except (OSError, ValueError):
            pass
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


def git(args, cwd, timeout=1800):
    try:
        r = subprocess.run([GIT] + args, cwd=cwd, capture_output=True, text=True,
                           timeout=timeout, env=env, encoding="utf-8", errors="replace",
                           creationflags=NO_WINDOW)
        return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()
    except subprocess.TimeoutExpired:
        return 124, "", "timeout after %ds" % timeout
    except OSError as e:
        return 125, "", str(e)


def last_attempt(name):
    p = os.path.join(STATE, name + ".last")
    try:
        return float(open(p, encoding="utf-8").read().strip())
    except (OSError, ValueError):
        return 0.0


def mark(name):
    os.makedirs(STATE, exist_ok=True)
    with open(os.path.join(STATE, name + ".last"), "w", encoding="utf-8") as f:
        f.write(str(time.time()))


def sync(path, name, force=False, quiet=False):
    if not os.path.isdir(os.path.join(path, ".git")):
        log("%s: not a git repo, skip" % name)
        return False
    if not force and time.time() - last_attempt(name) < MIN_INTERVAL:
        return False
    rc, dirty, _ = git(["status", "--porcelain"], path)
    if rc != 0:
        log("%s: status failed rc=%d" % (name, rc))
        return False
    if not dirty and not force:
        # nothing changed locally; still verify the remotes have our HEAD
        rc, head, _ = git(["rev-parse", "HEAD"], path)
        for r in REMOTES:
            rc2, out, _ = git(["ls-remote", "--heads", r], path, timeout=120)
            if rc2 != 0 or head not in out:
                log("%s: remote %s missing HEAD, will push" % (name, r))
                break
        else:
            mark(name)
            return False
    if dirty:
        git(["add", "-A"], path)
        rc, staged, _ = git(["diff", "--cached", "--name-only"], path)
        files = [f for f in staged.splitlines() if f.strip()]
        bad = [f for f in files if f.split("/")[0] in EXCLUDED.get(name, set())]
        if bad:
            log("%s: REFUSING to commit licence-excluded paths: %s" % (name, bad[:5]))
            git(["reset"], path)
            return False
        if not files:
            mark(name)
            return False
        msg = "auto-backup %s: %d file(s)\n\n%s" % (
            time.strftime("%Y-%m-%d %H:%M:%S"), len(files),
            "\n".join(files[:40]) + ("\n…" if len(files) > 40 else ""))
        rc, out, err = git(["commit", "-q", "-m", msg], path)
        if rc != 0:
            log("%s: commit failed rc=%d %s" % (name, rc, err[:200]))
            return False
        log("%s: committed %d file(s)" % (name, len(files)))
    ok = True
    for r in REMOTES:
        rc, out, err = git(["push", r, "main"], path)
        if rc != 0:
            ok = False
            log("%s: push %s FAILED rc=%d %s" % (name, r, rc, (err or out)[:220]))
        else:
            rc2, head, _ = git(["rev-parse", "HEAD"], path)
            rc3, remote, _ = git(["ls-remote", "--heads", r], path, timeout=120)
            match = rc3 == 0 and head in remote
            log("%s: push %s ok, remote HEAD match=%s" % (name, r, match))
            ok = ok and match
    mark(name)
    return ok


def status():
    for path, name in REPOS:
        print("\n=== %s (%s) ===" % (name, path))
        rc, head, _ = git(["rev-parse", "--short", "HEAD"], path)
        rc2, dirty, _ = git(["status", "--porcelain"], path)
        n = len([x for x in dirty.splitlines() if x.strip()])
        print("  HEAD=%s  uncommitted=%d" % (head, n))
        for r in REMOTES:
            rc3, out, err = git(["ls-remote", "--heads", r], path, timeout=120)
            rc4, full, _ = git(["rev-parse", "HEAD"], path)
            print("  %-8s rc=%d match=%s %s" %
                  (r, rc3, rc3 == 0 and full in out, out.split()[0][:12] if out else err[:80]))
        la = last_attempt(name)
        print("  last auto attempt: %s" %
              (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(la)) if la else "never"))
    if os.path.isfile(LOG):
        print("\n--- log tail ---")
        for ln in open(LOG, encoding="utf-8", errors="replace").read().splitlines()[-12:]:
            print(" ", ln)


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "status":
        status()
    elif args[0] == "auto":
        for p, n in REPOS:
            try:
                sync(p, n)
            except Exception as e:
                log("%s: auto error %s: %s" % (n, type(e).__name__, e))
    elif args[0] == "now":
        for p, n in REPOS:
            sync(p, n, force=True)
        status()
    else:
        print("usage: git_backup.py [status|auto|now]")
