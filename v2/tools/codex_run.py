#!/usr/bin/env python3
"""Run OpenAI Codex (GPT) as a background worker for three jobs, so they do not use Claude usage (D57).

  critique   GPT critique of the Opus audit: v2/audit/critique/batch_NN.json -> v2/audit/critique/results/batch_NN.json
  audit2     fresh audit sample audited by GPT: v2/audit2/packets/*.json -> v2/audit2/results/*.json (v2/AUDIT.md, checked by audit.py)
  course56   C5/C6 course collection (v2/COURSE_COLLECT.md, 'Adding C5 and C6'), validated by validate_course.py

Each job is resumable: an item is done when its output validates. Usage: python3 v2/tools/codex_run.py <job> [--workers N]
"""
import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "v2"
CODEX = "/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex"
FIELDS = ["policy", "actor", "phase", "modality", "unit_stance", "about_ai", "binding", "final_type"]
sys.path.insert(0, str(V2 / "tools"))


LIMIT = False  # set when Codex reports the ChatGPT usage limit; remaining items are skipped, not failed


def codex(prompt, tag):
    global LIMIT
    if LIMIT:
        return
    log = ROOT / "logs" / "v2" / f"codex_{tag}_{int(time.time())}.log"
    with open(log, "w") as out:
        subprocess.run([CODEX, "exec", "-s", "workspace-write", "--skip-git-repo-check", "-c", "sandbox_workspace_write.network_access=true",
                        "-C", str(ROOT), prompt], stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT)
    if "usage limit" in log.read_text(errors="ignore"):
        LIMIT = True


# ---- critique ----
CR = V2 / "audit" / "critique"


def critique_ok(name):
    p = CR / "results" / f"{name}.json"
    if not p.exists():
        return False
    try:
        r = json.loads(p.read_text())
    except Exception:  # noqa: BLE001
        return False
    want = {x["uid"] for x in json.loads((CR / f"{name}.json").read_text())}
    got = {x.get("uid") for x in r} if isinstance(r, list) else set()
    return want == got and all(isinstance(x.get("fields"), dict) for x in r)


def critique_item(name):
    prompt = (f"You are an independent critic of a coding audit for a research dataset of US university generative-AI policies. Read v2/AUDIT.md "
              f"(field definitions), v2/THEME_REVIEW.md (binding and about_ai), the field values in v2/CODEBOOK.md (actor, phase, modality, unit_stance) "
              f"and type names in v2/policy_types_v3.json. Then read v2/audit/critique/{name}.json. Each item is one coded statement with its source "
              f"passage and context, the original codes, and either (kind=correction) the corrections a Claude Opus auditor proposed with reasons, or "
              f"(kind=confirmation) an item Opus judged fully correct. For each correction, decide per corrected field whether the ORIGINAL code or the "
              f"OPUS correction is right, from the passage and context only: side 'opus', 'original' (original defensible; Opus too strict or wrong), or "
              f"'neither' (give your value). For each confirmation, check all eight codes and report only fields that are clearly wrong (side 'neither' "
              f"with your value). Write ONLY a JSON array to v2/audit/critique/results/{name}.json, one object per item: "
              f'{{"uid": "...", "kind": "correction|confirmation", "fields": {{"<field>": {{"side": "opus|original|neither", "value": "...", "note": "<=20 words"}}}}}} '
              f"(fields is {{}} for a confirmation with nothing wrong). Every uid exactly once. Create the results folder if needed.")
    for _ in range(2):
        codex(prompt, f"critique_{name}")
        if critique_ok(name):
            break
    return name, critique_ok(name)


# ---- fresh audit sample ----
A2 = V2 / "audit2"


