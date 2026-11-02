#!/usr/bin/env python3
"""Opus audit of a stratified sample of coded statements (D50).

  sample      draw the sample (seed 20261026) -> v2/audit/sample.json and packets of 25 in v2/audit/packets/
  run         headless Claude Opus auditors (v2/AUDIT.md) until every packet has a valid result file
  check P     validate v2/audit/results/<P>.json
  report      error rates per field (base sample = proportional, representative; oversample strata reported separately)
              with Wilson 95% CIs -> v2/audit/report.json

Strata: base = 300 statements about AI, proportional to final theme; oversamples = computing 60, school 40,
moved in the theme review 60, not about AI 30, UNCOVERED 20 (drawn from units not already sampled).
"""
import argparse
import json
import math
import os
import random
import subprocess
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "v2"
AU = V2 / "audit"
PK, RS = AU / "packets", AU / "results"
FIELDS = ["policy", "actor", "phase", "modality", "unit_stance", "about_ai", "binding", "final_type"]
sys.path.insert(0, str(V2 / "tools"))


def all_units():
    import export_xlsx as ex
    fa = json.loads((V2 / "theme_review" / "final_assignments.json").read_text())
    v3 = {t["id"]: t for t in json.loads((V2 / "policy_types_v3.json").read_text())["types"]}
    out = {}
    for p in sorted((V2 / "inst").glob("*.json")):
        data = json.loads(p.read_text())
        for d in data.get("documents", []):
            tf, src = ex._source(data["slug"], d["id"])
            raw = src[0]
            for i, u in enumerate(d.get("units", []), 1):
                uid = f"{data['slug']}|{d['id']}-u{i:02d}"
                r = fa.get(uid)
                a, b = ex._find(u.get("anchor"), src)
                if not r or a == -1:
                    continue
                out[uid] = {"uid": uid, "university": data["slug"], "layer": d.get("layer"), "doc_title": d.get("title"),
                            "passage": ex._sentence(raw, a, b, u.get("frag_start"), u.get("frag_end"), src),
                            "context": raw[max(0, a - 700): b + 700],
                            "policy": u.get("policy") or "", "actor": u.get("actor"), "phase": u.get("phase"), "modality": u.get("modality"),
                            "unit_stance": u.get("unit_stance"), "about_ai": r["about_ai"], "binding": r["binding"],
                            "final_type": f"{r['type']}: {v3.get(r['type'], {}).get('name', 'UNCOVERED')}",
                            "_theme": v3.get(r["type"], {}).get("theme_v3"), "_via": r["via"]}
    return out


def sample():
    U = all_units()
    rnd = random.Random(20261026)
    chosen = {}

    def draw(pool, n, stratum):
        pool = [u for u in pool if u not in chosen]
        rnd.shuffle(pool)
        for uid in sorted(pool[:n]):
            chosen[uid] = stratum

    ai = [uid for uid, u in U.items() if u["about_ai"] == "yes"]
    by_theme = defaultdict(list)
    for uid in sorted(ai):
        by_theme[U[uid]["_theme"]].append(uid)
    for th, us in sorted(by_theme.items(), key=lambda x: str(x[0])):  # proportional allocation, base n = 300
        draw(us, round(300 * len(us) / len(ai)), "base")
    draw(sorted(uid for uid, u in U.items() if u["layer"] == "computing"), 60, "computing")
    draw(sorted(uid for uid, u in U.items() if u["layer"] == "school"), 40, "school")
    draw(sorted(uid for uid, u in U.items() if u["_via"] != "reviewer keep"), 60, "moved")
    draw(sorted(uid for uid, u in U.items() if u["about_ai"] == "no"), 30, "not-about-ai")
    draw(sorted(uid for uid, u in U.items() if u["final_type"].startswith("UNCOVERED")), 20, "uncovered")
    PK.mkdir(parents=True, exist_ok=True)
    RS.mkdir(parents=True, exist_ok=True)
    (AU / "sample.json").write_text(json.dumps({"seed": 20261026, "strata": chosen, "population": len(U), "about_ai_population": len(ai)}, indent=0))
    ids = sorted(chosen, key=lambda x: (chosen[x], x))
    for k in range(0, len(ids), 25):
        name = f"A{k // 25 + 1:02d}"
        (PK / f"{name}.json").write_text(json.dumps({"packet": name, "units": [{kk: v for kk, v in U[x].items() if not kk.startswith("_")}
                                                                                  for x in ids[k:k + 25]]}, indent=0, ensure_ascii=False))
    print(f"sampled {len(chosen)} units: {dict(Counter(chosen.values()))}; {math.ceil(len(ids) / 25)} packets")


