#!/usr/bin/env python3
"""Merge documents found by the computing-layer recheck (D36) into the collect files.

For each v2/recheck/<slug>.json, documents not already in v2/collect/<slug>.json (by URL) are appended with
"found_by": "recheck"; searched.computing / searched.school are set to "found" when a document of that layer was added.
If the university was already coded (v2/inst/<slug>.json exists), its coded file is moved to v2/run/superseded/ so the
code phase recodes the whole university with the new documents; the move is logged in v2/recheck_merge_log.json.
Idempotent. Run screen_docs.py afterwards so the new documents get a screening decision.
"""
import json
import shutil
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "v2"


def norm(u):
    return (u or "").split("#")[0].rstrip("/").lower()


def main():
    logp = V2 / "recheck_merge_log.json"
    log = json.loads(logp.read_text()) if logp.exists() else []
    for rp in sorted((V2 / "recheck").glob("*.json")):
        r = json.loads(rp.read_text())
        slug = r.get("slug") or rp.stem
        cp = V2 / "collect" / f"{slug}.json"
        if not cp.exists():
            continue
        c = json.loads(cp.read_text())
        have = {norm(d.get("url")) for d in c.get("documents", [])}
        added = []
        for d in r.get("documents", []):
            if norm(d.get("url")) in have or not d.get("text_file"):
                continue
            d = {k: v for k, v in d.items() if k != "in_first_collection"}
            d["found_by"] = "recheck"
            c["documents"].append(d)
            have.add(norm(d.get("url")))
            added.append(d["id"])
            if d.get("layer") in ("computing", "school"):
                c.setdefault("searched", {})[d["layer"]] = "found"
        if not added:
            continue
        c["notes"] = (c.get("notes") or "") + f" Recheck (D36) added: {', '.join(added)}."
        cp.write_text(json.dumps(c, indent=1, ensure_ascii=False))
        entry = {"slug": slug, "added": added, "time": time.strftime("%Y-%m-%d %H:%M")}
        inst = V2 / "inst" / f"{slug}.json"
        if inst.exists():
            dest = V2 / "run" / "superseded"
            dest.mkdir(parents=True, exist_ok=True)
            shutil.move(str(inst), str(dest / f"{slug}.json"))
            for k in ("coderA", "coderB"):
                p = V2 / "run" / k / f"{slug}.json"
                if p.exists():
                    shutil.move(str(p), str(dest / f"{slug}.{k}.json"))
            entry["recode"] = True
        log.append(entry)
        print(slug, "added", added, "recode" if entry.get("recode") else "")
    logp.write_text(json.dumps(log, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
