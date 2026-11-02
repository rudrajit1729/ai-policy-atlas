#!/usr/bin/env python3
"""Theme review step 2 (D47): apply Claude's synthesis (v2/theme_review/synthesis.json) to the reviewer tags.

  resolve      step-1 tags + label_map -> v2/theme_review/resolved.json (uid -> type, about_ai, binding, via)
  splitpackets units whose resolved type is in synthesis.splits -> v2/theme_review/split_packets/SPLIT_<type>_NN.json
  run          headless reviewers assign each split unit to one of the listed options (v2/THEME_REVIEW.md, "Split packets")
  check P      validate v2/theme_review/split_tags/<P>.json
  final        resolved + split tags -> v2/theme_review/final_assignments.json and v2/policy_types_v3.json; prints counts

Deterministic except for the reviewer pass. Never edits v2/inst.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "v2"
TR = V2 / "theme_review"
SP, ST = TR / "split_packets", TR / "split_tags"
SIZE = 200


def syn():
    return json.loads((TR / "synthesis.json").read_text())


def v3_types():
    s = syn()
    base = json.loads((V2 / "policy_types.json").read_text())
    out = []
    for t in base["types"]:
        t = dict(t)
        t["name_v2"] = t["name"]
        t["name"] = s["names"].get(t["id"], t["name"])
        if t["id"] in s["retired"]:
            t["retired"] = s["retired"][t["id"]]
        out.append(t)
    for n in s["new_types"]:
        out.append({**n, "theme": None, "added": "2026-10-26 theme review (D47)"})
    return out


def resolve():
    s = syn()
    lm = s["label_map"]
    res = {}
    for tp in sorted((TR / "tags").glob("*.json")):
        t = json.loads(tp.read_text())
        pk = {u["uid"]: u for u in json.loads((TR / "packets" / tp.name).read_text())["units"]}
        for u in t["units"]:
            cur = pk[u["uid"]]["current_type"] or "UNCOVERED"
            ty, via, label = u["type"], "reviewer keep", None
            if ty == "keep":
                ty = cur
            elif ty.startswith("NEW: "):
                label = ty[5:].strip()
                ty = lm.get(label.lower(), "UNCOVERED")
                via = "reviewer NEW label mapped by synthesis" if ty != "UNCOVERED" else "reviewer NEW label (no type yet)"
            else:
                via = "reviewer move"
            res[u["uid"]] = {"coded_type": cur, "type": ty, "about_ai": u["about_ai"], "binding": u["binding"], "via": via,
                             "label": label, "note": u.get("note") or "", "university": pk[u["uid"]]["university"]}
    (TR / "resolved.json").write_text(json.dumps(res, indent=0, ensure_ascii=False))
    print(f"resolved {len(res)} units; via: {dict(Counter(r['via'] for r in res.values()))}")


def splitpackets():
    s = syn()
    res = json.loads((TR / "resolved.json").read_text())
    units = {}
    for tp in (TR / "packets").glob("*.json"):
        for u in json.loads(tp.read_text())["units"]:
            units[u["uid"]] = u
    SP.mkdir(parents=True, exist_ok=True)
    ST.mkdir(parents=True, exist_ok=True)
    types = {t["id"]: t for t in v3_types()}
    n = 0
    for st, spec in s["splits"].items():
        us = sorted((uid for uid, r in res.items() if r["type"] == st), key=lambda x: units[x]["university"])
        opts = [{"id": o, "name": types[o]["name"], "covers": types[o].get("covers", "")} for o in spec["options"] if o != "OTHER"]
        for k in range(0, len(us), SIZE):
            name = f"SPLIT_{st}_{k // SIZE + 1:02d}"
            if (SP / f"{name}.json").exists():
                continue
            (SP / f"{name}.json").write_text(json.dumps({
                "packet": name, "split_type": st, "why": spec["why"], "options": opts, "other_allowed": "OTHER" in spec["options"],
                "units": [{k2: units[uid][k2] for k2 in ("uid", "university", "layer", "passage", "policy", "why")} for uid in us[k:k + SIZE]]},
                indent=0, ensure_ascii=False))
            n += 1
    print(f"wrote {n} split packets")


def check(name):
    errs = []
    tp = ST / f"{name}.json"
    if not tp.exists():
        return ["no tag file"]
    try:
        t = json.loads(tp.read_text())
    except Exception as e:  # noqa: BLE001
        return [f"not valid JSON: {e}"]
    pk = json.loads((SP / f"{name}.json").read_text())
    want = {u["uid"] for u in pk["units"]}
    opts = {o["id"] for o in pk["options"]}
    allt = {x["id"] for x in v3_types() if not x.get("retired")}
    seen = set()
    for u in t.get("units", []):
        uid, ty = u.get("uid"), u.get("type") or ""
        if uid not in want:
            errs.append(f"unknown uid {uid}")
            continue
        if uid in seen:
            errs.append(f"duplicate uid {uid}")
        seen.add(uid)
        ok = ty in opts or (pk["other_allowed"] and (ty in allt or (ty.startswith("NEW: ") and len(ty) > 6)))
        if not ok:
            errs.append(f"{uid}: type {ty!r} is not one of the options" + (" or another existing type / NEW: <label>" if pk["other_allowed"] else ""))
        if ty != pk["split_type"] and not (u.get("note") or "").strip():
            errs.append(f"{uid}: note required when the unit leaves {pk['split_type']}")
    for uid in sorted(want - seen):
        errs.append(f"missing uid {uid}")
    return errs


def work(names):
    prompt = ("You are the THEME REVIEWER. Read v2/THEME_REVIEW.md, section 'Split packets', and follow it for each of these packets, in order: "
              + ", ".join(names) + ". For each, read v2/theme_review/split_packets/<packet>.json, write v2/theme_review/split_tags/<packet>.json, "
              "and run python3 v2/tools/theme_apply.py check <packet> until it prints OK.")
    env = {**os.environ, "CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS": "0"}
    for attempt in range(3):
        log = ROOT / "logs" / "v2" / f"split_{names[0]}_{int(time.time())}.json"
        with open(log, "w") as out, open(ROOT / "logs" / "v2" / f"split_{names[0]}.err", "a") as err:
            subprocess.run(["claude", "-p", prompt, "--model", "sonnet", "--permission-mode", "acceptEdits", "--allowedTools",
                            "Read", "Write", "Edit", "Bash(python3:*)", "--output-format", "json"],
                           cwd=ROOT, env=env, stdin=subprocess.DEVNULL, stdout=out, stderr=err)
        if all(not check(n) for n in names):
            break
        time.sleep(30 * (attempt + 1))
    st = {n: not check(n) for n in names}
    print(time.strftime("%H:%M"), st, flush=True)
    return st


def final():
    s = syn()
    res = json.loads((TR / "resolved.json").read_text())
    lm = s["label_map"]
    for tp in ST.glob("*.json"):
        if check(tp.stem):
            print("WARNING: invalid split tags", tp.stem)
            continue
        for u in json.loads(tp.read_text())["units"]:
            r = res[u["uid"]]
            ty = u["type"]
            if ty.startswith("NEW: "):
                r["label"] = ty[5:].strip()
                ty = lm.get(r["label"].lower(), "UNCOVERED")
            if ty != r["type"]:
                r["via"] = f"split pass from {r['type']}"
                r["note"] = u.get("note") or r["note"]
            r["type"] = ty
    left = [uid for uid, r in res.items() if r["type"] in s["splits"] and r["type"] in s["retired"]]
    if left:
        print(f"WARNING: {len(left)} units still in a retired type (split pass incomplete)")
    (TR / "final_assignments.json").write_text(json.dumps(res, indent=0, ensure_ascii=False))
    types = v3_types()
    cnt, unis = Counter(), defaultdict(set)
    for r in res.values():
        if r["about_ai"] == "yes":
            cnt[r["type"]] += 1
            unis[r["type"]].add(r["university"])
    theme_of = {ty: th["id"] for th in s.get("themes", []) for ty in th["types"]}
    for t in types:
        t["policies"], t["universities"] = cnt.get(t["id"], 0), len(unis.get(t["id"], ()))
        t["theme_v3"] = theme_of.get(t["id"])
    (V2 / "policy_types_v3.json").write_text(json.dumps({"_note": "Theme review result (D46/D47): content-only names; counts are statements about AI.",
                                                         "themes": s.get("themes", []), "types": types}, indent=1, ensure_ascii=False))
    print(f"final: {len(res)} units; about AI {sum(cnt.values())}; UNCOVERED {cnt.get('UNCOVERED', 0)}; "
          f"types in use {sum(1 for t in types if cnt.get(t['id']))}; via {dict(Counter(r['via'] for r in res.values()))}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["resolve", "splitpackets", "run", "check", "final"])
    ap.add_argument("packet", nargs="?")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--chunk", type=int, default=2)
    a = ap.parse_args()
    if a.cmd == "resolve":
        resolve()
    elif a.cmd == "splitpackets":
        splitpackets()
    elif a.cmd == "check":
        e = check(a.packet)
        print("OK" if not e else "\n".join(e[:40]))
        sys.exit(1 if e else 0)
    elif a.cmd == "final":
        final()
    else:
        todo = sorted(p.stem for p in SP.glob("*.json") if check(p.stem))
        chunks = [todo[i:i + a.chunk] for i in range(0, len(todo), a.chunk)]
        print(f"{len(todo)} split packets in {len(chunks)} chunks", flush=True)
        with ThreadPoolExecutor(a.workers) as pool:
            r = list(pool.map(work, chunks))
        print(f"finished: {sum(v for x in r for v in x.values())}/{len(todo)}", flush=True)


if __name__ == "__main__":
    main()
