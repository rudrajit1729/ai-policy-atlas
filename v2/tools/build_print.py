#!/usr/bin/env python3
"""Print-ready PDFs of the role documents (D80), instructors first, without the appendices.

Same content as the Word files (tools/build_roles.py, from site/data/roles.json): about, stance key, and for each level the
stance x stage matrix (landscape page) and the policies by stance, stage and group, with variants. Instead of the appendix
lookup table, each policy ID links to the website, where every statement and source is listed.
Writes v2/exports/print/1_Instructor_AI_Policies.pdf and 2_Student_AI_Policies.pdf (via headless Chrome).
"""
import html
import json
import subprocess
from datetime import date
from pathlib import Path

V2 = Path(__file__).resolve().parents[1]
D = V2 / "site" / "data"
OUT = V2 / "exports" / "print"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SHORT = {"before-course": "Before the course", "course-start": "At the start", "during-work": "During the course", "during-assessment": "During assessment",
         "when-misuse": "When misuse is suspected", "over-time": "Over time", "background": "Background"}
e = html.escape
pl = lambda n, a, b: f"{n} {a if n == 1 else b}"
KO = ["rule", "recommendation", "option", "fact or warning"]


YOU = {"instructor": "you, the instructor", "student": "you, the student", "staff": "you, as staff or an administrator", "all": "everyone in the university"}
BT = {"asked": "must", "choice": "may", "fact": "fact"}
WHOSE = {"instructor": "instructors\u2019", "student": "students\u2019", "staff": "staff\u2019s", "all": "everyone\u2019s"}
WHO = {"instructor": "instructors", "student": "students", "staff": "staff and administrators", "all": "people in the university"}


def btag(gr, ctx):
    """D83: one tag per theme in the bird's-eye view: must/should (asked of you), may (left to you); counts only when a theme mixes them."""
    t = gr.get("tags", {})
    if ctx:
        return ""
    mixed = len(t) > 1
    return "".join(f"<span class='kb kb-{BT[k]}'>{k}{' ' + str(n) if mixed else ''}</span>" for k, n in t.items())


def kb(data, k, n=None):
    w = data["kinds"].get(k)
    return f"<span class='kb kb-{w[2]}'>{'' if n is None else str(n) + ' '}{w[0]}</span>" if w else e(k)