def audit2_sample():
    import random
    import audit
    U = audit.all_units()
    old = set(json.loads((V2 / "audit" / "sample.json").read_text())["strata"])
    pool = sorted(uid for uid, u in U.items() if u["about_ai"] == "yes" and uid not in old)
    rnd = random.Random(20261027)
    pick = sorted(rnd.sample(pool, 300))
    (A2 / "packets").mkdir(parents=True, exist_ok=True)
    (A2 / "results").mkdir(parents=True, exist_ok=True)
    (A2 / "sample.json").write_text(json.dumps({"seed": 20261027, "units": pick, "note": "fresh simple random sample of statements about AI, excluding the first audit sample"}))
    for k in range(0, 300, 25):
        (A2 / "packets" / f"F{k // 25 + 1:02d}.json").write_text(json.dumps({"packet": f"F{k // 25 + 1:02d}", "units": [
            {kk: v for kk, v in U[x].items() if not kk.startswith("_")} for x in pick[k:k + 25]]}, indent=0, ensure_ascii=False))
    print("fresh sample: 300 units, 12 packets")


def audit2_ok(name):
    import audit
    audit.PK, audit.RS = A2 / "packets", A2 / "results"
    return not audit.check(name)


def audit2_item(name):
    prompt = (f"You are the AUDITOR. Read v2/AUDIT.md and follow it for packet {name}, with these paths instead of the ones in the brief: read "
              f"v2/audit2/packets/{name}.json and write v2/audit2/results/{name}.json (same output format). Then run "
              f"python3 v2/tools/codex_run.py check-audit2 {name} and fix every error until it prints OK.")
    for _ in range(2):
        codex(prompt, f"audit2_{name}")
        if audit2_ok(name):
            break
    return name, audit2_ok(name)


# ---- C5/C6 collection ----
def course56_items():
    import run_v2
    run_v2.PHASE = "course56"
    q = json.loads((V2 / "queue.json").read_text())
    return [x for x in q if not run_v2.course56_done(x["slug"])]


def course56_item(chunk):
    import run_v2
    names = "; ".join(f"{q['slug']} = {q['university']}" for q in chunk)
    prompt = (f"You are the COURSE COLLECTOR. Read v2/COURSE_COLLECT.md, including the section 'Adding C5 and C6 to an existing file', and follow that "
              f"section for each of these universities, in order: {names}. Use web search to find catalogs and syllabi, and fetch pages only with "
              f"python3 tools/fetch_text.py \"<url>\" v2c-<slug>-<slot>[-n]. Edit v2/course/<slug>.json for each (keep C1-C4 unchanged) and run "
              f"python3 v2/tools/validate_course.py --slots C1,C2,C3,C4,C5,C6 v2/course/<slug>.json until it prints OK. Do not record instructor names.")
    for _ in range(2):
        codex(prompt, f"course56_{chunk[0]['slug']}")
        if all(run_v2.course56_done(q["slug"]) for q in chunk):
            break
    return {q["slug"]: run_v2.course56_done(q["slug"]) for q in chunk}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("job", choices=["critique", "audit2-sample", "audit2", "check-audit2", "course56"])
    ap.add_argument("packet", nargs="?")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--limit", type=int, default=400)
    a = ap.parse_args()
    (ROOT / "logs" / "v2").mkdir(parents=True, exist_ok=True)
    if a.job == "check-audit2":
        import audit
        audit.PK, audit.RS = A2 / "packets", A2 / "results"
        e = audit.check(a.packet)
        print("OK" if not e else "\n".join(e[:40]))
        sys.exit(1 if e else 0)
    if a.job == "audit2-sample":
        audit2_sample()
        return
    if a.job == "critique":
        (CR / "results").mkdir(parents=True, exist_ok=True)
        todo = sorted(p.stem for p in CR.glob("batch_*.json") if not critique_ok(p.stem))
        f, items = critique_item, todo
    elif a.job == "audit2":
        todo = sorted(p.stem for p in (A2 / "packets").glob("*.json") if not audit2_ok(p.stem))
        f, items = audit2_item, todo
    else:
        todo = course56_items()[: a.limit]
        f, items = course56_item, [todo[i:i + 3] for i in range(0, len(todo), 3)]
    print(f"{a.job}: {len(items)} items, {a.workers} Codex workers", flush=True)
    with ThreadPoolExecutor(a.workers) as pool:
        for r in pool.map(f, items):
            print(time.strftime("%H:%M"), r, flush=True)


if __name__ == "__main__":
    main()
