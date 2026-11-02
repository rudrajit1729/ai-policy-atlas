#!/usr/bin/env python3
"""CSV files behind each page of the site (D68), written to v2/site/data/csv/ from the same data the site reads.

People can download a page's CSV, edit it (e.g. reword a policy sentence, move a statement to another policy, add a
reviewer note column) and send it back; edits are folded in by hand or by a later import script, never silently.
Run after build_v2.py.
"""
import csv
import json
from collections import Counter
from pathlib import Path

V2 = Path(__file__).resolve().parents[1]
D = V2 / "site" / "data"
OUT = D / "csv"
SET = ("rr", "fact")
CATN = {"rr": "rule or recommendation", "fact": "fact or warning", "template": "template", "description": "description", "other": "reason, definition or resource"}


def write(name, head, rows):
    with open(OUT / name, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(head)
        w.writerows(rows)
    print(f"{name}: {len(rows)} rows")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    P = json.loads((D / "policies.json").read_text())
    POS = json.loads((D / "positions.json").read_text())
    U = json.loads((D / "universities.json").read_text())
    C = json.loads((D / "courses.json").read_text())
    M = json.loads((D / "meta.json").read_text())
    T = {t["id"]: t["name"] for t in json.loads((D / "types.json").read_text())}
    CB = {t["id"]: t["name"] for t in (C.get("codebook") or {}).get("types", [])}
    un = {u["slug"]: u["name"] for u in U} | {u["slug"]: u.get("name") or u["slug"] for u in C["universities"]}
    ai = [x for x in P if x["about_ai"] == "yes"]
    by_pos = {}
    for x in ai:
        if x.get("pos"):
            by_pos.setdefault(x["pos"], []).append(x)
    who = lambda q: "; ".join(f"{a} {m} {k}" for a, m, k in q.get("who", []))
    types = lambda q, names: "; ".join(f"{t} {names.get(t, t)}" for t in q.get("types", [q.get("type")]))

    # policies (institutional): the set and the other coded text
    head = ["policy id", "policy sentence", "category", "kind", "who it addresses", "stage", "topics (types)", "statements", "universities",
            "who and how strongly", "merged from", "example original wording 1", "university 1", "example original wording 2", "university 2", "example original wording 3", "university 3", "reviewer note"]
    def prow(q):
        ex = [by_id[e] for e in q.get("examples", []) if e in by_id]
        cells = [c for x in ex[:3] for c in (x["anchor"], un.get(x["uni"], x["uni"]))] + [""] * (6 - 2 * min(3, len(ex)))
        return [q["pid"], q["sentence"], CATN.get(q["cat"], q["cat"]), q.get("policy_kind"), q["actor"], q["phase"], types(q, T), q["n"], q["n_unis"], who(q),
                " | ".join(x["sentence"] for x in q.get("parts", [])) if len(q.get("parts", [])) > 1 else ""] + cells + [""]
    by_id = {x["id"]: x for x in ai}
    write("policy_set.csv", head, [prow(q) for q in POS if q["cat"] in SET])
    write("other_coded.csv", ["layer"] + head, [["institutional"] + prow(q) for q in POS if q["cat"] not in SET]
          + [["course", q["pid"], q["sentence"], CATN.get(q["cat"], q["cat"]), q.get("policy_kind"), q["actor"], q["phase"], types(q, CB), q["n"], q["n_unis"], who(q),
              " | ".join(x["sentence"] for x in q.get("parts", [])) if len(q.get("parts", [])) > 1 else ""]
             + [c for x in q["examples"][:3] for c in (x["anchor"], un.get(x["uni"], x["uni"]))] + [""] * (6 - 2 * min(3, len(q["examples"]))) + [""]
             for q in C.get("policies", []) if q["cat"] not in SET])
    shead = ["policy id", "policy sentence", "statement id", "university", "level", "original wording", "source link", "who (coded)", "force", "binding", "stage", "topic"]
    srow = lambda q, x: [q["pid"], q["sentence"], x["id"], un.get(x["uni"], x["uni"]), x["layer"], x["anchor"], x["link"], x.get("actor_coded", x["actor"]), x["modality"], x.get("binding"), x["phase"], x["type"]]
    write("policy_set_statements.csv", shead, [srow(q, x) for q in POS if q["cat"] in SET for x in by_pos.get(q["pid"], [])])

    # course policies and their syllabus statements
    cst = {}
    for u in C["universities"]:
        for sl in u["slots"]:
            for pp in sl["passages"]:
                for l in pp.get("labels") or []:
                    if l.get("pos"):
                        cst.setdefault(l["pos"], []).append([un.get(u["slug"], u["slug"]), sl["slot"], sl.get("course"), pp.get("term"), l["anchor"], pp["link"], l.get("ct")])
    CP = [q for q in C.get("policies", []) if q["cat"] in SET]
    write("course_policies.csv", head[:11] + ["example original wording 1", "university 1", "example original wording 2", "university 2", "example original wording 3", "university 3", "reviewer note"],
          [[q["pid"], q["sentence"], CATN[q["cat"]], q.get("policy_kind"), q["actor"], q["phase"], types(q, CB), q["n"], q["n_unis"], who(q),
            " | ".join(x["sentence"] for x in q.get("parts", [])) if len(q.get("parts", [])) > 1 else ""]
           + [c for x in q["examples"][:3] for c in (x["anchor"], un.get(x["uni"], x["uni"]))] + [""] * (6 - 2 * min(3, len(q["examples"]))) + [""] for q in CP])
    write("course_policy_statements.csv", ["policy id", "policy sentence", "university", "course slot", "course", "term", "original wording", "syllabus link", "course topic"],
          [[q["pid"], q["sentence"]] + r for q in CP for r in cst.get(q["pid"], [])])

    # counts behind the overview and the matrix: distinct policies in the set per level x who x stage
    cnt = Counter()
    seen = set()
    posd = {q["pid"]: q for q in POS}
    for x in ai:
        q = posd.get(x.get("pos"))
        if q and q["cat"] in SET and (x["layer"], q["pid"]) not in seen:
            seen.add((x["layer"], q["pid"]))
            cnt[(x["layer"], q["actor"], q["phase"])] += 1
    for q in CP:
        cnt[("course", q["actor"], q["phase"])] += 1
    write("policy_set_counts.csv", ["level", "who it addresses", "stage", "policies"], [[*k, v] for k, v in sorted(cnt.items())])
    pl = M.get("pipeline", {})
    sa = pl.get("set_aside", {})
    write("pipeline.csv", ["layer", "step", "count", "set aside at this step"], [
        ["institutional", "documents", M["n_documents"], ""], ["institutional", "statements coded", M["n_units"], ""],
        ["institutional", "statements about AI", len(ai), f"{M['n_units'] - len(ai)} not about AI"],
        ["institutional", "statements with a topic", sum(x["type"] != "UNCOVERED" for x in ai), f"{sa.get('unique', 0)} rare one-offs, {sa.get('not_policy', 0)} no policy"],
        ["institutional", "groups within a topic", pl.get("fine_positions"), ""], ["institutional", "must and should merged", pl.get("force_merged"), ""],
        ["institutional", "same policy across topics merged", pl.get("cross_type_merged"), "; ".join(f"{v} {CATN[k]}" for k, v in Counter(q["cat"] for q in POS if q["cat"] not in SET).items())],
        ["institutional", "policy set", sum(q["cat"] in SET for q in POS), ""],
        ["course", "statements coded", sum(len(pp.get("labels") or []) for u in C["universities"] for sl in u["slots"] for pp in sl["passages"]), ""],
        ["course", "grouped within a course topic", pl.get("course_grouped"), f"{pl.get('course_not_ai_statements', 0)} statements not about AI"],
        ["course", "same policy across topics merged", pl.get("course_merged"), "; ".join(f"{v} {CATN[k]}" for k, v in Counter(q["cat"] for q in C.get("policies", []) if q["cat"] not in SET).items())],
        ["course", "course policy set", len(CP), ""]])

    # universities, statements, course coverage, decisions
    write("universities.csv", ["slug", "university", "state", "type", "documents", "statements about AI"],
          [[u["slug"], u["name"], u.get("state"), u.get("type"), len(u["documents"]), sum(1 for x in ai if x["uni"] == u["slug"])] for u in U])
    write("statements.csv", ["statement id", "university", "level", "document", "original wording", "source link", "AI-normalized statement", "who (coded)", "force", "binding",
                             "stage", "topic", "policy id", "category", "about AI"],
          [[x["id"], un.get(x["uni"], x["uni"]), x["layer"], x["doc"], x["anchor"], x["link"], x.get("policy") or "", x.get("actor_coded", x["actor"]), x["modality"], x.get("binding"),
            x["phase"], x["type"], x.get("pos") or "", CATN.get(x.get("cat"), ""), x["about_ai"]] for x in P])
    write("course_coverage.csv", ["university", "slot", "course", "title", "status", "syllabi", "AI passages"],
          [[un.get(u["slug"], u["slug"]), sl["slot"], sl.get("course"), sl.get("title"), sl.get("status"), " ".join(y.get("url") or "" for y in sl["syllabi"]), len(sl["passages"])]
           for u in C["universities"] for sl in u["slots"]])
    dec = json.loads((V2 / "decisions.json").read_text())["decisions"]
    write("decisions.csv", ["id", "date", "section", "decided by", "decision", "rationale"], [[x["id"], x["date"], x["section"], x["by"], x["decision"], x["rationale"]] for x in dec])


if __name__ == "__main__":
    main()
