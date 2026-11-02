#!/usr/bin/env python3
"""Deterministic document dates for chronological ordering (no model involved).

date_of(date_or_term, text) -> (date "YYYY", "YYYY-MM" or "YYYY-MM-DD" | None, source string)
1. The collector's date_or_term field, ignoring the access date ("accessed 2026-10-25"): the latest explicit date in it
   (a revision date is later than an issue date, so the latest is the version in hand).
2. Else the saved document text: the latest date that follows "last updated", "updated", "revised", "effective",
   "approved", "adopted", "published", "posted" or "last modified"; the matched words are returned as the source.
3. Else None ("undated"). Dates after the collection month are ignored.
Run directly to print coverage over v2/inst.
"""
import re

MONTHS = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
SEASON = {"spring": 1, "summer": 6, "fall": 8, "autumn": 8, "winter": 12}
CUTOFF = (2026, 10, 31)
MON = r"(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|sept?(?:ember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\.?"
PATS = [
    (re.compile(r"\b(20[12]\d)-(\d{1,2})-(\d{1,2})\b"), lambda m: (int(m[1]), int(m[2]), int(m[3]))),
    (re.compile(r"\b(\d{1,2})/(\d{1,2})/(20[12]\d)\b"), lambda m: (int(m[3]), int(m[1]), int(m[2]))),
    (re.compile(MON + r"\s+(\d{1,2}),?\s+(20[12]\d)\b", re.I), lambda m: (int(m[3]), MONTHS[m[1][:3].lower()], int(m[2]))),
    (re.compile(r"\b(\d{1,2})\s+" + MON + r"\s+(20[12]\d)\b", re.I), lambda m: (int(m[3]), MONTHS[m[2][:3].lower()], int(m[1]))),
    (re.compile(MON + r",?\s+(20[12]\d)\b", re.I), lambda m: (int(m[2]), MONTHS[m[1][:3].lower()], None)),
    (re.compile(r"\b(spring|summer|fall|autumn|winter)\s+(20[12]\d)\b", re.I), lambda m: (int(m[2]), SEASON[m[1].lower()], None)),
    (re.compile(r"\b(20[12]\d)\b"), lambda m: (int(m[1]), None, None)),
]
CUE = re.compile(r"(last\s+updated|last\s+modified|last\s+revised|updated|revised|effective|approved|adopted|published|posted)\s*(?:on|:|-|date:?)?\s*", re.I)


def _dates(s):
    """All dates in s as (y, m, d, start, end), most specific pattern first, non-overlapping."""
    taken, out = [], []
    for rx, f in PATS:
        for m in rx.finditer(s):
            if any(a < m.end() and m.start() < b for a, b in taken):
                continue
            try:
                y, mo, d = f(m)
            except (KeyError, ValueError):
                continue
            if mo is not None and not 1 <= mo <= 12:
                continue
            if (y, mo or 1, d or 1) > CUTOFF or y < 2018:
                continue
            taken.append((m.start(), m.end()))
            out.append((y, mo, d, m.start(), m.end()))
    return out


def _fmt(y, mo, d):
    return f"{y}" + (f"-{mo:02d}" if mo else "") + (f"-{d:02d}" if mo and d else "")


def date_of(field, text):
    f = re.sub(r"accessed\s+20\d\d-\d\d-\d\d", "", field or "", flags=re.I)
    f = re.sub(r"\(?\s*\d{4}\s+footer\s*\)?", "", f, flags=re.I)  # a copyright footer year is not a policy date
    ds = _dates(f)
    if ds:
        y, mo, d, *_ = max(ds, key=lambda x: (x[0], x[1] or 0, x[2] or 0))
        return _fmt(y, mo, d), "collector: " + (field or "").strip()[:80]
    best = None
    for m in CUE.finditer(text or ""):
        window = text[m.end(): m.end() + 40]
        ds = [x for x in _dates(window) if x[3] <= 3]  # the date must follow the cue directly
        if ds:
            y, mo, d, a, b = ds[0]
            cand = ((y, mo or 0, d or 0), _fmt(y, mo, d), re.sub(r"\s+", " ", text[m.start(): m.end() + b]).strip())
            if best is None or cand[0] > best[0]:
                best = cand
    if best:
        return best[1], "document text: “" + best[2][:80] + "”"
    return None, "undated"


if __name__ == "__main__":
    import json
    from collections import Counter
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[2]
    c, ex = Counter(), []
    for p in sorted((ROOT / "v2" / "inst").glob("*.json")):
        u = json.loads(p.read_text())
        col = json.loads((ROOT / "v2" / "collect" / p.name).read_text())
        tf = {d["id"]: d.get("text_file") for d in col.get("documents", [])}
        for d in u["documents"]:
            t = tf.get(d["id"]) or d.get("text_file") or ""
            tp = Path(t) if t.startswith("/") else ROOT / t
            text = tp.read_text(errors="ignore") if t and tp.exists() else ""
            dt, src = date_of(d.get("date_or_term"), text)
            c[src.split(":")[0]] += 1
            if dt:
                c["year " + dt[:4]] += 1
            if len(ex) < 12 and src.startswith("document"):
                ex.append((d["id"], dt, src))
    print(dict(sorted(c.items())))
    for e in ex:
        print(e)
