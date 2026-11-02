#!/usr/bin/env python3
"""Drive the full v2 run: split the queue into chunks and keep N headless worker sessions busy.

Resumable: a university is done when v2/inst/<slug>.json validates; finished ones are skipped.
Usage: python3 v2/tools/run_v2.py --workers 5 --chunk 4 [--only slug1,slug2] [--limit N]
"""
import argparse
import json
import subprocess
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor

MERGE_LOCK = threading.Lock()
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "v2"
ALLOWED = ["WebSearch", "WebFetch", "Read", "Write", "Edit", "Glob", "Grep", "Agent",
           "Bash(python3:*)", "Bash(curl:*)", "Bash(ls:*)", "Bash(cat:*)", "Bash(head:*)", "Bash(wc:*)", "Bash(mkdir:*)", "Bash(grep:*)"]


def done(slug):
    p = V2 / "inst" / f"{slug}.json"
    if not p.exists():
        return False
    r = subprocess.run([sys.executable, str(V2 / "tools" / "validate_inst.py"), str(p)], capture_output=True, text=True)
    return r.returncode == 0


PHASE = "code"
MODEL = "sonnet"


def collected(slug):
    p = V2 / "collect" / f"{slug}.json"
    try:
        return bool(json.loads(p.read_text()).get("searched"))
    except Exception:
        return False


def rechecked(slug):
    p = V2 / "recheck" / f"{slug}.json"
    try:
        return bool(json.loads(p.read_text()).get("units_searched"))
    except Exception:
        return False


def course_done(slug, slots="C1,C2,C3,C4"):
    p = V2 / "course" / f"{slug}.json"
    if not p.exists():
        return False
    r = subprocess.run([sys.executable, str(V2 / "tools" / "validate_course.py"), "--slots", slots, str(p)], capture_output=True, text=True)
    return r.returncode == 0


def course56_done(slug):
    return course_done(slug, "C1,C2,C3,C4,C5,C6")


def finished(slug):
    return {"collect": collected, "recheck": rechecked, "course": course_done, "course56": course56_done}.get(PHASE, done)(slug)


def work(chunk):
    names = "; ".join(f"{q['slug']} = {q['university']}" for q in chunk)
    if PHASE == "course":
        prompt = (f"You are the COURSE COLLECTOR. Read v2/COURSE_COLLECT.md and follow it for each of these universities, in order: {names}. "
                  "Write v2/course/<slug>.json for each and validate it until it prints OK. Skip a university whose course file already validates.")
    elif PHASE == "course56":
        prompt = (f"You are the COURSE COLLECTOR. Read v2/COURSE_COLLECT.md, including the section 'Adding C5 and C6 to an existing file', "
                  f"and follow that section for each of these universities, in order: {names}. Edit v2/course/<slug>.json for each and run "
                  "python3 v2/tools/validate_course.py --slots C1,C2,C3,C4,C5,C6 v2/course/<slug>.json until it prints OK. "
                  "Do not change C1-C4. Skip a university whose file already validates with all six slots.")
    elif PHASE == "recheck":
        prompt = (f"You are the RECHECKER. Read v2/RECHECK_COMPUTING.md and follow it for each of these universities, in order: {names}. "
                  "Write v2/recheck/<slug>.json for each. Skip a university whose recheck file already exists.")
    elif PHASE == "collect":
        prompt = (f"You are the COLLECTOR. Read v2/COLLECT.md and follow it for each of these universities, in order: {names}. "
                  "Their known URLs from an earlier pass are in v2/queue.json under each slug. Write v2/collect/<slug>.json for each. "
                  "Skip a university whose collect file already exists. Course syllabi are deferred: do not collect them.")
    else:
        prompt = (f"Read v2/WORKER.md and carry it out for these universities, in order: {names}. "
                  "Subagents must run in the foreground.")
    tag = chunk[0]["slug"]
    env = {**__import__("os").environ, "CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS": "0", "POLICY_TEXT_DIR": str(ROOT / ".cache" / "text")}
    for attempt in range(3):
        log = ROOT / "logs" / "v2" / f"{tag}_{int(time.time())}.json"
        with open(log, "w") as out, open(ROOT / "logs" / "v2" / f"{tag}.err", "a") as err:
            subprocess.run(["claude", "-p", prompt, "--model", MODEL, "--permission-mode", "acceptEdits", "--allowedTools", *ALLOWED,
                            "--output-format", "json"], cwd=ROOT, env=env, stdin=subprocess.DEVNULL, stdout=out, stderr=err)
        if all(finished(q["slug"]) for q in chunk):
            break
        time.sleep(60 * (attempt + 1))
    if PHASE == "recheck":
        # merge found documents and screen them right away, so the code phase can take this university next
        with MERGE_LOCK:
            subprocess.run([sys.executable, str(V2 / "tools" / "merge_recheck.py")], cwd=ROOT)
            subprocess.run([sys.executable, str(V2 / "tools" / "screen_docs.py")], cwd=ROOT, capture_output=True)
    elif PHASE in ("course", "course56"):
        subprocess.run([sys.executable, str(V2 / "tools" / "build_course_xlsx.py")], cwd=ROOT, capture_output=True)
    else:
        subprocess.run([sys.executable, str(V2 / "tools" / "export_xlsx.py")], cwd=ROOT)
    status = {q["slug"]: finished(q["slug"]) for q in chunk}
    print(time.strftime("%H:%M"), "chunk", tag, status, flush=True)
    return status


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--chunk", type=int, default=4)
    ap.add_argument("--only", default="")
    ap.add_argument("--limit", type=int, default=36, help="universities per batch (one batch per launch)")
    ap.add_argument("--phase", choices=["collect", "code", "recheck", "course", "course56"], default="code")
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--require-recheck", action="store_true", help="code phase: only universities whose computing recheck is done (D40)")
    a = ap.parse_args()
    global PHASE, MODEL
    PHASE, MODEL = a.phase, a.model
    queue = json.loads((V2 / "queue.json").read_text())
    if a.only:
        want = set(a.only.split(","))
        queue = [q for q in queue if q["slug"] in want]
    if PHASE in ("collect", "recheck", "course", "course56"):
        todo = [q for q in queue if not finished(q["slug"])]
        if PHASE == "recheck":  # not-yet-coded universities first, so coding can follow right behind
            todo.sort(key=lambda q: done(q["slug"]))
    else:
        todo = [q for q in queue if collected(q["slug"]) and not done(q["slug"])]
        if a.require_recheck:
            todo = [q for q in todo if rechecked(q["slug"])]
    if a.limit:
        todo = todo[: a.limit]
    chunks = [todo[i:i + a.chunk] for i in range(0, len(todo), a.chunk)]
    print(f"{len(todo)} universities to do in {len(chunks)} chunks, {a.workers} workers", flush=True)
    with ThreadPoolExecutor(a.workers) as ex:
        results = list(ex.map(work, chunks))
    ok = sum(v for r in results for v in r.values())
    print(f"finished: {ok}/{len(todo)} universities reconciled", flush=True)


if __name__ == "__main__":
    main()
