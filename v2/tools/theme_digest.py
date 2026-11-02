#!/usr/bin/env python3
"""Aggregate the theme-review tags (D46 step 1) into a digest for synthesis (step 2).

Writes v2/theme_review/digest.json and prints a compact per-type report:
units reviewed, universities, about_ai = no, binding mix, moves out (to which types), NEW labels (with universities),
subgroups proposed by reviewers, coherence votes and name suggestions.
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TR = ROOT / "v2" / "theme_review"


def main():
    types = {t["id"]: t for t in json.loads((ROOT / "v2" / "policy_types.json").read_text())["types"]}
    agg = defaultdict(lambda: {"n": 0, "unis": set(), "no_ai": 0, "binding": Counter(), "moves": Counter(), "new": defaultdict(set),
                               "subgroups": [], "coherence": Counter(), "names": []})
    moved_in = Counter()
    for tp in sorted(TR.glob("tags/*.json")):
        t = json.loads(tp.read_text())
        pk = json.loads((TR / "packets" / tp.name).read_text())
        uni = {u["uid"]: u["university"] for u in pk["units"]}
        a = agg[t["current_type"]]
        a["coherence"][t.get("coherence")] += 1
        a["names"].append(t.get("name_suggestion"))
        for g in t.get("subgroups", []):
            a["subgroups"].append({"label": g["label"], "definition": g.get("definition"), "n": len(g["uids"]),
                                   "universities": len({uni[x] for x in g["uids"] if x in uni})})
        for u in t["units"]:
            a["n"] += 1
            a["unis"].add(uni.get(u["uid"]))
            a["no_ai"] += u["about_ai"] == "no"
            a["binding"][u["binding"]] += 1
            ty = u["type"]
            if ty.startswith("NEW: "):
                a["new"][ty[5:].strip()].add(uni.get(u["uid"]))
            elif ty != "keep":
                a["moves"][ty] += 1
                moved_in[ty] += 1
    new_all = defaultdict(set)
    for k, a in agg.items():
        for lab, us in a["new"].items():
            new_all[lab.lower()] |= us
    out = {k: {"name": types.get(k, {}).get("name", k), "n": a["n"], "universities": len(a["unis"]), "no_ai": a["no_ai"],
               "binding": dict(a["binding"]), "moves_out": dict(a["moves"].most_common()), "moved_in": moved_in.get(k, 0),
               "new": {lab: sorted(us) for lab, us in sorted(a["new"].items(), key=lambda x: -len(x[1]))},
               "subgroups": a["subgroups"], "coherence": dict(a["coherence"]), "name_suggestions": a["names"]}
           for k, a in sorted(agg.items())}
    (TR / "digest.json").write_text(json.dumps({"by_type": out, "new_labels": {k: sorted(v) for k, v in
                                                sorted(new_all.items(), key=lambda x: -len(x[1]))}}, indent=1, ensure_ascii=False))
    tot = sum(a["n"] for a in agg.values())
    print(f"{tot} units reviewed in {len(agg)} types; about_ai=no: {sum(a['no_ai'] for a in agg.values())}; "
          f"NEW labels: {len(new_all)} ({sum(1 for v in new_all.values() if len(v) >= 3)} at 3+ universities)")


if __name__ == "__main__":
    main()
