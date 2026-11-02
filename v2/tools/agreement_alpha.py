#!/usr/bin/env python3
"""Inter-coder agreement between Coder A and Coder B (TACT stage 4), computed deterministically from their files.

Units are paired within each document by the overlap of their anchors' character spans in the saved source text
(a pair needs overlap >= 50% of the shorter span; greedy, best overlap first). Reported:
  unitizing   matched pairs / (matched + only A + only B)
  alpha       Krippendorff's alpha (nominal, two coders, matched pairs) for actor, phase, modality, unit_stance,
              policy_type, and document stance; 95% CI from 1,000 bootstrap resamples of universities
  percent     raw percent agreement for the same fields
Writes v2/exports/agreement_alpha.json and prints a table.
"""
import json
import random
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "v2"
sys.path.insert(0, str(V2 / "tools"))
import export_xlsx as ex  # noqa: E402

FIELDS = ["actor", "phase", "modality", "unit_stance", "policy_type"]


def alpha(pairs):
    """Krippendorff's alpha, nominal data, 2 coders, no missing values."""
    pairs = [(a, b) for a, b in pairs if a is not None and b is not None]
    n = 2 * len(pairs)
    if n < 2:
        return None
    nc = Counter()
    for a, b in pairs:
        nc[a] += 1
        nc[b] += 1
    do = sum(1 for a, b in pairs if a != b) * 2 / n  # observed disagreement (each mismatched pair contributes 2 ordered pairs)
    de = (n * n - sum(v * v for v in nc.values())) / (n * (n - 1))
    return 1 - do / de if de else None


def spans(data):
    out = {}
    for d in data.get("documents", []):
        tf, src = ex._source(data.get("slug"), d["id"])
        out[d["id"]] = (d, [(ex._find(u.get("anchor"), src), u) for u in d.get("units", [])])
    return out


def match(ua, ub):
    cand = []
    for i, ((a0, a1), u) in enumerate(ua):
        for j, ((b0, b1), v) in enumerate(ub):
            if a0 < 0 or b0 < 0:
                continue
            ov = min(a1, b1) - max(a0, b0)
            short = min(a1 - a0, b1 - b0)
            if short > 0 and ov / short >= 0.5:
                cand.append((ov / short, i, j))
    used_a, used_b, pairs = set(), set(), []
    for _, i, j in sorted(cand, reverse=True):
        if i not in used_a and j not in used_b:
            used_a.add(i)
            used_b.add(j)
            pairs.append((ua[i][1], ub[j][1]))
    return pairs, len(ua) - len(used_a), len(ub) - len(used_b)


def main():
    per_uni = {}
    for pa in sorted((V2 / "run" / "coderA").glob("*.json")):
        pb = V2 / "run" / "coderB" / pa.name
        if not pb.exists():
            continue
        A, B = json.loads(pa.read_text()), json.loads(pb.read_text())
        sa, sb = spans(A), spans(B)
        rec = {"pairs": {f: [] for f in FIELDS + ["doc_stance"]}, "matched": 0, "only_a": 0, "only_b": 0}
        for did in set(sa) | set(sb):
            ua = sa.get(did, (None, []))[1]
            ub = sb.get(did, (None, []))[1]
            pairs, oa, ob = match(ua, ub)
            rec["matched"] += len(pairs)
            rec["only_a"] += oa
            rec["only_b"] += ob
            for u, v in pairs:
                for f in FIELDS:
                    rec["pairs"][f].append((u.get(f), v.get(f)))
            if did in sa and did in sb:
                rec["pairs"]["doc_stance"].append((sa[did][0].get("stance"), sb[did][0].get("stance")))
        per_uni[pa.stem] = rec
    unis = list(per_uni)

    def summarize(sample):
        res = {}
        for f in FIELDS + ["doc_stance"]:
            ps = [p for s in sample for p in per_uni[s]["pairs"][f]]
            res[f] = alpha(ps)
        return res

    point = summarize(unis)
    pct = {f: (sum(1 for s in unis for a, b in per_uni[s]["pairs"][f] if a == b) /
               max(1, sum(len(per_uni[s]["pairs"][f]) for s in unis))) for f in FIELDS + ["doc_stance"]}
    rnd = random.Random(20261026)
    boots = [summarize([rnd.choice(unis) for _ in unis]) for _ in range(1000)]
    ci = {}
    for f in FIELDS + ["doc_stance"]:
        xs = sorted(b[f] for b in boots if b[f] is not None)
        ci[f] = (xs[int(0.025 * len(xs))], xs[int(0.975 * len(xs)) - 1]) if xs else (None, None)
    m = sum(r["matched"] for r in per_uni.values())
    oa = sum(r["only_a"] for r in per_uni.values())
    ob = sum(r["only_b"] for r in per_uni.values())
    out = {"universities": len(unis), "matched_pairs": m, "only_A": oa, "only_B": ob, "unitizing_agreement": m / (m + oa + ob),
           "fields": {f: {"alpha": point[f], "ci95": ci[f], "percent_agreement": pct[f],
                          "pairs": sum(len(per_uni[s]["pairs"][f]) for s in unis)} for f in FIELDS + ["doc_stance"]},
           "note": "Coder A and Coder B coded independently with the same codebook version; pairs matched by anchor-span overlap >= 50%."}
    (V2 / "exports" / "agreement_alpha.json").write_text(json.dumps(out, indent=1))
    print(f"{len(unis)} universities; {m} matched pairs; only A {oa}; only B {ob}; unitizing agreement {out['unitizing_agreement']:.3f}")
    for f, r in out["fields"].items():
        print(f"{f:12s} alpha {r['alpha']:.3f}  95% CI [{r['ci95'][0]:.3f}, {r['ci95'][1]:.3f}]  agreement {r['percent_agreement']:.3f}  (n={r['pairs']})")


if __name__ == "__main__":
    main()
