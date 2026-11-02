#!/usr/bin/env python3
"""Policy synthesis passes after D60 (D62-D65). Each pass writes its own files under v2/positions/; `apply` combines them.

  course     D63: course statements -> course policies per course type (actor + action, force merged), each with a stage
  dedupe     D62: merge policies that say the same thing across types (semantic and latent equivalence), per actor group;
             give each no-stage ('general') policy a stage, or mark it background (definition, reason or fact)
  uncovered  D64: place each UNCOVERED statement in a policy, or set it aside (not about AI / not a policy / unique)
  apply      write v2/positions/final.json (institutional + course policies) for build_v2.py, export_xlsx.py and the site

  python3 v2/tools/synthesis.py course --workers 5
  python3 v2/tools/synthesis.py dedupe --layer inst      (then --layer course)
  python3 v2/tools/synthesis.py uncovered
  python3 v2/tools/synthesis.py apply
"""
import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

V2 = Path(__file__).resolve().parents[1]
OUT = V2 / "positions"
sys.path.insert(0, str(V2 / "tools"))
from positions import PHASES, parse  # noqa: E402

GROUP = {"student": "student", "instructor": "instructor", "ta-staff": "staff", "admin": "staff", "all": "all"}
GROUP_NAME = {"student": "students", "instructor": "instructors", "staff": "teaching assistants, staff and administrators", "all": "everyone (the whole community)"}
STAGES = PHASES[:-1] + ["background"]  # 'general' is resolved into a stage or 'background'


FILES = os.environ.get("SYN_MODE") == "files"  # when the headless CLI cannot run: prompts go to files, subagents write answers


def claude(prompt, model, key):
    if FILES:
        (OUT / "prompts").mkdir(exist_ok=True)
        (OUT / "answers").mkdir(exist_ok=True)
        (OUT / "prompts" / f"{key}.txt").write_text(prompt)
        a = OUT / "answers" / f"{key}.json"
        try:
            return parse(a.read_text()) if a.exists() else None
        except Exception:  # noqa: BLE001
            return None
    r = subprocess.run(["claude", "-p", "--model", model, "--output-format", "text"], input=prompt, capture_output=True, text=True, cwd=OUT)
    try:
        return parse(r.stdout)
    except Exception:  # noqa: BLE001
        return None


def fold(s):
    s = (s or "").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace(" ", " ")
    return re.sub(r"\s+", " ", s).strip().lower()


# ---------------------------------------------------------------- course policies (D63)
CPROMPT = """You turn CS course-syllabus statements about generative AI into COURSE POLICIES. All statements below were coded
with one course type: {tid} "{tname}" ({tcovers}).

A policy is ONE thing a syllabus asks: WHO is asked to do WHAT, and WHEN in the course. Group statements that ask the same
actor for the same thing, however strongly (must / should / may to do it: one policy). Keep separate: different actors
(students vs instructor/course staff vs everyone), different actions or objects, and a prohibition vs a permission of the
same act. Merge statements that say the same thing in different words. Usually 1-10 policies per type.

For each policy give:
  "sentence": the policy stated directly, at most 20 words, naming its actor ("Students ...", "The instructor ...",
     "Course staff ...", "Everyone ..."); for a fact or reason state it directly ("AI-generated code is often wrong.").
     Restate only what the statements say; add nothing. Never write "Syllabi say/state that".
  "actor": student | instructor | ta-staff | all
  "stage": when it applies in the course: before-course (course design, before term) | course-start (syllabus, first
     week, setting expectations) | during-work (while students do homework, labs, projects) | during-assessment (exams,
     quizzes, in-class tests) | when-misuse (suspected or found misuse, penalties, reporting) | over-time (policy changes,
     revisions during or after the term) | background (definitions, reasons, facts with no time of action)
  "about_ai": "no" only for a group of statements that are not about AI at all (generic integrity or course rules), else "yes"
  "members": line numbers; "examples": the 3 line numbers whose wording states the policy most clearly, different universities where possible.
Every line number 0..{last} must appear in exactly one policy.
Return ONLY this JSON, no prose, no code fence:
{{"policies": [{{"sentence": "...", "actor": "...", "stage": "...", "about_ai": "yes", "members": [0, 3], "examples": [3, 0]}}]}}

Lines: n | uni | course slot | actor | force | label (coder's) | original wording
{lines}
"""


