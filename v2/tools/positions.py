#!/usr/bin/env python3
"""Policy positions under each policy type (D59). A type is a topic; a position is one policy inside it: who is asked
to do what, and when. Per type, a Sonnet worker groups the about-AI statements by actor + required action + phase and
writes one plain policy sentence per group (AI-written, labelled as such). Every position keeps its statement ids; the
example wordings are original anchors picked by id and re-checked verbatim against the saved text (export_xlsx._find).

  python3 v2/tools/positions.py run --only P31 P10 P30 --workers 3   # pilot
  python3 v2/tools/positions.py run --workers 4                      # all types (skips finished ones)
  python3 v2/tools/positions.py merge                                # check + write v2/positions/positions.json
"""
import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

V2 = Path(__file__).resolve().parents[1]
ROOT = V2.parent
OUT = V2 / "positions"
RS = OUT / "results"
PHASES = ["before-course", "course-start", "during-work", "during-assessment", "when-misuse", "over-time", "general"]

PROMPT = """You group university generative-AI policy statements into POLICY POSITIONS. All statements below share one
policy type (a topic): {tid} "{tname}" ({tcovers}). A topic holds many different policies. Your job is to find them.

A position is ONE policy: WHO is asked to do WHAT, and WHEN. Two statements belong together only if they ask the same
actor to do the same thing (or forbid / permit / recommend the same thing) at the same point. Split by:
  - the action asked for (e.g. "check AI output against a source" vs "acknowledge AI can be wrong" vs "teach students to verify");
  - who must act (student / instructor / TA / admin / everyone);
  - force: must / must not / should / may, and statements that only describe or warn ("informs") with no ask;
  - when, if the timing differs (before the course, at course start, during work, during assessment, after misuse, over time).
Merge statements that say the same thing in different words. Do not split on wording, tool names or examples alone.
Usually 3-15 positions per type (fewer for small types, more only if the policies truly differ; at most 20).

For each position write "sentence": one plain policy sentence, like a rule in a policy document, e.g.
"Students must check AI output against a reliable source before submitting it." For "informs" positions write what the
policies state, e.g. "Policies warn that AI output can be inaccurate or fabricated." Rules for the sentence:
  - it must only restate what most of its member statements say; add no detail, condition or reason they do not give;
  - plain words, at most 25 words, no hedges like "generally", no topic labels, no "this position".
Also give "actor" (student|instructor|ta-staff|admin|all), "modality" (must|must-not|should|should-not|may|informs),
"phase" (one of {phases}), "members" (line numbers) and "examples": the 3 line numbers whose wording states the position
most clearly, from different universities where possible (uni is the first field).

Every line number 0..{last} must appear in exactly one position's members.
Return ONLY this JSON, no prose, no code fence:
{{"positions": [{{"sentence": "...", "actor": "...", "modality": "...", "phase": "...", "members": [0, 5], "examples": [5, 0]}}]}}

Lines: n | uni | actor | modality | phase | statement (AI-normalized) | original wording
{lines}
"""


CPROMPT = """Below are fine-grained policy positions found in US university generative-AI policies, grouped by policy type.
Each line: position id | actor | force | phase | statements | universities | sentence.
Within each type, MERGE positions that ask the SAME ACTOR for the same thing, however strongly (must, should, may to do it).
Example: "Students must verify AI output" and "Students should critically evaluate and verify AI output" are ONE policy:
"Students verify AI output before using or submitting it." Never merge positions with different actors: a student policy,
an everyone ("all") policy and an instructor policy stay separate even when they ask for the same action.
Keep positions separate when the action or its object differs: teaching students to verify is not verifying; checking that
AI-cited sources exist, or testing AI-written code, are distinct concrete policies. Keep a prohibition apart from a
permission of the same act (must-not vs may are opposite policies). Never merge across types.

For each merged policy write "sentence": the policy itself, stated directly, at most 20 words, naming its actor
("Students ...", "Instructors ...", "Staff ...", "Everyone ..." for actor all, "Administrators ..." for admin).
  - A rule or practice: "Students verify the accuracy of AI output before using or submitting it."
  - A statement of fact or warning: state the fact itself ("AI output can be inaccurate, fabricated or biased.").
    Never write "Policies warn/state/say that".
  - Restate only what the merged positions say; add nothing.
Also give "phase": the phase of most of its statements.

Return ONLY this JSON, no prose, no code fence:
{"types": {"P31": [{"sentence": "...", "phase": "...", "members": ["P31.02", "P31.04"]}]}}
Every position id must appear in exactly one merged policy of its own type.

{lines}
"""


