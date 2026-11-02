#!/usr/bin/env python3
"""Build v2/exports/course_layer.xlsx from v2/course/*.json (D41): the course-layer data set for later analysis.

Deterministic. Every "AI passage (verbatim)" cell is cut by this script from the saved syllabus text between the
collector's ai_start and ai_end markers. No AI-written text goes into any source column.
Sheets: README, Frame (one row per university x slot), Syllabi (one row per syllabus), AI passages (one row per passage),
Coverage (per university: how many of the 4 frame courses have a public syllabus / an AI policy).
"""
import json
import re
from pathlib import Path
from urllib.parse import quote

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "v2"


def fold_map(t):
    """Folded text plus a map from folded index to original index."""
    out, idx, prev_space = [], [], False
    tr = {"’": "'", "‘": "'", "“": '"', "”": '"', " ": " "}
    for i, ch in enumerate(t):
        ch = tr.get(ch, ch)
        if ch.isspace():
            if prev_space:
                continue
            ch, prev_space = " ", True
        else:
            prev_space = False
        out.append(ch)
        idx.append(i)
    return "".join(out), idx


def fold(s):
    return fold_map(s)[0].strip()


def cut(text, start, end):
    ft, idx = fold_map(text)
    st, en = fold(start), fold(end)
    i0 = ft.find(st) if st else -1
    if i0 < 0:
        return None, None
    j = ft.find(en, i0) if en else -1
    if j < 0:
        return None, None
    a, b = idx[i0], idx[min(j + len(en), len(idx)) - 1] + 1
    return text[a:b], a


def sheet(wb, name, head, rows, widths):
    ws = wb.create_sheet(name)
    ws.append(head)
    for c in ws[1]:
        c.font = Font(bold=True)
    for r in rows:
        ws.append([json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v for v in r])
    for i, w in enumerate(widths):
        ws.column_dimensions[ws.cell(1, i + 1).column_letter].width = w
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "A2"


