#!/usr/bin/env python3
"""Write the living Excel record of the v2 corpus: v2/exports/atlas_v2.xlsx.

Rebuilt after every university finishes, so every coded snippet lives in the workbook, not only in caches.
Sheets: README, Definitions (what each term means), Universities, Documents, Policies (reconciled), CoderA, CoderB, Agreement, PolicyTypes, Matrix, Codebook.
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "v2"
sys.path.insert(0, str(V2 / "tools"))
from build_v2 import frag_link  # noqa: E402

HEAD = Font(bold=True, color="FFFFFF")
FILL = PatternFill("solid", fgColor="3B3F9C")


def sheet(wb, title, header, rows, widths=None):
    ws = wb.create_sheet(title)
    ws.append(header)
    for c in ws[1]:
        c.font, c.fill = HEAD, FILL
        c.alignment = Alignment(vertical="top", wrap_text=True)
    for r in rows:
        ws.append(["" if v is None else (", ".join(v) if isinstance(v, list) else v) for v in r])
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    for i, w in enumerate(widths or [], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(vertical="top", wrap_text=True)
    return ws


import re as _re
sys.path.insert(0, str(ROOT / "tools"))
from verify_build import fold_with_map  # noqa: E402

STOP = set("the a an and or of to in for on with by is are be as at this that it its from your you their they may must not no any all if when".split())
_text_cache = {}


def _source(slug, doc_id, collect_cache={}):
    if slug not in collect_cache:
        p = V2 / "collect" / f"{slug}.json"
        collect_cache[slug] = {d["id"]: d for d in json.loads(p.read_text()).get("documents", [])} if p.exists() else {}
    d = collect_cache[slug].get(doc_id) or {}
    tf = d.get("text_file") or ""
    if tf not in _text_cache:
        fp = Path(tf) if tf.startswith("/") else ROOT / tf
        raw = fp.read_text(errors="ignore") if tf and fp.exists() else ""
        _text_cache[tf] = (raw, *fold_with_map(raw))
    return tf, _text_cache[tf]


def _find(needle, src):
    raw, f, m = src
    n = fold_with_map(needle or "")[0].strip()
    if not n:
        return -1, -1
    i = f.find(n)
    return (m[i], m[i + len(n) - 1] + 1) if i >= 0 else (-1, -1)


def _sentence(raw, a, b, fs, fe, src):
    """Source passage cut deterministically: frag_start..frag_end if both found around the anchor, else the sentence."""
    s1, _ = _find(fs, src)
    _, e2 = _find(fe, src)
    if s1 != -1 and e2 != -1 and s1 <= a and e2 >= b and e2 - s1 < 1500:
        return _re.sub(r"\s+", " ", raw[s1:e2]).strip()
    lo = max(raw.rfind(". ", 0, a), raw.rfind("\n\n", 0, a)) + 1
    hi_c = [x for x in (raw.find(". ", b), raw.find("\n\n", b)) if x != -1]
    hi = min(hi_c) + 1 if hi_c else min(len(raw), b + 300)
    return _re.sub(r"\s+", " ", raw[max(0, lo):hi]).strip()[:1500]


NOT_AI_NOTE = _re.compile(r"not (?:\w+ )?(?:AI[- ]specific|specific to (?:generative )?AI|about (?:generative )?AI)|(?:does not|doesn't) (?:mention|name|refer to) (?:generative )?AI\b", _re.I)
NOT_AI_TEXT = "Not about AI (kept, not quoted)"
NOT_AI = ("no", "no (coder note)")


REVIEW = {}  # uid -> theme-review result (v2/theme_review/final_assignments.json, D46/D47), loaded in main()
V3 = {}  # type id -> v3 type (content-only name, theme)
THEMES = {}


def about_ai(u, rv=None):
    """D45: 'yes' / 'no' from the theme review when present; before that, 'no (coder note)' when a coder's
    fit or uncovered note says the statement is not about AI; otherwise 'not yet checked'."""
    if rv:
        return rv["about_ai"]
    if u.get("about_ai") in ("yes", "no"):
        return u["about_ai"]
    if NOT_AI_NOTE.search(" ".join(filter(None, [u.get("fit_note"), u.get("uncovered_note")]))):
        return "no (coder note)"
    return "not yet checked"


def unit_rows(data, who):
    for d in data.get("documents", []):
        tf, src = _source(data.get("slug"), d["id"])
        raw = src[0]
        for i, u in enumerate(d.get("units", []), 1):
            a, b = _find(u.get("anchor"), src)
            fs_ok = _find(u.get("frag_start"), src)[0] != -1
            fe_ok = _find(u.get("frag_end"), src)[0] != -1
            passage = _sentence(raw, a, b, u.get("frag_start"), u.get("frag_end"), src) if a != -1 else ""
            exact_anchor = _re.sub(r"\s+", " ", raw[a:b]) if a != -1 else ""
            quotes = _re.findall(r"[\"\u201c]([^\"\u201d]{3,200})[\"\u201d]", u.get("why") or "")
            bad_q = [q for q in quotes if _find(q, src)[0] == -1]
            pol = u.get("policy") or ""
            words = [w for w in _re.findall(r"[a-z]{4,}", pol.lower()) if w not in STOP]
            overlap = (sum(1 for w in words if w in passage.lower()) / len(words)) if words and passage else None
            flags = []
            if a == -1:
                flags.append("ANCHOR NOT IN SOURCE")
            if not (fs_ok and fe_ok):
                flags.append("highlight bounds not in source")
            if bad_q:
                flags.append("rationale quotes not in source: " + " | ".join(bad_q[:3]))
            if overlap is not None and overlap < 0.5:
                flags.append(f"normalized policy shares only {overlap:.0%} of key words with its source passage")
            rv = REVIEW.get(f"{data.get('slug')}|{d['id']}-u{i:02d}") if who == "reconciled" else None
            ai = about_ai(u, rv)
            ft = rv["type"] if rv else ""
            review_cols = [rv["binding"] if rv else "", ft, (V3.get(ft) or {}).get("name", "UNCOVERED" if ft == "UNCOVERED" else ""),
                           THEMES.get((V3.get(ft) or {}).get("theme_v3"), ""), (rv["via"] + (": " + rv["note"] if rv.get("note") else "")) if rv else ""]
            if ai in NOT_AI:  # D45: kept as a row, but its source wording is not quoted
                exact_anchor, passage, link = NOT_AI_TEXT, NOT_AI_TEXT, ""
            else:
                exact_anchor, link = exact_anchor or u.get("anchor"), frag_link(d.get("url", ""), u.get("frag_start"), u.get("frag_end"))
            yield [who, data.get("slug"), data.get("university"), d["id"], f"{d['id']}-u{i:02d}", d.get("layer"), d.get("stance"),
                   exact_anchor, passage, a if a != -1 else None, d.get("url"), tf, link,
                   u.get("why"), u.get("policy"),
                   u.get("actor"), u.get("phase"), u.get("modality"), u.get("unit_stance"), u.get("policy_type"), u.get("uncovered_note"), u.get("fit_note"), u.get("topics"), ai, *review_cols,
                   "yes" if a != -1 else "NO", "; ".join(flags), PROV.get(who, who)]


PROV = {
    "reconciled": "AI-coded by Claude Sonnet 5.5: Coder A and Coder B coded independently (rationale first, shared codebook), then a Reconciler agent resolved disagreements against the source text. Original-wording columns were cut and verified by script, not by AI. Not yet audited (Opus + GPT audit pending).",
    "coderA": "AI-coded by Claude, Coder A alone (independent first coding, before reconciliation). Dry-run rows: Claude Opus 5.5, calibration only.",
    "coderB": "AI-coded by Claude, Coder B alone (independent first coding, before reconciliation). Dry-run rows: Claude Opus 5.5, calibration only.",
}
UNIT_HEAD = ["source", "university_slug", "university", "doc_id", "unit_id", "layer", "doc_stance",
             "ORIGINAL WORDING: anchor (source text, script-verified)", "ORIGINAL WORDING: source passage (cut by script from the saved document)",
             "anchor char offset in saved text", "source URL", "saved text file", "highlight link",
             "AI rationale (written before the codes were assigned)", "AI-normalized policy statement (blank = the original wording states the policy)",
             "actor", "phase", "modality", "unit_stance", "policy_type", "uncovered_note", "fit_note", "topics",
             "about AI (D45: no = kept, not quoted, not counted)",
             "binding (theme review)", "final type (theme review)", "final type name", "final theme", "theme review: how decided",
             "anchor verified in source", "verification flags", "AI coding provenance"]
UNIT_W = [10, 16, 26, 26, 30, 11, 11, 40, 60, 9, 40, 30, 40, 50, 50, 11, 16, 10, 10, 11, 24, 24, 24, 14, 14, 11, 34, 26, 40, 9, 45, 60]
TYPE_COL = UNIT_HEAD.index("policy_type")
VER_COL = UNIT_HEAD.index("anchor verified in source")
AI_COL = UNIT_HEAD.index("about AI (D45: no = kept, not quoted, not counted)")
FINAL_COL = UNIT_HEAD.index("final type (theme review)")


def ftype(r):
    return r[FINAL_COL] or r[TYPE_COL]


def main():
    tp = V2 / ("policy_types.json" if (V2 / "policy_types.json").exists() else "policy_types_v0.json")
    types = json.loads(tp.read_text())
    tname = {t["id"]: t["name"] for t in types["types"]}
    inst = [json.loads(p.read_text()) for p in sorted((V2 / "inst").glob("*.json"))]
    fa = V2 / "theme_review" / "final_assignments.json"
    if fa.exists():
        REVIEW.update(json.loads(fa.read_text()))
    if (V2 / "policy_types_v3.json").exists():
        v3 = json.loads((V2 / "policy_types_v3.json").read_text())
        V3.update({t["id"]: t for t in v3["types"]})
        THEMES.update({th["id"]: th["label"] for th in v3.get("themes", [])})
    wb = Workbook()
    wb.remove(wb.active)
    sheet(wb, "README", ["item", "description"], [
        ["What this is", "Living record of the Computing AI Policy Atlas v2: every coded policy, with rationale, original wording and a highlight link."],
        ["Layers", "university (university-wide) · school (school/college) · computing (CS and CS-related units) · course (add-on)."],
        ["Policies", "One row per policy unit from the reconciled coding. Columns marked ORIGINAL WORDING are taken from the saved source text by a script (never by a model) and checked; the 'AI rationale' and 'AI-normalized policy statement' columns were written by AI coding agents, and 'AI coding provenance' records which model and agent roles coded each row and whether it has been audited. Rows whose anchor is not found in the source go to the Unverified sheet. 'verification flags' lists any rationale quote not in the source and any normalized policy that drifts from its passage."],
        ["Not about AI (D45)", "Statements and documents that do not talk about AI are kept in the file but not quoted: their ORIGINAL WORDING cells read 'Not about AI (kept, not quoted)', and they are moved from Policies to the NotAboutAI sheet and left out of every count (PolicyTypes, TypeLog, Matrix). Column 'about AI' says how each statement was judged: 'no (coder note)' when a coder flagged it, 'yes'/'no' after the theme review, 'not yet checked' before it. Excluded non-AI documents are listed in the Screening sheet."],
        ["CoderA / CoderB", "The two independent codings before reconciliation (rationale-first, TACT Stage 4)."],
        ["Agreement", "Per-university agreement between the coders, as written by the Reconciler."],
        ["Policies (D59-D68)", "PolicySet sheet: the policy set (rules, recommendations, facts and warnings), the unit counted everywhere. OtherCoded sheet: templates, descriptions, reasons, definitions and resources, kept but not counted. Matrix: statements behind the policy set by the group and stage of their policy and the document stance. Each policy row: the distinct policies, one per actor group and action (must/should wordings of the same action merged; the same policy found under several types merged once and listed under each; TAs, staff and administrators form one actor group; each policy has a stage, or is background: a definition, reason or fact). The policy sentence was written by a Claude Sonnet worker from the grouped statements and restates only what they say; the ORIGINAL WORDING columns are verbatim anchors, script-checked against the saved source text. 'all supporting statement ids' ties every policy to its statements."],
        ["Editing", "Collaborators may add columns (e.g. 'reviewer_note', 'proposed_type') in Policies; the build ignores extra columns."],
    ], [22, 110])
    sheet(wb, "Universities", ["slug", "university", "state", "type", "university layer", "school layer", "computing layer", "course layer", "documents", "policies", "notes"],
          [[u["slug"], u["university"], u.get("state"), u.get("type")] + [(u.get("searched") or {}).get(l) for l in ("university", "school", "computing", "course")]
           + [len(u["documents"]), sum(len(d.get("units", [])) for d in u["documents"]), u.get("notes")] for u in inst],
          [16, 34, 7, 14, 14, 14, 14, 14, 10, 10, 60])
    sheet(wb, "Documents", ["doc_id", "university", "layer", "unit", "course", "title", "url", "date_or_term", "stance", "stance rationale", "tiers", "summary (analyst)", "policies"],
          [[d["id"], u["university"], d.get("layer"), d.get("unit"), d.get("course"), d.get("title"), d.get("url"), d.get("date_or_term"), d.get("stance"),
            d.get("stance_why"), d.get("tiers"), d.get("summary"), len(d.get("units", []))] for u in inst for d in u["documents"]],
          [28, 26, 11, 26, 12, 34, 40, 14, 11, 40, 30, 50, 9])
    scr = json.loads((V2 / "screening_log.json").read_text()) if (V2 / "screening_log.json").exists() else []
    sheet(wb, "Screening", ["doc_id", "university_slug", "layer", "title", "url", "decision", "about AI?", "reason", "AI-term mentions", "decided by"],
          [[x.get("doc_id"), x.get("university"), x.get("layer"), x.get("title"), x.get("url"), x.get("decision"),
            "Not about AI (kept, not quoted)" if not x.get("ai_terms") and x.get("decision") != "include" else ("yes" if x.get("ai_terms") else "few AI terms; included by decision"),
            x.get("decision_reason") or ("fewer than 3 AI-term mentions" if not x.get("ai_terms") else ""), x.get("ai_mentions"), x.get("decision_by")] for x in scr],
          [30, 18, 11, 40, 45, 10, 26, 50, 10, 10])
    allrows = [r for u in inst for r in unit_rows(u, "reconciled")]
    # D64: statements that fit no type at first: placed ones take their policy's type; ones found not about AI are not counted
    ff0 = V2 / "positions" / "final.json"
    if ff0.exists():
        F0 = json.loads(ff0.read_text())
        placed = {m: q["type"] for q in F0["institutional"] for m in q.get("placed", [])}
        aside = F0.get("uncovered_set_aside", {})
        for r in allrows:
            sid = f"{r[1]}:{r[4]}"
            if sid in placed:
                r[FINAL_COL] = placed[sid]
            elif aside.get(sid) == "not_ai":
                r[AI_COL] = "no"
    pol = [r for r in allrows if r[VER_COL] == "yes"]
    ai_ok = [r for r in pol if r[AI_COL] not in NOT_AI]
    # D59-D65: final policies (positions/final.json): one per actor group and action, merged across topics when they say the same
    # thing; every statement keeps its policy id; stage resolves coded 'general' into a stage or 'background'
    ff = V2 / "positions" / "final.json"
    FIN = json.loads(ff.read_text()) if ff.exists() else {"institutional": [], "course": []}
    pos_of = {m: q for q in FIN["institutional"] for m in q["members"]}
    GRP = {"ta-staff": "staff and administrators", "admin": "staff and administrators", "student": "students", "instructor": "instructors", "all": "everyone"}
    # D67/D68: the policy set is rules, recommendations, facts and warnings; the rest is other coded text, kept but not counted
    def cat_of(q):
        if not q:
            return ""
        if q.get("policy_kind") in ("rule", "recommendation"):
            return "policy set: rule or recommendation"
        if q.get("bg_kind") == "fact":
            return "policy set: fact or warning"
        return "other coded text: " + (q.get("policy_kind") if q.get("policy_kind") in ("template", "description") else "reason, definition or resource")
    pos_cols = lambda r: [(pos_of.get(f"{r[1]}:{r[4]}") or {}).get(k, "") for k in ("pid", "sentence", "phase")] + [cat_of(pos_of.get(f"{r[1]}:{r[4]}")), GRP.get(r[15], r[15])]
    extra_h = ["policy id (D59-D65)", "policy (shared by its statements)", "policy stage (D62)", "category (D67/D68)", "actor group (D65)"]
    sheet(wb, "Policies", UNIT_HEAD + ["policy_type name"] + extra_h, [r + [tname.get(r[TYPE_COL], r[TYPE_COL])] + pos_cols(r) for r in ai_ok], UNIT_W + [30, 12, 60, 16, 26, 18])
    if FIN["institutional"]:
        pol_by = {f"{r[1]}:{r[4]}": r for r in ai_ok}
        ex_cols = lambda sid: [pol_by[sid][7], pol_by[sid][2], pol_by[sid][12]] if sid in pol_by else ["", "", ""]
        phead = ["policy id", "policy (shared by its statements)", "category (D67/D68)", "actor group", "stage", "kind", "type", "type name", "also under types",
                                "statements", "universities", "who and how strongly (statements)"] \
            + [f"{k} {i}" for i in (1, 2, 3) for k in ("ORIGINAL WORDING", "university", "highlight link")] + ["merged from (D62)", "why merged", "all supporting statement ids"]
        prow = lambda q: ([q["pid"], q["sentence"], cat_of(q), GRP.get(q["actor"], q["actor"]), q["phase"], q.get("policy_kind"), q["type"], tname.get(q["type"], q["type"]),
                ", ".join(f"{t} {tname.get(t, t)}" for t in q["types"][1:]), q["n"], q["n_unis"], "; ".join(f"{a} {m} {k}" for a, m, k in q["who"])]
               + [c for i in range(3) for c in ex_cols(q["examples"][i] if i < len(q["examples"]) else "")]
               + [" | ".join(f"{x['pid']}: {x['sentence']}" for x in q["parts"]) if len(q["parts"]) > 1 else "", q.get("merge_why", ""), "; ".join(q["members"])])
        pw = [9, 60, 26, 16, 16, 12, 7, 30, 30, 9, 9, 30] + [40, 22, 30] * 3 + [60, 40, 60]
        sheet(wb, "PolicySet", phead, [prow(q) for q in FIN["institutional"] if cat_of(q).startswith("policy set")], pw)
        sheet(wb, "OtherCoded", phead, [prow(q) for q in FIN["institutional"] if not cat_of(q).startswith("policy set")], pw)
    sheet(wb, "NotAboutAI", UNIT_HEAD + ["policy_type name"], [r + [tname.get(r[TYPE_COL], r[TYPE_COL])] for r in pol if r[AI_COL] in NOT_AI], UNIT_W + [30])
    sheet(wb, "Unverified", UNIT_HEAD, [r for r in allrows if r[VER_COL] != "yes"], UNIT_W)
    for who in ("coderA", "coderB"):
        rows = [r for p in sorted((V2 / "dryrun" / who).glob("*.json")) for r in unit_rows(json.loads(p.read_text()), who)]
        rows += [r for p in sorted((V2 / "run" / who).glob("*.json")) for r in unit_rows(json.loads(p.read_text()), who)] if (V2 / "run" / who).exists() else []
        sheet(wb, "Coder" + who[-1], UNIT_HEAD, rows, UNIT_W)
    ag = []
    for p in sorted(list((V2 / "dryrun").glob("agreement_*.json")) + list((V2 / "run").glob("agreement_*.json"))):
        a = json.loads(p.read_text())
        ag.append([p.stem.replace("agreement_", "")] + [a.get(k) for k in ("documents", "units_A", "units_B", "matched", "only_A", "only_B", "kept_only_A", "kept_only_B",
                                                                          "agree_actor", "agree_phase", "agree_modality", "agree_policy_type", "agree_stance_docs", "notes")])
    sheet(wb, "Agreement", ["university", "documents", "units_A", "units_B", "matched", "only_A", "only_B", "kept_only_A", "kept_only_B",
                            "agree_actor", "agree_phase", "agree_modality", "agree_policy_type", "agree_stance_docs", "notes"], ag,
          [18] + [10] * 13 + [80])
    counted = ai_ok  # D45: statements not about AI are kept but not counted
    cnt = Counter(ftype(r) for r in counted)
    unis = defaultdict(set)
    for r in counted:
        unis[ftype(r)].add(r[1])
    tlist = list(V3.values()) if V3 else types["types"]
    sheet(wb, "PolicyTypes", ["id", "name (content-only, theme review)", "name before theme review", "theme", "definition", "status", "policies", "universities"],
          [[t["id"], t["name"], t.get("name_v2", ""), THEMES.get(t.get("theme_v3"), t.get("theme")), t.get("covers"),
            "retired: " + t["retired"] if t.get("retired") else ("added in theme review" if "theme review" in (t.get("added") or "") else ""),
            cnt.get(t["id"], 0), len(unis.get(t["id"], ()))] for t in tlist]
          + [["UNCOVERED", "No existing type fits", "", "", "See uncovered_note and theme-review label in Policies", "", cnt.get("UNCOVERED", 0), len(unis.get("UNCOVERED", ()))]],
          [8, 44, 36, 26, 70, 18, 10, 12])
    if THEMES:
        sheet(wb, "Themes", ["theme", "label", "types", "policies", "universities"],
              [[th_id, lab, ", ".join(t["id"] for t in tlist if t.get("theme_v3") == th_id),
                sum(cnt.get(t["id"], 0) for t in tlist if t.get("theme_v3") == th_id),
                len(set().union(*[unis.get(t["id"], set()) for t in tlist if t.get("theme_v3") == th_id]))] for th_id, lab in THEMES.items()],
              [8, 40, 60, 10, 12])
    stances = [x for x in ["prohibit", "restrict", "permit", "encourage", "require", "delegates"] if any(r[6] == x for r in counted)]  # D58: no empty columns
    # D62/D65/D68: statements behind the policy set only, by the group and stage of their policy
    cell = Counter((GRP.get(pos_of[f"{r[1]}:{r[4]}"]["actor"], pos_of[f"{r[1]}:{r[4]}"]["actor"]), pos_of[f"{r[1]}:{r[4]}"]["phase"], r[6]) for r in counted
                   if cat_of(pos_of.get(f"{r[1]}:{r[4]}")).startswith("policy set"))
    keys = sorted({(a, p) for a, p, _ in cell})
    sheet(wb, "Matrix", ["actor group", "policy stage"] + stances + ["total"],
          [[a, p] + [cell.get((a, p, s), 0) for s in stances] + [sum(cell.get((a, p, s), 0) for s in stances)] for a, p in keys], [12, 18] + [11] * 7)
    alp = V2 / "exports" / "agreement_alpha.json"
    if alp.exists():
        al = json.loads(alp.read_text())
        sheet(wb, "Alpha", ["field", "Krippendorff's alpha (nominal)", "95% CI low", "95% CI high", "percent agreement", "matched pairs"],
              [[f, round(r["alpha"], 3), round(r["ci95"][0], 3), round(r["ci95"][1], 3), round(r["percent_agreement"], 3), r["pairs"]]
               for f, r in al["fields"].items()]
              + [["unitizing (matched / all units)", round(al["unitizing_agreement"], 3), "", "", "", f"{al['matched_pairs']} matched, {al['only_A']} only A, {al['only_B']} only B"]],
              [30, 16, 10, 10, 14, 40])
    dec = json.loads((V2 / "decisions.json").read_text())
    sheet(wb, "Decisions", ["id", "date", "section", "decided by", "decision", "rationale"],
          [[x["id"], x["date"], x["section"], x["by"], x["decision"], x["rationale"]] for x in dec["decisions"]], [6, 11, 22, 16, 70, 60])
    cand = json.loads((V2 / "candidate_types.json").read_text())["candidates"] if (V2 / "candidate_types.json").exists() else []
    sheet(wb, "TypeLog", ["id", "name", "status", "theme", "definition", "when added / first seen", "policies so far", "universities so far"],
          [[t["id"], t["name"], "type (added from the data)" if t.get("added") else "type (initial list)", t.get("theme"), t.get("covers"),
            t.get("added", "initial"), cnt.get(t["id"], 0), len(unis.get(t["id"], ()))] for t in types["types"]]
          + [["", c["name"], c["status"], "", c["definition"], c["first_seen"], "", ", ".join(c["universities"])] for c in cand],
          [6, 40, 22, 14, 70, 24, 10, 30])
    sheet(wb, "Definitions", ["line", "text"], [[i, line] for i, line in enumerate((V2 / "DEFINITIONS.md").read_text().splitlines(), 1) if line.strip()], [8, 160])
    sheet(wb, "Codebook", ["section", "text"], [[i, line] for i, line in enumerate((V2 / "CODEBOOK.md").read_text().splitlines(), 1) if line.strip()], [8, 140])
    out = V2 / "exports"
    out.mkdir(exist_ok=True)
    wb.save(out / "atlas_v2.xlsx")
    print(f"wrote v2/exports/atlas_v2.xlsx: {len(inst)} universities, {len(pol)} reconciled policies "
          f"({len(pol) - len(counted)} marked not about AI: kept, not quoted, not counted)")


if __name__ == "__main__":
    main()
