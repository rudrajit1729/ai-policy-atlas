#!/usr/bin/env python3
"""Theme review (D34/D37/D38/D45): every coded statement is read once more and tagged by a reviewer agent.

  packets   group every reconciled unit not yet reviewed by its current policy_type into packets of <= SIZE units
            (v2/theme_review/packets/<packet>.json); incremental, so universities coded later get their own packets
  run       keep N headless reviewer sessions busy until every packet has a valid tag file
  check P   validate v2/theme_review/tags/<P>.json against its packet (prints OK or the errors)
  status    packets, valid tag files, units reviewed

The review is a separate layer keyed by uid (<slug>|<unit_id>); the coded files in v2/inst are never edited.
A unit's review is stale if its anchor or policy changed since the packet was built (field h).
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "v2"
TR = V2 / "theme_review"
PK, TG = TR / "packets", TR / "tags"
SIZE = 200
MIN_TYPE = 40  # a type with fewer unreviewed units than this goes into MIXED packets
sys.path.insert(0, str(V2 / "tools"))
import export_xlsx as ex  # noqa: E402  (reuses the deterministic source-passage cutter)

BINDING = {"rule", "template", "recommendation", "description"}


def uh(u):
    return hashlib.sha1(((u.get("anchor") or "") + "|" + (u.get("policy") or "")).encode()).hexdigest()[:10]


def units():
    for p in sorted((V2 / "inst").glob("*.json")):
        data = json.loads(p.read_text())
        for d in data.get("documents", []):
            tf, src = ex._source(data.get("slug"), d["id"])
            for i, u in enumerate(d.get("units", []), 1):
                a, b = ex._find(u.get("anchor"), src)
                if a == -1:
                    continue  # unverified units are not reviewed (they are not in the Policies sheet)
                yield {"uid": f"{data['slug']}|{d['id']}-u{i:02d}", "h": uh(u), "university": data["slug"], "layer": d.get("layer"),
                       "passage": ex._sentence(src[0], a, b, u.get("frag_start"), u.get("frag_end"), src),
                       "policy": u.get("policy") or "", "why": (u.get("why") or "")[:400], "actor": u.get("actor"),
                       "modality": u.get("modality"), "current_type": u.get("policy_type"),
                       "fit_note": u.get("fit_note") or "", "uncovered_note": u.get("uncovered_note") or ""}


def reviewed():
    """uid -> h for every unit in a valid tag file."""
    out = {}
    for t in TG.glob("*.json"):
        if check(t.stem):
            continue
        pk = json.loads((PK / f"{t.stem}.json").read_text())
        out.update({u["uid"]: u["h"] for u in pk["units"]})
    return out


def packets():
    PK.mkdir(parents=True, exist_ok=True)
    TG.mkdir(parents=True, exist_ok=True)
    done = reviewed()
    pending = {u["uid"] for p in PK.glob("*.json") if not (TG / p.name).exists() for u in json.loads(p.read_text())["units"]}
    by = {}
    for u in units():
        if done.get(u["uid"]) == u["h"] or u["uid"] in pending:
            continue
        by.setdefault(u["current_type"] or "UNCOVERED", []).append(u)
    stamp = time.strftime("%m%d%H%M")
    n = 0
    small = sorted((u for t, us in by.items() if len(us) < MIN_TYPE for u in us), key=lambda u: (u["current_type"] or "", u["university"]))
    by = {t: us for t, us in by.items() if len(us) >= MIN_TYPE}
    for k in range(0, len(small), SIZE):  # types with few new units share MIXED packets; each unit carries its own current_type
        name = f"MIXED_{stamp}_{k // SIZE + 1:02d}"
        (PK / f"{name}.json").write_text(json.dumps({"packet": name, "current_type": "MIXED", "units": small[k:k + SIZE]}, indent=0, ensure_ascii=False))
        n += 1
    for t, us in sorted(by.items()):
        us.sort(key=lambda u: (u["layer"] != "computing", u["university"]))
        for k in range(0, len(us), SIZE):
            name = f"{t}_{stamp}_{k // SIZE + 1:02d}"
            (PK / f"{name}.json").write_text(json.dumps({"packet": name, "current_type": t, "units": us[k:k + SIZE]}, indent=0, ensure_ascii=False))
            n += 1
    print(f"wrote {n} packets ({sum(len(v) for v in by.values())} units)")


def check(name):
    errs = []
    tp = TG / f"{name}.json"
    if not tp.exists():
        return ["no tag file"]
    try:
        t = json.loads(tp.read_text())
    except Exception as e:  # noqa: BLE001
        return [f"not valid JSON: {e}"]
    pk = json.loads((PK / f"{name}.json").read_text())
    want = {u["uid"] for u in pk["units"]}
    types = {x["id"] for x in json.loads((V2 / "policy_types.json").read_text())["types"]}
    seen = set()
    for u in t.get("units", []):
        uid = u.get("uid")
        if uid not in want:
            errs.append(f"unknown uid {uid}")
            continue
        if uid in seen:
            errs.append(f"duplicate uid {uid}")
        seen.add(uid)
        if u.get("about_ai") not in ("yes", "no"):
            errs.append(f"{uid}: about_ai must be yes or no")
        if u.get("binding") not in BINDING:
            errs.append(f"{uid}: binding must be one of {sorted(BINDING)}")
        ty = u.get("type") or ""
        if not (ty == "keep" or ty in types or (ty.startswith("NEW: ") and len(ty) > 6)):
            errs.append(f"{uid}: type must be keep, an existing type id, or 'NEW: <label>' (got {ty!r})")
        cur = pk["current_type"] if pk["current_type"] != "MIXED" else next(x["current_type"] for x in pk["units"] if x["uid"] == uid)
        if ty == "keep" and cur in ("UNCOVERED", None):
            errs.append(f"{uid}: an UNCOVERED unit cannot be 'keep'; give an existing type or NEW: <label>")
        if (ty != "keep" or u.get("about_ai") == "no") and not (u.get("note") or "").strip():
            errs.append(f"{uid}: note required when type is not keep or about_ai is no")
    for uid in sorted(want - seen):
        errs.append(f"missing uid {uid}")
    if pk["current_type"] != "MIXED" and t.get("coherence") not in ("coherent", "mostly coherent", "mixed"):
        errs.append("coherence must be coherent, mostly coherent or mixed")
    if pk["current_type"] == "MIXED":
        return errs
    for g in t.get("subgroups", []):
        if not set(g.get("uids", [])) <= want:
            errs.append(f"subgroup {g.get('label')!r} lists uids not in the packet")
    return errs


def work(names):
    prompt = ("You are the THEME REVIEWER. Read v2/THEME_REVIEW.md and follow it for each of these packets, in order: "
              + ", ".join(names) + ". For each, read v2/theme_review/packets/<packet>.json, write v2/theme_review/tags/<packet>.json, "
              "and run python3 v2/tools/theme_review.py check <packet> until it prints OK.")
    env = {**os.environ, "CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS": "0"}
    for attempt in range(3):
        log = ROOT / "logs" / "v2" / f"review_{names[0]}_{int(time.time())}.json"
        with open(log, "w") as out, open(ROOT / "logs" / "v2" / f"review_{names[0]}.err", "a") as err:
            subprocess.run(["claude", "-p", prompt, "--model", MODEL, "--permission-mode", "acceptEdits", "--allowedTools",
                            "Read", "Write", "Edit", "Bash(python3:*)", "--output-format", "json"],
                           cwd=ROOT, env=env, stdin=subprocess.DEVNULL, stdout=out, stderr=err)
        if all(not check(n) for n in names):
            break
        time.sleep(30 * (attempt + 1))
    st = {n: not check(n) for n in names}
    print(time.strftime("%H:%M"), st, flush=True)
    return st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["packets", "run", "check", "status"])
    ap.add_argument("packet", nargs="?")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--chunk", type=int, default=2)
    ap.add_argument("--model", default="sonnet")
    a = ap.parse_args()
    global MODEL
    MODEL = a.model
    (ROOT / "logs" / "v2").mkdir(parents=True, exist_ok=True)
    if a.cmd == "packets":
        packets()
    elif a.cmd == "check":
        e = check(a.packet)
        print("OK" if not e else "\n".join(e[:40]))
        sys.exit(1 if e else 0)
    elif a.cmd == "status":
        ps = sorted(p.stem for p in PK.glob("*.json"))
        ok = [p for p in ps if not check(p)]
        print(f"{len(ok)}/{len(ps)} packets reviewed; {len(reviewed())} units reviewed")
    else:
        todo = sorted(p.stem for p in PK.glob("*.json") if check(p.stem))
        chunks = [todo[i:i + a.chunk] for i in range(0, len(todo), a.chunk)]
        print(f"{len(todo)} packets in {len(chunks)} chunks, {a.workers} workers", flush=True)
        with ThreadPoolExecutor(a.workers) as pool:
            res = list(pool.map(work, chunks))
        print(f"finished: {sum(v for r in res for v in r.values())}/{len(todo)} packets", flush=True)


if __name__ == "__main__":
    main()