def course_rows():
    pk = {p["pid"]: p for f in (V2 / "course_code" / "packets").glob("*.json") for p in json.loads(f.read_text())["passages"]}
    CA = json.loads((V2 / "course_code" / "course_assignments.json").read_text())["statements"]
    rows = defaultdict(list)
    for f in sorted((V2 / "course_code" / "results").glob("*.json")):
        for p in json.loads(f.read_text())["passages"]:
            for k, s in enumerate(p["statements"]):
                sid = f"{p['pid']}#{k}"
                t = (CA.get(sid) or {}).get("type") or ""
                src = pk[p["pid"]]
                rows[t if not t.startswith("OTHER") else "OTHER"].append(
                    {"sid": sid, "uni": src["university"], "slot": src["slot"], "course": src["course"], "url": src["url"],
                     "actor": s["actor"], "modality": s["modality"], "label": s["label"], "anchor": s["anchor"],
                     "verified": fold(s["anchor"]) in fold(src["text"])})
    return rows


def course(workers, model):
    cb = {t["id"]: t for t in json.loads((V2 / "course_codebook.json").read_text())["types"]}
    cb["OTHER"] = {"name": "Other course statements (no course type fits)", "covers": "statements the coders labelled OTHER"}
    rows = course_rows()
    R = OUT / "course"
    R.mkdir(parents=True, exist_ok=True)

    def one(tid):
        rs = sorted(rows[tid], key=lambda r: r["sid"])
        clean = lambda s: re.sub(r"\s+", " ", s or "").replace("|", "/").strip()
        lines = "\n".join(f"{i} | {r['uni']} | {r['slot']} | {r['actor']} | {r['modality']} | {clean(r['label'])} | {clean(r['anchor'])}" for i, r in enumerate(rs))
        prompt = CPROMPT.format(tid=tid, tname=cb[tid]["name"], tcovers=cb[tid].get("covers", ""), last=len(rs) - 1, lines=lines)
        for _ in range(1 if FILES else 3):
            res = claude(prompt, model, f"course_{tid}")
            if not res or not res.get("policies"):
                continue
            seen = Counter(i for q in res["policies"] for i in q.get("members", []))
            if set(seen) == set(range(len(rs))) and max(seen.values()) == 1 and all(q.get("stage") in STAGES for q in res["policies"]):
                res["sids"] = [r["sid"] for r in rs]
                res["model"] = model
                (R / f"{tid}.json").write_text(json.dumps(res, indent=1))
                return tid, f"ok ({len(res['policies'])} policies from {len(rs)} statements)"
        return tid, "FAILED"

    todo = [t for t in sorted(rows, key=lambda t: -len(rows[t])) if not (R / f"{t}.json").exists()]
    with ThreadPoolExecutor(workers) as ex:
        for tid, msg in ex.map(one, todo):
            print(tid, msg, flush=True)


def course_policies():
    """Course policies with members (statement ids), examples (verified anchors) and actor/stage, before dedupe."""
    rows = {r["sid"]: r for rs in course_rows().values() for r in rs}
    out = []
    for f in sorted((OUT / "course").glob("*.json")):
        res = json.loads(f.read_text())
        for k, q in enumerate(res["policies"]):
            mem = [res["sids"][i] for i in q["members"]]
            ex = [res["sids"][i] for i in q.get("examples", []) if i in q["members"]]
            ex = [s for s in ex + mem if rows[s]["verified"]]
            ex = list(dict.fromkeys(ex))[:3]
            out.append({"pid": f"{f.stem}.c{k + 1:02d}", "type": f.stem, "sentence": q["sentence"].strip(), "actor": q.get("actor") or "student",
                        "phase": q["stage"], "about_ai": q.get("about_ai", "yes"), "members": mem, "examples": ex,
                        "n": len(mem), "n_unis": len({rows[m]["uni"] for m in mem})})
    return out, rows