def check(name):
    tp = RS / f"{name}.json"
    if not tp.exists():
        return ["no result file"]
    try:
        t = json.loads(tp.read_text())
    except Exception as e:  # noqa: BLE001
        return [f"not valid JSON: {e}"]
    want = {u["uid"] for u in json.loads((PK / f"{name}.json").read_text())["units"]}
    errs, seen = [], set()
    for u in t.get("units", []):
        uid = u.get("uid")
        if uid not in want or uid in seen:
            errs.append(f"unknown or duplicate uid {uid}")
            continue
        seen.add(uid)
        fs = u.get("fields", {})
        for f in FIELDS:
            v = fs.get(f, {})
            if v.get("verdict") not in ("ok", "wrong"):
                errs.append(f"{uid}: {f} verdict must be ok or wrong")
            elif v["verdict"] == "wrong" and not str(v.get("correct") or "").strip():
                errs.append(f"{uid}: {f} is wrong but has no correct value")
        bad = any(fs.get(f, {}).get("verdict") == "wrong" for f in FIELDS)
        if u.get("unit_ok") != ("no" if bad else "yes"):
            errs.append(f"{uid}: unit_ok must be {'no' if bad else 'yes'}")
        if bad and not (u.get("why") or "").strip():
            errs.append(f"{uid}: why required when a field is wrong")
    errs += [f"missing uid {x}" for x in sorted(want - seen)]
    return errs


def work(names):
    d = PK.parent.name  # audit (first sample) or audit2 (fresh sample, D57)
    prompt = ("You are the AUDITOR. Read v2/AUDIT.md and follow it for each of these packets, in order: " + ", ".join(names)
              + f". For each, read v2/{d}/packets/<packet>.json, write v2/{d}/results/<packet>.json, and run "
              f"python3 v2/tools/audit.py check <packet> --dir {d} until it prints OK.")
    env = {**os.environ, "CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS": "0"}
    for attempt in range(3):
        log = ROOT / "logs" / "v2" / f"audit_{names[0]}_{int(time.time())}.json"
        with open(log, "w") as out, open(ROOT / "logs" / "v2" / f"audit_{names[0]}.err", "a") as err:
            subprocess.run(["claude", "-p", prompt, "--model", "opus", "--permission-mode", "acceptEdits", "--allowedTools",
                            "Read", "Write", "Edit", "Bash(python3:*)", "--output-format", "json"],
                           cwd=ROOT, env=env, stdin=subprocess.DEVNULL, stdout=out, stderr=err)
        if all(not check(n) for n in names):
            break
        time.sleep(30 * (attempt + 1))
    st = {n: not check(n) for n in names}
    print(time.strftime("%H:%M"), st, flush=True)
    return st


def wilson(k, n):
    if not n:
        return (None, None)
    z, p = 1.96, k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (round(c - h, 3), round(c + h, 3))


def report():
    strata = json.loads((AU / "sample.json").read_text())["strata"]
    res = {}
    for tp in RS.glob("*.json"):
        if not check(tp.stem):
            for u in json.loads(tp.read_text())["units"]:
                res[u["uid"]] = u
    out = {}
    for st in ["base"] + sorted(set(strata.values()) - {"base"}):
        us = [res[x] for x, s in strata.items() if s == st and x in res]
        row = {"n": len(us)}
        for f in FIELDS + ["unit"]:
            k = sum(1 for u in us if (u["unit_ok"] == "no" if f == "unit" else u["fields"][f]["verdict"] == "wrong"))
            row[f] = {"wrong": k, "rate": round(k / len(us), 3) if us else None, "ci95": wilson(k, len(us))}
        out[st] = row
    (AU / "report.json").write_text(json.dumps(out, indent=1))
    for st, row in out.items():
        print(st, row["n"], " ".join(f"{f}={row[f]['rate']}" for f in FIELDS + ["unit"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["sample", "run", "check", "report"])
    ap.add_argument("packet", nargs="?")
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--chunk", type=int, default=2)
    ap.add_argument("--dir", default="audit", help="audit (first sample) or audit2 (fresh sample)")
    a = ap.parse_args()
    global PK, RS
    PK, RS = V2 / a.dir / "packets", V2 / a.dir / "results"
    if a.cmd == "sample":
        sample()
    elif a.cmd == "check":
        e = check(a.packet)
        print("OK" if not e else "\n".join(e[:40]))
        sys.exit(1 if e else 0)
    elif a.cmd == "report":
        report()
    else:
        todo = sorted(p.stem for p in PK.glob("*.json") if check(p.stem))
        chunks = [todo[i:i + a.chunk] for i in range(0, len(todo), a.chunk)]
        print(f"{len(todo)} audit packets in {len(chunks)} chunks", flush=True)
        with ThreadPoolExecutor(a.workers) as pool:
            r = list(pool.map(work, chunks))
        print(f"finished: {sum(v for x in r for v in x.values())}/{len(todo)}", flush=True)


if __name__ == "__main__":
    main()
