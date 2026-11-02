#!/usr/bin/env python3
"""Code course statements with the course codebook (D49): coder A on all, coder B on a 25% random sample (seed 20261026).

  packets   -> v2/course_code/assign_packets/{A,B}_NN.json (150 statements each)
  run       headless Sonnet coders (v2/COURSE_ASSIGN.md)
  check P   validate a result
  alpha     Krippendorff's alpha (nominal) A vs B on the sample, and write v2/course_code/course_assignments.json
"""
import argparse
import json
import os
import random
import subprocess
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "v2"
CC = V2 / "course_code"
AP, AR = CC / "assign_packets", CC / "assign_results"
sys.path.insert(0, str(V2 / "tools"))


def statements():
    pk = {p["pid"]: p for f in (CC / "packets").glob("*.json") for p in json.loads(f.read_text())["passages"]}
    out = []
    for f in sorted((CC / "results").glob("*.json")):
        for p in json.loads(f.read_text())["passages"]:
            for k, s in enumerate(p["statements"]):
                out.append({"sid": f"{p['pid']}#{k}", "slot": pk[p["pid"]]["slot"], "anchor": s["anchor"], "label": s["label"],
                            "passage": pk[p["pid"]]["text"][:2500]})
    return out


def packets():
    AP.mkdir(parents=True, exist_ok=True)
    AR.mkdir(parents=True, exist_ok=True)
    # incremental: statements already in a packet keep their packets and their coder-B sample; only new ones are packed,
    # coder A on all of them and coder B on a 25% sample of them, numbered after the existing packets
    have = {s["sid"] for f in AP.glob("A_*.json") for s in json.loads(f.read_text())["statements"]}
    S = [s for s in statements() if s["sid"] not in have]
    if not S:
        return print("no new statements")
    rnd = random.Random(20261026)
    samp = sorted(rnd.sample(range(len(S)), round(0.25 * len(S))))
    for who, idx in (("A", range(len(S))), ("B", samp)):
        xs = [S[i] for i in idx]
        start = len(list(AP.glob(f"{who}_*.json")))
        for k in range(0, len(xs), 150):
            name = f"{who}_{start + k // 150 + 1:02d}"
            (AP / f"{name}.json").write_text(json.dumps({"packet": name, "coder": who, "statements": xs[k:k + 150]}, indent=0, ensure_ascii=False))
    print(f"{len(S)} statements; coder A all, coder B {len(samp)}")


def check(name):
    tp = AR / f"{name}.json"
    if not tp.exists():
        return ["no result file"]
    try:
        t = json.loads(tp.read_text())
    except Exception as e:  # noqa: BLE001
        return [f"not valid JSON: {e}"]
    want = {s["sid"] for s in json.loads((AP / f"{name}.json").read_text())["statements"]}
    ids = {t["id"] for t in json.loads((V2 / "course_codebook.json").read_text())["types"]}
    errs, seen = [], set()
    for s in t.get("statements", []):
        sid, ty = s.get("sid"), s.get("type") or ""
        if sid not in want or sid in seen:
            errs.append(f"unknown or duplicate sid {sid}")
            continue
        seen.add(sid)
        if not (ty in ids or (ty.startswith("OTHER: ") and len(ty) > 8)):
            errs.append(f"{sid}: type must be a CT id or 'OTHER: <label>'")
        if ty.startswith("OTHER") and not (s.get("note") or "").strip():
            errs.append(f"{sid}: note required for OTHER")
    errs += [f"missing sid {x}" for x in sorted(want - seen)]
    return errs


def work(names):
    prompt = ("You are the COURSE CODER. Read v2/COURSE_ASSIGN.md and v2/course_codebook.json, then code each of these packets, in order: "
              + ", ".join(names) + ". For each, read v2/course_code/assign_packets/<packet>.json, write v2/course_code/assign_results/<packet>.json, "
              "and run python3 v2/tools/course_assign.py check <packet> until it prints OK.")
    env = {**os.environ, "CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS": "0"}
    for attempt in range(3):
        with open(ROOT / "logs" / "v2" / f"cassign_{names[0]}_{int(time.time())}.json", "w") as out, open(ROOT / "logs" / "v2" / f"cassign_{names[0]}.err", "a") as err:
            subprocess.run(["claude", "-p", prompt, "--model", "sonnet", "--permission-mode", "acceptEdits", "--allowedTools",
                            "Read(v2/COURSE_ASSIGN.md)", "Read(v2/course_codebook.json)", "Read(v2/course_code/**)", "Write(v2/course_code/assign_results/**)",
                            "Edit(v2/course_code/assign_results/**)", "Bash(python3 v2/tools/course_assign.py:*)", "--output-format", "json"],
                           cwd=ROOT, env=env, stdin=subprocess.DEVNULL, stdout=out, stderr=err)
        if all(not check(n) for n in names):
            break
        time.sleep(30 * (attempt + 1))
    st = {n: not check(n) for n in names}
    print(time.strftime("%H:%M"), st, flush=True)
    return st


def alpha():
    from agreement_alpha import alpha as kalpha
    res = {"A": {}, "B": {}}
    for f in AR.glob("*.json"):
        if not check(f.stem):
            t = json.loads(f.read_text())
            res[t.get("coder") or f.stem[0]].update({s["sid"]: s for s in t["statements"]})
    pairs = [(res["A"][k]["type"], res["B"][k]["type"]) for k in res["B"] if k in res["A"]]
    a = kalpha(pairs)
    agree = sum(x == y for x, y in pairs) / len(pairs) if pairs else 0
    S = {s["sid"]: s for s in statements()}
    out = {k: {"type": v["type"], "note": v.get("note", ""), "slot": S[k]["slot"], "second_coder": res["B"].get(k, {}).get("type")} for k, v in res["A"].items()}
    (CC / "course_assignments.json").write_text(json.dumps({"alpha_type": a, "percent_agreement": agree, "pairs": len(pairs), "statements": out}, indent=0, ensure_ascii=False))
    print(f"coder A {len(res['A'])} statements; B {len(res['B'])}; pairs {len(pairs)}; alpha {a:.3f}; agreement {agree:.3f}")
    print(Counter(v["type"] if not v["type"].startswith("OTHER") else "OTHER" for v in out.values()).most_common(55))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["packets", "run", "check", "alpha"])
    ap.add_argument("packet", nargs="?")
    ap.add_argument("--workers", type=int, default=5)
    a = ap.parse_args()
    if a.cmd == "packets":
        packets()
    elif a.cmd == "check":
        e = check(a.packet)
        print("OK" if not e else "\n".join(e[:40]))
        sys.exit(1 if e else 0)
    elif a.cmd == "alpha":
        alpha()
    else:
        todo = sorted(p.stem for p in AP.glob("*.json") if check(p.stem))
        with ThreadPoolExecutor(a.workers) as pool:
            r = list(pool.map(work, [[n] for n in todo]))
        print(f"finished: {sum(v for x in r for v in x.values())}/{len(todo)}", flush=True)


if __name__ == "__main__":
    main()
