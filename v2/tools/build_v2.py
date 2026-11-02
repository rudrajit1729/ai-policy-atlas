#!/usr/bin/env python3
"""Assemble v2/inst/*.json (reconciled per-university codings) into site data.

Writes v2/site/data/{universities,policies,types,meta}.json and v2/exports/atlas.xlsx.
Every unit gets: an id, the university/document it came from, its anchor verbatim from the
saved text (page characters substituted), and a text-fragment link to the full passage.
"""
import json
import re
import sys
import urllib.parse
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from verify_build import fold_with_map  # noqa: E402

V2 = ROOT / "v2"
OUT = V2 / "site" / "data"
OUT.mkdir(parents=True, exist_ok=True)

STANCES = ["prohibit", "restrict", "permit", "encourage", "require", "delegates"]
# D65: TAs/staff and administrators form one actor group ("staff"); the coded actor is kept as actor_coded
ACTORS = ["student", "instructor", "staff", "all"]
GROUP = {"student": "student", "instructor": "instructor", "ta-staff": "staff", "admin": "staff", "all": "all"}
# D67: the policy set is rules and recommendations ("rr") plus facts and warnings ("fact"); templates, descriptions and the
# other background (reasons, definitions, resources: "other") are kept and shown apart, never counted in the policy set
def cat_of(q):
    if q.get("policy_kind") in ("rule", "recommendation"):
        return "rr"
    if q.get("bg_kind") == "fact":
        return "fact"
    return q.get("policy_kind") if q.get("policy_kind") in ("template", "description") else "other"


# D62: a statement's stage is its policy's stage; coded 'general' becomes a stage or 'background' (definitions, reasons, facts)
PHASES = ["background", "before-course", "course-start", "during-work", "during-assessment", "when-misuse", "over-time"]
FINAL = json.loads((V2 / "positions" / "final.json").read_text()) if (V2 / "positions" / "final.json").exists() else None
LAYERS = ["university", "school", "computing", "course"]


def exact(needle, hay, hay_fold, hay_map):
    n = fold_with_map(needle)[0].strip()
    if not n:
        return None
    pos = hay_fold.find(n)
    if pos < 0:
        return None
    return re.sub(r"\s+", " ", hay[hay_map[pos]: hay_map[pos + len(n) - 1] + 1])


def frag_link(url, start, end):
    enc = lambda s: urllib.parse.quote(s, safe="")  # noqa: E731
    base = url.split("#")[0]
    if base.lower().endswith(".pdf") or not start:
        return base
    return f"{base}#:~:text={enc(start)}" + (f",{enc(end)}" if end and end != start else "")


def build_courses():
    """Course layer for the app: frame, statuses, syllabi and verbatim AI passages (cut by build_course_xlsx.py)."""
    import openpyxl
    wb = openpyxl.load_workbook(V2 / "exports" / "course_layer.xlsx", read_only=True)
    rows = list(wb["AI passages"].iter_rows(values_only=True))
    h = rows[0]
    txt = [k for k in h if k and k.startswith("ORIGINAL WORDING")][0]
    ix = {k: h.index(k) for k in h}
    pas, seen = defaultdict(list), Counter()
    for r in rows[1:]:
        if r[ix[txt]]:
            pid = f"{r[ix['university_slug']]}|{r[ix['slot']]}|{r[ix['course']]}|{r[ix['term']]}|{r[ix['passage #']]}"
            seen[pid] += 1
            if seen[pid] > 1:  # a second section of the same course and term: section suffix, as in course_code.py
                pid += f"|s{seen[pid]}"
            pas[(r[ix["university_slug"]], r[ix["slot"]])].append({"pid": pid, "term": r[ix["term"]], "text": r[ix[txt]], "url": r[ix["syllabus URL"]],
                                                                   "link": r[ix["highlight link"]] or r[ix["syllabus URL"]]})
    cap = V2 / "course_code" / "course_assignments.json"
    CA = json.loads(cap.read_text())["statements"] if cap.exists() else {}
    cc = {}
    ccp = V2 / "course_code" / "results"
    if ccp.exists():
        for f in ccp.glob("*.json"):
            for p in json.loads(f.read_text()).get("passages", []):
                cc[p["pid"]] = p
    CPOS = {m: q["pid"] for q in (FINAL or {}).get("course", []) for m in q["members"]}
    out = []
    for f in sorted((V2 / "course").glob("*.json")):
        c = json.loads(f.read_text())
        prog = c.get("program") or {}
        slots = []
        for x in sorted(c.get("courses", []), key=lambda x: x.get("slot", "")):
            sy = [{"term": y.get("term"), "year": y.get("year"), "url": y.get("url")} for y in x.get("syllabi", [])]
            slots.append({"slot": x.get("slot"), "course": x.get("course"), "title": x.get("title"), "status": x.get("status") if x.get("course") else "no-such-course",
                          "note": x.get("note"), "syllabi": sy, "passages": pas.get((c["slug"], x.get("slot")), [])})
        for sl in slots:
            for p in sl["passages"]:
                k = cc.get(p["pid"])
                if k:
                    p["stance"] = k.get("passage_stance")
                    p["labels"] = [{"label": x["label"], "stance": x["stance"], "cs": x["cs_specific"], "anchor": x["anchor"],
                                    "ct": CA.get(f"{p['pid']}#{j}", {}).get("type"), "pos": CPOS.get(f"{p['pid']}#{j}")} for j, x in enumerate(k.get("statements", []))]
        out.append({"slug": c["slug"], "name": c.get("university"), "program": prog.get("name"), "unit": prog.get("unit"), "slots": slots})
    return out


