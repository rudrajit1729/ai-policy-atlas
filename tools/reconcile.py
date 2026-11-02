#!/usr/bin/env python3
"""Reconcile verified statements into consolidated guidelines (Amershi-style).

Each statement is assigned to exactly one guideline in two steps:
  1. a transparent rule on its primary code + wording (RULES below), then
  2. the analyst's manual overrides (OVERRIDES), recorded after reviewing every cluster.
Labels are analyst-written names for clusters; the evidence is always the verbatim statements.

Writes corpus/synthesis.json (base + guidelines + patterns) and corpus/reconcile_review.md.
"""
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# id, label, theme, phase, actor, exemplar statement id, optional analyst note
GUIDELINES = [
    ("G01", "Prohibit AI on graded work by default", "stance", "course-start", "student", "stanford-cs106b-honor-code-e1"),
    ("G02", "Permit or encourage AI by default", "stance", "course-start", "student", "cmu-15112-e2"),
    ("G03", "Discourage AI without forbidding it", "stance", "course-start", "student", "princeton-cos226-e2"),
    ("G04", "Let each instructor or assignment set the rule", "stance", "before-course", "instructor", "oregonstate-ctl-ai-teaching-guidance-e2"),
    ("G05", "Name explicit tiers or levels of AI use", "stance", "before-course", "department", "pomona-cs-ai-policy-tier-system-e1"),
    ("G06", "Define the fallback rule when a syllabus is silent", "stance", "course-start", "student", "oregonstate-eecs-ai-guidance-e1"),
    ("G07", "Cover AI built into editors, IDEs, and agents", "stance", "before-course", "student", "uw-allen-ai-support-and-growth-e3"),
    ("G08", "Stage AI permission as skills develop", "stance", "before-course", "instructor", "neu-cs3100-e4"),
    ("G09", "Require an AI statement in every syllabus", "communicate", "before-course", "department", "oregonstate-eecs-ai-guidance-e6"),
    ("G10", "When unsure, students should ask before using AI", "communicate", "course-start", "student", "gatech-cs1301-e3"),
    ("G11", "Each course's policy governs only that course", "communicate", "course-start", "student", "uiuc-cs124-syllabus-e7"),
    ("G12", "Allow AI as a tutor for understanding concepts", "permitted", "during-work", "student", "mit-6100a-e2"),
    ("G13", "Allow AI to explain errors and help debug", "permitted", "during-work", "student", "hmc-cs70-e5"),
    ("G14", "Allow AI for practice, study aids, and review", "permitted", "during-work", "student", "gatech-cs1331-chambers-e4"),
    ("G15", "Allow AI for brainstorming and exploring approaches", "permitted", "during-work", "student", "gatech-cs1301-e1"),
    ("G16", "Allow AI-generated code under stated conditions", "permitted", "during-work", "student", "uwaterloo-cs349-e2"),
    ("G17", "Provide a sanctioned, course-specific AI tool", "permitted", "during-work", "instructor", "harvard-cs50-e1"),
    ("G18", "Treat AI for prose separately from AI for code", "permitted", "during-work", "student", "brown-csci0190-e6"),
    ("G19", "Do not have AI produce the work you submit", "prohibited", "during-work", "student", "utoronto-csc108-e1"),
    ("G20", "Do not feed assignment specs or your code to AI", "prohibited", "during-work", "student", "neu-cs2100-e4"),
    ("G21", "Do not use AI to debug or check graded work", "prohibited", "during-work", "student", "penn-cis1200-e2"),
    ("G22", "No AI on exams, quizzes, or in-class assessments", "prohibited", "during-assessment", "student", "princeton-cos226-e1"),
    ("G23", "Keep AI conversations apart from the work itself", "prohibited", "during-work", "student", "gatech-cs1301-e6"),
    ("G24", "Disclose AI use with each submission", "disclosure", "during-work", "student", "oregonstate-eecs-ai-guidance-e4"),
    ("G25", "Cite the tool, the prompt, and the output", "disclosure", "during-work", "student", "middlebury-csci201-e3"),
    ("G26", "Keep and submit transcripts, logs, or reflections", "disclosure", "during-work", "student", "stanford-cs221-e4"),
    ("G27", "Mark AI-derived code where it is used", "disclosure", "during-work", "student", "uwaterloo-cs349-e3"),
    ("G28", "Make disclosure safe and nondisclosure the violation", "disclosure", "when-misuse", "instructor", "princeton-cos226-e8"),
    ("G29", "Students own everything they submit", "accountability", "during-work", "student", "jhu-en601220-e7"),
    ("G30", "Students must be able to explain every line", "accountability", "during-work", "student", "dartmouth-cs10-e6"),
    ("G31", "Verify AI output; it is often wrong", "accountability", "during-work", "student", "tufts-cs15-e3"),
    ("G32", "Students stay the primary problem-solver", "accountability", "during-work", "student", "vt-cs3214-e4"),
    ("G33", "Shift weight to proctored, unassisted assessment", "assessment", "before-course", "instructor", "vt-cs3214-e3"),
    ("G34", "Check understanding through code reviews, interviews, or oral exams", "assessment", "during-assessment", "instructor", "princeton-cos226-e3"),
    ("G35", "Redesign assignments and grading around AI", "assessment", "before-course", "instructor", "uiuc-cs124-syllabus-e4"),
    ("G36", "Treat unauthorized AI use as academic misconduct", "enforcement", "when-misuse", "student", "gatech-cs1301-e2"),
    ("G37", "State concrete penalties in advance", "enforcement", "when-misuse", "instructor", "ucalgary-cpsc219-e7"),
    ("G38", "Offer a self-report window or amnesty", "enforcement", "when-misuse", "student", "harvard-cs50-e5"),
    ("G39", "Do not rely on AI detectors", "enforcement", "when-misuse", "instructor", "oregonstate-eecs-ai-guidance-e7"),
    ("G40", "Use similarity checks and process evidence instead", "enforcement", "when-misuse", "instructor", "stanford-cs221-e7"),
    ("G41", "Explain that AI shortcuts the practice that builds skill", "rationale", "course-start", "instructor", "macalester-comp123-e2"),
    ("G42", "Protect novices; fundamentals come first", "rationale", "before-course", "instructor", "penn-cis1100-e4"),
    ("G43", "Warn that AI gives a false sense of mastery", "rationale", "course-start", "student", "utoronto-csc108-e2"),
    ("G44", "Teach effective AI use as a professional skill", "rationale", "before-course", "instructor", "uiuc-cs124-ai-e2"),
    ("G45", "Treat AI like a human collaborator under existing rules", "rationale", "course-start", "student", "stanford-cs106b-honor-code-e5"),
    ("G46", "Humans, not AI, assign grades", "faculty", "during-assessment", "instructor", "oregonstate-eecs-ai-guidance-e5"),
    ("G47", "Disclose instructor AI use to students", "faculty", "course-start", "instructor", "ualberta-cmput301-e6"),
    ("G48", "Review and disclose AI-made course materials", "faculty", "before-course", "instructor", "neu-cs3100-e6"),
    ("G49", "Do not upload course materials to AI tools", "responsible", "during-work", "student", "uw-cse312-ai-policy-e5"),
    ("G50", "Protect personal data and prefer vetted tools", "responsible", "during-work", "student", "unc-comp110-e3"),
    ("G51", "Do not require paid tools; keep access equitable", "responsible", "before-course", "instructor", "cornell-gai-education-report-e7"),
    ("G52", "Consider licensing and copyright of AI output", "responsible", "during-work", "student", "uwaterloo-cs136-e4"),
    ("G53", "Name bias, harms, and environmental costs", "responsible", "course-start", "student", "unc-comp110-e2"),
    ("G54", "Revisit the policy regularly", "governance", "over-time", "instructor", "oregonstate-ctl-ai-teaching-guidance-e8"),
    ("G55", "Gather evidence on how AI affects learning", "governance", "over-time", "instructor", "uiuc-cs124-ai-e7"),
    ("G56", "Set an institution-wide framework for responsible AI use", "governance", "before-course", "department", "binghamton-policy-312-genai-e1"),
    ("G57", "Talk with the student before escalating suspected misuse", "enforcement", "when-misuse", "instructor", "usd-ai-faculty-e7"),
]