def consolidate(model, size=130, only=None):
    """D60: merge fine positions that ask the same actor for the same thing (across force only); one Sonnet call per batch of types."""
    fine = json.loads((OUT / "positions_fine.json").read_text())
    CR = OUT / "consolidated"
    CR.mkdir(exist_ok=True)
    todo = [t for t in sorted(only or fine, key=lambda t: -len(fine[t])) if not (CR / f"{t}.json").exists()]
    batches, cur = [], []
    for t in todo:
        if cur and sum(len(fine[x]) for x in cur) + len(fine[t]) > size:
            batches.append(cur)
            cur = []
        cur.append(t)
    batches += [cur] if cur else []

    def one(ts):
        lines = "\n\n".join(f"TYPE {t}\n" + "\n".join(f"{q['pid']} | {q['actor']} | {q['modality']} | {q['phase']} | {q['n']} | {q['n_unis']} | {q['sentence']}"
                                                         for q in fine[t]) for t in ts)
        for attempt in range(3):
            r = subprocess.run(["claude", "-p", "--model", model, "--output-format", "text"], input=CPROMPT.replace("{lines}", lines),
                               capture_output=True, text=True, cwd=OUT)
            try:
                res = parse(r.stdout)["types"]
            except Exception:  # noqa: BLE001
                continue
            ok = []
            for t in ts:
                want = [q["pid"] for q in fine[t]]
                got = [m for g in res.get(t, []) for m in g.get("members", [])]
                actor = {q["pid"]: q["actor"] for q in fine[t]}
                one_actor = all(len({actor.get(m) for m in g.get("members", [])}) == 1 for g in res.get(t, []))
                if sorted(got) == sorted(want) and one_actor and all(g.get("sentence") for g in res[t]):
                    (CR / f"{t}.json").write_text(json.dumps({"model": model, "groups": res[t]}, indent=1))
                    ok.append(t)
            ts = [t for t in ts if t not in ok]
            if not ts:
                return "ok"
        return "FAILED: " + " ".join(ts)

    with ThreadPoolExecutor(4) as ex:
        for ts, msg in zip(batches, ex.map(one, batches)):
            print(len(ts), "types", msg, flush=True)


def load():
    pol = json.loads((V2 / "site" / "data" / "policies.json").read_text())
    types = {t["id"]: t for t in json.loads((V2 / "site" / "data" / "types.json").read_text())}
    by = {}
    for p in pol:
        if p.get("about_ai") == "yes":
            by.setdefault(p["type"], []).append(p)
    for t in by:
        by[t].sort(key=lambda p: p["id"])
    return by, types


def packet(tid, rows, t):
    clean = lambda s: re.sub(r"\s+", " ", s or "").replace("|", "/").strip()
    lines = "\n".join(f"{i} | {p['uni']} | {p['actor']} | {p['modality']} | {p['phase']} | {clean(p.get('policy') or p['anchor'])} | {clean(p['anchor'])}"
                      for i, p in enumerate(rows))
    return PROMPT.format(tid=tid, tname=t.get("name_v2") or t.get("name", ""), tcovers=t.get("covers", ""),
                         phases="|".join(PHASES), last=len(rows) - 1, lines=lines)


def parse(txt):
    m = re.search(r"\{.*\}", txt, re.S)
    return json.loads(m.group(0)) if m else None


