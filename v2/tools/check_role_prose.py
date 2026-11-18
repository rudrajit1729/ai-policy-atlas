#!/usr/bin/env python3
"""Check the role-document prose (D76) against the data before it is used.

For every paragraph in a prose file ({role: {layer: {"intro": str, "stances": {stance: str}}}}):
- every cited policy ID must exist in that part (and, in a stance paragraph, in that stance);
- every number must be a count that appears in that part's data (policies, universities, statements per policy,
  per stance, per stage or per matrix cell, or the part totals) or a percentage of two such counts;
- stance ids must match the stances present in the part.
Prints problems; exits 1 if any.
Usage: check_role_prose.py prose.json [prose2.json ...]
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_roles  # noqa: E402

ID = re.compile(r"\b(?:P\d{2,3}\.\d{2}|CT\d{2}\.c\d{2}|CNEW\.c\d{2}|NEW\d*\.\d+|[A-Z]+\d*\.[a-z]?\d+)\b")
NUM = re.compile(r"(?<![\w.])(\d{1,3}(?:,\d{3})+|\d+)(%?)(?![\w.]\d)")


def allowed(part):
    a = {part["n"], part["n_statements"], part["n_unis"]} | set(part["stage_n"].values())
    for x in part["stances"]:
        a |= {x["n"], x["n_unis"]}
        for g in x["stages"]:
            a.add(len(g["policies"]))
            for q in g["policies"]:
                a |= {q["n_unis"], q["n"]}
    for r in part["matrix"].values():
        a |= {c["n"] for c in r.values()}
    pct = {round(100 * k / n) for k in a for n in a if n and k <= n}
    return a, pct


def main():
    data = build_roles.build()
    bad = 0
    for f in sys.argv[1:]:
        P = json.loads(Path(f).read_text())
        for rk, layers in P.items():
            for layer, pr in layers.items():
                part = next(p for p in data["roles"][rk]["parts"] if p["layer"] == layer)
                ids = {q["pid"]: x["id"] for x in part["stances"] for g in x["stages"] for q in g["policies"]}
                a, pct = allowed(part)
                extra = set(pr.get("stances", {})) - {x["id"] for x in part["stances"]}
                missing = {x["id"] for x in part["stances"]} - set(pr.get("stances", {}))
                if extra or missing:
                    bad += 1
                    print(f"{rk}/{layer}: stance keys extra {sorted(extra)} missing {sorted(missing)}")
                for key, text in [("intro", pr.get("intro", ""))] + [(k, v) for k, v in pr.get("stances", {}).items()]:
                    for i in ID.findall(text):
                        if i not in ids:
                            bad += 1
                            print(f"{rk}/{layer}/{key}: unknown ID {i}")
                        elif key != "intro" and ids[i] != key:
                            bad += 1
                            print(f"{rk}/{layer}/{key}: {i} belongs to {ids[i]}")
                    for n, p in NUM.findall(ID.sub("", text)):
                        v = int(n.replace(",", ""))
                        if (p and v not in pct) or (not p and v not in a):
                            bad += 1
                            print(f"{rk}/{layer}/{key}: number {n}{p} not in the data")
    print("problems:", bad)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
