#!/usr/bin/env python3
"""Render v2/decisions.json as a methods-ready Markdown file: v2/METHODS_DECISIONS.md."""
import json
from pathlib import Path

V2 = Path(__file__).resolve().parents[1]
d = json.loads((V2 / "decisions.json").read_text())
out = ["# Study decisions (methods register)", "",
       "Every design decision, grouped by methods section. Each entry lists its id, date, who decided it, the decision, and the rationale. Generated from `v2/decisions.json`; do not edit by hand.", ""]
# sections listed in decisions.json first, then any section a later decision introduced, in order of first use
secs = list(d["sections"]) + [x["section"] for x in d["decisions"] if x["section"] not in d["sections"]]
for sec in dict.fromkeys(secs):
    rows = [x for x in d["decisions"] if x["section"] == sec]
    if not rows:
        continue
    out += [f"## {sec}", ""]
    for x in rows:
        out.append(f"- **{x['id']}** ({x['date']}, decided by {x['by']}). {x['decision']} *Rationale:* {x['rationale']}")
    out.append("")
(V2 / "METHODS_DECISIONS.md").write_text("\n".join(out))
print("wrote v2/METHODS_DECISIONS.md", len(d["decisions"]), "decisions")