def main():
    frame, syl, pas, cov, other = [], [], [], [], []
    for f in sorted((V2 / "course").glob("*.json")):
        c = json.loads(f.read_text())
        prog = c.get("program") or {}
        n_pub = n_ai = 0
        extra = {}
        for x in c.get("courses", []):
            st = x.get("status") if x.get("course") else "no-such-course"
            frame.append([c.get("slug"), c.get("university"), prog.get("name"), prog.get("unit"), x.get("slot"), x.get("course"),
                          x.get("title"), st, len(x.get("syllabi", [])), x.get("sections_in_term"), x.get("catalog_url"),
                          prog.get("requirements_url"), x.get("alternatives"), x.get("searches"), x.get("note")])
            if x.get("slot") in ("C5", "C6"):
                extra[x["slot"]] = f"{x.get('course') or '-'}: {st}"
                for alt in x.get("alternatives") or []:
                    other.append([c.get("slug"), x.get("slot"), "alternative listed in the catalog", alt, ""])
            else:
                n_pub += st in ("public-ai-policy", "public-no-ai", "public-generic-only")
                n_ai += st in ("public-ai-policy", "public-generic-only")
                for alt in x.get("alternatives") or []:
                    other.append([c.get("slug"), x.get("slot"), "alternative listed in the catalog", alt, ""])
            for y in x.get("syllabi", []):
                tf = y.get("text_file") or ""
                p = Path(tf) if tf.startswith("/") else ROOT / tf
                text = p.read_text(errors="ignore") if tf and p.exists() else ""
                syl.append([c.get("slug"), x.get("slot"), x.get("course"), y.get("id"), y.get("term"), y.get("year"), y.get("older"), y.get("section"),
                            st, y.get("url"), tf, len(text), len(y.get("ai_passages", []))])
                for k, a in enumerate(y.get("ai_passages", [])):
                    passage, off = cut(text, a.get("ai_start", ""), a.get("ai_end", ""))
                    link = (y.get("url") or "").split("#")[0] + "#:~:text=" + quote(a.get("ai_start", "")[:80]) if passage else ""
                    pas.append([c.get("slug"), c.get("university"), x.get("slot"), x.get("course"), x.get("title"), y.get("term"), st,
                                k + 1, passage if passage is not None else "", off, "yes" if passage else "NO: markers not found in saved text",
                                len((passage or "").split()), y.get("url"), link, tf])
        cov.append([c.get("slug"), c.get("university"), prog.get("name") if prog else "no CS program", n_pub, n_ai,
                    "profile possible" if n_pub >= 3 else ("insufficient" if prog else "n/a"), extra.get("C5", "not yet collected"), extra.get("C6", "not yet collected")])
    for rp in sorted((V2 / "recheck").glob("*.json")):
        r = json.loads(rp.read_text())
        for ex in r.get("course_examples", []):
            other.append([r.get("slug") or rp.stem, "", "course syllabus seen during the computing recheck (not collected)",
                          ex if isinstance(ex, str) else json.dumps(ex, ensure_ascii=False), ""])
    wb = Workbook()
    ws = wb.active
    ws.title = "README"
    for line in [
        "Course layer (D41): CS syllabi collected on a fixed frame at every university, for bottom-up analysis.",
        "Frame: C1 = CS1 (first required programming course of the CS major); C2 = CS2 (next required programming course);",
        "C3 = required algorithms course (else required systems course); C4 = required software engineering course (else capstone).",
        "Added (D53): C5 = AI / machine learning course (required if required, else the most-offered intro AI or ML course); C6 = upper-level systems or security course, different from C3.",
        "Why these: they are required (or near-universal) in US CS majors, so every department contributes the same courses; they span the degree (novice programming, data structures, theory, professional practice, AI as a subject, systems and security); a fixed frame avoids sampling only courses that happen to post AI policies.",
        "Left out of the frame (see the 'Out of frame' sheet): other electives, non-major intro courses, graduate courses. Courses seen during collection but not in the frame are listed there so they can be collected and coded later.",
        "Courses are identified from the official catalog or degree requirements; the most recent public syllabus is used (2025-26 or later preferred).",
        "status: public-ai-policy | public-no-ai | public-generic-only (only points to a higher-level policy) | outdated (newest public syllabus is Fall 2022 or earlier, pre-ChatGPT) | undated-only | not-public (behind login) | not-found.",
        "public-* statuses count only syllabi from Spring 2023 or later; a pre-ChatGPT syllabus that does not mention AI says nothing about AI policy.",
        "AI passages are cut verbatim by script from the saved syllabus text between collector-chosen start and end words; 'cut verified' = yes means the markers were found.",
        "No coding has been done yet: this file is the input for later qualitative analysis.",
        "A department profile needs current (2023 or later) public syllabi for at least 3 of the 4 frame courses (Coverage sheet).",
        "Instructor names are not recorded.",
    ]:
        ws.append([line])
    ws.column_dimensions["A"].width = 140
    sheet(wb, "Coverage", ["university_slug", "university", "CS program", "frame courses with public syllabus (of 4)",
                           "frame courses with AI text (of 4)", "department profile (C1-C4)", "C5 AI/ML", "C6 systems/security"], cov, [22, 34, 30, 14, 14, 18, 30, 30])
    sheet(wb, "Out of frame", ["university_slug", "near slot", "how it was seen", "course or URL", "collector note"], other, [22, 9, 40, 80, 40])
    sheet(wb, "Frame", ["university_slug", "university", "CS program", "unit", "slot", "course", "title", "status", "syllabi collected",
                        "sections in term", "catalog URL", "degree requirements URL", "alternatives", "searches run", "collector note"],
          frame, [22, 30, 24, 28, 6, 12, 32, 18, 8, 8, 40, 40, 20, 50, 50])
    sheet(wb, "Syllabi", ["university_slug", "slot", "course", "syllabus id", "term", "year", "older than 2025-26", "section", "status", "URL",
                          "saved text file", "saved text chars", "AI passages"], syl, [22, 6, 12, 22, 12, 6, 8, 10, 18, 50, 40, 10, 8])
    sheet(wb, "AI passages", ["university_slug", "university", "slot", "course", "title", "term", "status", "passage #",
                              "ORIGINAL WORDING: AI passage (verbatim, cut by script from the saved syllabus)", "char offset", "cut verified",
                              "words", "syllabus URL", "highlight link", "saved text file"], pas, [22, 30, 6, 12, 30, 12, 18, 6, 100, 9, 12, 8, 45, 45, 35])
    ca_p = V2 / "course_code" / "course_assignments.json"
    if ca_p.exists():  # D49: course codebook coding
        ca = json.loads(ca_p.read_text())["statements"]
        cb = {t["id"]: t for t in json.loads((V2 / "course_codebook.json").read_text())["types"]}
        al = json.loads((V2 / "course_alignment.json").read_text())["map"]
        rows = []
        for f in sorted((V2 / "course_code" / "results").glob("*.json")):
            for pp in json.loads(f.read_text())["passages"]:
                for k, x in enumerate(pp["statements"]):
                    sid = f"{pp['pid']}#{k}"
                    r = ca.get(sid, {})
                    ty = r.get("type", "")
                    rows.append([pp["pid"].split("|")[0], pp["pid"].split("|")[1], pp["pid"].split("|")[2], sid, x["anchor"], x["label"], ty,
                                 (cb.get(ty) or {}).get("name", ty), x["stance"], x["actor"], x["modality"], x["cs_specific"], pp["passage_stance"],
                                 r.get("second_coder") or "", x["why"]])
        sheet(wb, "Course statements", ["university_slug", "slot", "course", "statement id", "ORIGINAL WORDING: anchor (exact syllabus words, script-checked)",
                                        "open-coding label (AI)", "course type", "course type name", "stance", "actor", "modality", "CS-specific", "passage stance",
                                        "second coder's type (25% sample)", "AI rationale"], rows, [18, 6, 10, 30, 60, 30, 8, 34, 10, 10, 10, 8, 10, 10, 60])
        sheet(wb, "Course codebook", ["id", "theme", "name", "covers", "institutional counterpart", "relation", "why"],
              [[t, cb[t]["theme"], cb[t]["name"], cb[t]["covers"], ", ".join(al.get(t, {}).get("institutional", [])), al.get(t, {}).get("relation"), al.get(t, {}).get("why")] for t in cb],
              [7, 6, 40, 70, 20, 10, 60])
        # D63: course policies, built bottom-up from the course statements (positions/final.json)
        ff = V2 / "positions" / "final.json"
        if ff.exists():
            anc = {r[3]: (r[0], r[4]) for r in rows}
            pol_of = {}
            CP = json.loads(ff.read_text())["course"]
            for q in CP:
                for m in q["members"]:
                    pol_of[m] = q["pid"]
            # D67/D68: the course policy set (rules, recommendations, facts and warnings) and the other coded text, on separate sheets
            catq = lambda q: "policy set" if q.get("policy_kind") in ("rule", "recommendation") or q.get("bg_kind") == "fact" else "other coded text"
            CPall = CP
            CP = [q for q in CPall if catq(q) == "policy set"]
            sheet(wb, "Course policies", ["policy id", "policy (shared by its statements)", "actor group", "stage", "course type(s)", "statements", "universities",
                                          "who and how strongly"] + [f"{k} {i}" for i in (1, 2, 3) for k in ("ORIGINAL WORDING", "university_slug")] + ["merged from", "all statement ids"],
                  [[q["pid"], q["sentence"], q["actor"], q["phase"], ", ".join(f"{t} {(cb.get(t) or {}).get('name', t)}" for t in q["types"]), q["n"], q["n_unis"],
                    "; ".join(f"{a} {m} {k}" for a, m, k in q["who"])]
                   + [c for i in range(3) for c in ((anc[q["examples"][i]][1], anc[q["examples"][i]][0]) if i < len(q["examples"]) and q["examples"][i] in anc else ("", ""))]
                   + [" | ".join(f"{x['pid']}: {x['sentence']}" for x in q["parts"]) if len(q["parts"]) > 1 else "", "; ".join(q["members"])] for q in CP],
                  [9, 60, 14, 16, 34, 9, 9, 30, 50, 18, 50, 18, 50, 18, 60, 60])
            sheet(wb, "Course other coded", ["policy id", "text (shared by its statements)", "kind", "background kind", "actor group", "stage", "course type(s)", "statements", "universities", "all statement ids"],
                  [[q["pid"], q["sentence"], q.get("policy_kind"), q.get("bg_kind", ""), q["actor"], q["phase"], ", ".join(f"{t} {(cb.get(t) or {}).get('name', t)}" for t in q["types"]),
                    q["n"], q["n_unis"], "; ".join(q["members"])] for q in CPall if catq(q) != "policy set"], [9, 60, 14, 14, 14, 16, 34, 9, 9, 60])
    out = V2 / "exports"
    out.mkdir(exist_ok=True)
    wb.save(out / "course_layer.xlsx")
    print(f"wrote v2/exports/course_layer.xlsx: {len(cov)} universities, {len(syl)} syllabi, {len(pas)} AI passages "
          f"({sum(1 for r in pas if r[10] == 'yes')} verified)")


if __name__ == "__main__":
    main()
