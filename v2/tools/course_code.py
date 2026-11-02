#!/usr/bin/env python3
"""Course-layer open coding (D49): packets of verbatim AI passages from v2/exports/course_layer.xlsx, Sonnet coders, checks.

  packets   new passages (not yet in a packet) -> v2/course_code/packets/C_<stamp>_NN.json (20 passages each)
  run       headless coders (v2/COURSE_CODE.md) until every packet has a valid result
  check P   validate v2/course_code/results/<P>.json (every anchor must be an exact, whitespace/quote-folded substring)
  labels    print label frequencies across all valid results (input for the course codebook)
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "v2"
CC = V2 / "course_code"
PK, RS = CC / "packets", CC / "results"
STANCE_P = {"prohibit", "restrict", "permit", "encourage", "require", "mixed", "none"}
STANCE_S = {"prohibit", "restrict", "permit", "encourage", "require", "neutral"}
ACTOR = {"student", "instructor", "ta-staff", "all"}
MODAL = {"must", "must-not", "may", "should", "should-not", "informs"}


def fold(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace(" ", " ")
    return re.sub(r"\s+", " ", s).strip()


def passages():
    wb = openpyxl.load_workbook(V2 / "exports" / "course_layer.xlsx", read_only=True)
    rows = list(wb["AI passages"].iter_rows(values_only=True))
    h = rows[0]
    ix = {k: h.index(k) for k in h}
    txt = [k for k in h if k and k.startswith("ORIGINAL WORDING")][0]
    out, seen = [], Counter()
    for r in rows[1:]:
        if not r[ix[txt]]:
            continue
        pid = f"{r[ix['university_slug']]}|{r[ix['slot']]}|{r[ix['course']]}|{r[ix['term']]}|{r[ix['passage #']]}"
        # a second section of the same course and term repeats the id; it gets a section suffix (2026-11-02)
        seen[pid] += 1
        if seen[pid] > 1:
            pid += f"|s{seen[pid]}"
        out.append({"pid": pid, "university": r[ix["university_slug"]], "slot": r[ix["slot"]], "course": r[ix["course"]],
                    "term": r[ix["term"]], "url": r[ix["syllabus URL"]], "text": r[ix[txt]]})
    return out


def packets():
    PK.mkdir(parents=True, exist_ok=True)
    RS.mkdir(parents=True, exist_ok=True)
    have = {p["pid"] for f in PK.glob("*.json") for p in json.loads(f.read_text())["passages"]}
    new = [p for p in passages() if p["pid"] not in have]
    stamp = time.strftime("%m%d%H%M")
    for k in range(0, len(new), 20):
        name = f"C_{stamp}_{k // 20 + 1:02d}"
        (PK / f"{name}.json").write_text(json.dumps({"packet": name, "passages": new[k:k + 20]}, indent=0, ensure_ascii=False))
    print(f"{len(new)} new passages in {(len(new) + 19) // 20} packets")


def check(name):
    tp = RS / f"{name}.json"
    if not tp.exists():
        return ["no result file"]
    try:
        t = json.loads(tp.read_text())
    except Exception as e:  # noqa: BLE001
        return [f"not valid JSON: {e}"]
    pk = {p["pid"]: p for p in json.loads((PK / f"{name}.json").read_text())["passages"]}
    errs, seen = [], set()
    for p in t.get("passages", []):
        pid = p.get("pid")
        if pid not in pk or pid in seen:
            errs.append(f"unknown or duplicate pid {pid}")
            continue
        seen.add(pid)
        if p.get("passage_stance") not in STANCE_P:
            errs.append(f"{pid}: passage_stance must be one of {sorted(STANCE_P)}")
        ft = fold(pk[pid]["text"])
        if not p.get("statements"):
            errs.append(f"{pid}: no statements")
        for i, s in enumerate(p.get("statements", [])):
            a = fold(s.get("anchor", ""))
            if len(a.split()) < 3 or a not in ft:
                errs.append(f"{pid} statement {i}: anchor is not an exact quote from the passage")
            for k, allowed in (("actor", ACTOR), ("modality", MODAL), ("stance", STANCE_S), ("cs_specific", {"yes", "no"})):
                if s.get(k) not in allowed:
                    errs.append(f"{pid} statement {i}: {k} must be one of {sorted(allowed)}")
            if not (s.get("label") or "").strip() or not (s.get("why") or "").strip():
                errs.append(f"{pid} statement {i}: label and why are required")
    errs += [f"missing pid {x}" for x in sorted(set(pk) - seen)]
    return errs


def work(names):
    prompt = ("You are the COURSE CODER. Read v2/COURSE_CODE.md and follow it for each of these packets, in order: " + ", ".join(names)
              + ". For each, read v2/course_code/packets/<packet>.json, write v2/course_code/results/<packet>.json, and run "
              "python3 v2/tools/course_code.py check <packet> until it prints OK. Write the result file directly with the Write tool; do not write or run any other script. Do not read any institutional type list.")
    env = {**os.environ, "CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS": "0"}
    for attempt in range(3):
        log = ROOT / "logs" / "v2" / f"coursecode_{names[0]}_{int(time.time())}.json"
        with open(log, "w") as out, open(ROOT / "logs" / "v2" / f"coursecode_{names[0]}.err", "a") as err:
            subprocess.run(["claude", "-p", prompt, "--model", "sonnet", "--permission-mode", "acceptEdits", "--allowedTools",
                            "Read(v2/COURSE_CODE.md)", "Read(v2/DEFINITIONS.md)", "Read(v2/course_code/**)", "Write(v2/course_code/results/**)",
                            "Edit(v2/course_code/results/**)", "Bash(python3 v2/tools/course_code.py:*)", "--output-format", "json"],
                           cwd=ROOT, env=env, stdin=subprocess.DEVNULL, stdout=out, stderr=err)
        if all(not check(n) for n in names):
            break
        time.sleep(30 * (attempt + 1))
    st = {n: not check(n) for n in names}
    print(time.strftime("%H:%M"), st, flush=True)
    return st


def labels():
    c, cs = Counter(), Counter()
    for tp in RS.glob("*.json"):
        if check(tp.stem):
            continue
        for p in json.loads(tp.read_text())["passages"]:
            for s in p["statements"]:
                c[s["label"].strip().lower()] += 1
                cs[s["cs_specific"]] += 1
    print(f"{sum(c.values())} statements, {len(c)} distinct labels, cs_specific {dict(cs)}")
    for k, v in c.most_common():
        print(v, k)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["packets", "run", "check", "labels"])
    ap.add_argument("packet", nargs="?")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--chunk", type=int, default=2)
    a = ap.parse_args()
    if a.cmd == "packets":
        packets()
    elif a.cmd == "check":
        e = check(a.packet)
        print("OK" if not e else "\n".join(e[:40]))
        sys.exit(1 if e else 0)
    elif a.cmd == "labels":
        labels()
    else:
        todo = sorted(p.stem for p in PK.glob("*.json") if check(p.stem))
        chunks = [todo[i:i + a.chunk] for i in range(0, len(todo), a.chunk)]
        print(f"{len(todo)} packets in {len(chunks)} chunks", flush=True)
        with ThreadPoolExecutor(a.workers) as pool:
            r = list(pool.map(work, chunks))
        print(f"finished: {sum(v for x in r for v in x.values())}/{len(todo)}", flush=True)


if __name__ == "__main__":
    main()
