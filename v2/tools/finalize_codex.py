#!/usr/bin/env python3
"""One-call wrap-up after the Codex jobs (D57): fresh-audit error rates, critique summary, C5/C6 status, and rebuild of the
course Excel, app data and findings page. Prints a short summary only."""
import glob
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "v2"
sys.path.insert(0, str(V2 / "tools"))
import audit  # noqa: E402

audit.PK, audit.RS = V2 / "audit2" / "packets", V2 / "audit2" / "results"
res = [u for f in audit.RS.glob("*.json") if not audit.check(f.stem) for u in json.loads(f.read_text())["units"]]
if res:
    n = len(res)
    rates = {f: sum(u["fields"][f]["verdict"] == "wrong" for u in res) for f in audit.FIELDS}
    rates["any field"] = sum(u["unit_ok"] == "no" for u in res)
    out = {f: {"wrong": k, "rate": round(k / n, 3), "ci95": audit.wilson(k, n)} for f, k in rates.items()}
    (V2 / "audit2" / "report.json").write_text(json.dumps({"n": n, "auditor": "Claude Opus (fresh sample, seed 20261027)", "fields": out}, indent=1))
    print(f"fresh Opus audit: {n} statements;", ", ".join(f"{f} {100 * v['rate']:.1f}%" for f, v in out.items()))
else:
    print("fresh Opus audit: no results yet")
side, byf, n = Counter(), Counter(), 0
for f in glob.glob(str(V2 / "audit" / "critique" / "results" / "*.json")):
    for it in json.load(open(f)):
        n += 1
        for fld, v in it["fields"].items():
            if it["kind"] == "correction":
                side[v["side"]] += 1
print(f"GPT critique: {n} items; on Opus corrections GPT sides with Opus {side['opus']}, original {side['original']}, neither {side['neither']}")
import run_v2  # noqa: E402
run_v2.PHASE = "course56"
q = json.loads((V2 / "queue.json").read_text())
left = [x["slug"] for x in q if not run_v2.course56_done(x["slug"])]
print(f"C5/C6: {len(q) - len(left)} of {len(q)} universities done, {len(left)} left")
for cmd in (["build_course_xlsx.py"], ["build_v2.py"], ["build_site_data.py"], ["build_findings_page.py"]):
    subprocess.run([sys.executable, str(V2 / "tools" / cmd[0])], cwd=ROOT, capture_output=True)
print("rebuilt course_layer.xlsx, app data and findings page")
