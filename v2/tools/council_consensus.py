#!/usr/bin/env python3
"""Consensus of the three-member thematic council (D77).

Each member grouped the policies inside every stance x stage cell with 5 or more policies (47 cells, 783 policies), working
independently. Agreement between two members on a cell is the adjusted Rand index (ARI) of their groupings. The consensus
keeps, per cell, the member grouping with the highest mean ARI to the other two (the medoid), with its labels.
Writes v2/role_groups.json ({"cells": {...}, "agreement": {...}}) and prints agreement statistics.
Usage: council_consensus.py member_1.json member_2.json member_3.json
"""
import json
import sys
from collections import Counter
from itertools import combinations
from math import comb
from pathlib import Path


def ari(a, b):
    """Adjusted Rand index of two partitions given as {item: group}."""
    items = list(a)
    n = len(items)
    if n < 2:
        return 1.0
    ct = Counter((a[i], b[i]) for i in items)
    sa, sb = Counter(a[i] for i in items), Counter(b[i] for i in items)
    idx = sum(comb(v, 2) for v in ct.values())
    ea, eb = sum(comb(v, 2) for v in sa.values()), sum(comb(v, 2) for v in sb.values())
    exp, mx = ea * eb / comb(n, 2), (ea + eb) / 2
    return 1.0 if mx == exp else (idx - exp) / (mx - exp)


def main():
    M = [json.loads(Path(f).read_text())["cells"] for f in sys.argv[1:4]]
    out, stats = {}, {}
    tot_w = 0
    pair_sum = Counter()
    for cell in M[0]:
        parts = [{p: gi for gi, g in enumerate(m[cell]) for p in g["pids"]} for m in M]
        assert all(set(x) == set(parts[0]) for x in parts), cell
        pa = {f"{i + 1}-{j + 1}": ari(parts[i], parts[j]) for i, j in combinations(range(3), 2)}
        mean = [sum(v for k, v in pa.items() if str(i + 1) in k.split("-")) / 2 for i in range(3)]
        best = max(range(3), key=lambda i: mean[i])
        out[cell] = M[best][cell]
        n = len(parts[0])
        stats[cell] = {"n": n, "pairwise_ari": {k: round(v, 3) for k, v in pa.items()}, "medoid": best + 1,
                       "groups": [len(m[cell]) for m in M]}
        tot_w += n
        for k, v in pa.items():
            pair_sum[k] += v * n
    agg = {k: round(v / tot_w, 3) for k, v in pair_sum.items()}
    meanari = round(sum(agg.values()) / 3, 3)
    med = Counter(s["medoid"] for s in stats.values())
    V2 = Path(__file__).resolve().parents[1]
    (V2 / "role_groups.json").write_text(json.dumps({"cells": out, "agreement": {"weighted_pairwise_ari": agg, "mean_ari": meanari,
                                                                                 "medoid_counts": dict(med), "cells": stats}}, ensure_ascii=False, indent=1))
    print("cells", len(out), "policies", tot_w, "pairwise ARI (weighted by policies)", agg, "mean", meanari, "medoid from member", dict(med))
    low = sorted(stats.items(), key=lambda kv: sum(kv[1]["pairwise_ari"].values()))[:6]
    for c, s in low:
        print("lowest:", c, s)


if __name__ == "__main__":
    main()