# ---------------------------------------------------------------- cross-type dedupe and stages (D62)
DPROMPT = """Below are policies found in {what}, all addressed to {who}. Each line:
policy id | topic (policy type) | stage | universities | policy sentence.

Task 1. MERGE policies that say the same thing, even when they sit under different topics or use different words.
Judge both semantic equivalence (the same requirement, permission, prohibition or fact, worded differently) and latent
equivalence (the same underlying intent and the same act asked of the same people, even if one is phrased as a rule and
the other as advice). Examples of the same policy: "Students disclose any AI use in their submissions" and "Students
acknowledge AI assistance on each assignment". Do NOT merge when the action differs, the object differs (code vs prose,
data vs output), a condition differs materially (with permission vs always), or the direction differs (prohibit vs
permit). Merely related or co-occurring policies stay separate. Be exhaustive: check every policy against all others.
For each merged group give the member ids, one merged "sentence" (at most 20 words, naming the actor, stating the policy
directly, adding nothing) and a one-line "why" they are the same.

Task 2. Each policy whose stage is "general" has no stage yet. Give it one:
  - if it asks someone to do or not do something at an identifiable point, its stage: before-course | course-start |
    during-work | during-assessment | when-misuse | over-time;
  - if it is a definition, scope statement, reason, value or fact with no time of action: "background".

Return ONLY this JSON, no prose, no code fence:
{{"merges": [{{"members": ["P24.03", "P96.02"], "sentence": "...", "why": "..."}}],
  "stages": [{{"pid": "P61.01", "stage": "background"}}]}}
List only groups of 2 or more in "merges". List every "general" policy in "stages".

{lines}
"""


def dedupe(layer, model):
    if layer == "inst":
        pol = [q | {"type": t} for t, qs in json.loads((OUT / "positions.json").read_text()).items() for q in qs]
        tname = {t["id"]: t.get("name") for t in json.loads((V2 / "site" / "data" / "types.json").read_text())}
        what = "US university, school and computing-department generative-AI policies"
    else:
        pol, _ = course_policies()
        pol = [q for q in pol if q["about_ai"] == "yes"]
        tname = {t["id"]: t["name"] for t in json.loads((V2 / "course_codebook.json").read_text())["types"]} | {"OTHER": "Other"}
        what = "US computer-science course syllabi (generative-AI policies)"
    R = OUT / f"dedupe_{layer}"
    R.mkdir(exist_ok=True)
    by = defaultdict(list)
    for q in pol:
        by[GROUP.get(q["actor"], q["actor"])].append(q)

    def one(g):
        if (R / f"{g}.json").exists():
            return g, "done"
        qs = sorted(by[g], key=lambda q: (q["type"], q["pid"]))
        lines = "\n".join(f"{q['pid']} | {tname.get(q['type'], q['type'])} | {q['phase']} | {q['n_unis']} | {q['sentence']}" for q in qs)
        ids = {q["pid"] for q in qs}
        gen = {q["pid"] for q in qs if q["phase"] == "general"}
        for _ in range(1 if FILES else 3):
            res = claude(DPROMPT.format(what=what, who=GROUP_NAME[g], lines=lines), model, f"dedupe_{layer}_{g}")
            if not res:
                continue
            ms = [m for x in res.get("merges", []) for m in x.get("members", [])]
            if len(ms) != len(set(ms)) or not set(ms) <= ids:
                continue
            stg = {x["pid"]: x["stage"] for x in res.get("stages", []) if x.get("pid") in gen and x.get("stage") in STAGES}
            if gen - set(stg):
                continue
            res["model"] = model
            (R / f"{g}.json").write_text(json.dumps(res, indent=1))
            return g, f"ok: {len(res.get('merges', []))} merges covering {len(ms)} of {len(qs)} policies; {len(stg)} stages set"
        return g, "FAILED"

    with ThreadPoolExecutor(4) as ex:
        for g, msg in ex.map(one, list(by)):
            print(layer, g, msg, flush=True)


# ---------------------------------------------------------------- UNCOVERED statements (D64)
UPROMPT = """Each numbered statement below comes from a US university generative-AI policy document but fit none of the
policy topics during coding. Decide for each:
  "place": it states one of the existing policies listed under POLICIES (same meaning, same actor) -> give that policy id;
  "not_ai": it is not about AI (generic rules, unrelated content);
  "not_policy": it is about AI but states no rule, recommendation, reason or fact a policy would keep (navigation text,
               headings, event notices, contact lines);
  "unique": it is an AI policy that none of the listed policies states (a rare, specific policy).
Return ONLY this JSON, no prose, no code fence:
{{"decisions": [{{"n": 0, "decision": "place", "pid": "P31.02"}}, {{"n": 1, "decision": "unique"}}]}}
Decide every statement.

STATEMENTS (n | actor | AI-normalized statement | original wording)
{stmts}

POLICIES (id | actor group | sentence)
{pols}
"""


