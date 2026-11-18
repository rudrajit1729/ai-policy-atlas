#!/usr/bin/env python3
"""Role documents (D75): what AI policies ask of students, and of instructors.

For each role, two parts: (1) university, school and department policies combined; (2) CS course policies. Each part has a
matrix of course stage x stance (how many policies, and their themes) and then the policies stage by stage, grouped by theme.
Appendices give, for every policy, original wording with links to the source and a link to the website, where every
statement behind the policy is listed. Nothing is written here that is not in the data: policy sentences are the synthesized
policy set (each summarizes the statements merged into it), themes come from the codebooks, stances follow D72.

Writes v2/site/data/roles.json (read by the site's Students and Instructors pages) and v2/exports/{Student,Instructor}_AI_Policies.docx
(also copied to v2/site/data/ for download). Run after build_report.py.
"""
import json
import shutil
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_report import STANCE, STG, kind, load  # noqa: E402

V2 = Path(__file__).resolve().parents[1]
D = V2 / "site" / "data"
SITE = "https://rudrajit1729.github.io/ai-policy-atlas/"
ROLES = [("student", "Students", "students"), ("instructor", "Instructors", "instructors"), ("staff", "Staff and administrators", "roles"), ("all", "Everyone", "roles")]
DOCS = ("student", "instructor")
LEVN = {"university": "U", "school": "S", "computing": "C"}
SORDER = list(STANCE)
STAGE_NOTE = {"before-course": "Before the course", "course-start": "At the start of the course", "during-work": "During the course",
              "during-assessment": "During assessment", "when-misuse": "When misuse is suspected", "over-time": "Over time",
              "background": "Background: facts and context"}
SDEF = {"prohibit": "AI is not allowed.", "restrict": "AI is allowed only for listed uses.", "permit": "AI is allowed under conditions such as disclosure.",
        "encourage": "AI use is invited or promoted.", "require": "Something is required when AI is used (or AI use is required).",
        "delegates": "The instructor or assignment decides.", "none": "Duties and facts that hold whatever the stance on AI use."}

# D82 (Peggy): tell enforced rules apart from recommendations and from options the policy leaves to the reader
KORDER = ["rule", "recommendation", "option", "fact or warning"]
KINDS = {"rule": ["must", "A rule: you must or must not."], "recommendation": ["should", "A recommendation: you should or should not."],
         "option": ["may", "An option: you may, or need not; the choice is yours."], "fact or warning": ["fact", "A fact or warning."]}

# PI after meeting Peggy: say at the start who writes these policies and who the document is for
AUD = {"instructor": "Who this is for. These are the AI policies that universities, schools and computing departments write for their instructors: what exists, and what instructors are asked to do. They come from provosts, teaching centers, academic integrity offices and department committees, so the first readers are the administrators and committees who write such policies and the instructors who receive them. The CS course level adds the few policies instructors write for themselves in their own syllabi.",
       "student": "Who this is for. These are the AI policies written for students. At the university, school and department level they come from administrators, academic integrity offices and departments. At the CS course level they come from instructors, in their syllabi: instructors writing for their students. The first readers are the instructors and administrators who write such policies and the students who must follow them."}


def accessed():
    """D82: date accessed, from the latest link check (tools/check_links.py)."""
    fs = sorted((V2 / "linkcheck").glob("links_*.csv"))
    if not fs:
        return ""
    import csv
    r = list(csv.DictReader(open(fs[-1])))
    day = date.fromisoformat(r[0]["checked"])
    ok = sum(x["http_status"][0] in "23" for x in r)
    blk = sum(x["http_status"] == "403" for x in r)
    to = sum(x["http_status"] == "000" for x in r)
    gone = sum(x["http_status"] in ("404", "410") for x in r)
    return (f"Date accessed. Sources were collected in October 2026, and the text of every source as it was read is kept in the project records. "
            f"All {len(r):,} source links were checked on {day:%B %-d, %Y}: {ok:,} opened, {blk} refused the automated check (such pages usually open in a browser), "
            f"{to} did not answer in time, and {gone} are no longer at their address. A page that has moved or changed since then does not affect the quotes, which are kept as read.")


