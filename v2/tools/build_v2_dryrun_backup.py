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
ACTORS = ["student", "instructor", "ta-staff", "admin", "all"]
PHASES = ["general", "before-course", "course-start", "during-work", "during-assessment", "when-misuse", "over-time"]
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


def main():
    types_src = json.loads((V2 / "policy_types.json").read_text()) if (V2 / "policy_types.json").exists() \
        else json.loads((V2 / "policy_types_v0.json").read_text())
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
                anchor = exact(x["anchor"], hay, hay_fold, hay_map) if hay else None
                if not anchor:
                    issues.append(f"{uid}: anchor not verbatim")
                fs = exact(x.get("frag_start", ""), hay, hay_fold, hay_map) if hay else None
                fe = exact(x.get("frag_end", ""), hay, hay_fold, hay_map) if hay else None
                units.append({
                    "id": uid, "uni": u["slug"], "doc": d["id"], "layer": d["layer"], "stance": d["stance"],
                    "anchor": anchor or x["anchor"], "verified": bool(anchor),
                    "policy": x.get("policy"), "actor": x["actor"], "phase": x["phase"], "modality": x["modality"],
                    "type": x["policy_type"], "topics": x.get("topics", []),
                    "link": frag_link(d["url"], fs or anchor, fe),
                })
                ids.append(uid)
            docs.append({k: d.get(k) for k in ("id", "layer", "unit", "course", "title", "url", "date_or_term", "stance", "tiers", "summary")} | {"units": ids})
        docs.sort(key=lambda d: (LAYERS.index(d["layer"]), d.get("unit") or "", d.get("course") or ""))
        unis.append({"slug": u["slug"], "name": u["university"], "state": u.get("state"), "type": u.get("type"),
                     "searched": u.get("searched", {}), "notes": u.get("notes", ""), "documents": docs})

    # policy types: counts, representative unit (analyst-chosen in representatives.json, else most typical)
    by_type = defaultdict(list)
    for x in units:
        by_type[x["type"]].append(x)
    types = []
    for t in types_src["types"]:
        mem = by_type.get(t["id"], [])
        rep = reps.get(t["id"])
        if not rep and mem:
            # default: a verified unit from the most common (actor, modality) cell, preferring anchor-only units
            common = Counter((m["actor"], m["modality"]) for m in mem).most_common(1)[0][0]
            cands = [m for m in mem if (m["actor"], m["modality"]) == common and m["verified"]]
            cands.sort(key=lambda m: (m["policy"] is not None, len(m["policy"] or m["anchor"])))
            rep = (cands or mem)[0]["id"]
        types.append(t | {"n_units": len(mem), "n_unis": len({m["uni"] for m in mem}), "rep": rep})
    new = Counter(x["type"] for x in units if x["type"].startswith("NEW:"))

    meta = {"stances": STANCES, "actors": ACTORS, "phases": PHASES, "layers": LAYERS, "themes": types_src["themes"],
            "n_universities": len(unis), "n_documents": sum(len(u["documents"]) for u in unis), "n_units": len(units),
            "n_verified": sum(x["verified"] for x in units), "unmapped_new_types": dict(new)}
    for name, obj in (("universities", unis), ("policies", units), ("types", types), ("meta", meta)):
        (OUT / f"{name}.json").write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")))
    (V2 / "build_issues.txt").write_text("\n".join(issues) + "\n")
    print(f"{len(unis)} universities, {meta['n_documents']} documents, {len(units)} units "
          f"({meta['n_verified']} verbatim-verified), {len(issues)} issues, new types: {dict(new)}")


if __name__ == "__main__":
    main()