def problems(res, n):
    if not res or not isinstance(res.get("positions"), list) or not res["positions"]:
        return ["no positions"]
    seen = Counter(i for q in res["positions"] for i in q.get("members", []))
    errs = [f"line {i} missing" for i in range(n) if i not in seen][:5]
    errs += [f"line {i} twice" for i, k in seen.items() if k > 1][:5]
    errs += [f"line {i} out of range" for i in seen if not (isinstance(i, int) and 0 <= i < n)][:5]
    for q in res["positions"]:
        if not q.get("sentence") or not q.get("members"):
            errs.append("empty position")
    return errs


def run_one(tid, rows, t, model):
    RS.mkdir(parents=True, exist_ok=True)
    out = RS / f"{tid}.json"
    for attempt in range(2):
        r = subprocess.run(["claude", "-p", "--model", model, "--output-format", "text"], input=packet(tid, rows, t),
                           capture_output=True, text=True, cwd=OUT)
        try:
            res = parse(r.stdout)
        except json.JSONDecodeError:
            res = None
        errs = problems(res, len(rows))
        # a line placed in two positions stays only in the one whose actor, modality and phase match it best (recorded as repaired)
        if res and any(e.endswith("twice") for e in errs) and not any(e.endswith("range") or e == "empty position" for e in errs):
            fitn = lambda q, p: sum(a == b for a, b in zip([q.get("actor"), q.get("modality"), q.get("phase")], [p["actor"], p["modality"], p["phase"]]))
            homes = {}
            for q in res["positions"]:
                for i in q["members"]:
                    homes.setdefault(i, []).append(q)
            for i, qs in homes.items():
                if len(qs) > 1:
                    keep = max(qs, key=lambda q: fitn(q, rows[i]))
                    for q in qs:
                        if q is not keep:
                            q["members"] = [j for j in q["members"] if j != i]
                            q["examples"] = [j for j in q.get("examples", []) if j != i]
                    res.setdefault("repaired", []).append(i)
            res["positions"] = [q for q in res["positions"] if q["members"]]
            errs = problems(res, len(rows))
        # small coverage gaps are repaired, not retried: a missing line goes to the largest position with its actor, modality
        # and phase (else its actor and modality, else the largest position); repaired line numbers are recorded
        if res and errs and all(e.endswith("missing") for e in errs):
            have = {i for q in res["positions"] for i in q["members"]}
            for i in range(len(rows)):
                if i not in have:
                    p = rows[i]
                    fit = lambda q, n: [q.get("actor"), q.get("modality"), q.get("phase")][:n] == [p["actor"], p["modality"], p["phase"]][:n]
                    best = max(res["positions"], key=lambda q: (fit(q, 3), fit(q, 2), len(q["members"])))
                    best["members"].append(i)
                    res.setdefault("repaired", []).append(i)
            errs = problems(res, len(rows))
        if not errs:
            res["ids"] = [p["id"] for p in rows]
            res["model"] = model
            out.write_text(json.dumps(res, indent=1))
            return tid, f"ok ({len(res['positions'])} positions)"
    (RS / f"{tid}.failed.txt").write_text(r.stdout[-4000:] + "\n" + r.stderr[-2000:])
    return tid, "FAILED: " + "; ".join(errs[:3])