def gaps(matrix, who):
    """D82: empty cells are findings. Where AI is allowed or encouraged while work is done but no policy says what that means at assessment."""
    w = lambda s, g: matrix[s][g]["n"]
    ok = [s for s in ("permit", "encourage") if w(s, "during-work") >= 3]
    lead = "Read the empty cells as findings: no policy at this level takes that stance at that point in the course."
    if not ok or any(w(s, "during-assessment") > 1 for s in ok):
        return lead
    nn = lambda n: "none" if n == 0 else ("only one" if n == 1 else str(n))
    bits = [f"{STANCE[s]} has {w(s, 'during-work')} policies during the course and {nn(w(s, 'during-assessment'))} during assessment" for s in ok]
    return (f"{lead} {'; '.join(bits)}. AI use is allowed or encouraged while the work is done, and {who} are left to work out for themselves "
            "what that means when the work is graded.")


def build():
    d = load()
    P, POS, CP = d["P"], d["POS"], d["CP"]
    T = {t["id"]: t for t in json.loads((D / "types.json").read_text())}
    M = json.loads((D / "meta.json").read_text())
    TH = {t["id"]: t["label"] for t in M["themes"]}
    THO = [t["id"] for t in sorted(M["themes"], key=lambda t: t.get("rank", 9))]
    C = json.loads((D / "courses.json").read_text())
    CB = {t["id"]: t for t in C["codebook"]["types"]}
    CTH = {t["id"]: t["label"] for t in C["codebook"]["themes"]}
    CTHO = [t["id"] for t in C["codebook"]["themes"]]
    U = {u["slug"]: u["name"] for u in json.loads((D / "universities.json").read_text())} | {u["slug"]: u.get("name") or u["slug"] for u in C["universities"]}

    # statements behind each policy (institutional: coded statements; course: syllabus passages)
    st_inst = defaultdict(list)
    for x in P:
        if x["about_ai"] == "yes" and x.get("pos"):
            st_inst[x["pos"]].append(x)
    st_course = defaultdict(list)
    for u in C["universities"]:
        for sl in u["slots"]:
            for pp in sl["passages"]:
                for l in pp.get("labels") or []:
                    if l.get("pos"):
                        st_course[l["pos"]].append({"anchor": l["anchor"], "uni": u["slug"], "link": pp["link"], "course": sl.get("course") or sl["slot"]})

    def inst_examples(q):
        xs = st_inst[q["pid"]]
        ids = q.get("examples", [])
        first = [x for i in ids for x in xs if x["id"] == i]
        rest = sorted((x for x in xs if x not in first), key=lambda x: (x.get("binding") != "rule", len(x["anchor"])))
        out, seen = [], set()
        for x in first + rest:
            if x["uni"] in seen:
                continue
            seen.add(x["uni"])
            out.append({"anchor": x["anchor"], "uni": U.get(x["uni"], x["uni"]), "link": x["link"], "level": x["layer"]})
            if len(out) == 3:
                break
        return out

    def course_examples(q):
        out, seen = [], set()
        for x in st_course[q["pid"]] or q.get("examples", []):
            if x["uni"] in seen:
                continue
            seen.add(x["uni"])
            out.append({"anchor": x["anchor"], "uni": U.get(x["uni"], x["uni"]), "link": x["link"], "course": x.get("course")})
            if len(out) == 3:
                break
        return out

    import os
    PROSE = json.loads((V2 / "role_prose.json").read_text()) if (V2 / "role_prose.json").exists() and not os.environ.get("NOPROSE") else {}
    # D77: sub-groups inside a stance x stage cell from the three-member thematic council, and directive wording addressed to the reader
    GROUPS = json.loads((V2 / "role_groups.json").read_text())["cells"] if (V2 / "role_groups.json").exists() else {}
    DIRV = json.loads((V2 / "role_directives.json").read_text()) if (V2 / "role_directives.json").exists() else {}
    # D79: near-duplicates merged inside each group into one item, clearer group labels, AI link for policies that never say AI
    RI = json.loads((V2 / "role_items.json").read_text()) if (V2 / "role_items.json").exists() else {"cells": {}, "ai_link": {}}
    ITEMS, AIL = RI["cells"], RI["ai_link"]
    roles = {}
    for rk, rl, slug in ROLES:
        parts = []
        for layer, pols, theme_of, thl, tho, ex, sts in [
                ("inst", POS, lambda q: T.get(q["type"], {}).get("theme", "other"), TH, THO, inst_examples, lambda q: st_inst[q["pid"]]),
                ("course", CP, lambda q: CB.get(q["type"], {}).get("theme", "other"), CTH, CTHO, course_examples, lambda q: st_course[q["pid"]])]:
            # D81: general integrity or procedural rules restated in AI documents are not AI policies; they are left out of the role views
            L = [q for q in pols if q["actor"] == rk and AIL.get(q["pid"], {}).get("class") != "general"]
            unis = lambda qs: len({x["uni"] for q in qs for x in sts(q)})
            pr = PROSE.get(rk, {}).get(layer, {})
            matrix = {s: {g: {"n": 0, "themes": []} for g, _ in STG} for s in SORDER}
            stances = []
            for s in SORDER:
                S = [q for q in L if q["stance"] == s]
                if not S:
                    continue
                stages = []
                for g, _ in STG:
                    G = sorted((q for q in S if q["phase"] == g), key=lambda q: (-q["n_unis"], -q["n"]))
                    if G:
                        matrix[s][g] = {"n": len(G), "themes": [[thl.get(t, "Other"), n] for t, n in Counter(theme_of(q) for q in G).most_common()],
                                       "kinds": {k: n for k in KORDER if (n := sum(1 for q in G if kind(q) == k))}}
                        ck = f"{rk}|{layer}|{s}|{g}"
                        pols = [{"pid": q["pid"], "sentence": q["sentence"], "directive": (AIL.get(q["pid"], {}).get("directive") or DIRV.get(q["pid"], "")),
                                 "general": AIL.get(q["pid"], {}).get("class") == "general", "stance": s, "stage": g, "theme": thl.get(theme_of(q), "Other"), "kind": kind(q),
                                 "n_unis": q["n_unis"], "n": len(sts(q)), "levels": [LEVN[l] for l in q.get("levels", [])], "examples": ex(q)} for q in G]
                        byq = {q["pid"]: q for q in G}
                        bypol = {x["pid"]: x for x in pols}
                        if ck in ITEMS:
                            gl = []
                            for gr0 in ITEMS[ck]:
                                its0 = []
                                for it in gr0["items"]:
                                    if it["pids"][0] in byq:
                                        vs0 = [v for v in it.get("variants", []) if v["pid"] in byq]
                                        its0.append({**it, "pids": [it["pids"][0]] + [v["pid"] for v in vs0], "variants": vs0})
                                    else:
                                        its0 += [{"pids": [v["pid"]], "directive": "", "variants": []} for v in it.get("variants", []) if v["pid"] in byq]
                                if its0:
                                    gl.append({"label": gr0["label"], "items": its0})
                        else:
                            gl = [{"label": gr["label"], "items": [{"pids": [i], "directive": ""} for i in gr["pids"]]} for gr in GROUPS.get(ck, [])] or [{"label": "", "items": [{"pids": [x["pid"]], "directive": ""} for x in pols]}]
                        groups = []
                        for gr in gl:
                            its = []
                            for it in gr["items"]:
                                qs = [byq[i] for i in it["pids"]]
                                ps = [bypol[i] for i in it["pids"]]
                                exs, seen = [], set()
                                for x in ps:
                                    for e in x["examples"]:
                                        if e["uni"] not in seen and len(exs) < 3:
                                            seen.add(e["uni"])
                                            exs.append(e)
                                vs = [{"id": v["pid"], "differs": v["differs"], "n_unis": bypol[v["pid"]]["n_unis"], "directive": bypol[v["pid"]]["directive"] or bypol[v["pid"]]["sentence"], "kind": bypol[v["pid"]]["kind"]}
                                      for v in it.get("variants", [])]
                                its.append({"ids": it["pids"], "directive": it.get("directive") or ps[0]["directive"] or ps[0]["sentence"], "variants": vs,
                                            "n_unis": len({x["uni"] for q in qs for x in sts(q)}), "n": sum(len(sts(q)) for q in qs),
                                            "kind": ", ".join(dict.fromkeys(x["kind"] for x in ps)), "levels": [l for l in ("U", "S", "C") if any(l in x["levels"] for x in ps)],
                                            "general": all(x["general"] for x in ps), "examples": exs})
                            its.sort(key=lambda t: (t["general"], -t["n_unis"], -t["n"]))
                            groups.append({"label": gr["label"], "n": sum(len(t["ids"]) for t in its), "items": its})
                        stages.append({"id": g, "label": STAGE_NOTE[g], "groups": groups, "policies": pols})
                stances.append({"id": s, "label": STANCE[s], "def": SDEF[s], "n": len(S), "n_unis": unis(S), "prose": pr.get("stances", {}).get(s, ""), "stages": stages})
            parts.append({"layer": layer, "title": "University, school and department level" if layer == "inst" else "CS course level",
                          "n": len(L), "n_statements": sum(len(sts(q)) for q in L), "n_unis": unis(L), "intro": pr.get("intro", ""),
                          "stage_n": {g: sum(1 for q in L if q["phase"] == g) for g, _ in STG}, "stance_order": [x["id"] for x in stances],
                          "matrix": {s: matrix[s] for s in (x["id"] for x in stances)}, "stances": stances,
                          "kinds": {k: n for k in KORDER if (n := sum(1 for q in L if kind(q) == k))}, "gaps": gaps(matrix, rl.lower())})
        roles[rk] = {"label": rl, "slug": slug, "audience": AUD.get(rk, ""), "parts": parts}
    out = {"generated": date.today().isoformat(), "site": SITE, "accessed": accessed(), "stance_labels": STANCE, "stance_defs": SDEF, "kinds": KINDS, "stages": [[g, STAGE_NOTE[g]] for g, _ in STG], "roles": roles}
    (D / "roles.json").write_text(json.dumps(out, ensure_ascii=False))
    return out


