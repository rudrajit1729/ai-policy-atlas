#!/usr/bin/env python3
"""Validate a v2 per-university coding file against CODEBOOK.md.

Checks: JSON shape, enums, policy_type ids, anchor/frag are exact substrings of the saved
document text (whitespace/quote-insensitive), anchors <= 15 words. Prints OK or a list of errors.
Usage: python3 v2/tools/validate_inst.py v2/inst/<slug>.json [more files]
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_tp = ROOT / "v2" / ("policy_types.json" if (ROOT / "v2" / "policy_types.json").exists() else "policy_types_v0.json")
TYPES = {t["id"] for t in json.loads(_tp.read_text())["types"]} | {"UNCOVERED"}
REQUIRE_WHY = "--no-why" not in sys.argv
ENUM = {
    "layer": {"university", "school", "computing", "course"},
    "stance": {"prohibit", "restrict", "permit", "encourage", "require", "delegates"},
    "actor": {"student", "instructor", "ta-staff", "admin", "all"},
    "phase": {"before-course", "course-start", "during-work", "during-assessment", "when-misuse", "over-time", "general"},
    "modality": {"must", "must-not", "may", "should", "should-not", "informs"},
    "unit_stance": {"prohibit", "restrict", "permit", "encourage", "require", "neutral"},
}
FOLD = {"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-", " ": " ", "…": "..."}


def fold(s):
    s = "".join(FOLD.get(ch, ch) for ch in s)
    return re.sub(r"\s+", " ", s).strip().lower()


def text_for(doc, collect):
    tf = doc.get("text_file") or next((d.get("text_file") for d in collect.get("documents", []) if d["id"] == doc["id"]), None)
    if not tf:
        return None
    p = Path(tf) if Path(tf).is_absolute() else ROOT / tf
    return fold(p.read_text()) if p.exists() else None


def check(path):
    errs = []
    data = json.loads(Path(path).read_text())
    cpath = ROOT / "v2" / "collect" / f"{data.get('slug')}.json"
    collect = json.loads(cpath.read_text()) if cpath.exists() else {}
    new_names = {t["name"] for t in data.get("new_types", [])}
    screened = {d["id"]: d.get("screen") for d in collect.get("documents", [])}
    for d in data.get("documents", []):
        did = d.get("id", "?")
        if screened.get(did) not in (None, "include"):
            errs.append(f"{did}: document was screened '{screened.get(did)}', so it must not be coded")
        for f in ("layer", "stance"):
            if d.get(f) not in ENUM[f]:
                errs.append(f"{did}: bad {f} {d.get(f)!r}")
        if REQUIRE_WHY and not (d.get("stance_why") or "").strip():
            errs.append(f"{did}: missing stance_why (rationale before stance)")
        hay = text_for(d, collect)
        if hay is None:
            errs.append(f"{did}: no saved text found (text_file)")
        if not d.get("units"):
            errs.append(f"{did}: no units coded")
        for i, u in enumerate(d.get("units", []), 1):
            tag = f"{did} unit {i}"
            for f in ("actor", "phase", "modality"):
                if u.get(f) not in ENUM[f]:
                    errs.append(f"{tag}: bad {f} {u.get(f)!r}")
            if REQUIRE_WHY and u.get("unit_stance") not in ENUM["unit_stance"]:
                errs.append(f"{tag}: bad unit_stance {u.get('unit_stance')!r}")
            if REQUIRE_WHY and len((u.get("why") or "").split()) < 6:
                errs.append(f"{tag}: missing or too-short rationale 'why' (write it before coding)")
            if u.get("policy_type") == "UNCOVERED" and not (u.get("uncovered_note") or "").strip():
                errs.append(f"{tag}: UNCOVERED needs uncovered_note")
            pt = u.get("policy_type", "")
            if pt not in TYPES and not (pt.startswith("NEW:") and pt[4:] in new_names):
                errs.append(f"{tag}: bad policy_type {pt!r} (NEW types must be listed in new_types)")
            a = u.get("anchor") or ""
            if len(a.split()) > 15:
                errs.append(f"{tag}: anchor is {len(a.split())} words (max 15)")
            if hay is not None:
                for f in ("anchor", "frag_start", "frag_end"):
                    v = u.get(f) or ""
                    if not v or fold(v) not in hay:
                        errs.append(f"{tag}: {f} not found verbatim in saved text: {v[:60]!r}")
    return errs


if __name__ == "__main__":
    bad = 0
    for p in [a for a in sys.argv[1:] if not a.startswith("--")]:
        e = check(p)
        if e:
            bad += 1
            print(f"{p}: {len(e)} errors")
            for x in e[:40]:
                print("  -", x)
        else:
            print(f"{p}: OK")
    sys.exit(1 if bad else 0)
