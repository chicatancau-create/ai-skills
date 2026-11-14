"""Phase D: make cc-switch agree with the "only two skills on" policy.

- register headroom + skill-router in the skills table (directory = the junction
  already created under .cc-switch\\skills), enabled for EVERY agent column
- set every other skill row's enabled_* to 0

Backs up cc-switch.db first.  Dry run by default; --apply to execute.
"""
import os, sys, sqlite3, shutil, time, json

APPLY = "--apply" in sys.argv
DB = r"C:\Users\Admin\.cc-switch\cc-switch.db"
BACKUP = r"G:\AIrenwu\03_备份\_backup"
STAMP = time.strftime("%Y%m%d-%H%M%S")
ALWAYS = ["headroom", "skill-router"]
SKILLS_DIR = r"C:\Users\Admin\.cc-switch\skills"

log = []
def say(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); log.append(s)

if not os.path.isfile(DB):
    say("DB not found:", DB); sys.exit(1)

# work on a copy for inspection, then apply to the real DB in one short transaction
work = r"G:\AIrenwu\05_取证扫描\_scan\ccswitch_work.db"
shutil.copy2(DB, work)
con = sqlite3.connect(work)
con.row_factory = sqlite3.Row
cur = con.cursor()

cols = [r["name"] for r in cur.execute("PRAGMA table_info(skills)")]
say("skills columns:", ", ".join(cols))
en_cols = [c for c in cols if c.startswith("enabled_")]
say(f"\n{len(en_cols)} agent switch columns:", ", ".join(en_cols))

rows = [dict(r) for r in cur.execute("SELECT * FROM skills")]
say(f"\nexisting {len(rows)} skill rows:")
for r in rows:
    on = [c for c in en_cols if r.get(c)]
    say(f"  {r['id']:28s} dir={r.get('directory')!r:24s} enabled={on or 'none'}")

# ---- what we want
say("\n=== plan ===")
have = {r["id"] for r in rows}
inserts = []
for name in ALWAYS:
    sid = f"local:{name}"
    p = os.path.join(SKILLS_DIR, name)
    sm = os.path.join(p, "SKILL.md")
    say(f"  {sid}: dir={name} exists={os.path.isdir(p)} SKILL.md={os.path.isfile(sm)}")
    if sid not in have:
        inserts.append(sid)
        say(f"    INSERT {sid} with all {len(en_cols)} switches = 1")
    else:
        say(f"    UPDATE {sid} set all {len(en_cols)} switches = 1")
for r in rows:
    if r["id"] in [f"local:{n}" for n in ALWAYS]:
        continue
    if any(r.get(c) for c in en_cols):
        say(f"    UPDATE {r['id']} set all switches = 0")
    else:
        say(f"    (already all-off) {r['id']}")
con.close()

if not APPLY:
    say("\n=== DRY RUN ===")
    with open(r"G:\AIrenwu\05_取证扫描\_scan\phaseD_plan.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(log))
    sys.exit(0)

# ---- backup then apply
os.makedirs(BACKUP, exist_ok=True)
bak = os.path.join(BACKUP, f"cc-switch-db-{STAMP}.db")
shutil.copy2(DB, bak)
say(f"\nBACKUP {bak} ({os.path.getsize(bak)} bytes)")

con = sqlite3.connect(DB, timeout=30)
con.row_factory = sqlite3.Row
cur = con.cursor()
now = int(time.time() * 1000)
try:
    cur.execute("BEGIN IMMEDIATE")
    for name in ALWAYS:
        sid = f"local:{name}"
        sm = os.path.join(SKILLS_DIR, name, "SKILL.md")
        desc = ""
        if os.path.isfile(sm):
            import re
            txt = open(sm, "r", encoding="utf-8", errors="replace").read()
            m = re.search(r"^description:\s*(.+)$", txt, re.M)
            if m: desc = m.group(1).strip()[:500]
        vals = {c: 1 for c in en_cols}
        exists = cur.execute("SELECT 1 FROM skills WHERE id=?", (sid,)).fetchone()
        if exists:
            sets = ", ".join(f"{c}=?" for c in en_cols) + ", updated_at=?"
            cur.execute(f"UPDATE skills SET {sets} WHERE id=?",
                        [vals[c] for c in en_cols] + [now, sid])
            say(f"  UPDATED {sid}")
        else:
            fields = ["id", "name", "description", "directory", "installed_at", "updated_at"] + en_cols
            data = [sid, name, desc, name, now, now] + [1] * len(en_cols)
            ph = ", ".join("?" for _ in fields)
            cur.execute(f"INSERT INTO skills ({', '.join(fields)}) VALUES ({ph})", data)
            say(f"  INSERTED {sid}")
    off = ", ".join(f"{c}=0" for c in en_cols)
    ids = [f"local:{n}" for n in ALWAYS]
    q = f"UPDATE skills SET {off}, updated_at=? WHERE id NOT IN ({', '.join('?' for _ in ids)})"
    cur.execute(q, [now] + ids)
    say(f"  DISABLED {cur.rowcount} other skill row(s)")
    con.commit()
    say("  COMMIT ok")
except Exception as e:
    con.rollback()
    say("  ROLLBACK:", repr(e))
    raise
finally:
    con.close()

# ---- verify from a fresh copy
shutil.copy2(DB, work)
con = sqlite3.connect(work); con.row_factory = sqlite3.Row
say("\n=== verify ===")
for r in con.execute("SELECT * FROM skills ORDER BY id"):
    d = dict(r)
    on = [c.replace("enabled_", "") for c in en_cols if d.get(c)]
    say(f"  {d['id']:28s} -> {len(on)} agent(s) on: {','.join(on) if on else '(none)'}")
con.close()
with open(r"G:\AIrenwu\05_取证扫描\_scan\phaseD_plan.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(log))
say("\n=== APPLIED ===")
