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

    PROSE = json.loads((V2 / "role_prose.json").read_text()) if (V2 / "role_prose.json").exists() else {}
    # D77: sub-groups inside a stance x stage cell from the three-member thematic council, and directive wording addressed to the reader
    GROUPS = json.loads((V2 / "role_groups.json").read_text())["cells"] if (V2 / "role_groups.json").exists() else {}
    DIRV = json.loads((V2 / "role_directives.json").read_text()) if (V2 / "role_directives.json").exists() else {}
    roles = {}
    for rk, rl, slug in ROLES:
        parts = []
        for layer, pols, theme_of, thl, tho, ex, sts in [
                ("inst", POS, lambda q: T.get(q["type"], {}).get("theme", "other"), TH, THO, inst_examples, lambda q: st_inst[q["pid"]]),
                ("course", CP, lambda q: CB.get(q["type"], {}).get("theme", "other"), CTH, CTHO, course_examples, lambda q: st_course[q["pid"]])]:
            L = [q for q in pols if q["actor"] == rk]
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
                        matrix[s][g] = {"n": len(G), "themes": [[thl.get(t, "Other"), n] for t, n in Counter(theme_of(q) for q in G).most_common()]}
                        gr = GROUPS.get(f"{rk}|{layer}|{s}|{g}", [])
                        stages.append({"id": g, "label": STAGE_NOTE[g], "groups": gr, "policies": [{
                            "pid": q["pid"], "sentence": q["sentence"], "directive": DIRV.get(q["pid"], ""), "stance": s, "stage": g, "theme": thl.get(theme_of(q), "Other"), "kind": kind(q),
                            "n_unis": q["n_unis"], "n": len(sts(q)), "levels": [LEVN[l] for l in q.get("levels", [])], "examples": ex(q)} for q in G]})
                stances.append({"id": s, "label": STANCE[s], "def": SDEF[s], "n": len(S), "n_unis": unis(S), "prose": pr.get("stances", {}).get(s, ""), "stages": stages})
            parts.append({"layer": layer, "title": "University, school and department policies" if layer == "inst" else "CS course policies",
                          "n": len(L), "n_statements": sum(len(sts(q)) for q in L), "n_unis": unis(L), "intro": pr.get("intro", ""),
                          "stage_n": {g: sum(1 for q in L if q["phase"] == g) for g, _ in STG}, "stance_order": [x["id"] for x in stances],
                          "matrix": {s: matrix[s] for s in (x["id"] for x in stances)}, "stances": stances})
        roles[rk] = {"label": rl, "slug": slug, "parts": parts}
    out = {"generated": date.today().isoformat(), "site": SITE, "stance_labels": STANCE, "stance_defs": SDEF, "stages": [[g, STAGE_NOTE[g]] for g, _ in STG], "roles": roles}
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
    SHORT = {"before-course": "Before the course", "course-start": "At the start", "during-work": "While students work", "during-assessment": "During assessment",
             "when-misuse": "When misuse is suspected", "over-time": "Over time", "background": "Background"}
    plural = lambda n, one, many: f"{n} {one if n == 1 else many}"

    doc.add_heading(f"AI policies for {who}", 0)
    p = doc.add_paragraph()
    run(p, f"US universities and their computer science courses. AI Policy Atlas, {date.fromisoformat(data['generated']):%B %-d, %Y}. Website: ", color="5B6570")
    link(p, url, url)
    doc.add_heading("About this document", 1)
    for t in [
        f"This document lists every policy that US university documents and CS course syllabi address to {who}. It draws on {M['n_documents']} university-wide, school and department documents from {M['n_universities']} universities, and on {cpas} AI passages in CS syllabi at {cuni} of those universities.",
        f"A policy is one thing asked of one group. Statements that ask {who} to do the same thing are merged into one policy, whether they say must or should and however they are worded. The policy sentence summarizes those statements. Appendices A and B quote the original wording with links to the sources, and the website lists every statement behind each policy.",
        "Part 1 combines university-wide, school and department documents; Part 2 covers CS course syllabi. Within each part, policies are grouped by stance, that is, what the policy does about AI use. Within a stance, they follow the course from before it starts to after it ends.",
        "Each policy ends with its theme, whether it is a rule, a recommendation or a fact, and two counts. \u201c13 universities, 15 statements\u201d means that 15 statements from 13 different universities were merged into the policy; a university counts once however many of its documents state it. Levels: U university-wide, S school or college, C computing department. The ID links to the policy's sources in the appendix.",
        f"Policies addressed to everyone in a university also apply to {who}. They are not repeated here; the website lists them on its Other roles page."]:
        doc.add_paragraph(t)
    parts = R["parts"]
    t = doc.add_table(rows=1, cols=4)
    t.style = "Table Grid"
    for c, v in zip(t.rows[0].cells, ["Stance", "What the policy does about AI use", "Part 1", "Part 2"]):
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

    for i, part in enumerate(parts, 1):
        landscape(True)
        doc.add_heading(f"Part {i}. {part['title']} for {who}", 1)
        p = doc.add_paragraph()
        run(p, part["intro"] or f"{plural(part['n'], 'policy', 'policies')} from {part['n_statements']:,} statements at {part['n_unis']} universities.")
        p = doc.add_paragraph()
        run(p, "On the website: ", size=9, color="5B6570")
        link(p, f"{url}/{part['layer']}", f"{url}/{part['layer']}", size=9)
        stg = [g for g, _ in data["stages"]]
        mx = max([c["n"] for s in part["matrix"].values() for c in s.values()] or [1])
        t = doc.add_table(rows=1, cols=len(stg) + 2)
        t.style = "Table Grid"
        for c, v in zip(t.rows[0].cells, ["Stance"] + [SHORT[g] for g in stg] + ["All"]):
            c.text = ""
            run(c.paragraphs[0], v, bold=True, size=8)
            shade(c, "EEEEEE")
        for x in part["stances"]:
            cells = t.add_row().cells
            cells[0].text = ""
            run(cells[0].paragraphs[0], x["label"], bold=True, size=8)
            for c, g in zip(cells[1:], stg):
                c.text = ""
                cell = part["matrix"][x["id"]][g]
                if not cell["n"]:
                    continue
                run(c.paragraphs[0], str(cell["n"]), bold=True, size=9)
                sg = next(z for z in x["stages"] if z["id"] == g)
                for lab, n in ([[gr["label"], len(gr["pids"])] for gr in sg["groups"]] if sg["groups"] else cell["themes"]):
                    q = c.add_paragraph()
                    q.paragraph_format.space_after = Pt(0)
                    run(q, f"{lab} ({n})", size=7)
                shade(c, mix(0.08 + 0.5 * (cell["n"] / mx) ** 0.5))
            cells[-1].text = ""
            run(cells[-1].paragraphs[0], str(x["n"]), bold=True, size=9)
        cells = t.add_row().cells
        for c, v in zip(cells, ["All stances"] + [str(part["stage_n"][g] or "–") for g in stg] + [str(part["n"])]):
            c.text = ""
            run(c.paragraphs[0], v, bold=True, size=8.5)
        for row in t.rows:
            row.cells[0].width = Inches(1.25)
        p = doc.add_paragraph()
        run(p, "Each cell: number of policies, then the groups they fall into, with counts. Darker cells hold more policies; empty cells have none.", italic=True, size=8, color="5B6570")
        landscape(False)
        for x in part["stances"]:
            doc.add_heading(f"{x['label']}: {plural(x['n'], 'policy', 'policies')}, {plural(x['n_unis'], 'university', 'universities')}", 2)
            p = doc.add_paragraph()
            run(p, x["def"] + " ", italic=True, color="5B6570")
            if x["prose"]:
                run(p, x["prose"])
            for g in x["stages"]:
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(6)
                p.paragraph_format.space_after = Pt(2)
                run(p, f"{g['label']} ({len(g['policies'])})", bold=True, size=9.5, color="1F5F8B")
                byid = {q["pid"]: q for q in g["policies"]}
                for gr in (g["groups"] or [{"label": "", "pids": [q["pid"] for q in g["policies"]]}]):
                    if gr["label"]:
                        p = doc.add_paragraph()
                        p.paragraph_format.space_before = Pt(3)
                        p.paragraph_format.space_after = Pt(1)
                        p.paragraph_format.left_indent = Inches(0.1)
                        run(p, f"{gr['label']} ({len(gr['pids'])})", bold=True, italic=True, size=9)
                    for q in (byid[i] for i in gr["pids"] if i in byid):
                      p = doc.add_paragraph(style="List Bullet")
                      p.paragraph_format.space_after = Pt(1)
                      run(p, (q["directive"] or q["sentence"]) + " ")
                      run(p, f"{q['kind']} · {plural(q['n_unis'], 'university', 'universities')}, {plural(q['n'], 'statement', 'statements')}"
                        + (f" · {' '.join(q['levels'])}" if q["levels"] else "") + " · ", size=8.5, color="5B6570")
                      link(p, bid(q["pid"]), q["pid"], size=8.5, anchor=True)

    for i, part in enumerate(parts, 1):
        doc.add_page_break()
        doc.add_heading(f"Appendix {'AB'[i - 1]}. Sources for Part {i}", 1)
        p = doc.add_paragraph()
        run(p, "For each policy: up to three statements in the institutions' own words, each from a different university, with a link to the source. "
            "The website link lists every statement behind the policy.", size=9, color="5B6570")
        for x in part["stances"]:
            for g in x["stages"]:
                for q in g["policies"]:
                    p = doc.add_paragraph()
                    p.paragraph_format.space_before = Pt(6)
                    p.paragraph_format.space_after = Pt(1)
                    run(p, q["pid"] + "  ", bold=True, size=9)
                    run(p, q["directive"] or q["sentence"], bold=True, size=9)
                    bookmark(p, bid(q["pid"]))
                    p = doc.add_paragraph()
                    p.paragraph_format.space_after = Pt(1)
                    run(p, f"{x['label']} · {g['label']} · {q['theme']} · {plural(q['n_unis'], 'university', 'universities')}, {plural(q['n'], 'statement', 'statements')} · ", size=8, color="5B6570")
                    link(p, f"{url}/{part['layer']}/{q['pid']}", "all statements on the website", size=8)
                    for e in q["examples"]:
                        p = doc.add_paragraph()
                        p.paragraph_format.left_indent = Inches(0.25)
                        p.paragraph_format.space_after = Pt(1)
                        run(p, f"\u201c{e['anchor']}\u201d ", italic=True, size=8.5)
                        run(p, f"{e['uni']}" + (f", {e['course']}" if e.get("course") else "") + " · ", size=8, color="5B6570")
                        link(p, e["link"], "source", size=8)
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