def uncovered(model):
    final = json.loads((OUT / "final.json").read_text())["institutional"]
    pols = "\n".join(f"{q['pid']} | {q['actor']} | {q['sentence']}" for q in final)
    allp = json.loads((V2 / "site" / "data" / "policies.json").read_text())
    un = sorted((x for x in allp if x["about_ai"] == "yes" and x["type"] == "UNCOVERED"), key=lambda x: x["id"])
    R = OUT / "uncovered"
    R.mkdir(exist_ok=True)
    clean = lambda s: re.sub(r"\s+", " ", s or "").replace("|", "/").strip()
    batches = [un[k:k + 120] for k in range(0, len(un), 120)]
    valid = {q["pid"] for q in final}

    def one(k):
        f = R / f"b{k:02d}.json"
        if f.exists():
            return k, "done"
        xs = batches[k]
        stmts = "\n".join(f"{i} | {x['actor']} | {clean(x.get('policy') or x['anchor'])} | {clean(x['anchor'])}" for i, x in enumerate(xs))
        for _ in range(1 if FILES else 3):
            res = claude(UPROMPT.format(stmts=stmts, pols=pols), model, f"uncovered_b{k:02d}")
            ds = (res or {}).get("decisions", [])
            if sorted(d.get("n") for d in ds) == list(range(len(xs))) and all(d["decision"] != "place" or d.get("pid") in valid for d in ds):
                f.write_text(json.dumps({"ids": [x["id"] for x in xs], "decisions": ds, "model": model}, indent=1))
                return k, "ok " + str(Counter(d["decision"] for d in ds))
        return k, "FAILED"

    with ThreadPoolExecutor(3) as ex:
        for k, msg in ex.map(one, range(len(batches))):
            print("uncovered batch", k, msg, flush=True)


# ---------------------------------------------------------------- course statements coded after grouping (2026-11-02)
PPROMPT = """Each numbered statement below comes from a CS course syllabus passage about generative AI that was coded after the
course policies were built. Decide for each:
  "place": it states one of the existing COURSE POLICIES listed below (same meaning, same actor) -> give that policy id;
  "new": it states a course policy none of them states -> give "sentence" (the policy stated directly, at most 20 words,
         naming its actor), "actor" (student|instructor|ta-staff|all) and "stage" (one of {stages});
  "not_ai": it is not about AI (generic course or integrity rules).
Statements from the same passage that state the same new policy must get the identical "sentence".
Return ONLY this JSON, no prose, no code fence:
{{"decisions": [{{"n": 0, "decision": "place", "pid": "CT17.c02"}}, {{"n": 1, "decision": "new", "sentence": "...", "actor": "student", "stage": "during-work"}}]}}
Decide every statement.

STATEMENTS (n | university | course slot | course topic | actor | force | coder label | original wording)
{stmts}

COURSE POLICIES (id | actor | stage | sentence)
{pols}
"""


def course_place(model):
    F = json.loads((OUT / "final.json").read_text())
    have = {s for q in F["course"] for s in q["members"]} | {s for g in F.get("course_not_ai", []) for s in g}
    rows = [r | {"type": t} for t, rs in course_rows().items() for r in rs if r["sid"] not in have]
    if not rows:
        return print("no new course statements")
    cb = {t["id"]: t["name"] for t in json.loads((V2 / "course_codebook.json").read_text())["types"]}
    clean = lambda x: re.sub(r"\s+", " ", x or "").replace("|", "/").strip()
    stmts = "\n".join(f"{i} | {r['uni']} | {r['slot']} | {cb.get(r['type'], 'Other')} | {r['actor']} | {r['modality']} | {clean(r['label'])} | {clean(r['anchor'])}" for i, r in enumerate(rows))
    pols = "\n".join(f"{q['pid']} | {q['actor']} | {q['phase']} | {q['sentence']}" for q in F["course"])
    res = claude(PPROMPT.format(stages="|".join(STAGES), stmts=stmts, pols=pols), model, "course_place")
    ds = (res or {}).get("decisions", [])
    ok = sorted(d.get("n") for d in ds) == list(range(len(rows))) and all(
        (d["decision"] == "place" and d.get("pid") in {q["pid"] for q in F["course"]}) or (d["decision"] == "new" and d.get("sentence") and d.get("stage") in STAGES)
        or d["decision"] == "not_ai" for d in ds)
    if ok:
        (OUT / "course_place.json").write_text(json.dumps({"sids": [r["sid"] for r in rows], "decisions": ds, "model": model}, indent=1))
    print(f"{len(rows)} new course statements:", "ok " + str(Counter(d["decision"] for d in ds)) if ok else "FAILED")


