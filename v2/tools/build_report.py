#!/usr/bin/env python3
"""Shareable report (D70): where things stand, the pipeline, the numbers, what the policies show, decisions for advisors,
and the full policy set (675 institutional + 229 course) grouped by who it addresses and stage so it prints well.

Writes v2/site/report.html (linked from the site's Report page) and v2/site/data/AI_Policy_Atlas_report.docx
(copied to v2/exports/). Reads the same data as the site; run after build_v2.py, export_site_csv.py and build_site_data.py.
No method or reliability section: that stays on the site's Method page.
"""
import csv
import html
import json
import shutil
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

V2 = Path(__file__).resolve().parents[1]
D = V2 / "site" / "data"
SET = ("rr", "fact")
ACT = [("student", "Students"), ("instructor", "Instructors"), ("staff", "Staff and administrators"), ("all", "Everyone")]
STG = [("before-course", "Before the course"), ("course-start", "At the start of the course"), ("during-work", "While students work"),
       ("during-assessment", "During assessment"), ("when-misuse", "When misuse is suspected"), ("over-time", "Over time"),
       ("background", "Background (facts and context)")]
LEV = [("university", "University-wide"), ("school", "School or college"), ("computing", "Computing unit"), ("course", "CS course syllabi")]
LAB = {"university": "U", "school": "S", "computing": "C"}
# D72: stance tag per policy, from the stance of its statements (prohibit, restrict, permit, encourage, require, neutral).
# A policy takes its most common non-neutral stance when at least a quarter of its statements take one; otherwise it is
# "Instructor decides" if its topics are about who decides (P04, P85, CT04), else "No position" (it states a duty or fact without a stance on AI use).
STANCE = {"prohibit": "Prohibit", "restrict": "Only listed uses", "permit": "Allowed with conditions", "encourage": "Encourage", "require": "Require",
          "delegates": "Instructor decides", "none": "No position"}
DECIDES = {"P04", "P85", "CT04"}
KIND = {"rule": "rule", "recommendation": "recommendation", "fact": "fact or warning"}


def kind(q):
    return "fact or warning" if q["cat"] == "fact" else KIND.get(q.get("policy_kind"), q.get("policy_kind") or "")


def stance(c, types):
    n = sum(c.values())
    nn = {k: v for k, v in c.items() if k in STANCE and k not in ("delegates", "none")}
    if nn and sum(nn.values()) >= 0.25 * n:
        return max(nn, key=nn.get)
    return "delegates" if DECIDES & set(types) else "none"


def load():
    P = json.loads((D / "policies.json").read_text())
    POS = [q for q in json.loads((D / "positions.json").read_text()) if q["cat"] in SET]
    C = json.loads((D / "courses.json").read_text())
    M = json.loads((D / "meta.json").read_text())
    CP = [q for q in C.get("policies", []) if q["cat"] in SET]
    lev, stc = defaultdict(set), defaultdict(Counter)
    for x in P:
        if x["about_ai"] == "yes" and x.get("pos"):
            lev[x["pos"]].add(x["layer"])
            stc[x["pos"]][x["unit_stance"]] += 1
    for q in POS:
        q["levels"] = [l for l, _ in LEV if l in lev[q["pid"]]]
        q["stance"] = stance(stc[q["pid"]], q.get("types", [q["type"]]))
    cs = defaultdict(Counter)
    for u in C["universities"]:
        for sl in u["slots"]:
            for pp in sl["passages"]:
                for l in pp.get("labels") or []:
                    if l.get("pos"):
                        cs[l["pos"]][l.get("stance")] += 1
    for q in CP:
        q["stance"] = stance(cs[q["pid"]], q.get("types", [q["type"]]))
    cnt = Counter()
    for r in csv.DictReader(open(D / "csv" / "policy_set_counts.csv")):
        cnt[(r["level"], r["who it addresses"], r["stage"])] += int(r["policies"])
    cu = sum(1 for u in C["universities"] if any(s["passages"] for s in u["slots"]))
    cpas = sum(len(s["passages"]) for u in C["universities"] for s in u["slots"])
    cst = sum(len(p.get("labels") or []) for u in C["universities"] for s in u["slots"] for p in s["passages"])
    n_ai = sum(1 for x in P if x["about_ai"] == "yes")
    return dict(P=P, POS=POS, CP=CP, M=M, cnt=cnt, cu=cu, cpas=cpas, cst=cst, n_ai=n_ai)


