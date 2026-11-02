#!/usr/bin/env python3
"""NOT USED: probability scoring was dropped by the PI on 2026-10-05. Kept for the record.

Score guideline membership with TypeSafe's Jev (System One) as an independent second coder.

Stage A, statement -> guideline: one Choice over all guidelines plus "none_fit", asked twice in
the same request with forward and reversed option order (Jev can lean toward the first option);
the two distributions are averaged.
Stage B, guideline -> group: for each built-in grouping (theme, phase, actor), one Choice per
guideline over that grouping's groups, again in both orders.

Every response is cached in corpus/jev_cache.jsonl, so re-runs only pay for new statements.
Writes corpus/jev_scores.json and corpus/jev_disagreements.md.

Key: TYPESAFE_API_KEY environment variable, or the first line of .typesafe_key in the project root.
Usage: python3 tools/jev_score.py [--limit N] [--model jev-1.13.0]
"""
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "corpus" / "jev_cache.jsonl"
API = "https://api.typesafe.ai/v1/systemone"
MODEL = sys.argv[sys.argv.index("--model") + 1] if "--model" in sys.argv else "jev-1.13.0"  # pinned for reproducibility


def api_key():
    k = os.environ.get("TYPESAFE_API_KEY")
    if not k and (ROOT / ".typesafe_key").exists():
        k = (ROOT / ".typesafe_key").read_text().strip().splitlines()[0].strip()
    if not k:
        raise SystemExit("No TypeSafe key: set TYPESAFE_API_KEY or put the key in .typesafe_key (see context.md).")
    return k


_cache = {}
if CACHE.exists():
    for line in CACHE.read_text().splitlines():
        if line.strip():
            rec = json.loads(line)
            _cache[rec["key"]] = rec["response"]


