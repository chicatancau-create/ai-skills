# -*- coding: utf-8 -*-
"""Self-healing shield for the skill library and the default window.

WHY THIS EXISTS (incident 2026-11-15 02:04:06)
---------------------------------------------
D:\\Skills-active holds two junctions into D:\\Skills.  Something deleted the
*contents* of D:\\Skills-active through the Windows shell (the files landed in the
Recycle Bin, which rules out a plain Python rmtree).  The shell FOLLOWED the
junctions and recycled the real targets: D:\\Skills\\headroom\\SKILL.md and all
11 files of D:\\Skills\\skill-router were wiped in a single 0.5s operation.
Every agent lost both default skills at once.

A junction gives one source of truth, but it also gives one source of destruction.
So keep a real mirror OUTSIDE the junction graph and repair from it automatically.

WHAT IT DOES each tick
----------------------
  * library file present and newer than the mirror  -> refresh the mirror
  * library file missing/empty but mirror has it    -> restore it
  * default-window junction missing                 -> recreate it
It never deletes anything, and it never touches a library file that is present
and non-empty (so it cannot clobber an edit in progress).

USAGE
    python skill_shield.py --status
    python skill_shield.py --once
    python skill_shield.py --snapshot     # also write a dated zip backup
"""
import os
import shutil
import subprocess
import sys
import time
import zipfile

LIB = r"D:\Skills"
ACTIVE = r"D:\Skills-active"
MIRROR = r"D:\Skills-mirror"
ZIPDIR = "G:\\AIrenwu\\03_\u5907\u4efd\\_backup\\skill-shield"
PROTECTED = ["headroom", "skill-router"]
STATE = os.path.join(os.environ.get("AI_SHARED_SKILLS_STATE_DIR", r"D:\\AI-Tool-State"),
                     "wire-guard")
LOG = os.path.join(STATE, "shield.log")


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


def files_of(root):
    """relpath -> (size, mtime) for every file under root, not following junctions."""
    out = {}
    if not os.path.isdir(root):
        return out
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns
                  if d != "__pycache__"
                  and not getattr(os.lstat(os.path.join(dp, d)), "st_reparse_tag", 0)]
        for fn in fns:
            if fn.endswith(".pyc"):
                continue
            p = os.path.join(dp, fn)
            try:
                st = os.stat(p)
            except OSError:
                continue
            out[os.path.relpath(p, root)] = (st.st_size, st.st_mtime)
    return out


def tick(verbose=True):
    actions = []
    for name in PROTECTED:
        live = os.path.join(LIB, name)
        mir = os.path.join(MIRROR, name)
        lf, mf = files_of(live), files_of(mir)

        # 1. restore anything the library lost
        for rel, (sz, mt) in mf.items():
            if rel in lf and lf[rel][0] > 0:
                continue
            src, dst = os.path.join(mir, rel), os.path.join(live, rel)
            try:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                actions.append("RESTORED %s\\%s (%dB)" % (name, rel, sz))
            except OSError as e:
                actions.append("RESTORE FAILED %s\\%s: %s" % (name, rel, e))

        # 2. refresh the mirror from anything new in the library
        lf = files_of(live)
        for rel, (sz, mt) in lf.items():
            if sz == 0:
                continue
            if rel in mf and mf[rel][0] == sz and mf[rel][1] >= mt - 1:
                continue
            src, dst = os.path.join(live, rel), os.path.join(mir, rel)
            try:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                actions.append("MIRRORED %s\\%s (%dB)" % (name, rel, sz))
            except OSError as e:
                actions.append("MIRROR FAILED %s\\%s: %s" % (name, rel, e))

    # 3. the default window must always expose both skills
    try:
        os.makedirs(ACTIVE, exist_ok=True)
        for name in PROTECTED:
            link = os.path.join(ACTIVE, name)
            tgt = os.path.join(LIB, name)
            if os.path.exists(link) and os.path.isfile(os.path.join(link, "SKILL.md")):
                continue
            if os.path.exists(link):
                # a real dir or a dangling link: only remove it if it is empty
                try:
                    if os.listdir(link):
                        actions.append("WINDOW %s exists but unreadable and NOT empty -> left alone" % name)
                        continue
                    if getattr(os.lstat(link), "st_reparse_tag", 0):
                        os.rmdir(link)
                    else:
                        os.rmdir(link)
                except OSError as e:
                    actions.append("WINDOW %s cleanup failed: %s" % (name, e))
                    continue
            r = subprocess.run(["cmd", "/c", "mklink", "/J", link, tgt],
                               capture_output=True, text=True, timeout=60,
                               creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            if r.returncode == 0:
                actions.append("WINDOW rebuilt junction %s" % name)
            else:
                actions.append("WINDOW mklink %s failed: %s" % (name, (r.stderr or "").strip()[:100]))
    except OSError as e:
        actions.append("WINDOW check failed: %s" % e)

    if verbose:
        for a in actions:
            log(a)
    return actions


def snapshot():
    os.makedirs(ZIPDIR, exist_ok=True)
    dst = os.path.join(ZIPDIR, "skills-%s.zip" % time.strftime("%Y%m%d-%H%M%S"))
    n = 0
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for name in PROTECTED:
            root = os.path.join(LIB, name)
            for rel in files_of(root):
                z.write(os.path.join(root, rel), os.path.join(name, rel))
                n += 1
    log("SNAPSHOT %s (%d files, %dB)" % (dst, n, os.path.getsize(dst)))
    return dst


def status():
    for name in PROTECTED:
        lf = files_of(os.path.join(LIB, name))
        mf = files_of(os.path.join(MIRROR, name))
        link = os.path.join(ACTIVE, name)
        rp = getattr(os.lstat(link), "st_reparse_tag", 0) if os.path.exists(link) else 0
        print("%-13s library=%2d files  mirror=%2d files  window=%s SKILL.md=%s" % (
            name, len(lf), len(mf),
            ("junction" if rp else ("real" if os.path.exists(link) else "MISSING")),
            os.path.isfile(os.path.join(link, "SKILL.md"))))
    print("mirror root: %s (exists=%s)" % (MIRROR, os.path.isdir(MIRROR)))


def main():
    if "--status" in sys.argv:
        status()
        return
    a = tick()
    if not a:
        print("shield: nothing to do (library, mirror and window all consistent)")
    if "--snapshot" in sys.argv:
        snapshot()


if __name__ == "__main__":
    main()
