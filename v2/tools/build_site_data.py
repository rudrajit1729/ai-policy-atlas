#!/usr/bin/env python3
"""Compute v2/site_data/summary.json (every number on the findings page) from the coded data. Deterministic.

Inputs: v2/inst/*.json, v2/theme_review/final_assignments.json, v2/policy_types_v3.json, v2/exports/course_layer.xlsx,
v2/exports/agreement_alpha.json, v2/audit/report.json (if present).
"""
import collections
import glob
import json
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "v2"


def origin(t):
    a = t.get("added") or ""
    if "theme review" in a:
        return "theme review"
    if a:
        return "added during coding"
    return "initial list"


def main():
    fa = json.loads((V2 / "theme_review" / "final_assignments.json").read_text())
    # D64: type and about-AI as finally shown (placed UNCOVERED statements take their policy's type; not-about-AI ones drop out)
    for x in json.loads((V2 / "site" / "data" / "policies.json").read_text()):
        k = f"{x['uni']}|{x['id'].split(':', 1)[1]}"
        if k in fa:
            fa[k] = fa[k] | {"type": x["type"], "about_ai": x["about_ai"]}
    v3 = json.loads((V2 / "policy_types_v3.json").read_text())
    lay, dstance, inst = {}, collections.Counter(), {}
    for f in glob.glob(str(V2 / "inst" / "*.json")):
        d = json.load(open(f))
        for x in d["documents"]:
            dstance[(x["layer"], x.get("stance"))] += 1
            L = lay.setdefault(x["layer"], {"universities": set(), "documents": 0, "statements": 0, "about_ai": 0,
                                            "binding": collections.Counter(), "modality": collections.Counter()})
            L["universities"].add(d["slug"])
            L["documents"] += 1
            for i, u in enumerate(x.get("units", []), 1):
                inst[f"{d['slug']}|{x['id']}-u{i:02d}"] = (x["layer"], u)
    for uid, r in fa.items():
        l, u = inst[uid]
        L = lay[l]
        L["statements"] += 1
        if r["about_ai"] == "yes":
            L["about_ai"] += 1
            L["binding"][r["binding"]] += 1
            L["modality"][u.get("modality")] += 1
    levels = [{"level": k, "universities": len(v["universities"]), "documents": v["documents"], "statements": v["statements"],
               "about_ai": v["about_ai"], "binding": dict(v["binding"]), "modality": dict(v["modality"])} for k, v in lay.items()]
    wb = openpyxl.load_workbook(V2 / "exports" / "course_layer.xlsx", read_only=True)
    cov = list(wb["Coverage"].iter_rows(values_only=True))[1:]
    fr = list(wb["Frame"].iter_rows(values_only=True))[1:]
    syl = list(wb["Syllabi"].iter_rows(values_only=True))[1:]
    pas = list(wb["AI passages"].iter_rows(values_only=True))[1:]
    slots = sorted({r[4] for r in fr if r[4]})
    core = [r for r in fr if r[4] in ("C1", "C2", "C3", "C4")]
    course = {"universities_collected": len(cov), "syllabi": len(syl), "ai_passages": len(pas),
              "universities_with_ai_passage": len({r[0] for r in pas}),
              "profiles": dict(collections.Counter(r[5] for r in cov)), "slots": dict(collections.Counter(r[7] for r in core)),
              "slot_list": slots, "by_slot": {s: dict(collections.Counter(r[7] for r in fr if r[4] == s)) for s in slots}}
    cnt, unis = collections.Counter(), collections.defaultdict(set)
    for uid, r in fa.items():
        if r["about_ai"] == "yes":
            cnt[r["type"]] += 1
            unis[r["type"]].add(r["university"])
    types = [{"id": t["id"], "name": t["name"], "name_v2": t.get("name_v2"), "theme": t.get("theme_v3"), "covers": t.get("covers"),
              "statements": cnt.get(t["id"], 0), "universities": len(unis.get(t["id"], ())), "origin": origin(t),
              "retired": bool(t.get("retired"))} for t in v3["types"]]
    themes = []
    for th in v3["themes"]:
        ts = [t for t in types if t["theme"] == th["id"]]
        themes.append({"id": th["id"], "label": th["label"], "statements": sum(t["statements"] for t in ts),
                       "universities": len(set().union(*[unis.get(t["id"], set()) for t in ts])), "types": [t["id"] for t in ts]})
    out = {"generated": __import__("time").strftime("%Y-%m-%d"), "levels": levels, "course": course, "themes": themes, "types": types,
           "uncovered": {"statements": cnt.get("UNCOVERED", 0), "universities": len(unis.get("UNCOVERED", ()))},
           "doc_stance": {f"{a}|{b}": n for (a, b), n in dstance.items()},
           "alpha": json.loads((V2 / "exports" / "agreement_alpha.json").read_text()), "universities": 342}
    ap = V2 / "audit" / "report.json"
    if ap.exists():
        out["audit"] = json.loads(ap.read_text())
    a2 = V2 / "audit2" / "report.json"
    if a2.exists():
        out["audit2"] = json.loads(a2.read_text())
    # GPT critique of the Opus audit (D50/D57): per corrected field, whom GPT sides with; per confirmation, whether GPT flags it
    crit = [it for f in sorted((V2 / "audit" / "critique" / "results").glob("*.json")) for it in json.loads(f.read_text())]
    if crit:
        side = collections.Counter(v["side"] for it in crit if it["kind"] == "correction" for v in it["fields"].values())
        conf = [it for it in crit if it["kind"] != "correction"]
        out["critique"] = {"items": len(crit), "corrected_fields": sum(side.values()), "sides": dict(side),
                           "confirmations": len(conf), "confirmations_flagged": sum(1 for it in conf if it["fields"])}
    # D59-D65: final policies; status numbers and the distribution of distinct policies by level x actor group x stage
    ff = V2 / "positions" / "final.json"
    if ff.exists():
        F = json.loads(ff.read_text())
        sp = json.loads((V2 / "site" / "data" / "policies.json").read_text())
        lay = {x["id"]: x["layer"] for x in sp}
        dist = {}
        for L in ("university", "school", "computing"):
            c = collections.Counter()
            for q in F["institutional"]:
                if any(lay.get(m) == L for m in q["members"]):
                    c[f"{q['actor']}|{q['phase']}"] += 1
            dist[L] = dict(c)
        dist["course"] = dict(collections.Counter(f"{q['actor']}|{q['phase']}" for q in F["course"]))
        ai = [x for x in sp if x["about_ai"] == "yes"]
        CA = json.loads((V2 / "course_code" / "course_assignments.json").read_text())
        out["distribution"] = dist
        out["status"] = {"about_ai": len(ai), "typed": sum(x["type"] != "UNCOVERED" for x in ai), "uncovered": sum(x["type"] == "UNCOVERED" for x in ai),
                         "set_aside": dict(collections.Counter(F.get("uncovered_set_aside", {}).values())),
                         "placed": sum(1 for x in sp if x.get("via", "").startswith("placed")),
                         "types": len({x["type"] for x in ai if x["type"] != "UNCOVERED"}), "themes": len(out.get("themes", [])),
                         "policies": len(F["institutional"]), "background": sum(q["kind"] == "background" for q in F["institutional"]),
                         "merged": sum(len(q["parts"]) > 1 for q in F["institutional"]), "multi_type": sum(len(q["types"]) > 1 for q in F["institutional"]),
                         "course_statements": len(CA["statements"]), "course_alpha": CA.get("alpha_type"), "course_policies": len(F["course"]),
                         "course_background": sum(q["kind"] == "background" for q in F["course"]),
                         # D67/D68: the policy set counted everywhere (rules, recommendations, facts and warnings)
                         "policy_set": sum(q.get("policy_kind") in ("rule", "recommendation") or q.get("bg_kind") == "fact" for q in F["institutional"]),
                         "course_policy_set": sum(q.get("policy_kind") in ("rule", "recommendation") or q.get("bg_kind") == "fact" for q in F["course"])}
        out["positions"] = {"types": len({t for q in F["institutional"] for t in q["types"]}), "positions": len(F["institutional"])}
        # D66: the pipeline from documents to policies, what kind of text each policy is, and background kinds with examples
        PL = F.get("pipeline", {})
        cu = json.loads((V2 / "site" / "data" / "courses.json").read_text())
        npas = [p for u in cu["universities"] for sl in u["slots"] for p in sl["passages"]]
        kinds = lambda L: dict(collections.Counter(q.get("policy_kind", q["kind"]) for q in L))
        bgk = lambda L: {k: {"n": sum(1 for q in L if q.get("bg_kind") == k), "examples": [q["sentence"] for q in sorted(L, key=lambda q: -q["n_unis"]) if q.get("bg_kind") == k][:4]}
                         for k in ("definition", "reason", "fact", "resource")}
        out["pipeline"] = {
            "inst": {"universities": len({x["uni"] for x in sp}), "documents": len({x["doc"] for x in sp}), "statements": len(sp), "about_ai": len(ai),
                     "not_ai": len(sp) - len(ai), "typed": out["status"]["typed"], "uncovered": out["status"]["uncovered"], "placed": out["status"]["placed"],
                     "types": out["status"]["types"], "themes": out["status"]["themes"], **{k: PL.get(k) for k in ("fine_positions", "force_merged", "cross_type_merged")},
                     "merged_groups": out["status"]["merged"], "kinds": kinds(F["institutional"]), "binding": dict(collections.Counter(x.get("binding") for x in ai)),
                     "background": bgk(F["institutional"])},
            "course": {"universities_checked": len(cu["universities"]), "syllabi": sum(len(sl["syllabi"]) for u in cu["universities"] for sl in u["slots"]),
                       "passages": len(npas), "universities_with_passage": len({u["slug"] for u in cu["universities"] for sl in u["slots"] if sl["passages"]}),
                       "statements": out["status"]["course_statements"], "types": len((cu.get("codebook") or {}).get("types", [])),
                       "themes": len((cu.get("codebook") or {}).get("themes", [])), **{k: PL.get(k) for k in ("course_grouped", "course_not_ai_groups", "course_not_ai_statements", "course_merged")},
                       "kinds": kinds(F["course"]), "background": bgk(F["course"])}}
        # the policy set for the findings page: every policy with every statement behind it (loaded on demand)
        tn = {t["id"]: t.get("name") for t in json.loads((V2 / "site" / "data" / "types.json").read_text())}
        th_of = {t["id"]: t.get("theme") for t in json.loads((V2 / "site" / "data" / "types.json").read_text())}
        uidx, ul = {}, []
        def ui(slug):
            if slug not in uidx:
                uidx[slug] = len(ul)
                ul.append(slug)
            return uidx[slug]
        by_pos = collections.defaultdict(list)
        for x in sp:
            if x.get("pos") and x["about_ai"] == "yes":
                by_pos[x["pos"]].append([ui(x["uni"]), x["layer"][0], x["anchor"], x["link"]])
        cby = collections.defaultdict(list)
        for u in cu["universities"]:
            for sl in u["slots"]:
                for pp in sl["passages"]:
                    for l in pp.get("labels") or []:
                        if l.get("pos"):
                            cby[l["pos"]].append([ui(u["slug"]), sl["slot"], l["anchor"], pp["link"]])
        pol = lambda q, stm, theme: {"id": q["pid"], "s": q["sentence"], "k": q.get("policy_kind"), "bk": q.get("bg_kind"), "st": q["phase"], "a": q["actor"],
                                     "t": q["types"], "th": theme, "n": q["n"], "u": q["n_unis"], "parts": [x["sentence"] for x in q["parts"]] if len(q["parts"]) > 1 else [], "m": stm}
        unames = {u["slug"]: u["name"] for u in json.loads((V2 / "site" / "data" / "universities.json").read_text())} | {u["slug"]: u.get("name") or u["slug"] for u in cu["universities"]}
        cbt = {t["id"]: t for t in (cu.get("codebook") or {}).get("types", [])}
        polset = {"inst": [pol(q, by_pos[q["pid"]], th_of.get(q["type"])) for q in F["institutional"]],
                  "course": [pol(q, cby[q["pid"]], (cbt.get(q["type"]) or {}).get("theme")) for q in F["course"]],
                  "unis": [unames.get(s_, s_) for s_ in ul], "types": tn | {t: c["name"] for t, c in cbt.items()},
                  "themes": {th["id"]: th["label"] for th in out.get("themes", [])} | {th["id"]: th.get("label") or th.get("name") for th in (cu.get("codebook") or {}).get("themes", [])}}
        (V2 / "site" / "policyset.json").write_text(json.dumps(polset, ensure_ascii=False, separators=(",", ":")))
    (V2 / "site_data").mkdir(exist_ok=True)
    (V2 / "site_data" / "summary.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print("wrote v2/site_data/summary.json", {o: sum(1 for t in types if t["origin"] == o and not t["retired"]) for o in ("initial list", "added during coding", "theme review")})


if __name__ == "__main__":
    main()
