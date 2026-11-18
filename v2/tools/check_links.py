#!/usr/bin/env python3
"""D82: check that every source link behind the role views still answers (date accessed). Writes v2/linkcheck/links_<date>.csv."""
import csv, json, subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path
V2 = Path(__file__).resolve().parents[1]; D = V2 / "site" / "data"
P = json.loads((D / "policies.json").read_text()); C = json.loads((D / "courses.json").read_text())
L = {x["link"].split("#")[0] for x in P if x.get("link") and x["about_ai"] == "yes"}
for u in C["universities"]:
    for s in u["slots"]:
        for p in s["passages"]:
            for k in ("link", "url"):
                if p.get(k): L.add(p[k].split("#")[0])
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
def chk(u):
    r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-L", "--max-time", "25", "-A", UA, "-w", "%{http_code}", u], capture_output=True, text=True)
    return u, r.stdout.strip() or "000"
with ThreadPoolExecutor(24) as ex:
    res = list(ex.map(chk, sorted(L)))
out = V2 / "linkcheck" / f"links_{date.today().isoformat()}.csv"
with open(out, "w", newline="") as f:
    w = csv.writer(f); w.writerow(["url", "http_status", "checked"]); [w.writerow([u, c, date.today().isoformat()]) for u, c in res]
from collections import Counter
print(len(res), Counter(c[0] for _, c in res))