# ---------------------------------------------------------------- apply
def merged(pols, layer, label_of, uni_of, phase_of):
    """Apply dedupe merges and stage decisions to a policy list; returns final policies (ids kept from the largest part)."""
    R = OUT / f"dedupe_{layer}"
    by = {q["pid"]: q for q in pols}
    stage, groups = {}, []
    for f in R.glob("*.json"):
        res = json.loads(f.read_text())
        stage |= {x["pid"]: x["stage"] for x in res.get("stages", [])}
        groups += [g for g in res.get("merges", []) if len([m for m in g["members"] if m in by]) > 1]
    done, out = set(), []
    for g in groups + [{"members": [p]} for p in by]:
        ms = [m for m in g["members"] if m in by and m not in done]
        if not ms:
            continue
        done |= set(ms)
        parts = sorted((by[m] for m in ms), key=lambda q: -q["n_unis"])
        head = parts[0]
        mem = list(dict.fromkeys(s for q in parts for s in q["members"]))
        ex = []
        for s in [e for q in parts for e in q["examples"]]:
            if uni_of(s) not in {uni_of(e) for e in ex}:
                ex.append(s)
        ph = Counter()
        for q in parts:
            ph[stage.get(q["pid"], q["phase"]) if q["phase"] == "general" else q["phase"]] += q["n"]
        who = Counter((label_of(s)[0], label_of(s)[1]) for s in mem)
        types = list(dict.fromkeys(q["type"] for q in parts))
        out.append({"pid": head["pid"], "sentence": (g.get("sentence") or head["sentence"]).strip(), "merge_why": g.get("why", ""),
                    "actor": GROUP.get(head["actor"], head["actor"]), "phase": ph.most_common(1)[0][0],
                    "kind": "background" if ph.most_common(1)[0][0] == "background" else "action",
                    "type": types[0], "types": types, "n": len(mem), "n_unis": len({uni_of(s) for s in mem}),
                    "who": [[a, m, k] for (a, m), k in who.most_common()], "examples": ex[:3], "members": mem,
                    "parts": [{"pid": q["pid"], "type": q["type"], "sentence": q["sentence"]} for q in parts]})
    out.sort(key=lambda q: (STAGES.index(q["phase"]) if q["phase"] in STAGES else 99, -q["n_unis"]))
    return out


