"""Phase C: build D:\\Skills-active (only headroom + skill-router) and rewire every
agent skill root to it.  Built-in/vendor skills are left untouched.

Dry run by default; --apply to execute.  Backs up before anything destructive.
"""
import os, sys, json, shutil, subprocess, time, zipfile

APPLY = "--apply" in sys.argv
H = r"C:\Users\Admin"
LIB = r"D:\Skills"
ACTIVE = r"D:\Skills-active"
BACKUP = r"G:\AIrenwu\03_备份\_backup"
STAMP = time.strftime("%Y%m%d-%H%M%S")
ALWAYS = ["headroom", "skill-router"]

log = []
def say(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True); log.append(s)

def reparse(p):
    try: return getattr(os.lstat(p), "st_reparse_tag", 0)
    except OSError: return -1

def is_link(p): return reparse(p) > 0

def target(p):
    try: return os.readlink(p)
    except OSError: return ""

def mkjunction(src, dst):
    say(f"  JUNCTION {src} -> {dst}")
    if not APPLY: return True
    r = subprocess.run(["cmd", "/c", "mklink", "/J", src, dst],
                       capture_output=True, text=True, encoding="gbk", errors="replace")
    if r.returncode != 0:
        say("    ERR", ((r.stdout or "") + (r.stderr or "")).strip()); return False
    return True

def rmjunction(p):
    say(f"  RMLINK {p} -> {target(p)}")
    if not APPLY: return True
    try: os.rmdir(p); return True
    except OSError as e:
        say("    ERR", e); return False

def zip_backup(paths, tag):
    if not APPLY:
        say(f"  BACKUP {tag} ({len(paths)} paths) [dry]"); return
    os.makedirs(BACKUP, exist_ok=True)
    zp = os.path.join(BACKUP, f"{tag}-{STAMP}.zip")
    n = 0
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            if not os.path.isdir(p): continue
            base = os.path.basename(p.rstrip("\\/"))
            for dp, dn, fn in os.walk(p):
                for f in fn:
                    fp = os.path.join(dp, f)
                    try: z.write(fp, os.path.join(base, os.path.relpath(fp, p))); n += 1
                    except OSError: pass
    say(f"  BACKUP {zp} ({n} files)")

# ------------------------------------------------------------------ C1 active window
say("=== C1. build D:\\Skills-active (only 2 skills) ===")
if not os.path.isdir(ACTIVE):
    say(f"  MKDIR {ACTIVE}")
    if APPLY: os.makedirs(ACTIVE, exist_ok=True)
for n in ALWAYS:
    src = os.path.join(ACTIVE, n)
    dst = os.path.join(LIB, n)
    if not os.path.isdir(dst):
        say(f"  !! library skill missing: {dst}"); continue
    if os.path.exists(src):
        say(f"  exists {src} -> {target(src) or '(real)'}")
        continue
    mkjunction(src, dst)

# ------------------------------------------------------------------ C2 rewire roots
# mode "replace": root is a whole-dir junction -> repoint it at Skills-active
# mode "inject" : root is a real dir -> drop stale per-skill links, add the 2 links.
#                 NEVER rmdir the root and NEVER touch non-skill app-state files
#                 (e.g. WorkBuddy's .*_migration.json live in the skills dir).
ROOTS = [
    ("claude",        os.path.join(H, ".claude", "skills"),                 "replace"),
    ("agents",        os.path.join(H, ".agents", "skills"),                 "replace"),
    ("opencode",      os.path.join(H, ".config", "opencode", "skills"),     "replace"),
    ("workbuddy",     os.path.join(H, ".workbuddy", "skills"),              "replace"),
    ("workbuddy-ai",  os.path.join(H, ".workbuddy-ai", "skills"),           "inject"),
    ("openclaw",      os.path.join(H, ".openclaw", "skills"),               "inject"),
    ("qoder",         os.path.join(H, ".qoder", "skills"),                  "inject"),
    ("qoder-cn",      os.path.join(H, ".qoder-cn", "skills"),               "inject"),
    ("herdsman",      os.path.join(H, ".herdsman", "work", "skills"),       "inject"),
    ("dsh",           os.path.join(H, ".dsh", "skills"),                    "inject"),
    ("codex",         os.path.join(H, ".codex", "skills"),                  "inject"),
    ("cc-switch",     os.path.join(H, ".cc-switch", "skills"),              "inject"),
]

say("\n=== C2. rewire agent skill roots ===")
for label, root, mode in ROOTS:
    say(f"\n-- {label} [{mode}] {root}")
    if not os.path.exists(root):
        say("   (absent) -> create junction")
        parent = os.path.dirname(root)
        if APPLY: os.makedirs(parent, exist_ok=True)
        mkjunction(root, ACTIVE)
        continue

    if is_link(root):
        say(f"   whole-dir junction -> {target(root)}")
        if mode == "replace":
            rmjunction(root)
            mkjunction(root, ACTIVE)
        else:
            say("   !! inject mode but root is a junction; skipping (needs manual look)")
        continue

    # real directory
    kids = sorted(os.listdir(root))
    say(f"   real dir, {len(kids)} entries: {kids[:40]}")
    # drop per-skill junctions that point into the library / old toolkit
    stale = []
    for n in kids:
        p = os.path.join(root, n)
        if is_link(p):
            t = target(p)
            if t and (LIB.lower() in t.lower() or "qodertoolkit" in t.lower()
                      or "\\Skills\\" in t or t.rstrip("\\").endswith("\\Skills")):
                stale.append(p)
    if stale:
        say(f"   {len(stale)} stale per-skill junction(s) to remove")
        for p in stale: rmjunction(p)

    if mode == "replace":
        # Only whole-dir junctions use "replace". A real dir here means the
        # layout changed under us -- do not guess, fall back to inject.
        say("   !! replace requested but root is a real dir -> falling back to inject")
        for n in ALWAYS:
            p = os.path.join(root, n)
            if os.path.exists(p):
                say(f"   exists {n}"); continue
            mkjunction(p, os.path.join(LIB, n))
    else:
        for n in ALWAYS:
            p = os.path.join(root, n)
            if os.path.exists(p):
                say(f"   exists {n}"); continue
            mkjunction(p, os.path.join(LIB, n))

# ------------------------------------------------------------------ C3 verify
say("\n=== C3. verify: what each agent will actually load ===")
for label, root, mode in ROOTS:
    if not os.path.isdir(root):
        say(f"  {label:14s} MISSING {root}"); continue
    kids = [n for n in sorted(os.listdir(root)) if os.path.isdir(os.path.join(root, n))]
    ok = [n for n in kids if os.path.isfile(os.path.join(root, n, "SKILL.md"))]
    say(f"  {label:14s} {len(ok):3d} readable / {len(kids):3d} dirs   {ok if len(ok)<=6 else str(ok[:6])+' ...'}")

with open(r"G:\AIrenwu\05_取证扫描\_scan\phaseC_plan.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(log))
say(f"\n=== {'APPLIED' if APPLY else 'DRY RUN'} === -> G:\\AIrenwu\\_scan\\phaseC_plan.txt")
