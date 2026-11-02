#!/usr/bin/env python3
"""Merge corpus/raw/*.json, re-fetch every source, and verify each excerpt verbatim.

For each excerpt we locate `text`, `frag_start`, `frag_end` in the live page text
(whitespace/quote-insensitive), then replace them with the page's exact characters.
Writes corpus/corpus.json and corpus/verification_report.md.

Usage: python3 tools/verify_build.py [--offline] [--refetch doc_id1,doc_id2]
"""
import hashlib
import json
import re
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fetch_text import fetch, normalize, to_text  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CACHE = Path("/private/tmp/claude-502/-Users-rudrajit-Documents-Current-Research-AI-in-education-policy-guidelines/904d4b53-12af-418e-ba9c-da606f5ae71a/scratchpad/verify")
CACHE.mkdir(parents=True, exist_ok=True)

FOLD = {"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-",
        " ": " ", "…": "...", "​": ""}


def fold_with_map(s):
    """Lowercased, quote/dash-folded, whitespace-collapsed string + index map back to s."""
    out, idx, prev_space = [], [], False
    for i, ch in enumerate(s):
        ch = FOLD.get(ch, ch)
        for c in ch:
            if c.isspace():
                if prev_space:
                    continue
                c, prev_space = " ", True
            else:
                prev_space = False
            out.append(c.lower())
            idx.append(i)
    return "".join(out), idx


def fold(s):
    return fold_with_map(s)[0].strip()


REFETCH = set()  # URLs to fetch fresh, ignoring the cache (--refetch id1,id2)


def page_text(url):
    key = hashlib.sha1(url.encode()).hexdigest()[:16]
    p = CACHE / f"{key}.txt"
    if p.exists() and url not in REFETCH:
        return p.read_text()
    if "--offline" in sys.argv:
        return ""
    try:
        raw = fetch(url)
        text = normalize(to_text(raw))
    except Exception as e:  # noqa: BLE001
        text = ""
        print("fetch failed", url, e, file=sys.stderr)
    p.write_text(text)
    return text


def locate(needle, hay, hay_fold, hay_map):
    """Return the exact page substring matching needle, or None."""
    n = fold(needle)
    if not n:
        return None
    pos = hay_fold.find(n)
    if pos < 0:
        return None
    start, end = hay_map[pos], hay_map[pos + len(n) - 1] + 1
    return re.sub(r"\s+", " ", hay[start:end])


def frag_url(url, start, end):
    enc = lambda s: urllib.parse.quote(s, safe="")  # noqa: E731  (encodes , and -)
    base = url.split("#")[0]
    if url.lower().endswith(".pdf"):
        return base
    if start and end and fold(start) != fold(end):
        return f"{base}#:~:text={enc(start)},{enc(end)}"
    return f"{base}#:~:text={enc(start or end)}"