def blocks(d):
    """The report as a list of blocks: ("h1"|"h2"|"h3"|"p"|"ul"|"table"|"policies"|"pagebreak", payload)."""
    M, POS, CP, cnt = d["M"], d["POS"], d["CP"], d["cnt"]
    pl, sa = M["pipeline"], M["pipeline"]["set_aside"]
    k = Counter(kind(q) for q in POS)
    kc = Counter(kind(q) for q in CP)
    other = len(json.loads((D / "positions.json").read_text())) - len(POS)
    pct = lambda a, b: f"{a / b:.0%}" if b else "–"
    lvl_tot = {l: sum(v for (L, a, s), v in cnt.items() if L == l) for l, _ in LEV}
    big5 = sum(q["n_unis"] >= 5 for q in POS), sum(q["n_unis"] >= 5 for q in CP)
    merged5 = sum(len(q.get("parts", [])) >= 5 for q in POS)
    B = [("h1", "AI Policy Atlas: the synthesized policy set"),
         ("p", f"Generative-AI policies at US universities and in their computer science courses. Status as of {date.today():%B %-d, %Y}."),
         ("h2", "1. Where things stand"),
         ("ul", [f"**Institutional corpus.** {M['n_documents']:,} policy documents from {M['n_universities']} universities: university-wide, school or college, and computing unit (CS department or college). {M['n_units']:,} statements coded; {d['n_ai']:,} are about AI.",
                 f"**CS course syllabi.** {d['cpas']} AI passages from syllabi at {d['cu']} universities, across six course slots (CS1, CS2, algorithms, software engineering, AI/ML, systems or security). {d['cst']:,} statements coded.",
                 f"**Policy set.** {len(POS)} institutional policies ({k['rule']} rules, {k['recommendation']} recommendations, {k['fact or warning']} facts and warnings) and {len(CP)} course policies ({kc['rule']} rules, {kc['recommendation']} recommendations, {kc['fact or warning']} facts and warnings).",
                 "**A policy** is one thing asked of one group: statements that ask the same group to do the same thing are merged into one policy, whatever their wording, and whether they say must or should. Policies for different groups stay separate.",
                 "**Conflicting policies** are handled by direction: each group's policies are sorted into what to do, what not to do, what is allowed and what to know (the site's By role page), so a \"may\" and a \"must not\" about the same act sit side by side."]),
         ("table", (["Step", "Status"], [
             ["Collect policy documents and syllabi", "Done"],
             ["Code statements (two coders, reconciliation, audit)", "Done"],
             ["Topics and themes", "Done: 139 institutional topics in 15 themes; 50 course topics"],
             ["Synthesize the policy set", f"Done: {len(POS)} institutional + {len(CP)} course"],
             ["Compare CS courses with institutions", "Done by topic; policy-by-policy comparison next"],
             ["Website and editable CSVs", "Done (local)"],
             ["Human review of the policy set", "Next: on a sample (decision 2)"]])),
         ("h2", "2. From statements to policies"),
         ("table", (["Step", "Institutional", "CS courses"], [
             ["Statements coded", f"{M['n_units']:,}", f"{d['cst']:,}"],
             ["About AI", f"{d['n_ai']:,}", f"{d['cst'] - pl['course_not_ai_statements']:,}"],
             ["With a topic", f"{d['n_ai'] - sa['unique'] - sa['not_policy']:,} ({sa['unique']} one-off statements and {sa['not_policy']} non-policies set aside)", "all"],
             ["Grouped within a topic", f"{pl['fine_positions']:,}", f"{pl['course_grouped']}"],
             ["Must and should merged", f"{pl['force_merged']:,}", "–"],
             ["Same policy across topics merged", f"{pl['cross_type_merged']:,}", f"{pl['course_merged']}"],
             ["Templates, descriptions, reasons, definitions, resources (kept apart)", f"{other}", f"{pl['course_merged'] - len(CP)}"],
             ["Policy set: rules, recommendations, facts and warnings", f"**{len(POS)}**", f"**{len(CP)}**"]])),
         ("h2", "3. The numbers"),
         ("p", "Policies in the set by level. A policy found at more than one level counts once at each, so the institutional columns add to more than " + f"{len(POS)}."),
         ("h3", "Who the policies address"),
         ("table", (["Who it addresses"] + [n for _, n in LEV], [[an] + [f"{sum(v for (L, a, s), v in cnt.items() if L == l and a == ak)} ({pct(sum(v for (L, a, s), v in cnt.items() if L == l and a == ak), lvl_tot[l])})" for l, _ in LEV] for ak, an in ACT]
                    + [["Total"] + [str(lvl_tot[l]) for l, _ in LEV]])),
         ("h3", "When the policies apply"),
         ("table", (["Stage"] + [n for _, n in LEV], [[sn] + [f"{sum(v for (L, a, s), v in cnt.items() if L == l and s == sk)} ({pct(sum(v for (L, a, s), v in cnt.items() if L == l and s == sk), lvl_tot[l])})" for l, _ in LEV] for sk, sn in STG])),
         ("h3", "Stance of the policies"),
         ("table", (["Stance", "Institutional", "CS course syllabi"], [[STANCE[st], f"{sum(q['stance'] == st for q in POS)} ({pct(sum(q['stance'] == st for q in POS), len(POS))})",
                     f"{sum(q['stance'] == st for q in CP)} ({pct(sum(q['stance'] == st for q in CP), len(CP))})"] for st in STANCE])),
         ("p", "A policy's stance is the stance most of its statements take on AI use. \"No position\" means the policy sets a duty or states a fact without allowing or restricting AI (for example, verify AI output; AI output can be wrong)."),
         ("h2", "4. What the policies show"),
         ("h3", "Little is binding at the top"),
         ("table", (["Level", "Rule", "Recommendation", "Description", "Template"], [
             ["University-wide", "21%", "33%", "28%", "19%"], ["School or college", "13%", "28%", "28%", "31%"], ["Computing unit", "**45%**", "23%", "27%", "5%"]])),
         ("p", "Share of each level's statements about AI. About a fifth of what universities publish about AI is a rule; the rest is advice, background or sample syllabus text. Schools mostly offer sample text. Computing units write rules."),
         ("h3", "CS compared with universities and schools"),
         ("table", (["", "University-wide", "School or college", "Computing unit", "CS course syllabi"], [
             ["Statements that are rules", "21%", "13%", "45%", f"{pct(kc['rule'], len(CP))} of course policies"],
             ["Documents that take a position (not \"instructor decides\")", "21%", "–", "74%", "–"],
             ["Main group addressed", "instructors", "instructors", "instructors", "students"]])),
         ("ul", ["**CS is more binding.** Rules rise from about a fifth of university statements to almost half for computing units and most of what syllabi say.",
                 "**CS takes a position.** 79% of university-wide documents leave AI to each instructor; 74% of computing-unit documents take a stance themselves.",
                 "**CS is stricter.** Where the university leaves the decision to instructors, 37% of CS course passages ban AI outright (134 of 362).",
                 "**Rules loosen across the degree.** AI is banned in 48% of CS1 passages, 44% of CS2, 34% of algorithms and 11% of software engineering (AI/ML 37%, systems or security 39%).",
                 "**Different audience.** Universities and schools write mostly to instructors (decide your policy, state it in the syllabus). Syllabi write to students (what you may do on this work).",
                 "**Work versus the whole course.** About a quarter of university and school policies are about setting things up before the course. Syllabi spend most of their policies on the work itself.",
                 "**CS talks about code.** Course-only practices: ask AI for explanations, not code (16 universities); AI homework hurts exam readiness (14); AI for test cases (5); sharing AI sessions (3). Courses also add line caps on AI-written code, coding agents, and AI for documentation, comments and formatting.",
                 "**CS leaves out the institution.** 14 topics found at 100 or more universities never appear in syllabi, among them faculty support, policy review, AI literacy, tool approval, research, values and principles, and how the policy was made.",
                 "**Schools and computing units add little that is new.** Only 10 of the 675 institutional policies appear nowhere in a university-wide document; 457 (68%) are university-wide only."]),
         ("h3", "Gaps"),
         ("ul", ["**Assessment is the least-addressed stage.** 16 of 675 institutional policies (2.4%) and 11 of 229 course policies (4.8%). No institutional policy asks staff or administrators anything during assessment.",
                 "**Staff and administrators are rarely addressed in courses.** 2 of 229 course policies, against 102 of 675 institutional policies.",
                 "**Students hear about the work, not the start.** 71% of institutional student policies and 89% of course student policies are about doing the work. Two institutional policies, and none in courses, tell students anything before the course starts."]),
         ("h2", "5. Decisions for the advisors"),
         ("ol", [f"**Is {len(POS)} + {len(CP)} the right size for the synthesized policy set?** All are kept as policies. A core view could show the policies found at 5 or more universities ({big5[0]} institutional, {big5[1]} course) without dropping the rest.",
                 f"**How to run the human review on a sample.** Proposal: two reviewers check (a) every policy merged from 5 or more versions ({merged5}), and (b) a random sample of about 10% of the rest, drawn evenly across who it addresses and stage (about 60 institutional, 25 course). For each: does the sentence say what its statements say, are the merges right, are the group and stage right. Report agreement, fix, and extend the review where errors cluster."]),
         ("pagebreak", None),
         ("h2", f"Appendix A. Institutional policy set ({len(POS)})"),
         ("p", "Grouped by who the policy addresses, then by stage in course order. Within a stage, most widespread first. Universities = how many universities state it. Stance: what the policy does about AI use (Prohibit, Only listed uses, Allowed with conditions, Encourage, Require, Instructor decides, or No position). Levels: U university-wide, S school or college, C computing unit. Each sentence summarizes the statements merged into it; the original wording and sources are in policy_set_statements.csv."),
         ("policies", ("inst", POS)),
         ("pagebreak", None),
         ("h2", f"Appendix B. CS course policy set ({len(CP)})"),
         ("p", "Same grouping. Universities = how many universities have a syllabus that states it. Original wording and syllabus links are in course_policy_statements.csv."),
         ("policies", ("course", CP))]
    return B


