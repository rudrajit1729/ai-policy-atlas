#!/usr/bin/env python3
"""Build v2/site/findings.html from the template and v2/site_data/summary.json (numbers are never typed by hand)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
t = (ROOT / "v2" / "site" / "findings_template.html").read_text()
data = json.dumps(json.loads((ROOT / "v2" / "site_data" / "summary.json").read_text()), ensure_ascii=False).replace("</", "<\\/")
(ROOT / "v2" / "site" / "findings.html").write_text(t.replace("__DATA__", data))
print("wrote v2/site/findings.html", len(t) + len(data), "bytes")