# ---------- Word ----------
def docx_for(data, rk):
    from docx import Document
    from docx.enum.section import WD_ORIENT
    from docx.enum.text import WD_BREAK
    from docx.opc.constants import RELATIONSHIP_TYPE as RT
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Inches, Pt, RGBColor

    R = data["roles"][rk]
    url = data["site"] + "#" + R["slug"]
    doc = Document()
    sty = doc.styles["Normal"]
    sty.font.name, sty.font.size = "Calibri", Pt(10.5)
    bm = [0]

    def link(par, href, text, size=None, anchor=False):
        h = OxmlElement("w:hyperlink")
        if anchor:
            h.set(qn("w:anchor"), href)
        else:
            h.set(qn("r:id"), par.part.relate_to(href, RT.HYPERLINK, is_external=True))
        r = OxmlElement("w:r")
        rp = OxmlElement("w:rPr")
        c = OxmlElement("w:color")
        c.set(qn("w:val"), "1F5F8B")
        u = OxmlElement("w:u")
        u.set(qn("w:val"), "single")
        rp.append(c)
        rp.append(u)
        if size:
            sz = OxmlElement("w:sz")
            sz.set(qn("w:val"), str(int(size * 2)))
            rp.append(sz)
        r.append(rp)
        t = OxmlElement("w:t")
        t.text = text
        t.set(qn("xml:space"), "preserve")
        r.append(t)
        h.append(r)
        par._p.append(h)

    def bookmark(par, name):
        bm[0] += 1
        s = OxmlElement("w:bookmarkStart")
        s.set(qn("w:id"), str(bm[0]))
        s.set(qn("w:name"), name)
        e = OxmlElement("w:bookmarkEnd")
        e.set(qn("w:id"), str(bm[0]))
        par._p.insert(0, s)
        par._p.append(e)

    def run(par, text, bold=False, italic=False, size=None, color=None):
        r = par.add_run(text)
        r.bold, r.italic = bold, italic
        if size:
            r.font.size = Pt(size)
        if color:
            r.font.color.rgb = RGBColor.from_string(color)
        return r

    def shade(cell, hexcol):
        tcPr = cell._tc.get_or_add_tcPr()
        s = OxmlElement("w:shd")
        s.set(qn("w:val"), "clear")
        s.set(qn("w:color"), "auto")
        s.set(qn("w:fill"), hexcol)
        tcPr.append(s)

    def mix(f):  # white -> accent blue by f in [0,1]
        a = (0x1F, 0x5F, 0x8B)
        return "".join(f"{round(255 + (c - 255) * f):02X}" for c in a)

    bid = lambda pid: "p_" + "".join(ch if ch.isalnum() else "_" for ch in pid)

    def landscape(on):
        sec = doc.add_section()
        w, h = sec.page_width, sec.page_height
        if on != (sec.orientation == WD_ORIENT.LANDSCAPE):
            sec.orientation = WD_ORIENT.LANDSCAPE if on else WD_ORIENT.PORTRAIT
            sec.page_width, sec.page_height = h, w
        for m in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
            setattr(sec, m, Inches(0.7))

    who = R["label"].lower()
    M = json.loads((D / "meta.json").read_text())
    C = json.loads((D / "courses.json").read_text())
    cpas = sum(len(sl["passages"]) for u in C["universities"] for sl in u["slots"])
    cuni = sum(1 for u in C["universities"] if any(sl["passages"] for sl in u["slots"]))
    SHORT = {"before-course": "Before the course", "course-start": "At the start", "during-work": "During the course", "during-assessment": "During assessment",
             "when-misuse": "When misuse is suspected", "over-time": "Over time", "background": "Background"}
    plural = lambda n, one, many: f"{n} {one if n == 1 else many}"

    doc.add_heading(f"AI policies for {who}", 0)
    p = doc.add_paragraph()
    run(p, f"US universities and their computer science courses. AI Policy Atlas, {date.fromisoformat(data['generated']):%B %-d, %Y}. Website: ", color="5B6570")
    link(p, url, url)
    p = doc.add_paragraph()
    run(p, "Who this is for. ", bold=True)
    run(p, R["audience"].removeprefix("Who this is for. "))
    doc.add_heading("About this document", 1)
    for t in [
        f"This document lists every policy that US university documents and CS course syllabi address to {who}. It draws on {M['n_documents']} university-wide, school and department documents from {M['n_universities']} universities, and on {cpas} AI passages in CS syllabi at {cuni} of those universities.",
        f"A policy is one thing asked of one group. Statements that ask {who} to do the same thing are merged into one policy, whether they say must or should and however they are worded. Each policy here is written as a directive to the reader. Appendices A and B are lookup tables: for every policy ID they quote the original wording, with links to the sources, and the website lists every statement behind each policy.",
        "The document has two levels. The university, school and department level combines university-wide, school or college, and computing department documents. The CS course level covers CS course syllabi. Within each level, policies are grouped by stance, that is, what the policy does about AI use; within a stance, they follow the course from before it starts to after it ends; within a stage, they are grouped by what they ask. The groups come from a thematic analysis by three independent coders, and policies that asked the same thing within a group were combined into one entry.",
        "Each entry gives the kind: a rule (must: you must or must not), a recommendation (should: you should), an option (may: you may, or need not; the choice is left to you), or a fact or warning (fact). It also gives two counts, the levels, and the policy ID or IDs. \u201c13 universities, 15 statements\u201d means that 15 statements from 13 different universities stand behind the entry; a university counts once however many of its documents state it. Levels: U university-wide, S school or college, C computing department. Each ID links to its row in the appendix.",
        f"Policies addressed to everyone in a university also apply to {who}. They are not repeated here; the website lists them on its Other roles page."] + ([data["accessed"]] if data.get("accessed") else []):
        doc.add_paragraph(t)
    parts = R["parts"]
    t = doc.add_table(rows=1, cols=4)
    t.style = "Table Grid"
    for c, v in zip(t.rows[0].cells, ["Stance", "What the policy does about AI use", "University, school, department", "CS course"]):
        c.text = ""
        run(c.paragraphs[0], v, bold=True, size=8.5)
        shade(c, "EEEEEE")
    for sk in SORDER:
        ns = [next((x["n"] for x in pt["stances"] if x["id"] == sk), 0) for pt in parts]
        if not any(ns):
            continue
        cells = t.add_row().cells
        for c, v in zip(cells, [data["stance_labels"][sk], data["stance_defs"][sk]] + [str(n) for n in ns]):
            c.text = ""
            run(c.paragraphs[0], v, size=8.5)
    cells = t.add_row().cells
    for c, v in zip(cells, ["All", "", str(parts[0]["n"]), str(parts[1]["n"])]):
        c.text = ""
        run(c.paragraphs[0], v, bold=True, size=8.5)
    for row in t.rows:
        for c, w in zip(row.cells, (1.4, 3.9, 0.6, 0.6)):
            c.width = Inches(w)

    def cellset(c, text, bold=False, italic=False, size=8.5, color=None):
        c.text = ""
        run(c.paragraphs[0], text, bold=bold, italic=italic, size=size, color=color)

    def header(t, cols):
        for c, v in zip(t.rows[0].cells, cols):
            cellset(c, v, bold=True, size=8)
            shade(c, "EEEEEE")
        tr = t.rows[0]._tr.get_or_add_trPr()
        e = OxmlElement("w:tblHeader")
        e.set(qn("w:val"), "true")
        tr.append(e)

    def widths(t, ws):
        for row in t.rows:
            for c, w in zip(row.cells, ws):
                c.width = Inches(w)

    for i, part in enumerate(parts):
        lev = part["title"]
        landscape(True)
        doc.add_heading(f"{lev}: policies for {who}", 1)
        p = doc.add_paragraph()
        run(p, part["intro"] or f"{plural(part['n'], 'policy', 'policies')} from {part['n_statements']:,} statements at {part['n_unis']} universities.")
        p = doc.add_paragraph()
        run(p, "On the website: ", size=9, color="5B6570")
        link(p, f"{url}/{part['layer']}", f"{url}/{part['layer']}", size=9)
        stg = [g for g, _ in data["stages"]]
        mx = max([c["n"] for s_ in part["matrix"].values() for c in s_.values()] or [1])
        t = doc.add_table(rows=1, cols=len(stg) + 2)
        t.style = "Table Grid"
        doc.add_heading(f"Bird\u2019s-eye view of policies for {who}: {lev}", 2)
        header(t, ["Stance \u2193 \u00b7 When \u2192"] + [SHORT[g] for g in stg] + ["All"])
        for x in part["stances"]:
            cells = t.add_row().cells
            cellset(cells[0], x["label"], bold=True, size=8)
            for c, g in zip(cells[1:], stg):
                c.text = ""
                cell = part["matrix"][x["id"]][g]
                if not cell["n"]:
                    continue
                run(c.paragraphs[0], str(cell["n"]), bold=True, size=9)
                if cell.get("kinds"):
                    q = c.add_paragraph()
                    q.paragraph_format.space_after = Pt(1)
                    run(q, "  ".join(f"{n} {data['kinds'][k][0]}" for k, n in cell["kinds"].items()), bold=True, size=7, color="1F5F8B")
                sg = next(z for z in x["stages"] if z["id"] == g)
                for gr in sg["groups"]:
                    if not gr["label"]:
                        continue
                    q = c.add_paragraph()
                    q.paragraph_format.space_after = Pt(0)
                    run(q, f"{gr['label']} ({gr['n']})", size=7)
                shade(c, mix(0.08 + 0.5 * (cell["n"] / mx) ** 0.5))
            cellset(cells[-1], str(x["n"]), bold=True, size=9)
        cells = t.add_row().cells
        for c, v in zip(cells, ["All stances"] + [str(part["stage_n"][g] or "–") for g in stg] + [str(part["n"])]):
            cellset(c, v, bold=True, size=8.5)
        for row in t.rows:
            row.cells[0].width = Inches(1.3)
        p = doc.add_paragraph()
        run(p, f"{lev}. Rows are stances; columns are when in the course a policy applies. Each cell: number of policies; how many are rules (must), recommendations (should), options (may) and facts or warnings (fact); then the groups they fall into, with counts. Darker cells hold more policies; empty cells have none.", italic=True, size=8, color="5B6570")
        if part.get("gaps"):
            doc.add_paragraph(part["gaps"])
        landscape(False)
        for x in part["stances"]:
            doc.add_heading(f"{lev} · {x['label']}: {plural(x['n'], 'policy', 'policies')}, {plural(x['n_unis'], 'university', 'universities')}", 2)
            p = doc.add_paragraph()
            run(p, x["def"] + " ", italic=True, color="5B6570")
            if x["prose"]:
                run(p, x["prose"])
            for g in x["stages"]:
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(8)
                p.paragraph_format.space_after = Pt(3)
                p.paragraph_format.keep_with_next = True
                run(p, f"{g['label']} ({plural(len(g['policies']), 'policy', 'policies')})", bold=True, size=10, color="1F5F8B")
                t = doc.add_table(rows=1, cols=4)
                t.style = "Table Grid"
                header(t, ["Policy", "Kind", "Universities (statements) · levels", "ID"])
                for gr in g["groups"]:
                    if gr["label"]:
                        row = t.add_row()
                        c = row.cells[0].merge(row.cells[-1])
                        cellset(c, f"{gr['label']} ({plural(gr['n'], 'policy', 'policies')})", bold=True, size=8.5, color="1F5F8B")
                        shade(c, "F3F1EC")
                    for it in gr["items"]:
                        cells = t.add_row().cells
                        cellset(cells[0], it["directive"], size=8.5)
                        if it["general"]:
                            run(cells[0].paragraphs[0], "  general rule", italic=True, size=7.5, color="8A6D3B")
                        for v in it["variants"]:
                            q = cells[0].add_paragraph()
                            q.paragraph_format.left_indent = Inches(0.12)
                            q.paragraph_format.space_after = Pt(0)
                            run(q, "Variant: ", bold=True, size=7.5, color="5B6570")
                            run(q, f"{v['differs']} ({plural(v['n_unis'], 'university', 'universities')}, ", size=7.5, color="5B6570")
                            link(q, bid(v["id"]), v["id"], size=7.5, anchor=True)
                            run(q, ")", size=7.5, color="5B6570")
                        cellset(cells[1], it["kind"], size=8, color="5B6570")
                        cellset(cells[2], f"{it['n_unis']} ({it['n']})" + (f" · {' '.join(it['levels'])}" if it["levels"] else ""), size=8, color="5B6570")
                        cells[3].text = ""
                        for k, pid in enumerate(it["ids"]):
                            if k:
                                run(cells[3].paragraphs[0], ", ", size=8)
                            link(cells[3].paragraphs[0], bid(pid), pid, size=8, anchor=True)
                widths(t, (4.3, 0.95, 1.05, 0.7))

    for i, part in enumerate(parts):
        lev = part["title"]
        doc.add_page_break()
        doc.add_heading(f"Appendix {'AB'[i]}. Lookup table, {lev}", 1)
        p = doc.add_paragraph()
        run(p, "One row per policy ID, in the order of the document. Original wording is quoted from up to three universities, each with a link to the source; the website link lists every statement behind the policy.", size=9, color="5B6570")
        t = doc.add_table(rows=1, cols=3)
        t.style = "Table Grid"
        header(t, ["ID", "Policy · where it sits", "Original wording and sources"])
        for x in part["stances"]:
            for g in x["stages"]:
                for gr in g["groups"]:
                    for it in gr["items"]:
                        for pid in it["ids"]:
                            pol = next(z for z in g["policies"] if z["pid"] == pid)
                            cells = t.add_row().cells
                            cellset(cells[0], pid, bold=True, size=8)
                            bookmark(cells[0].paragraphs[0], bid(pid))
                            cellset(cells[1], pol["directive"] or pol["sentence"], size=8)
                            q = cells[1].add_paragraph()
                            run(q, f"{x['label']} · {g['label']}" + (f" · {gr['label']}" if gr["label"] else "") + f" · {plural(pol['n_unis'], 'university', 'universities')}, {plural(pol['n'], 'statement', 'statements')}", size=7, color="5B6570")
                            cells[2].text = ""
                            first = True
                            for e in pol["examples"]:
                                q = cells[2].paragraphs[0] if first else cells[2].add_paragraph()
                                first = False
                                run(q, f"\u201c{e['anchor']}\u201d ", italic=True, size=7.5)
                                run(q, f"{e['uni']}" + (f", {e['course']}" if e.get("course") else "") + " · ", size=7, color="5B6570")
                                link(q, e["link"], "source", size=7)
                            q = cells[2].add_paragraph()
                            link(q, f"{url}/{part['layer']}/{pid}", "all statements on the website", size=7)
        widths(t, (0.75, 2.9, 3.35))
    name = f"{R['label'][:-1]}_AI_Policies.docx"
    doc.save(V2 / "exports" / name)
    shutil.copy(V2 / "exports" / name, D / name)
    return name


def main():
    data = build()
    for rk in DOCS:
        n = docx_for(data, rk)
        R = data["roles"][rk]
        print(n, " | ".join(f"{p['layer']}: {p['n']} policies, {p['n_statements']} statements, {p['n_unis']} universities" for p in R["parts"]))


if __name__ == "__main__":
    main()
