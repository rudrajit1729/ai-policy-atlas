#!/usr/bin/env python3
"""Compare the CS course layer with the institutional layers (D43, D49). Deterministic.

Inputs: v2/course_code/course_assignments.json (course types per statement), v2/course_code/results (passage stance),
v2/course_alignment.json (course type -> institutional types), v2/theme_review/final_assignments.json, v2/inst (document stance).
Writes v2/exports/layer_comparison.json and prints a summary:
  1. alignment: share of course statements whose type has the same / a partial / no institutional counterpart
  2. course types: statements, universities, relation, institutional prevalence of the counterpart
  3. institutional types common at universities (>= 100) that no course type covers ("never reach syllabi")
  4. stance by course slot (C1..C6) and versus the same university's institutional stance
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "v2"


def main():
    ca = json.loads((V2 / "course_code" / "course_assignments.json").read_text())
    st = ca["statements"]
    amap = json.loads((V2 / "course_alignment.json").read_text())["map"]
    cb = {t["id"]: t for t in json.loads((V2 / "course_codebook.json").read_text())["types"]}
    v3 = {t["id"]: t for t in json.loads((V2 / "policy_types_v3.json").read_text())["types"]}
    fa = json.loads((V2 / "theme_review" / "final_assignments.json").read_text())
    inst_unis = defaultdict(set)
    for uid, r in fa.items():
        if r["about_ai"] == "yes":
            inst_unis[r["type"]].add(r["university"])
    # 1-2 course types
    ct_n, ct_u = Counter(), defaultdict(set)
    for sid, r in st.items():
        uni = sid.split("|")[0]
        ct_n[r["type"]] += 1
        ct_u[r["type"]].add(uni)
    total = sum(ct_n.values())
    rel = Counter()
    for t, n in ct_n.items():
        rel[amap.get(t, {}).get("relation", "other")] += n
    types = []
    for t in cb:
        m = amap.get(t, {})
        types.append({"id": t, "name": cb[t]["name"], "theme": cb[t]["theme"], "statements": ct_n.get(t, 0), "universities": len(ct_u.get(t, ())),
                      "relation": m.get("relation"), "institutional": m.get("institutional", []), "why": m.get("why"),
                      "institutional_universities": len(set().union(*[inst_unis.get(p, set()) for p in m.get("institutional", [])])) if m.get("institutional") else 0})
    # 3 institutional types that never reach syllabi
    covered = {p for m in amap.values() for p in m["institutional"]}
    missing = sorted([{"id": p, "name": v3[p]["name"], "universities": len(u)} for p, u in inst_unis.items()
                      if p in v3 and p not in covered and len(u) >= 100], key=lambda x: -x["universities"])
    # 4 stance by slot and vs institution
    pstance, pslot = {}, {}
    for f in (V2 / "course_code" / "results").glob("*.json"):
        for p in json.loads(f.read_text())["passages"]:
            pstance[p["pid"]] = p["passage_stance"]
            pslot[p["pid"]] = p["pid"].split("|")[1]
    by_slot = defaultdict(Counter)
    for pid, s in pstance.items():
        by_slot[pslot[pid]][s] += 1
    uni_stance = {}
    for f in (V2 / "inst").glob("*.json"):
        d = json.loads(f.read_text())
        c = Counter(x.get("stance") for x in d["documents"] if x["layer"] == "university")
        if c:
            uni_stance[d["slug"]] = c.most_common(1)[0][0]
    cross = Counter()
    for pid, s in pstance.items():
        u = pid.split("|")[0]
        if u in uni_stance:
            cross[(uni_stance[u], s)] += 1
    out = {"course_statements": total, "alignment_share": {k: round(v / total, 3) for k, v in rel.items()},
           "course_types": sorted(types, key=lambda x: -x["statements"]), "never_reach_syllabi": missing,
           "stance_by_slot": {k: dict(v) for k, v in sorted(by_slot.items())},
           "university_vs_course_stance": {f"{a} -> {b}": n for (a, b), n in cross.most_common()},
           "type_alpha": ca.get("alpha_type"), "type_agreement": ca.get("percent_agreement"), "alpha_pairs": ca.get("pairs")}
    (V2 / "exports" / "layer_comparison.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(f"{total} course statements; alignment {out['alignment_share']}")
    print("top course types:", [(t["id"], t["name"], t["statements"], t["relation"]) for t in out["course_types"][:12]])
    print("no-counterpart types:", [(t["id"], t["name"], t["statements"], t["universities"]) for t in out["course_types"] if t["relation"] == "none"])
    print("never reach syllabi:", [(m["id"], m["name"], m["universities"]) for m in missing[:20]])
    print("stance by slot:", out["stance_by_slot"])
    print("university -> course stance:", list(out["university_vs_course_stance"].items())[:12])


if __name__ == "__main__":
    main()
