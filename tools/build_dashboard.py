#!/usr/bin/env python3
"""Inject corpus/corpus.json + corpus/synthesis.json into dashboard/template.html -> dashboard/index.html."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def safe(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


corpus = json.loads((ROOT / "corpus" / "corpus.json").read_text())
synthesis = json.loads((ROOT / "corpus" / "synthesis.json").read_text())
html = (ROOT / "dashboard" / "template.html").read_text()
html = html.replace("/*__CORPUS__*/", safe(corpus)).replace("/*__SYNTHESIS__*/", safe(synthesis))
(ROOT / "dashboard" / "index.html").write_text(html)
print("wrote dashboard/index.html", len(html) // 1024, "KB")
