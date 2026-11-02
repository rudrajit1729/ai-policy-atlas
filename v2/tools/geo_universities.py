#!/usr/bin/env python3
"""Coordinates for each corpus university (D74), for the Policy label map.

Source: IPEDS institutional directory 2022 (latitude, longitude), via the Urban Institute Education Data API, fetched
per state. Each university is matched by name within its state; v2/site/data/geo_overrides.json fixes matches by
IPEDS unitid when the name match is wrong. Writes v2/site/data/geo.json: {slug: [lat, lon, ipeds name, unitid, match score]}.
"""
import difflib
import json
import re
import urllib.request
from pathlib import Path

V2 = Path(__file__).resolve().parents[1]
D = V2 / "site" / "data"
FIPS = {"AL": 1, "AK": 2, "AZ": 4, "AR": 5, "CA": 6, "CO": 8, "CT": 9, "DE": 10, "DC": 11, "FL": 12, "GA": 13, "HI": 15, "ID": 16, "IL": 17,
        "IN": 18, "IA": 19, "KS": 20, "KY": 21, "LA": 22, "ME": 23, "MD": 24, "MA": 25, "MI": 26, "MN": 27, "MS": 28, "MO": 29, "MT": 30,
        "NE": 31, "NV": 32, "NH": 33, "NJ": 34, "NM": 35, "NY": 36, "NC": 37, "ND": 38, "OH": 39, "OK": 40, "OR": 41, "PA": 42, "RI": 44,
        "SC": 45, "SD": 46, "TN": 47, "TX": 48, "UT": 49, "VT": 50, "VA": 51, "WA": 53, "WV": 54, "WI": 55, "WY": 56, "PR": 72}
CACHE = Path("/private/tmp/claude-502/-Users-rudrajit-Documents-Current-Research-AI-in-education-policy-guidelines/cecbc1fa-eb97-4a86-95d3-86ca06826de3/scratchpad/geo")


def fetch(st):
    f = CACHE / f"{st}.json"
    if f.exists():
        return json.loads(f.read_text())
    rows, url = [], f"https://educationdata.urban.org/api/v1/college-university/ipeds/directory/2022/?fips={FIPS[st]}"
    while url:
        d = json.load(urllib.request.urlopen(url, timeout=90))
        rows += [{k: r[k] for k in ("unitid", "inst_name", "latitude", "longitude", "degree_granting")} for r in d["results"]]
        url = d.get("next")
    CACHE.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(rows))
    return rows


def norm(s):
    s = s.lower().replace("&", "and").replace("saint ", "st ").replace("st. ", "st ")
    s = re.sub(r"\b(the|main campus|campus)\b", " ", s.replace("-", " "))
    return re.sub(r"[^a-z0-9 ]+", " ", s).split()


STOP = {"university", "of", "at", "in", "and", "college", "suny"}


def pick(name, rows):
    """Exact name first; then IPEDS names that contain every word of ours (fewest extra words, main campus first); then closest spelling."""
    n = " ".join(norm(name))
    ex = [r for r in rows if " ".join(norm(r["inst_name"])) == n]
    if ex:
        return 1.0, ex[0]
    key = set(norm(name)) - STOP
    sup = [r for r in rows if key and key <= set(norm(r["inst_name"]))]
    if sup:
        r = min(sup, key=lambda r: ("main" not in r["inst_name"].lower(), "-" in r["inst_name"], len(norm(r["inst_name"]))))
        return 0.95, r
    return max(((score(name, r["inst_name"]), r) for r in rows), key=lambda t: t[0]) if rows else (0, None)


def score(a, b):
    ta, tb = norm(a), norm(b)
    r = difflib.SequenceMatcher(None, " ".join(ta), " ".join(tb)).ratio()
    if set(ta) <= set(tb):
        r = max(r, 0.85 - 0.02 * (len(tb) - len(ta)))
    return r


def main():
    U = json.loads((D / "universities.json").read_text())
    over = json.loads((D / "geo_overrides.json").read_text()) if (D / "geo_overrides.json").exists() else {}
    out, low = {}, []
    for u in U:
        rows = [r for r in fetch(u["state"]) if r["latitude"] and r["degree_granting"] == 1]
        if u["slug"] in over:
            r = next(r for r in rows if r["unitid"] == over[u["slug"]])
            s = 1.0
        else:
            s, r = pick(u["name"], rows)
        if r:
            out[u["slug"]] = [round(r["latitude"], 4), round(r["longitude"], 4), r["inst_name"], r["unitid"], round(s, 2)]
        if s < 1:
            low.append((round(s, 2), u["slug"], u["name"], r and r["inst_name"]))
    (D / "geo.json").write_text(json.dumps(out, ensure_ascii=False))
    print(f"geo.json: {len(out)} of {len(U)} universities")
    for x in sorted(low):
        print(*x, sep=" | ")


if __name__ == "__main__":
    main()