def main():
    docs, searched, excluded, new_codes = [], [], [], []
    for f in sorted((ROOT / "corpus" / "raw").glob("*.json")):
        data = json.loads(f.read_text())
        g = data.get("group", f.stem)
        for d in data.get("documents", []):
            if d.get("country") not in ("USA", "Canada"):  # scope: USA + Canada only
                continue
            d["group"] = g
            docs.append(d)
        for s in data.get("searched_universities", []):
            if any(m in s.get("university", "") for m in ("Monterrey", "UNAM", "ITAM", "Mexico")):
                continue
            s["group"] = g
            searched.append(s)
        excluded += data.get("excluded", [])
        new_codes += data.get("new_codes", [])

    # institutions outside the computing frame (no computing degree programs)
    oof = json.loads((ROOT / "corpus" / "out_of_frame.json").read_text())["patterns"]
    is_oof = lambda u: any(p.lower() in u.lower() for p in oof)  # noqa: E731
    for d in docs:
        if is_oof(d["university"]):
            excluded.append({"university": d["university"], "title": d["title"], "url": d["url"], "reason": "out of frame: no computing degree programs"})
    docs = [d for d in docs if not is_oof(d["university"])]
    for x in searched:
        if is_oof(x["university"]):
            x["result"] = "out-of-frame"

    # documents removed by PI decision (corpus/exclude_docs.json)
    drop = json.loads((ROOT / "corpus" / "exclude_docs.json").read_text())
    for d in docs:
        if d["id"] in drop:
            excluded.append({"university": d["university"], "title": d["title"], "url": d["url"], "reason": drop[d["id"]]})
    docs = [d for d in docs if d["id"] not in drop]

    # university-wide fallback documents only count where the institution has no computing-specific document
    # fallback order (PI, 2026-10-05): CS > CS-related unit (tiers 1-2: department/course/university-computing)
    # > school/college policy (school-general) > university-wide (university-general). Keep only the best tier present.
    TIER = {"department": 1, "course": 1, "university-computing": 1, "school-general": 3, "university-general": 4}
    best_tier = {}
    for d in docs:
        best_tier[d["university"]] = min(best_tier.get(d["university"], 9), TIER.get(d.get("level"), 1))
    docs = [d for d in docs if TIER.get(d.get("level"), 1) == best_tier[d["university"]] or d.get("keep_with_computing")]

    # de-duplicate documents by URL (keep the one with more excerpts)
    by_url = {}
    for d in docs:
        k = d["url"].split("#")[0].rstrip("/")
        if k not in by_url or len(d.get("excerpts", [])) > len(by_url[k].get("excerpts", [])):
            by_url[k] = d
    docs = list(by_url.values())
    seen_ids = set()
    for d in docs:
        base, n = d["id"], 2
        while d["id"] in seen_ids:
            d["id"] = f"{base}-{n}"
            n += 1
        seen_ids.add(d["id"])

    if "--refetch" in sys.argv:
        ids = set(sys.argv[sys.argv.index("--refetch") + 1].split(","))
        REFETCH.update(d["url"] for d in docs if d["id"] in ids)
        REFETCH.update("https://web.archive.org/web/2026/" + d["url"] for d in docs if d["id"] in ids)
    with ThreadPoolExecutor(12) as ex:
        texts = dict(zip([d["url"] for d in docs], ex.map(page_text, [d["url"] for d in docs])))
    # live page unreachable -> fall back to the Internet Archive's latest snapshot
    for d in docs:
        if len(texts.get(d["url"], "")) < 200 and "web.archive.org" not in d["url"]:
            arch = "https://web.archive.org/web/2026/" + d["url"]
            t = page_text(arch)
            if len(t) >= 200:
                texts[d["url"]] = t
                d["archive_url"] = arch

    browser_ok = json.loads((ROOT / "corpus" / "browser_verified.json").read_text())
    report, n_ok, n_bad, n_long = [], 0, 0, 0
    for d in docs:
        hay = texts.get(d["url"], "")
        hay_fold, hay_map = fold_with_map(hay)
        d["fetched_chars"] = len(hay)
        for i, e in enumerate(d.get("excerpts", []), 1):
            e["id"] = f"{d['id']}-e{i}"
            exact = locate(e["text"], hay, hay_fold, hay_map) if hay else None
            fs = locate(e.get("frag_start", ""), hay, hay_fold, hay_map) if hay else None
            fe = locate(e.get("frag_end", ""), hay, hay_fold, hay_map) if hay else None
            if exact:
                e["text"] = exact
                e["verified"] = "exact"
                n_ok += 1
            elif d["id"] in browser_ok:
                e["verified"] = "exact"
                e["verified_via"] = "rendered page in browser"
                fs, fe = e.get("frag_start"), e.get("frag_end")
                n_ok += 1
            else:
                e["verified"] = "unverified"
                n_bad += 1
                report.append(f"- `{e['id']}` not found on page ({'no text fetched' if not hay else 'mismatch'}): {e['text'][:60]}")
            words = len(e["text"].split())
            if words > 15:
                n_long += 1
                report.append(f"- `{e['id']}` is {words} words (cap 15)")
            # If frag_start first occurs in an earlier sentence, the browser would highlight from there;
            # start the highlight at the quote itself instead.
            if exact and fs:
                q_pos = hay_fold.find(fold(exact))
                if hay_fold.find(fold(fs)) < q_pos - 600 or hay_fold.find(fold(fs)) > q_pos:
                    fs = exact
            if exact and fe and hay_fold.find(fold(fe), hay_fold.find(fold(exact))) < 0:
                fe = None
            e["link"] = frag_url(d.get("archive_url", d["url"]), fs or (exact if exact else None), fe) if (fs or exact) else d.get("archive_url", d["url"])

    # One coverage row per institution: drop "not found" rows for institutions with included documents,
    # and let a pass-2 re-search replace a pass-1 verdict.
    included = {d["university"] for d in docs}
    best = {}
    for x in searched:
        u = x["university"]
        if u in included or any(u.startswith(i + " ") or u.startswith(i + " —") for i in included):
            x = {**x, "result": "included"}
        prev = best.get(u)
        if prev is None or str(x.get("group", "")).startswith("pass2") or x["result"] == "included":
            best[u] = x
    searched = list(best.values())

    # source tier per document (PI fallback order): 1 CS, 2 CS-related unit, 3 school/college, 4 university-wide
    CS = re.compile(r"comput|\bEECS\b|\bCSE\b|\bCS\b|electrical engineering", re.I)
    RELATED = re.compile(r"information|informatics|data science|artificial intelligence|\bAI\b|machine learning|software engineering|ischool|heinz|interactive computing", re.I)
    for d in docs:
        lvl = d.get("level")
        if lvl == "school-general":
            d["tier"] = 3
        elif lvl == "university-general":
            d["tier"] = 4
        elif lvl == "university-computing":
            d["tier"] = 1
        else:
            unit = d.get("unit") or ""
            d["tier"] = 2 if RELATED.search(unit) and not CS.search(unit) else 1

    # language tag (the corpus keeps French policies verbatim)
    FR = {"le", "la", "les", "des", "est", "une", "dans", "pour", "vous", "sans", "utilisation", "cours", "être", "doit"}
    for d in docs:
        words = " ".join(e["text"] for e in d.get("excerpts", [])).lower().split()
        d["language"] = "fr" if words and sum(w in FR for w in words) / len(words) > 0.08 else "en"

    out = {
        "built": "2026-10-05",
        "documents": sorted(docs, key=lambda d: (d["university"], d["level"], d.get("course") or "")),
        "searched_universities": searched,
        "excluded": excluded,
        "new_codes": new_codes,
    }
    (ROOT / "corpus" / "corpus.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    n_univ = len({d["university"] for d in docs})
    head = (f"# Verification report\n\n{len(docs)} documents from {n_univ} institutions; "
            f"{n_ok} excerpts verified exact, {n_bad} unverified, {n_long} over 15 words.\n\n")
    (ROOT / "corpus" / "verification_report.md").write_text(head + "\n".join(report) + "\n")
    print(head)


if __name__ == "__main__":
    main()
