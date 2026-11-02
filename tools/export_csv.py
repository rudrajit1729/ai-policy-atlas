#!/usr/bin/env python3
"""Export the verified corpus and reconciliation as CSVs for analysis and the paper's appendix."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
c = json.loads((ROOT / "corpus" / "corpus.json").read_text())
s = json.loads((ROOT / "corpus" / "synthesis.json").read_text())
g_of = {i: g["id"] for g in s["guidelines"] for i in g["members"]}
g_label = {g["id"]: g["label"] for g in s["guidelines"]}
out = ROOT / "exports"
out.mkdir(exist_ok=True)
with open(out / "documents.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["doc_id", "university", "country", "region", "unit", "level", "course", "title", "url", "archive_url",
                "date_or_term", "stance", "n_statements", "search_group", "analyst_summary"])
    for d in c["documents"]:
        w.writerow([d["id"], d["university"], d["country"], d.get("region"), d["unit"], d["level"], d.get("course"),
                    d["title"], d["url"], d.get("archive_url", ""), d.get("date_or_term"), d["stance"],
                    len(d["excerpts"]), d.get("group"), d.get("summary")])
with open(out / "statements.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["statement_id", "doc_id", "university", "verbatim_text", "verified", "topics", "phase", "actor",
                "guideline_id", "guideline_label", "highlight_link"])
    for d in c["documents"]:
        for e in d["excerpts"]:
            gid = g_of.get(e["id"], "")
            w.writerow([e["id"], d["id"], d["university"], e["text"], e["verified"], ";".join(e.get("topics", [])),
                        e.get("phase"), e.get("actor"), gid, g_label.get(gid, ""), e.get("link")])
with open(out / "searched_institutions.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["university", "result", "search_group", "notes"])
    for x in c["searched_universities"]:
        w.writerow([x["university"], x["result"], x.get("group"), x.get("notes")])
print("wrote exports/documents.csv, statements.csv, searched_institutions.csv")
