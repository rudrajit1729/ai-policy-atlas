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
ROLES = [("student", "Students", "students"), ("instructor", "Instructors", "instructors")]
LEVN = {"university": "U", "school": "S", "computing": "C"}
SORDER = list(STANCE)
STAGE_NOTE = {"before-course": "Before the course", "course-start": "At the start of the course", "during-work": "While students work",
              "during-assessment": "During assessment", "when-misuse": "When misuse is suspected", "over-time": "Over time",
              "background": "Background: facts and context"}
SDEF = {"prohibit": "AI is not allowed.", "restrict": "AI is allowed only for listed uses.", "permit": "AI is allowed under conditions such as disclosure.",
        "encourage": "AI use is invited or promoted.", "require": "Something is required when AI is used (or AI use is required).",
        "delegates": "The instructor or assignment decides.", "none": "Sets a duty or states a fact without allowing or restricting AI."}


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

    roles = {}
    for rk, rl, slug in ROLES:
        parts = []
        for layer, pols, theme_of, thl, tho, ex, nst in [
                ("inst", POS, lambda q: T.get(q["type"], {}).get("theme", "other"), TH, THO, inst_examples, lambda q: len(st_inst[q["pid"]])),
                ("course", CP, lambda q: CB.get(q["type"], {}).get("theme", "other"), CTH, CTHO, course_examples, lambda q: len(st_course[q["pid"]]))]:
            L = [q for q in pols if q["actor"] == rk]
            unis = set()
            for q in L:
                unis |= {x["uni"] for x in (st_inst[q["pid"]] if layer == "inst" else st_course[q["pid"]])}
            stances = [s for s in SORDER if any(q["stance"] == s for q in L)]
            stages = []
            for sk, _ in STG:
                S = [q for q in L if q["phase"] == sk]
                if not S:
                    stages.append({"id": sk, "label": STAGE_NOTE[sk], "n": 0, "cells": {}, "themes": []})
                    continue
                cells = {}
                for s in stances:
                    cq = [q for q in S if q["stance"] == s]
                    if cq:
                        cells[s] = {"n": len(cq), "themes": [[thl.get(t, "Other"), n] for t, n in Counter(theme_of(q) for q in cq).most_common()]}
                themes = []
                for t in tho + ["other"]:
                    tq = sorted((q for q in S if theme_of(q) == t), key=lambda q: (SORDER.index(q["stance"]), -q["n_unis"], -q["n"]))
                    if tq:
                        themes.append({"id": t, "label": thl.get(t, "Other"), "policies": [{
                            "pid": q["pid"], "sentence": q["sentence"], "stance": q["stance"], "kind": kind(q), "n_unis": q["n_unis"],
                            "n": nst(q), "levels": [LEVN[l] for l in q.get("levels", [])], "examples": ex(q)} for q in tq]})
                stages.append({"id": sk, "label": STAGE_NOTE[sk], "n": len(S), "cells": cells, "themes": themes})
            parts.append({"layer": layer, "title": "University, school and department policies" if layer == "inst" else "CS course policies",
                          "n": len(L), "n_statements": sum(nst(q) for q in L), "n_unis": len(unis), "stances": stances, "stages": stages,
                          "facts": facts(L, rl.lower(), layer)})
        roles[rk] = {"label": rl, "slug": slug, "parts": parts}
    out = {"generated": date.today().isoformat(), "site": SITE, "stance_labels": STANCE, "stance_defs": SDEF, "roles": roles}
    (D / "roles.json").write_text(json.dumps(out, ensure_ascii=False))
    return out


