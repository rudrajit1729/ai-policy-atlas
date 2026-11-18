#!/usr/bin/env python3
"""Assemble v2/role_items.json (D79) from the round-2 and round-3 analyst outputs.

Round 2 (out_<k>.json): clearer group labels per cell, merges of identical asks (one pair), and the AI link of policies whose
sentence never names AI ("context": directive rewritten so the AI link is explicit; "general": an integrity or procedural rule
restated in an AI document). Round 3 (clusters_<k>.json): inside each group, policies making the same point become one entry,
led by the most widespread policy, with the others shown as variants and a note on how each differs.
A variant is split back into its own entry when the lead and the variant point in opposite directions (one bans, the other
permits: "Do not ..."/"Never ..."/"Avoid ..." against "You may ..."), since those are contrasting positions, not variants;
SPLIT lists further manual splits (a ban paired with a softer limit, and one uncertain cluster).
Usage: assemble_role_items.py <dir with out_1..3.json and clusters_1..3.json>
"""
import json
import re
import sys
from pathlib import Path

V2 = Path(__file__).resolve().parents[1]
RELABEL = {"No unauthorized notes or devices in exams": "Do not use AI or other aids during exams"}
SPLIT = {"P46.03", "P39.03", "P101.06", "P51.09", "P109.09"}
OVERRIDE = {"P22.03": {"class": "context", "directive": "Do not use AI or other unauthorized resources, such as notes, electronic devices or the internet, during an exam; doing so is cheating.",
                        "why": "4 of 8 universities name AI explicitly (Nebraska-Lincoln, Pittsburgh, Vermont, William & Mary); the CUNY campuses ban devices used to generate information, in AI documents."}}
BAN = re.compile(r"^(do not|don't|never|you must not|you may not|you should not|you cannot|avoid|nobody|no one)\b", re.I)
PERMIT = re.compile(r"^(you may|you can|you are allowed|you are welcome)\b(?!.{0,12}\bnot\b)", re.I)
dirn = lambda t: "ban" if BAN.search(t.strip()) else "permit" if PERMIT.search(t.strip()) else "do"


def main():
    d = Path(sys.argv[1])
    DIRV = json.loads((V2 / "role_directives.json").read_text())
    cells, ail, split = {}, {}, []
    for k in "123":
        O = json.loads((d / f"out_{k}.json").read_text())
        Cl = json.loads((d / f"clusters_{k}.json").read_text())["cells"]
        ail.update(O.get("ai_link", {}))
        ail.update({p: v for p, v in OVERRIDE.items() if p in ail or k == "1"})
        merged = {pid: it["directive"] for grs in O["cells"].values() for g in grs for it in g["items"] if len(it["pids"]) > 1 for pid in it["pids"]}
        dirof = lambda pid: merged.get(pid) or (ail.get(pid, {}).get("directive") if ail.get(pid, {}).get("class") == "context" else None) or DIRV.get(pid, "")
        for ck, grs in Cl.items():
            out = []
            for g in grs:
                items = []
                for it in g["items"]:
                    lead, keep, alone = it["lead"], [], []
                    for v in it.get("variants", []):
                        a, b = dirof(lead), dirof(v["pid"])
                        if v["pid"] in SPLIT or {dirn(a), dirn(b)} == {"ban", "permit"}:
                            alone.append(v["pid"])
                            split.append((ck, lead, v["pid"], v["differs"]))
                        else:
                            keep.append(v)
                    items.append({"pids": [lead] + [v["pid"] for v in keep], "directive": dirof(lead), "variants": keep})
                    items += [{"pids": [p], "directive": dirof(p), "variants": []} for p in alone]
                out.append({"label": RELABEL.get(g["label"], g["label"]), "items": items})
            cells[ck] = out
    (V2 / "role_items.json").write_text(json.dumps({"cells": cells, "ai_link": ail}, ensure_ascii=False, indent=1))
    nv = sum(len(i["variants"]) for grs in cells.values() for g in grs for i in g["items"])
    ni = sum(1 for grs in cells.values() for g in grs for i in g["items"] if i["variants"])
    print(f"cells {len(cells)}; entries with variants {ni}; variants {nv}; split back {len(split)}")
    for s in split:
        print("  split:", *s)


if __name__ == "__main__":
    main()