def groups(pols):
    for ak, an in ACT:
        sub = [q for q in pols if q["actor"] == ak]
        if not sub:
            continue
        yield an, len(sub), [(sn, sorted([q for q in sub if q["phase"] == sk], key=lambda q: (-q["n_unis"], -q["n"]))) for sk, sn in STG if any(q["phase"] == sk for q in sub)]


def md_inline(s):
    out, bold = [], False
    for i, part in enumerate(s.split("**")):
        out.append(f"<strong>{html.escape(part)}</strong>" if i % 2 else html.escape(part))
    return "".join(out)


def to_html(B):
    h = []
    for t, x in B:
        if t in ("h1", "h2", "h3"):
            h.append(f"<{t}>{html.escape(x)}</{t}>")
        elif t == "p":
            h.append(f"<p>{md_inline(x)}</p>")
        elif t in ("ul", "ol"):
            h.append(f"<{t}>" + "".join(f"<li>{md_inline(i)}</li>" for i in x) + f"</{t}>")
        elif t == "table":
            head, rows = x
            h.append("<table><thead><tr>" + "".join(f"<th>{html.escape(c)}</th>" for c in head) + "</tr></thead><tbody>"
                     + "".join("<tr>" + "".join(f"<td>{md_inline(str(c))}</td>" for c in r) + "</tr>" for r in rows) + "</tbody></table>")
        elif t == "pagebreak":
            h.append('<div class="pb"></div>')
        elif t == "policies":
            layer, pols = x
            for an, n, stages in groups(pols):
                h.append(f'<h3 class="who">{html.escape(an)} <span>{n}</span></h3>')
                for sn, qs in stages:
                    cols = "<th>Policy</th><th>Stance</th><th>Kind</th><th title='Universities'>Univ.</th>" + ("<th>Levels</th>" if layer == "inst" else "")
                    h.append(f'<h4>{html.escape(sn)} <span>{len(qs)}</span></h4><table class="pol"><thead><tr>{cols}</tr></thead><tbody>')
                    for q in qs:
                        lv = f"<td>{' '.join(LAB[l] for l in q['levels'])}</td>" if layer == "inst" else ""
                        h.append(f"<tr><td>{html.escape(q['sentence'])}</td><td><span class='st st-{q['stance']}'>{STANCE[q['stance']]}</span></td><td>{kind(q)}</td><td class=n>{q['n_unis']}</td>{lv}</tr>")
                    h.append("</tbody></table>")
    css = """:root{--bg:#fbfaf7;--ink:#1d2329;--mute:#5b6570;--line:#d9d6cf;--head:#f0ede6;--acc:#1f5f8b}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#15181b;--ink:#e6e3dd;--mute:#9aa3ad;--line:#33383d;--head:#1f2428;--acc:#7fb3d9}}
:root[data-theme="dark"]{--bg:#15181b;--ink:#e6e3dd;--mute:#9aa3ad;--line:#33383d;--head:#1f2428;--acc:#7fb3d9}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 Georgia,'Iowan Old Style',serif}
main{max-width:860px;margin:0 auto;padding:32px 16px 64px}h1{font-size:30px;line-height:1.2;margin:0 0 6px}h1+p{color:var(--mute);margin-top:0}
h2{font-size:21px;margin:40px 0 10px;padding-bottom:4px;border-bottom:2px solid var(--acc)}h3{font-size:17px;margin:26px 0 8px}
h4{font:600 13px/1.4 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.04em;color:var(--mute);margin:18px 0 6px}
h3 span,h4 span{font:500 12px system-ui,sans-serif;color:var(--mute);margin-left:6px}h3.who{color:var(--acc);font-size:19px;margin-top:34px}
table{width:100%;border-collapse:collapse;margin:8px 0 14px;font:13.5px/1.45 system-ui,-apple-system,sans-serif}
th,td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}th{background:var(--head);font-weight:600}
td.n{text-align:right}table.pol{table-layout:fixed}table.pol th:nth-child(1){width:48%}table.pol th:nth-child(2){width:21%}table.pol th:nth-child(3){width:15%}
table.pol th:nth-child(n+4){width:8%}table.pol td:nth-child(3){color:var(--mute)}table.pol td{overflow-wrap:break-word;hyphens:auto}table.pol th{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
@media (max-width:640px){table.pol{font-size:12px}table.pol th:nth-child(1){width:40%}table.pol th:nth-child(2){width:23%}table.pol th:nth-child(3){width:17%}
table.pol th:nth-child(n+4){width:10%}table.pol th,table.pol td{padding:5px 4px}.st{white-space:normal}}
.st{display:inline-block;max-width:100%;font-size:11.5px;line-height:1.3;padding:1px 7px;border-radius:9px;border:1px solid var(--line)}
.st-prohibit{background:#f6dcdc;border-color:#e3b3b3;color:#7a1f1f}.st-restrict{background:#f8e9d2;border-color:#e6c89a;color:#6e4510}
.st-permit{background:#dcefe0;border-color:#b2d6ba;color:#1f5a2e}.st-encourage{background:#d6ecef;border-color:#a9d2d8;color:#145560}
.st-require{background:#e3def3;border-color:#c3b8e3;color:#3d2c7a}.st-delegates{background:#dde6f2;border-color:#b5c7e0;color:#1f3f6b}.st-none{color:var(--mute)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .st:not(.st-none){filter:brightness(.85) saturate(.9)}}
li{margin:4px 0}.bar{font:13px system-ui,sans-serif;display:flex;gap:14px;flex-wrap:wrap;margin:0 0 18px}.bar a{color:var(--acc)}
.tw{overflow-x:auto}
@media print{:root{--bg:#fff;--ink:#000;--head:#eee}.bar{display:none}main{max-width:none;padding:0}body{font-size:11pt}
.pb{break-before:page}tr,h4{break-inside:avoid}h3,h4{break-after:avoid}thead{display:table-header-group}}"""
    body = "\n".join(h)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI Policy Atlas report</title><style>{css}</style></head><body><main>