def has(t, pat):
    return re.search(pat, t, re.I) is not None

def rule(e):
    """Default guideline for a statement from its primary code and wording."""
    t, codes = e["text"], e.get("topics") or ["none"]
    c = codes[0]
    stance = e["doc"]["stance"]
    if c == "default-stance":
        if has(t, r"unless|assume|when no policy|not included in the authorized"):
            return "G06"
        if has(t, r"discourage|not recommended|strongly recommend"):
            return "G03"
        if has(t, r"welcome|encourag|allowed|permitted and|you may use|optional|embrace|assumed you will|choice|allowed as long|futile|Generally Permitted"):
            return "G02"
        return "G01"
    if c == "prohibited-uses":
        if has(t, r"exam|quiz"):
            return "G22"
        if has(t, r"debug|check|proofread|fix a bug|error message|feedback|reformat"):
            return "G21"
        if has(t, r"instructions|codebase|sharing assignment|translate|prompt|paste|upload|disguis"):
            return "G20"
        if has(t, r"code|copilot|solution|summary"):
            return "G19"
        return "G01"
    if c == "code-generation":
        if has(t, r"IDE|plugin|extension|disable|editor|built into|Cursor|Windsurf|in the IDE|act autonomously"):
            return "G07"
        if has(t, r"small|snippet|ten lines|15%|if cited|no restrictions|allowed to use|for code completion|syntax|may be used"):
            return "G16"
        return "G19"
    if c == "permitted-uses":
        if has(t, r"error|debug|syntax|failed tests|compil"):
            return "G13"
        if has(t, r"practice|study|review|preview|summari|testing your knowledge|examples"):
            return "G14"
        if has(t, r"brainstorm|ideas|explore|edge cases|alternative approaches"):
            return "G15"
        if has(t, r"code|projects|construct|solutions"):
            return "G16"
        return "G12"
    if c == "learning-rationale":
        if has(t, r"novice|beginning|introductory|fundamental|before relying|early|new to programming|basic|calculator|not yet|build your skills first"):
            return "G42"
        if has(t, r"exam|false sense|prepared|quiz|perform|negates"):
            return "G43"
        return "G41"
    if c == "disclosure-citation":
        if has(t, r"penalty|violation|cheating|lose points|regardless|receive credit|grade penalty|extension points"):
            return "G28"
        if has(t, r"transcript|log|journal|appendix|notes|exchange|reflection|drafts"):
            return "G26"
        if has(t, r"prompt|model|corporation|name/url|response"):
            return "G25"
        if has(t, r"comment|README|portions|where these|top of|acknowledgments\.txt|15%"):
            return "G27"
        return "G24"
    if c == "integrity-sanctions":
        if has(t, r"72 hours|withdraw|regret|approach you"):
            return "G38"
        if has(t, r"zero|\b0\b|grade|fail|letter|no credit|-100|2\.5|suspension|E’|Offence|offense results"):
            return "G37"
        return "G36"
    if c == "accountability-understanding":
        if has(t, r"interview|meet with"):
            return "G34"
        if has(t, r"explain|discuss|defend|demonstrate"):
            return "G30"
        if has(t, r"verif|wrong|reliable|correct|evaluate|mistakes|validat|accuracy|precedence|critical"):
            return "G31"
        if has(t, r"primary|replace your thinking|active role|think for you|assistant|skeleton|responsible for your own learning"):
            return "G32"
        return "G29"
    if c == "exams-in-person":
        return "G22"
    if c == "detection-tools":
        return "G39" if has(t, r"not reliable|promise not|not currently|not reported") else "G40"
    if c == "ai-literacy-career":
        return "G44"
    if c == "course-provided-tools":
        if has(t, r"Helix|IDEs that|configured"):
            return "G07"
        if has(t, r"optional|prefer to talk|free access"):
            return "G51"
        return "G17"
    if c == "use-categories-levels":
        return "G05"
    if c == "collaboration-analogy":
        return "G45"
    if c == "instructor-discretion":
        if has(t, r"unsure|ask|consult|contact"):
            return "G10"
        if has(t, r"only applies|another course"):
            return "G11"
        return "G04"
    if c == "assessment-design":
        if has(t, r"code reviews|oral"):
            return "G34"
        if has(t, r"individual knowledge|without access|unassisted|in class"):
            return "G33"
        return "G35"
    if c == "syllabus-communication":
        if has(t, r"unsure|questions|clarification|not sure"):
            return "G10"
        return "G09"
    if c == "privacy-data":
        return "G49" if has(t, r"course materials|course-specific") else "G50"
    if c == "faculty-grading-feedback":
        if has(t, r"Gemini|opt out"):
            return "G47"
        if has(t, r"baseline"):
            return "G35"
        return "G46"
    if c == "writing-assistance":
        return "G18"
    if c == "equity-access":
        return "G51"
    if c == "intellectual-property":
        return "G49" if has(t, r"course materials|prompt for an AI|submitting them") else "G52"
    if c == "faculty-course-materials":
        return "G48"
    if c == "policy-evolution":
        return "G55" if has(t, r"monitor|data") else "G54"
    if c == "ethics-bias-environment":
        return "G53"
    if c in ("instructor-staff-use",):
        return "G47"
    if c == "amnesty-regret":
        return "G38"
    return "G36"