def call(body):
    key = hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    if key in _cache:
        return _cache[key]
    data = json.dumps(body, ensure_ascii=False).encode()
    for attempt in range(8):
        req = urllib.request.Request(API, data=data, method="POST", headers={
            "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                resp = json.loads(r.read())
            break
        except urllib.error.HTTPError as e:
            if e.code in (429, 529, 500, 502, 503) and attempt < 7:
                time.sleep(min(30, 2 ** attempt) + 0.1 * attempt)
                continue
            raise SystemExit(f"TypeSafe API error {e.code}: {e.read()[:300]!r}")
        except urllib.error.URLError:
            time.sleep(2 ** attempt)
    _cache[key] = resp
    with open(CACHE, "a") as f:
        f.write(json.dumps({"key": key, "response": resp}, ensure_ascii=False) + "\n")
    return resp


def two_order_choice(instructions, options):
    """Same Choice asked with forward and reversed option order."""
    fwd = dict(options)
    rev = dict(reversed(list(options.items())))
    return {"fwd": {"type": "choice", "instructions": instructions, "criteria": fwd},
            "rev": {"type": "choice", "instructions": instructions, "criteria": rev}}


def averaged(resp):
    a, b = resp["answers"]["fwd"]["probabilities"], resp["answers"]["rev"]["probabilities"]
    probs = {k: (a.get(k, 0) + b.get(k, 0)) / 2 for k in set(a) | set(b)}
    top_a = max(a, key=a.get)
    top_b = max(b, key=b.get)
    return probs, top_a == top_b


def kappa(pairs):
    n = len(pairs)
    po = sum(x == y for x, y in pairs) / n
    ca, cb = Counter(x for x, _ in pairs), Counter(y for _, y in pairs)
    pe = sum(ca[k] * cb.get(k, 0) for k in ca) / (n * n)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def main():
    corpus = json.loads((ROOT / "corpus" / "corpus.json").read_text())
    syn = json.loads((ROOT / "corpus" / "synthesis.json").read_text())
    defs = json.loads((ROOT / "corpus" / "guideline_defs.json").read_text())
    gl = syn["guidelines"]
    analyst = {i: g["id"] for g in gl for i in g["members"]}

    g_options = {g["id"]: {"name": g["label"], "covers": defs[g["id"]]} for g in gl}
    g_options["none_fit"] = {"name": "None of these", "covers": "The statement does not express any of the listed guidelines."}
    instr = {
        "task": "Classify `policy_statement`, a verbatim excerpt from a university's generative-AI policy for computing courses.",
        "question": "Which guideline does `policy_statement` most directly express? Judge what the statement itself says, using `source` only as context.",
    }

    stmts = [(e, d) for d in corpus["documents"] for e in d["excerpts"]]
    if "--limit" in sys.argv:
        stmts = stmts[: int(sys.argv[sys.argv.index("--limit") + 1])]

    def score_statement(item):
        e, d = item
        body = {"model": MODEL,
                "state": {"policy_statement": e["text"],
                          "source": {"institution": d["university"], "unit": d["unit"], "course": d.get("course"),
                                     "document_level": d["level"]}},
                "questions": two_order_choice(instr, g_options)}
        probs, stable = averaged(call(body))
        return e["id"], probs, stable

    with ThreadPoolExecutor(16) as ex:
        results = list(ex.map(score_statement, stmts))

    st_out, pairs, dis = {}, [], []
    for sid, probs, stable in results:
        top = max(probs, key=probs.get)
        a = analyst.get(sid)
        st_out[sid] = {"top": top, "top_p": round(probs[top], 4), "p_analyst": round(probs.get(a, 0), 4),
                       "order_stable": stable,
                       "probs": {k: round(v, 4) for k, v in probs.items() if v >= 0.0005}}
        if a:
            pairs.append((a, top))
            if top != a:
                dis.append((sid, a, top, probs.get(a, 0), probs[top]))

    # Stage B: guideline -> group for each built-in grouping
    schemes = {"theme": syn["themes"], "phase": syn["phases"], "actor": syn["actors"]}
    ex_text = {e["id"]: e["text"] for e, _ in stmts}

    def score_guideline(args):
        g, scheme = args
        opts = {x["id"]: {"name": x["label"], "covers": x["desc"]} for x in schemes[scheme]}
        sample = [ex_text[i] for i in g["members"] if i in ex_text][:12]
        body = {"model": MODEL,
                "state": {"guideline": {"name": g["label"], "definition": defs[g["id"]], "example_statements": sample}},
                "questions": two_order_choice(
                    {"task": f"Place `guideline` (a consolidated guideline from university AI policies for computing courses) in one {scheme} group.",
                     "question": f"Which {scheme} group does `guideline` belong to?"}, opts)}
        probs, stable = averaged(call(body))
        return g["id"], scheme, probs, stable

    jobs = [(g, s) for g in gl for s in schemes]
    with ThreadPoolExecutor(16) as ex:
        gres = list(ex.map(score_guideline, jobs))
    g_out = {}
    for gid, scheme, probs, stable in gres:
        g_out.setdefault(gid, {})[scheme] = {"dist": {k: round(v, 4) for k, v in sorted(probs.items(), key=lambda x: -x[1])},
                                             "order_stable": stable}

    agree = sum(x == y for x, y in pairs) / len(pairs) if pairs else 0
    summary = {"model": MODEL, "n_statements": len(pairs), "agreement": round(agree, 4), "cohen_kappa": round(kappa(pairs), 4) if pairs else None,
               "order_stable_share": round(sum(v["order_stable"] for v in st_out.values()) / max(1, len(st_out)), 4),
               "jev_none_fit": sum(v["top"] == "none_fit" for v in st_out.values())}
    for scheme in schemes:
        assigned = {g["id"]: g[scheme] for g in gl}
        hits = sum(max(g_out[gid][scheme]["dist"], key=g_out[gid][scheme]["dist"].get) == assigned[gid] for gid in g_out)
        summary[f"guideline_{scheme}_agreement"] = round(hits / len(g_out), 4)
    (ROOT / "corpus" / "jev_scores.json").write_text(json.dumps(
        {"summary": summary, "statements": st_out, "guidelines": g_out}, indent=1, ensure_ascii=False))

    labels = {g["id"]: g["label"] for g in gl} | {"none_fit": "None of these"}
    lines = ["# Analyst vs Jev disagreements", "", json.dumps(summary), "",
             "| statement | verbatim text | analyst | p(analyst) | Jev top | p(top) |", "|---|---|---|---|---|---|"]
    for sid, a, top, pa, pt in sorted(dis, key=lambda x: -x[4]):
        lines.append(f"| `{sid}` | {ex_text[sid]} | {a} {labels[a]} | {pa:.2f} | {top} {labels[top]} | {pt:.2f} |")
    (ROOT / "corpus" / "jev_disagreements.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    KEY = api_key()
    main()