def facts(L, who, layer):
    """Short statements computed from the counts; nothing interpretive."""
    n = len(L)
    if not n:
        return []
    pct = lambda k: f"{k} of {n} ({k / n:.0%})"
    st = Counter(q["phase"] for q in L)
    sc = Counter(q["stance"] for q in L)
    kd = Counter(kind(q) for q in L)
    top, ts = st.most_common(1)[0], sc.most_common(1)[0]
    empty = [STAGE_NOTE[s].lower() for s, _ in STG if s != "background" and not st[s]]
    pl = lambda k, one, many: f"{k} {one if k == 1 else many}"
    where = "are background facts and context" if top[0] == "background" else "apply " + STAGE_NOTE[top[0]].lower()
    f = [f"{pct(top[1])} {where}.",
         f"The most common stance is {STANCE[ts[0]]}: {pct(ts[1])}.",
         f"{pl(kd['rule'], 'is a rule', 'are rules')}, {pl(kd['recommendation'], 'recommendation', 'recommendations')} and {pl(kd['fact or warning'], 'fact or warning', 'facts or warnings')}."]
    if empty:
        f.append("No policy for " + who + " applies " + ", ".join(empty) + ".")
    return f


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
    doc.add_heading(f"What AI policies ask of {who}", 0)
    p = doc.add_paragraph()
    run(p, f"US universities and their computer science courses. Generated {date.fromisoformat(data['generated']):%B %-d, %Y} from the AI Policy Atlas. ", color="5B6570")
    run(p, "Website: ", color="5B6570")
    link(p, url, url)
    doc.add_heading("How to read this", 1)
    for t in [
        f"Part 1 combines university-wide, school or college, and department (computing unit) documents. Part 2 covers CS course syllabi. Both list only policies addressed to {who}. Policies addressed to everyone also apply to {who}; they are on the website's Other roles page.",
        "A policy is one thing asked of one group. Statements that ask the same group to do the same thing are merged into one policy, whatever their wording. Each policy sentence summarizes the statements merged into it. Original wording, with a link to each source, is in the appendices; the website lists every statement.",
        "Each part opens with a matrix: course stages (rows, in course order) by stance (columns). A cell gives the number of policies and their themes. Darker cells hold more policies. The policies follow, stage by stage, grouped by theme.",
        "Each policy ends with its stance, its kind (rule, recommendation, or fact or warning), how many universities state it, and an ID that links to its sources in the appendix."]:
        doc.add_paragraph(t, style="List Bullet")
    p = doc.add_paragraph()
    run(p, "Stances. ", bold=True)
    run(p, " ".join(f"{data['stance_labels'][s]}: {data['stance_defs'][s]}" for s in SORDER))

    for i, part in enumerate(R["parts"], 1):
        landscape(True)
        doc.add_heading(f"Part {i}. {part['title']} for {who}", 1)
        p = doc.add_paragraph()
        run(p, f"{part['n']} policies, from {part['n_statements']:,} statements at {part['n_unis']} universities. ")
        run(p, " ".join(part["facts"]))
        p = doc.add_paragraph()
        run(p, "On the website: ", color="5B6570")
        link(p, f"{url}/{part['layer']}", f"{url}/{part['layer']}")
        sts = part["stances"]
        mx = max([c["n"] for s in part["stages"] for c in s["cells"].values()] or [1])
        t = doc.add_table(rows=1, cols=len(sts) + 2)
        t.style = "Table Grid"
        hdr = ["Stage"] + [data["stance_labels"][s] for s in sts] + ["All"]
        for c, v in zip(t.rows[0].cells, hdr):
            c.text = ""
            run(c.paragraphs[0], v, bold=True, size=8)
            shade(c, "EEEEEE")
        for s in part["stages"]:
            cells = t.add_row().cells
            cells[0].text = ""
            run(cells[0].paragraphs[0], s["label"], bold=True, size=8)
            for c, sk in zip(cells[1:], sts):
                c.text = ""
                cell = s["cells"].get(sk)
                if not cell:
                    continue
                run(c.paragraphs[0], str(cell["n"]), bold=True, size=9)
                for lab, n in cell["themes"]:
                    q = c.add_paragraph()
                    q.paragraph_format.space_after = Pt(0)
                    run(q, f"{lab} ({n})", size=7)
                shade(c, mix(0.08 + 0.5 * (cell["n"] / mx) ** 0.5))
            cells[-1].text = ""
            run(cells[-1].paragraphs[0], str(s["n"]) if s["n"] else "–", bold=True, size=9)
        for row in t.rows:
            row.cells[0].width = Inches(1.3)
        p = doc.add_paragraph()
        run(p, "Cells: number of policies, then their themes with counts. A dash means no policy for this stage.", italic=True, size=8, color="5B6570")
        landscape(False)
        doc.add_heading(f"Part {i} policies, stage by stage", 2)
        for s in part["stages"]:
            h = doc.add_heading(f"{s['label']} ({s['n']})", 3)
            if not s["n"]:
                doc.add_paragraph(f"No policy addressed to {who} at this stage.").runs[0].italic = True
                continue
            for th in s["themes"]:
                p = doc.add_paragraph()
                p.paragraph_format.space_after = Pt(2)
                run(p, th["label"], bold=True, size=9.5, color="1F5F8B")
                for q in th["policies"]:
                    p = doc.add_paragraph(style="List Bullet")
                    p.paragraph_format.space_after = Pt(1)
                    run(p, q["sentence"] + " ")
                    run(p, f"{data['stance_labels'][q['stance']]} · {q['kind']} · {q['n_unis']} {'university' if q['n_unis'] == 1 else 'universities'}"
                        + (f" · {' '.join(q['levels'])}" if q["levels"] else "") + " · ", size=8.5, color="5B6570")
                    link(p, bid(q["pid"]), q["pid"], size=8.5, anchor=True)

    for i, part in enumerate(R["parts"], 1):
        doc.add_page_break()
        doc.add_heading(f"Appendix {'AB'[i - 1]}. Sources for Part {i}", 1)
        p = doc.add_paragraph()
        run(p, "For each policy: up to three statements in the institution's own words, each from a different university, with a link to the source. "
            "The website link lists every statement behind the policy." + (" Levels: U university-wide, S school or college, C computing unit." if part["layer"] == "inst" else ""), size=9, color="5B6570")
        for s in part["stages"]:
            for th in s["themes"]:
                for q in th["policies"]:
                    p = doc.add_paragraph()
                    p.paragraph_format.space_before = Pt(6)
                    p.paragraph_format.space_after = Pt(1)
                    run(p, q["pid"] + "  ", bold=True, size=9)
                    run(p, q["sentence"], bold=True, size=9)
                    bookmark(p, bid(q["pid"]))
                    p = doc.add_paragraph()
                    p.paragraph_format.space_after = Pt(1)
                    run(p, f"{s['label']} · {th['label']} · {data['stance_labels'][q['stance']]} · {q['n']} statements at {q['n_unis']} universities · ", size=8, color="5B6570")
                    link(p, f"{url}/{part['layer']}/{q['pid']}", "all statements on the website", size=8)
                    for x in q["examples"]:
                        p = doc.add_paragraph()
                        p.paragraph_format.left_indent = Inches(0.25)
                        p.paragraph_format.space_after = Pt(1)
                        run(p, f"“{x['anchor']}” ", italic=True, size=8.5)
                        run(p, f"{x['uni']}" + (f", {x['course']}" if x.get("course") else "") + " · ", size=8, color="5B6570")
                        link(p, x["link"], "source", size=8)
    name = f"{R['label'][:-1]}_AI_Policies.docx"
    doc.save(V2 / "exports" / name)
    shutil.copy(V2 / "exports" / name, D / name)
    return name


def main():
    data = build()
    for rk, _, _ in ROLES:
        n = docx_for(data, rk)
        R = data["roles"][rk]
        print(n, " | ".join(f"{p['layer']}: {p['n']} policies, {p['n_statements']} statements, {p['n_unis']} universities" for p in R["parts"]))


if __name__ == "__main__":
    main()