def main():
    # final codebook from the theme review (D47) when present; per-unit final type, binding and about-AI (D45-D54)
    if (V2 / "policy_types_v3.json").exists():
        v3 = json.loads((V2 / "policy_types_v3.json").read_text())
        types_src = {"themes": [{"id": th["id"], "label": th["label"], "desc": ""} for th in v3["themes"]],
                     "types": [t | {"theme": t.get("theme_v3")} for t in v3["types"] if not t.get("retired")]}
    else:
        types_src = json.loads((V2 / "policy_types.json").read_text())
    fa_p = V2 / "theme_review" / "final_assignments.json"
    FA = json.loads(fa_p.read_text()) if fa_p.exists() else {}
    reps = json.loads((V2 / "representatives.json").read_text()) if (V2 / "representatives.json").exists() else {}
    unis, units, issues = [], [], []
    for f in sorted((V2 / "inst").glob("*.json")):
        u = json.loads(f.read_text())
        collect = json.loads((V2 / "collect" / f.name).read_text()) if (V2 / "collect" / f.name).exists() else {}
        tf_by_id = {d["id"]: d.get("text_file") for d in collect.get("documents", [])}
        docs = []
        for d in u["documents"]:
            tf = d.get("text_file") or tf_by_id.get(d["id"])
            p = Path(tf) if tf and Path(tf).is_absolute() else (ROOT / tf if tf else None)
            hay = p.read_text() if p and p.exists() else ""
            hay_fold, hay_map = fold_with_map(hay)
            ids = []
            for i, x in enumerate(d.get("units", []), 1):
                uid = f"{d['id']}-u{i:02d}"
                gid = f"{u['slug']}:{uid}"  # globally unique: some document ids repeat across universities
                anchor = exact(x["anchor"], hay, hay_fold, hay_map) if hay else None
                if not anchor:
                    issues.append(f"{uid}: anchor not verbatim")
                fs = exact(x.get("frag_start", ""), hay, hay_fold, hay_map) if hay else None
                fe = exact(x.get("frag_end", ""), hay, hay_fold, hay_map) if hay else None
                rv = FA.get(f"{u['slug']}|{uid}", {})
                units.append({
                    "id": gid, "uni": u["slug"], "doc": f"{u['slug']}:{d['id']}", "layer": d["layer"], "stance": d["stance"],
                    "about_ai": rv.get("about_ai", "yes"), "binding": rv.get("binding"), "coded_type": x["policy_type"],
                    "unit_stance": x.get("unit_stance"),
                    "anchor": anchor or x["anchor"], "verified": bool(anchor),
                    "policy": x.get("policy"), "actor": x["actor"], "phase": x["phase"], "modality": x["modality"],
                    "type": rv.get("type", x["policy_type"]), "topics": x.get("topics", []),
                    "link": frag_link(d["url"], fs or anchor, fe),
                })
                ids.append(gid)
            docs.append({k: d.get(k) for k in ("layer", "unit", "course", "title", "url", "date_or_term", "stance", "tiers", "summary")}
                        | {"id": f"{u['slug']}:{d['id']}", "units": ids})
        docs.sort(key=lambda d: (LAYERS.index(d["layer"]), d.get("unit") or "", d.get("course") or ""))
        unis.append({"slug": u["slug"], "name": u["university"], "state": u.get("state"), "type": u.get("type"),
                     "searched": u.get("searched", {}), "notes": u.get("notes", ""), "documents": docs})

    # D62-D65: policies (final.json) give each statement its policy, stage and actor group; UNCOVERED statements placed in
    # a policy take that policy's type (D64); the rest are set aside with a reason (not about AI ones are not counted)
    if FINAL:
        byid = {x["id"]: x for x in units}
        for q in FINAL["institutional"]:
            for m in q["members"]:
                x = byid.get(m)
                if not x:
                    continue
                x["pos"], x["stage"], x["cat"] = q["pid"], q["phase"], cat_of(q)
                if x["type"] == "UNCOVERED" and m in q.get("placed", []):
                    x["type"], x["via"] = q["type"], "placed in a policy (D64)"
        for m, why in FINAL.get("uncovered_set_aside", {}).items():
            if m in byid:
                byid[m]["set_aside"] = why
                if why == "not_ai":
                    byid[m]["about_ai"] = "no"
    for x in units:
        x["actor_coded"], x["actor"] = x["actor"], GROUP.get(x["actor"], x["actor"])
        x["phase_coded"] = x["phase"]
        x["phase"] = x.get("stage") or (x["phase"] if x["phase"] != "general" else "background")
        x.pop("stage", None)

    # policy types: counts, representative unit (analyst-chosen in representatives.json, else most typical)
    by_type = defaultdict(list)
    for x in units:
        if x["about_ai"] == "yes":  # D45: statements not about AI are kept but not counted
            by_type[x["type"]].append(x)
    types = []
    for t in types_src["types"]:
        mem = by_type.get(t["id"], [])
        rep = reps.get(t["id"])
        if not rep and mem:
            # default: a verified unit from the most common (actor, modality) cell, preferring anchor-only units
            common = Counter((m["actor"], m["modality"]) for m in mem).most_common(1)[0][0]
            cands = [m for m in mem if (m["actor"], m["modality"]) == common and m["verified"]]
            # D58: a full plain statement of moderate length reads best as the example; prefer rules, then recommendations
            cands = [m for m in mem if m["verified"]] or mem
            cands.sort(key=lambda m: (m["policy"] is None, abs(len(m["policy"] or m["anchor"]) - 140),
                                      {"rule": 0, "recommendation": 1, "description": 2, "template": 3}.get(m.get("binding"), 4)))
            rep = (cands or mem)[0]["id"]
        ph = Counter(m["phase"] for m in mem)
        types.append(t | {"n_units": len(mem), "n_unis": len({m["uni"] for m in mem}), "rep": rep,
                          # lifecycle position (D55): mean phase index of the type's statements, and its most common phase
                          "rank": round(sum(PHASES.index(m["phase"]) for m in mem) / len(mem), 3) if mem else 9,
                          "phase": ph.most_common(1)[0][0] if mem else None})
    new = Counter(x["type"] for x in units if x["type"].startswith("NEW:"))

    for th in types_src["themes"]:
        ms = [m for t in types if t.get("theme") == th["id"] for m in by_type.get(t["id"], [])]
        th["rank"] = round(sum(PHASES.index(m["phase"]) for m in ms) / len(ms), 3) if ms else 9
    types_src["themes"].sort(key=lambda th: th["rank"])
    n_ai = sum(1 for x in units if x["about_ai"] == "yes")
    meta = {"stances": STANCES, "n_about_ai": n_ai, "actors": ACTORS, "phases": PHASES, "layers": LAYERS, "themes": types_src["themes"],
            "n_universities": len(unis), "n_documents": sum(len(u["documents"]) for u in unis), "n_units": len(units),
            "n_verified": sum(x["verified"] for x in units), "unmapped_new_types": dict(new)}
    courses = {"universities": build_courses(),
               "codebook": json.loads((V2 / "course_codebook.json").read_text()) if (V2 / "course_codebook.json").exists() else None,
               "comparison": json.loads((V2 / "exports" / "layer_comparison.json").read_text()) if (V2 / "exports" / "layer_comparison.json").exists() else None}
    # D59-D65: policies for the site (members dropped; statements carry 'pos'); course policies go with the course data
    positions = [{k: v for k, v in q.items() if k not in ("members", "placed")} | {"cat": cat_of(q)} for q in (FINAL or {}).get("institutional", [])]
    if FINAL:
        meta["pipeline"] = FINAL["pipeline"] | {"set_aside": dict(Counter(FINAL.get("uncovered_set_aside", {}).values())),
                                                "placed": sum(len(q.get("placed", [])) for q in FINAL["institutional"])}
    if FINAL:
        crow = {}
        for f in (V2 / "course_code" / "results").glob("*.json"):
            for p in json.loads(f.read_text())["passages"]:
                for j, x in enumerate(p["statements"]):
                    crow[f"{p['pid']}#{j}"] = x["anchor"]
        pas = {pp["pid"]: (u["slug"], pp["link"]) for u in courses["universities"] for sl in u["slots"] for pp in sl["passages"]}
        courses["policies"] = [{k: v for k, v in q.items() if k != "members"} | {"cat": cat_of(q), "examples": [
            {"anchor": crow.get(e, ""), "uni": pas.get(e.split("#")[0], ("", ""))[0], "link": pas.get(e.split("#")[0], ("", ""))[1]} for e in q["examples"]]}
            for q in FINAL["course"]]
    for name, obj in (("universities", unis), ("policies", units), ("types", types), ("meta", meta), ("courses", courses), ("positions", positions)):
        (OUT / f"{name}.json").write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")))
    (V2 / "build_issues.txt").write_text("\n".join(issues) + "\n")
    print(f"{len(unis)} universities, {meta['n_documents']} documents, {len(units)} units "
          f"({meta['n_verified']} verbatim-verified), {len(issues)} issues, new types: {dict(new)}")


if __name__ == "__main__":
    main()