# Manual overrides recorded after reviewing every cluster (statement id -> guideline id).
OVERRIDES = {k: v for k, v in json.loads((ROOT / "corpus" / "reconcile_overrides.json").read_text()).items() if not k.startswith("_")} if (ROOT / "corpus" / "reconcile_overrides.json").exists() else {}


def main():
    base = json.loads((ROOT / "corpus" / "synthesis_base.json").read_text())
    corpus = json.loads((ROOT / "corpus" / "corpus.json").read_text())
    ex = {}
    for d in corpus["documents"]:
        for e in d["excerpts"]:
            e["doc"] = d
            ex[e["id"]] = e
    members = defaultdict(list)
    how = {}
    for eid, e in ex.items():
        g = OVERRIDES.get(eid)
        if g:
            how[eid] = "override"
        else:
            g, how[eid] = rule(e), "rule"
        members[g].append(eid)

    gl = []
    for gid, label, theme, phase, actor, exemplar in GUIDELINES:
        m = sorted(members.get(gid, []), key=lambda i: (ex[i]["doc"]["university"], i))
        if exemplar not in m and m:
            print(f"WARN {gid}: exemplar {exemplar} not in cluster")
        gl.append({"id": gid, "label": label, "theme": theme, "phase": phase, "actor": actor,
                   "exemplar": exemplar, "members": m})
    unknown = set(members) - {g[0] for g in GUIDELINES}
    if unknown:
        raise SystemExit(f"unknown guideline ids: {unknown}")

    patterns = json.loads((ROOT / "corpus" / "patterns.json").read_text()) if (ROOT / "corpus" / "patterns.json").exists() else []
    method = json.loads((ROOT / "corpus" / "method.json").read_text()) if (ROOT / "corpus" / "method.json").exists() else {}
    out = {**base, "guidelines": gl, "patterns": patterns, "method": method}
    jev_path = ROOT / "corpus" / "jev_scores.json"
    if jev_path.exists():
        jev = json.loads(jev_path.read_text())
        member_of = {i: g["id"] for g in gl for i in g["members"]}
        st = {}
        for sid, v in jev["statements"].items():
            if sid in member_of:  # p of the analyst's current assignment (overrides may have changed since scoring)
                st[sid] = [v["top"], v["top_p"], v["probs"].get(member_of[sid], 0.0)]
        out["jev"] = {"summary": jev["summary"], "statements": st, "guidelines": jev["guidelines"]}
    (ROOT / "corpus" / "synthesis.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))

    lines = ["# Reconciliation review", ""]
    for g in gl:
        unis = {ex[i]["doc"]["university"] for i in g["members"]}
        lines.append(f"## {g['id']} {g['label']} — {len(g['members'])} statements, {len(unis)} institutions")
        for i in g["members"]:
            lines.append(f"- `{i}` [{how[i]}] {ex[i]['text']}")
        lines.append("")
    (ROOT / "corpus" / "reconcile_review.md").write_text("\n".join(lines))
    n_over = sum(1 for v in how.values() if v == "override")
    print(f"{len(ex)} statements -> {len(gl)} guidelines ({n_over} manual overrides)")


if __name__ == "__main__":
    main()