def apply():
    allp = {x["id"]: x for x in json.loads((V2 / "site" / "data" / "policies.json").read_text())}
    inst = [q | {"type": t} for t, qs in json.loads((OUT / "positions.json").read_text()).items() for q in qs]
    I = merged(inst, "inst", lambda s: (GROUP.get(allp[s]["actor"], allp[s]["actor"]), allp[s]["modality"]), lambda s: allp[s]["uni"], None)
    # D64: UNCOVERED placements join their policy; other decisions are recorded per statement
    placed, setaside = {}, {}
    for f in sorted((OUT / "uncovered").glob("*.json")) if (OUT / "uncovered").exists() else []:
        res = json.loads(f.read_text())
        for d in res["decisions"]:
            sid = res["ids"][d["n"]]
            if d["decision"] == "place":
                placed[sid] = d["pid"]
            else:
                setaside[sid] = d["decision"]
    owner = {m: q for q in I for p in q["parts"] for m in [p["pid"]]}
    for sid, pid in placed.items():
        q = owner.get(pid) or next((x for x in I if x["pid"] == pid), None)
        if q and sid not in q["members"]:
            q["members"].append(sid)
            q["n"] += 1
            q["n_unis"] = len({allp[m]["uni"] for m in q["members"] if m in allp})
            q.setdefault("placed", []).append(sid)
    C, crow = course_policies()
    Cai = [q for q in C if q["about_ai"] == "yes"]
    Cf = merged(Cai, "course", lambda s: (GROUP.get(crow[s]["actor"], crow[s]["actor"]), crow[s]["modality"]), lambda s: crow[s]["uni"], None)
    # course statements coded after grouping: placed in a course policy, a new course policy, or set aside as not about AI
    cpf = OUT / "course_place.json"
    if cpf.exists():
        cp = json.loads(cpf.read_text())
        cown = {p["pid"]: q for q in Cf for p in q["parts"]}
        new = {}
        for d in cp["decisions"]:
            sid = cp["sids"][d["n"]]
            if d["decision"] == "place" and d["pid"] in cown:
                q = cown[d["pid"]]
                q["members"].append(sid)
                q.setdefault("placed", []).append(sid)
            elif d["decision"] == "new":
                new.setdefault((d["sentence"].strip(), GROUP.get(d.get("actor"), d.get("actor") or "student"), d["stage"]), []).append(sid)
        for k, ((sent, act, stg), mem) in enumerate(sorted(new.items()), 1):
            Cf.append({"pid": f"CNEW.c{k:02d}", "sentence": sent, "merge_why": "", "actor": act, "phase": stg, "kind": "background" if stg == "background" else "action",
                       "type": crow[mem[0]].get("type", "OTHER") if "type" in crow[mem[0]] else "OTHER", "types": [], "members": mem, "examples": [m for m in mem if crow[m]["verified"]][:3],
                       "parts": [{"pid": f"CNEW.c{k:02d}", "type": "", "sentence": sent}], "placed": mem})
        for q in Cf:
            if q.get("placed"):
                q["n"], q["n_unis"] = len(q["members"]), len({crow[m]["uni"] for m in q["members"]})
                q["who"] = [[a, m, c] for (a, m), c in Counter((GROUP.get(crow[s]["actor"], crow[s]["actor"]), crow[s]["modality"]) for s in q["members"]).most_common()]
        ctype = {r["sid"]: t for t, rs in course_rows().items() for r in rs}
        for q in Cf:
            if q["pid"].startswith("CNEW"):
                q["type"] = ctype.get(q["members"][0], "OTHER")
                q["types"] = [q["type"]]
                q["who"] = [[a, m, c] for (a, m), c in Counter((GROUP.get(crow[s]["actor"], crow[s]["actor"]), crow[s]["modality"]) for s in q["members"]).most_common()]
    # what kind of text each policy is (D66): rule / recommendation / template / description from its statements' binding
    # (institutional) or force (course); background policies carry their background kind and policy-document section
    bk = {}
    bf = OUT / "answers" / "bgkind.json"
    if bf.exists():
        bk = {x["pid"]: x for x in parse(bf.read_text())["items"]}
    for q in I:
        b = Counter(allp[m]["binding"] for m in q["members"] if m in allp and allp[m].get("binding"))
        q["binding"] = dict(b)
        q["policy_kind"] = "background" if q["kind"] == "background" else (b.most_common(1)[0][0] if b else "description")
    for q in Cf:
        f = Counter(crow[m]["modality"] for m in q["members"])
        top = f.most_common(1)[0][0]
        q["policy_kind"] = "background" if q["kind"] == "background" else {"should": "recommendation", "should-not": "recommendation", "informs": "description"}.get(top, "rule")
    for q in I + Cf:
        if q["kind"] == "background" and q["pid"] in bk:
            q["bg_kind"], q["section"] = bk[q["pid"]]["kind"], bk[q["pid"]].get("section", "")
            if bk[q["pid"]]["kind"] == "rule":  # misplaced as background: treat as an action policy without a stage
                q["kind"], q["policy_kind"] = "action", "recommendation"
    out = {"institutional": I, "course": Cf, "course_not_ai": [q["members"] for q in C if q["about_ai"] != "yes"],
           "pipeline": {"fine_positions": sum(len(v) for v in json.loads((OUT / "positions_fine.json").read_text()).values()),
                        "force_merged": len(inst), "cross_type_merged": len(I), "course_grouped": len(C), "course_not_ai_groups": len(C) - len(Cai),
                        "course_not_ai_statements": sum(q["n"] for q in C if q["about_ai"] != "yes"), "course_merged": len(Cf)},
           "uncovered_set_aside": setaside, "pid_alias": {p["pid"]: q["pid"] for qs in (I, Cf) for q in qs for p in q["parts"]}}
    (OUT / "final.json").write_text(json.dumps(out, indent=1))
    print(f"institutional: {len(inst)} policies -> {len(I)} after dedupe ({sum(len(q['types']) > 1 for q in I)} span 2+ types); "
          f"background {sum(q['kind'] == 'background' for q in I)}; UNCOVERED placed {len(placed)}, set aside {dict(Counter(setaside.values()))}")
    print(f"course: {len(C)} policies ({len(C) - len(Cai)} not about AI) -> {len(Cf)} after dedupe; background {sum(q['kind'] == 'background' for q in Cf)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["course", "dedupe", "uncovered", "apply", "course-place"])
    ap.add_argument("--layer", default="inst")
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--model", default=None)
    a = ap.parse_args()
    if a.cmd == "course":
        course(a.workers, a.model or "sonnet")
    elif a.cmd == "dedupe":
        dedupe(a.layer, a.model or "opus")
    elif a.cmd == "course-place":
        course_place(a.model or "sonnet")
    elif a.cmd == "uncovered":
        uncovered(a.model or "sonnet")
    else:
        apply()


if __name__ == "__main__":
    main()
