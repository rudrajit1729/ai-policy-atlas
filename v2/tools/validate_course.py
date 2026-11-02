#!/usr/bin/env python3
"""Validate a course-layer collection file (v2/course/<slug>.json, D41).

Checks: slots C1–C4 present (C1–C6 with --slots C1,C2,C3,C4,C5,C6); status from the closed list; every public syllabus has a saved text file;
every ai_start / ai_end is an exact substring of the saved text (whitespace- and quote-folded) and ai_end follows ai_start.
Prints OK or the list of errors.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATUS = {"public-ai-policy", "public-no-ai", "public-generic-only", "outdated", "undated-only", "not-public", "not-found"}


def fold(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace(" ", " ")
    return re.sub(r"\s+", " ", s).strip()


def read_text(tf):
    p = Path(tf) if tf.startswith("/") else ROOT / tf
    return p.read_text(errors="ignore") if p.exists() else None


def check(path):
    errs = []
    c = json.loads(Path(path).read_text())
    if c.get("program") is None:
        return [] if c.get("notes") else ["program is null but notes do not explain why"]
    slots = {x.get("slot"): x for x in c.get("courses", [])}
    for s in REQUIRED:
        if s not in slots:
            errs.append(f"missing slot {s}")
    for x in c.get("courses", []):
        tag = x.get("slot")
        if x.get("course") is None:
            continue
        if x.get("status") not in STATUS:
            errs.append(f"{tag}: bad status {x.get('status')}")
        if x.get("status", "").startswith("public") and not x.get("syllabi"):
            errs.append(f"{tag}: public status but no syllabi")
        if x.get("status") in ("outdated", "undated-only") and not x.get("syllabi"):
            errs.append(f"{tag}: {x.get('status')} but the syllabus is not recorded")
        years = []
        for y in x.get("syllabi", []):
            if not isinstance(y.get("year"), int) and not y.get("undated"):
                errs.append(f"{tag}: syllabus {y.get('url')} needs an integer year or undated: true")
            if isinstance(y.get("year"), int):
                years.append(y["year"])
        if x.get("status", "").startswith("public") and years and max(years) < 2023:
            errs.append(f"{tag}: newest syllabus is from {max(years)}; status must be outdated (pre-ChatGPT), not {x.get('status')}")
        if x.get("status", "").startswith("public") and not years:
            errs.append(f"{tag}: public status needs a dated syllabus; use undated-only")
        for y in x.get("syllabi", []):
            t = read_text(y.get("text_file") or "")
            if t is None:
                errs.append(f"{tag}: text_file missing for {y.get('url')}")
                continue
            ft = fold(t)
            if x.get("status") in ("public-ai-policy", "public-generic-only") and not y.get("ai_passages"):
                errs.append(f"{tag}: AI status but no ai_passages")
            for i, a in enumerate(y.get("ai_passages", [])):
                st, en = fold(a.get("ai_start", "")), fold(a.get("ai_end", ""))
                i0 = ft.find(st) if st else -1
                if i0 < 0:
                    errs.append(f"{tag} passage {i}: ai_start not found in saved text")
                    continue
                if not en or ft.find(en, i0) < 0:
                    errs.append(f"{tag} passage {i}: ai_end not found after ai_start")
    return errs


REQUIRED = ("C1", "C2", "C3", "C4")

if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["--slots"]:
        REQUIRED = tuple(args[1].split(","))
        args = args[2:]
    bad = 0
    for p in args:
        e = check(p)
        if e:
            bad = 1
            print(p)
            for x in e:
                print("  -", x)
    if not bad:
        print("OK")
    sys.exit(bad)
