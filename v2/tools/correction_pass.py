#!/usr/bin/env python3
"""Targeted correction pass after the Opus audit (D52).

The audit found two systematic errors: (1) sentences inside sample syllabus statements or quoted from other
institutions tagged binding=rule instead of template; (2) generic honor-code text in school and computing documents
tagged about_ai=yes. This pass re-judges binding and about_ai, with the surrounding text, for
  (a) every rule-tagged statement in a document that has at least one template-tagged statement, and
  (b) every school- and computing-layer statement.

  packets   -> v2/correction/packets/K_NN.json (200 units each)
  run       headless Sonnet reviewers (v2/CORRECTION.md)
  check P   validate v2/correction/results/<P>.json
  apply     write the corrected values into v2/theme_review/final_assignments.json (keeping the old values and the
            reason) and score the result against the Opus audit verdicts on sampled units
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
CO = V2 / "correction"
PK, RS = CO / "packets", CO / "results"
FA = V2 / "theme_review" / "final_assignments.json"
sys.path.insert(0, str(V2 / "tools"))


def packets():
    import audit
    U = audit.all_units()
    fa = json.loads(FA.read_text())
    bydoc = defaultdict(list)
    for uid, r in fa.items():
        bydoc[uid.rsplit("-u", 1)[0]].append(uid)
    tdocs = {d for d, us in bydoc.items() if any(fa[u]["binding"] == "template" for u in us)}
    target = {}
    for uid, u in U.items():
        why = []
        if fa[uid]["binding"] == "rule" and uid.rsplit("-u", 1)[0] in tdocs:
            why.append("binding")
        if u["layer"] in ("school", "computing"):
            why.append("about_ai")
        if why:
            target[uid] = why
    PK.mkdir(parents=True, exist_ok=True)
    RS.mkdir(parents=True, exist_ok=True)
    ids = sorted(target)
    for k in range(0, len(ids), 200):
        name = f"K{k // 200 + 1:02d}"
        (PK / f"{name}.json").write_text(json.dumps({"packet": name, "units": [
            {"uid": x, "layer": U[x]["layer"], "doc_title": U[x]["doc_title"], "passage": U[x]["passage"], "context": U[x]["context"],
             "binding": fa[x]["binding"], "about_ai": fa[x]["about_ai"], "check": target[x]} for x in ids[k:k + 200]]}, indent=0, ensure_ascii=False))
    print(f"{len(ids)} units in {(len(ids) + 199) // 200} packets; checks: {dict(Counter(c for v in target.values() for c in v))}")


def check(name):
    tp = RS / f"{name}.json"
    if not tp.exists():
        return ["no result file"]
    try:
        t = json.loads(tp.read_text())
    except Exception as e:  # noqa: BLE001
        return [f"not valid JSON: {e}"]
    pk = {u["uid"]: u for u in json.loads((PK / f"{name}.json").read_text())["units"]}
    errs, seen = [], set()
    for u in t.get("units", []):
        uid = u.get("uid")
        if uid not in pk or uid in seen:
            errs.append(f"unknown or duplicate uid {uid}")
            continue
        seen.add(uid)
        if u.get("binding") not in ("rule", "template", "recommendation", "description"):
            errs.append(f"{uid}: binding must be rule, template, recommendation or description")
        if u.get("about_ai") not in ("yes", "no"):
            errs.append(f"{uid}: about_ai must be yes or no")
        changed = u.get("binding") != pk[uid]["binding"] or u.get("about_ai") != pk[uid]["about_ai"]
        if changed and not (u.get("note") or "").strip():
            errs.append(f"{uid}: note required when a value changes")
    errs += [f"missing uid {x}" for x in sorted(set(pk) - seen)]
    return errs


def work(names):
    prompt = ("You are the CORRECTION REVIEWER. Read v2/CORRECTION.md and follow it for each of these packets, in order: " + ", ".join(names)
              + ". For each, read v2/correction/packets/<packet>.json, write v2/correction/results/<packet>.json, and run "
              "python3 v2/tools/correction_pass.py check <packet> until it prints OK.")
    env = {**os.environ, "CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS": "0"}
    for attempt in range(3):
        log = ROOT / "logs" / "v2" / f"correction_{names[0]}_{int(time.time())}.json"
        with open(log, "w") as out, open(ROOT / "logs" / "v2" / f"correction_{names[0]}.err", "a") as err:
            subprocess.run(["claude", "-p", prompt, "--model", "sonnet", "--permission-mode", "acceptEdits", "--allowedTools",
                            "Read", "Write", "Edit", "Bash(python3:*)", "--output-format", "json"],
                           cwd=ROOT, env=env, stdin=subprocess.DEVNULL, stdout=out, stderr=err)
        if all(not check(n) for n in names):
            break
        time.sleep(30 * (attempt + 1))
    st = {n: not check(n) for n in names}
    print(time.strftime("%H:%M"), st, flush=True)
    return st


def apply():
    fa = json.loads(FA.read_text())
    ch = Counter()
    for tp in sorted(RS.glob("*.json")):
        if check(tp.stem):
            print("WARNING: invalid", tp.stem)
            continue
        for u in json.loads(tp.read_text())["units"]:
            r = fa[u["uid"]]
            for f in ("binding", "about_ai"):
                old = r.get(f + "_before_correction", r[f])
                if u[f] != old:
                    r[f + "_before_correction"] = old
                    r[f] = u[f]
                    r["correction_note"] = u.get("note", "")
                    ch[(f, old, u[f])] += 1
    FA.write_text(json.dumps(fa, indent=0, ensure_ascii=False))
    print("changes:", dict(ch.most_common()))
    # score against the Opus audit on sampled units that were in this pass
    R = {}
    for f in (V2 / "audit" / "results").glob("*.json"):
        for u in json.loads(f.read_text())["units"]:
            R[u["uid"]] = u
    P = {}
    for f in (V2 / "audit" / "packets").glob("*.json"):
        for u in json.loads(f.read_text())["units"]:
            P[u["uid"]] = u
    inpass = {u["uid"] for p in PK.glob("*.json") for u in json.loads(p.read_text())["units"]}
    for f in ("binding", "about_ai"):
        n = before = after = 0
        for uid, r in R.items():
            if uid not in inpass:
                continue
            n += 1
            opus = r["fields"][f]["correct"] if r["fields"][f]["verdict"] == "wrong" else P[uid][f]
            before += P[uid][f] != opus
            after += fa[uid][f] != opus
        print(f"{f}: on {n} audited units in the pass, disagreement with Opus {before} before -> {after} after")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["packets", "run", "check", "apply"])
    ap.add_argument("packet", nargs="?")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--chunk", type=int, default=2)
    a = ap.parse_args()
    if a.cmd == "packets":
        packets()
    elif a.cmd == "check":
        e = check(a.packet)
        print("OK" if not e else "\n".join(e[:40]))
        sys.exit(1 if e else 0)
    elif a.cmd == "apply":
        apply()
    else:
        todo = sorted(p.stem for p in PK.glob("*.json") if check(p.stem))
        chunks = [todo[i:i + a.chunk] for i in range(0, len(todo), a.chunk)]
        print(f"{len(todo)} packets in {len(chunks)} chunks", flush=True)
        with ThreadPoolExecutor(a.workers) as pool:
            r = list(pool.map(work, chunks))
        print(f"finished: {sum(v for x in r for v in x.values())}/{len(todo)}", flush=True)


if __name__ == "__main__":
    main()