def merge():
    from export_xlsx import _find, _source  # noqa: E402
    by, types = load()
    pol = {p["id"]: p for rows in by.values() for p in rows}
    allpos, bad = {}, []
    for f in sorted(RS.glob("P*.json")):
        res = json.loads(f.read_text())
        tid, ids = f.stem, res["ids"]
        if sorted(ids) != sorted(p["id"] for p in by.get(tid, [])):
            bad.append(f"{tid}: statement set changed since grouping; rerun")
        out = []
        for k, q in enumerate(res["positions"]):
            mem = [ids[i] for i in q["members"]]
            ex = [ids[i] for i in q.get("examples", []) if i in q["members"]] or mem[:1]
            shown = []
            for sid in ex + [m for m in mem if m not in ex]:
                p = pol[sid]
                doc = p["doc"].split(":", 1)[1]
                if p.get("verified") and _find(p["anchor"], _source(p["uni"], doc)[1])[0] != -1:
                    shown.append(sid)
                if len(shown) == 3:
                    break
            if not shown:
                bad.append(f"{tid} position {k}: no verified wording")
            unis = sorted({pol[m]["uni"] for m in mem})
            out.append({"pid": f"{tid}.{k + 1:02d}", "sentence": q["sentence"].strip(), "sentence_source": f"AI-written ({res.get('model', 'sonnet')})",
                        "actor": q.get("actor"), "modality": q.get("modality"), "phase": q.get("phase"),
                        "n": len(mem), "n_unis": len(unis), "examples": shown, "members": mem})
        out.sort(key=lambda q: (PHASES.index(q["phase"]) if q["phase"] in PHASES else 99, -q["n_unis"]))
        for k, q in enumerate(out, 1):
            q["pid"] = f"{tid}.{k:02d}"
        allpos[tid] = out
    (OUT / "positions_fine.json").write_text(json.dumps(allpos, indent=1))
    # D60: where a consolidation exists, the shown policies are the merged groups; each keeps its fine positions as parts
    CR, merged = OUT / "consolidated", {}
    for tid, fine in allpos.items():
        cf = CR / f"{tid}.json"
        if not cf.exists():
            merged[tid] = fine
            continue
        fp = {q["pid"]: q for q in fine}
        out = []
        for g in json.loads(cf.read_text())["groups"]:
            parts = sorted((fp[m] for m in g["members"]), key=lambda q: -q["n_unis"])
            mem = [sid for q in parts for sid in q["members"]]
            ex, seen = [], set()
            for sid in [e for q in parts for e in q["examples"]]:
                if pol[sid]["uni"] not in seen:
                    ex.append(sid)
                    seen.add(pol[sid]["uni"])
            ex = ex[:3]
            who = Counter((pol[m]["actor"], pol[m]["modality"]) for m in mem)
            out.append({"pid": "", "sentence": g["sentence"].strip(), "sentence_source": f"written by {json.loads(cf.read_text()).get('model', 'sonnet')} from the merged positions",
                        "phase": g.get("phase") if g.get("phase") in PHASES else parts[0]["phase"],
                        "actor": who.most_common(1)[0][0][0], "modality": who.most_common(1)[0][0][1],
                        "who": [[a, m, k] for (a, m), k in who.most_common()],
                        "n": len(mem), "n_unis": len({pol[m]["uni"] for m in mem}), "examples": ex, "members": mem,
                        "parts": [{"pid": q["pid"], "sentence": q["sentence"], "n": q["n"]} for q in parts]})
        out.sort(key=lambda q: (PHASES.index(q["phase"]), -q["n_unis"]))
        for k, q in enumerate(out, 1):
            q["pid"] = f"{tid}.{k:02d}"
        merged[tid] = out
    (OUT / "positions.json").write_text(json.dumps(merged, indent=1))
    print(f"shown: {sum(len(v) for v in merged.values())} policies ({sum(1 for t in merged if (CR / f'{t}.json').exists())} types consolidated)")
    n = sum(len(v) for v in allpos.values())
    print(f"{len(allpos)} of {len(by)} types grouped, {n} positions; problems: {len(bad)}")
    for b in bad[:10]:
        print(" ", b)


def main():
    sys.path.insert(0, str(V2 / "tools"))
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "merge", "consolidate"])
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--model", default="sonnet")
    a = ap.parse_args()
    if a.cmd == "merge":
        return merge()
    if a.cmd == "consolidate":
        merge()
        consolidate(a.model, only=a.only)
        return merge()
    by, types = load()
    todo = [t for t in (a.only or sorted((t for t in by if t.startswith("P")), key=lambda t: -len(by[t]))) if not (RS / f"{t}.json").exists()]
    with ThreadPoolExecutor(a.workers) as ex:
        for tid, msg in ex.map(lambda t: run_one(t, by[t], types.get(t, {}), a.model), todo):
            print(tid, len(by[tid]), msg, flush=True)
    merge()


if __name__ == "__main__":
    main()