<div class="bar"><a href="index.html">Back to the atlas</a><a href="#" onclick="print();return false">Print or save as PDF</a><a href="data/AI_Policy_Atlas_report.docx" download>Download Word</a></div>
{body}</main><script>if(window.self!==window.top)document.querySelector(".bar").style.display="none"</script></body></html>"""


def to_docx(B, path):
    from docx import Document
    from docx.enum.section import WD_ORIENT  # noqa: F401
    from docx.enum.text import WD_BREAK
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Pt, RGBColor

    doc = Document()
    st = doc.styles["Normal"]
    st.font.name, st.font.size = "Calibri", Pt(10.5)

    def runs(par, s, size=None):
        for i, part in enumerate(s.split("**")):
            r = par.add_run(part)
            r.bold = bool(i % 2)
            if size:
                r.font.size = Pt(size)

    def table(head, rows, widths=None):
        t = doc.add_table(rows=1, cols=len(head))
        t.style = "Table Grid"
        for c, v in zip(t.rows[0].cells, head):
            c.text = ""
            runs(c.paragraphs[0], f"**{v}**", 9)
        tr = t.rows[0]._tr.get_or_add_trPr()
        e = OxmlElement("w:tblHeader")
        e.set(qn("w:val"), "true")
        tr.append(e)
        for r in rows:
            cells = t.add_row().cells
            for c, v in zip(cells, r):
                c.text = ""
                runs(c.paragraphs[0], str(v), 9)
        if widths:
            from docx.shared import Inches
            for row in t.rows:
                for c, w in zip(row.cells, widths):
                    c.width = Inches(w)
        doc.add_paragraph()

    for t, x in B:
        if t == "h1":
            doc.add_heading(x, 0)
        elif t == "h2":
            doc.add_heading(x, 1)
        elif t == "h3":
            doc.add_heading(x, 2)
        elif t == "p":
            runs(doc.add_paragraph(), x)
        elif t in ("ul", "ol"):
            for i in x:
                runs(doc.add_paragraph(style="List Bullet" if t == "ul" else "List Number"), i)
        elif t == "table":
            table(*x)
        elif t == "pagebreak":
            doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        elif t == "policies":
            layer, pols = x
            for an, n, stages in groups(pols):
                h = doc.add_heading(f"{an} ({n})", 2)
                for sn, qs in stages:
                    p = doc.add_paragraph()
                    r = p.add_run(f"{sn} ({len(qs)})")
                    r.bold, r.font.color.rgb = True, RGBColor(0x5B, 0x65, 0x70)
                    if layer == "inst":
                        table(["Policy", "Stance", "Kind", "Universities", "Levels"], [[q["sentence"], STANCE[q["stance"]], kind(q), q["n_unis"], " ".join(LAB[l] for l in q["levels"])] for q in qs], [3.6, 1.2, 1.0, 0.8, 0.5])
                    else:
                        table(["Policy", "Stance", "Kind", "Universities"], [[q["sentence"], STANCE[q["stance"]], kind(q), q["n_unis"]] for q in qs], [4.1, 1.2, 1.0, 0.8])
    doc.save(path)


def main():
    d = load()
    B = blocks(d)
    (V2 / "site" / "report.html").write_text(to_html(B), encoding="utf-8")
    out = D / "AI_Policy_Atlas_report.docx"
    to_docx(B, out)
    shutil.copy(out, V2 / "exports" / "AI_Policy_Atlas_report.docx")
    print("report.html and AI_Policy_Atlas_report.docx:", len(d["POS"]), "institutional,", len(d["CP"]), "course policies")


if __name__ == "__main__":
    main()