def page(data, rk):
    R = data["roles"][rk]
    who = R["label"].lower()
    url = data["site"] + "#" + R["slug"]
    M = json.loads((D / "meta.json").read_text())
    parts = R["parts"]
    h = [f"<h1>AI policies for {e(who)}</h1><p class='sub'>US universities and their computer science courses. AI Policy Atlas, {date.fromisoformat(data['generated']):%B %-d, %Y}. "
         f"Website: <a href='{url}'>{e(url)}</a>. Sources accessed and links checked: {date.fromisoformat(data['generated']):%B %-d, %Y}.</p>",
         f"<p class='aud'><b>Who this is for.</b> {e(R['audience'].removeprefix('Who this is for. '))}</p>",
         "<h2>About this document</h2>",
         f"<p>This document lists every policy that US university documents and CS course syllabi address to {e(who)}, drawn from {M['n_documents']} university-wide, school and department documents at {M['n_universities']} universities and from AI passages in CS course syllabi.</p>",
         f"<p>A policy is one thing asked of one group. Statements that ask {e(who)} to do the same thing are merged into one policy, whatever their wording, and each policy is written as a directive to the reader. Within each level, policies are grouped by stance (what the policy does about AI use), then follow the course from before it starts to after it ends, then are grouped by what they ask. The groups come from a thematic analysis by three independent coders. Policies that make the same point appear as one entry led by the most widespread policy, with the others listed as variants and how they differ.</p>",
         f"<p>Each entry is tagged <span class='kb kb-must'>Expected</span> ({e(who)} are expected to do it: the policy says they should or must), <span class='kb kb-may'>Choice</span> ({e(who)} may do it, or not: the choice is theirs) or <span class='kb kb-fact'>Fact</span> (a fact or warning that asks nothing of anyone). It also gives the number of universities and of statements behind it (“13 (15)” means 15 statements from 13 different universities), the levels where it appears (U university-wide, S school or college, C computing department), and its ID. <b>Sources:</b> every ID links to the website, which lists each statement behind the policy in the institution’s own words, with a link to the source.</p>",
         f"<p>Policies addressed to everyone in a university also apply to {e(who)}; the website lists them on its Other roles page.</p>",
         "<table class='key'><tr><th>Stance</th><th>What the policy does about AI use</th>" + "".join(f"<th>{e(p['title'])}</th>" for p in parts) + "</tr>"]
    for sk, lab in data["stance_labels"].items():
        ns = [next((x["n"] for x in p["stances"] if x["id"] == sk), 0) for p in parts]
        if any(ns):
            h.append(f"<tr><td>{e(lab)}</td><td>{e(data['stance_defs'][sk])}</td>" + "".join(f"<td class=n>{n}</td>" for n in ns) + "</tr>")
    h.append("<tr class='tot'><td>All</td><td></td>" + "".join(f"<td class=n>{p['n']}</td>" for p in parts) + "</tr></table>")
    stg = [g for g, _ in data["stages"]]
    for p in parts:
        lev = p["title"]
        link = f"{url}/{p['layer']}"
        mx = max([c["n"] for r in p["matrix"].values() for c in r.values()] or [1])
        h.append(f"<section class='wide'><h2>{e(lev)}: policies for {e(who)}</h2><p>{e(p['intro'])}</p>")
        h.append(f"<h3>Bird\u2019s-eye view of policies for {e(who)}: {e(lev)}</h3>")
        h.append(f"<p class='youline'>Each theme says who it addresses. <span class='kb kb-must'>Expected</span> {WHO[rk]} are expected to do it: the policy says they should or must. <span class='kb kb-may'>Choice</span> {WHO[rk]} may do it, or not: the choice is theirs. The number after each theme is how many policies it holds.</p>")
        # wider columns where the policies are, so theme lines wrap less; empty columns stay (an empty column is a finding)
        wt = {g: 0.45 if not p["stage_table"][g] else 1 + 1.6 * (p["stage_table"][g] / max(p["stage_table"].values())) ** 0.6 for g in stg}
        avail = 10.4 - 0.72 - 0.32
        cols = "<colgroup><col style='width:0.72in'>" + "".join(f"<col style='width:{avail * wt[g] / sum(wt.values()):.2f}in'>" for g in stg) + "<col style='width:0.32in'></colgroup>"
        h.append(f"<table class='mx'>{cols}<tr><th>Stance \u2193 When \u2192</th>" + "".join(f"<th>{SHORT[g]}</th>" for g in stg) + "<th>All</th></tr>")
        for x in [x for x in p["stances"] if x["id"] != "context"]:
            row = f"<tr><th>{e(x['label'])}</th>"
            for g in stg:
                c = p["matrix"][x["id"]][g]
                if not c["n"]:
                    row += "<td></td>"
                    continue
                sg = next(z for z in x["stages"] if z["id"] == g)
                a = 0.04 + 0.26 * (c["n"] / mx) ** 0.5
                row += (f"<td style='background:rgba(31,90,115,{a:.2f})'><b class='cn'>{pl(c['n'], 'policy', 'policies')}</b>"
                        + "".join(f"<div class='th{' sub' if ind else ''}'>{'' if t == 'fact' else f'<span class={chr(39)}kb kb-{BT[t]}{chr(39)}>{data[chr(107)+chr(105)+chr(110)+chr(100)+chr(115)][t][0]}</span>'}{e(lab.rstrip('.'))}{'' if ind else f' ({n})'}</div>" for t, lab, n, ind in c["lines"]) + "</td>")
            h.append(row + f"<td class=n><b>{x['n']}</b></td></tr>")
        h.append("<tr class='tot'><th>All stances</th>" + "".join(f"<td class=n>{p['stage_table'][g] or '–'}</td>" for g in stg) + f"<td class=n>{p['n_table']}</td></tr></table>")
        if p.get("context_note"):
            h.append(f"<p class='cap'>{e(p['context_note'])}</p>")
        h.append(f"<p class='cap'>{e(lev)}. Rows are stances; columns are when in the course a policy applies. Each cell lists every theme of policies at that point, tagged Expected or Choice, with the number of policies in it. Darker cells hold more policies. Online: <a href='{link}'>{e(link)}</a></p>")
        if p.get("gaps"):
            h.append(f"<p class='gaps'>{e(p['gaps'])}</p>")
        h.append("</section>")
        for x in p["stances"]:
            h.append(f"<h3>{e(lev)} · {e(x['label'])}: {pl(x['n'], 'policy', 'policies')}, {pl(x['n_unis'], 'university', 'universities')}</h3>")
            h.append(f"<p><i class='def'>{e(x['def'])}</i> {e(x['prose'])}</p>")
            for g in x["stages"]:
                h.append(f"<h4>{e(g['label'])} ({pl(len(g['policies']), 'policy', 'policies')})</h4><table class='pol'><tr><th>Policy</th><th>Tag</th><th>Universities (statements) · levels</th><th>ID</th></tr>")
                for gr in g["groups"]:
                    if gr["label"]:
                        h.append(f"<tr class='grp'><td colspan=4>{e(gr['label'].rstrip('.'))} ({pl(gr['n'], 'policy', 'policies')})</td></tr>")
                    for it in gr["items"]:
                        var = "".join(f"<div class='var'><b>Variant:</b> {e(v['differs'])} ({kb(data, v['kind']) + ', ' if v.get('kind') and v['kind'] != it['kind'] else ''}{pl(v['n_unis'], 'university', 'universities')}, <a href='{link}/{e(v['id'])}'>{e(v['id'])}</a>)</div>" for v in it["variants"])
                        gen = " <span class='gen'>general rule</span>" if it["general"] else ""
                        h.append(f"<tr><td>{e(it['directive'])}{gen}{var}</td><td class='k'>{' '.join(kb(data, k) for k in it['kind'].split(', '))}</td><td class='k'>{it['n_unis']} ({it['n']})" + (f" · {' '.join(it['levels'])}" if it["levels"] else "")
                                 + f"</td><td class='k'><a href='{link}/{e(it['ids'][0])}'>{e(it['ids'][0])}</a></td></tr>")
                h.append("</table>")
    h.append(f"<h2>Sources</h2><p>The lookup table is online. For any policy ID, open <a href='{url}'>{e(url)}</a>, choose the level, and open the policy to see its sources: every statement behind it in the institution\u2019s own words, with a link to the original document.</p>" + (f"<p>{e(data['accessed'])}</p>" if data.get("accessed") else ""))
    css = """@page{size:letter;margin:0.6in 0.6in 0.7in}@page wide{size:letter landscape;margin:0.35in 0.3in}
body{font:10pt/1.45 Georgia,'Times New Roman',serif;color:#1c2126}h1{font-size:22pt;margin:0 0 4pt}h2{font-size:15pt;margin:18pt 0 6pt;border-bottom:1.5pt solid #1f5a73;padding-bottom:2pt}
h3{font:600 11.5pt -apple-system,Helvetica,Arial,sans-serif;margin:16pt 0 4pt;color:#1c2126;break-after:avoid}h4{font:600 9.5pt -apple-system,Helvetica,Arial,sans-serif;color:#1f5a73;margin:10pt 0 3pt;break-after:avoid}
.sub{color:#5d6670;margin:0 0 10pt}a{color:#1f5a73}table{border-collapse:collapse;width:100%;font:8.5pt/1.35 -apple-system,Helvetica,Arial,sans-serif;margin:4pt 0 8pt}
th,td{border:0.5pt solid #cfc9bd;padding:3pt 5pt;vertical-align:top;text-align:left}th{background:#efece5}td.n{text-align:right}tr.tot td,tr.tot th{font-weight:600;background:#f6f4ef}
.wide{page:wide}.wide h2{margin-top:0}table.mx{table-layout:fixed;font-size:7.5pt}table.mx th,table.mx td{padding:2pt 2.5pt}table.mx th:first-child{width:0.78in}table.mx th:last-child{width:0.32in}
table.mx td .th{font-size:7.2pt;line-height:1.25;margin:0 0 2pt}table.mx td .th .kb{font-size:6pt;margin-right:3pt}table.mx .cn{display:block;font-size:7.5pt;margin-bottom:2pt}
.th.sub{margin-left:7pt;font-style:italic}.youline{font-size:8.5pt;margin:2pt 0 5pt}
table.pol td:first-child{width:64%}table.pol td.k{white-space:nowrap}td.k{color:#5d6670;font-size:8pt}tr.grp td{background:#f3f1ec;font-weight:600;color:#1f5a73}tr{break-inside:avoid}
.var{font-size:7.5pt;color:#5d6670;margin:2pt 0 0 8pt}.gen{font-size:7pt;color:#8a6d3b;border:0.5pt solid #e3d3b0;border-radius:6pt;padding:0 4pt}
.kb{display:inline-block;font:600 6.8pt/1.4 -apple-system,Helvetica,Arial,sans-serif;padding:0 3pt;border-radius:2.5pt;margin:0 2pt 1pt 0;white-space:nowrap;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.kb-must{background:#1f3b4d;color:#fff}.kb-should{background:#cfe0e8;color:#1f3b4d}.kb-may{background:#fff;color:#2f6b3a;border:0.6pt solid #6aa476}.kb-fact{background:#ecebe6;color:#5d6670}
table.mx .kbs{margin:1pt 0 2pt}.aud{border-left:2.5pt solid #1f5a73;padding:4pt 8pt;background:#f2f6f8;-webkit-print-color-adjust:exact;print-color-adjust:exact}.gaps{font-size:9pt;margin-top:4pt}
.cap{font-size:8pt;color:#5d6670;font-style:italic}.def{color:#5d6670}table.key td:nth-child(2){width:50%}"""
    return f"<!doctype html><html><head><meta charset='utf-8'><title>AI policies for {e(who)}</title><style>{css}</style></head><body>{''.join(h)}</body></html>"


def main():
    data = json.loads((D / "roles.json").read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    for i, (rk, name) in enumerate([("instructor", "Instructor"), ("student", "Student")], 1):
        f = OUT / f"{i}_{name}_AI_Policies.html"
        f.write_text(page(data, rk), encoding="utf-8")
        pdf = OUT / f"{i}_{name}_AI_Policies.pdf"
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}", f.as_uri()], check=True, capture_output=True, timeout=120)
        print(pdf.name, pdf.stat().st_size)


if __name__ == "__main__":
    main()
