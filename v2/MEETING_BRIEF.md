# Advisor meeting brief (2026-11-02)

## Before the meeting (10 minutes)
1. Double-click **Open AI Policy Atlas.command** in the project folder. The site opens at http://localhost:8792. Keep that Terminal window open.
2. Have **v2/exports/atlas_v2.xlsx** (institutional) and **v2/exports/course_layer.xlsx** (courses) ready in case they want raw rows.
3. Pick 2–3 policies to read aloud from the **By role** page (Student view works well).

## Suggested order to show the site
1. **Overview.** Status, then the pipeline: 24,536 statements from 774 documents at 342 universities → 23,948 about AI → 1,062 merged items → **675 policies** (207 rules, 404 recommendations, 64 facts and warnings). The other 387 are templates, descriptions and background, kept on their own tab.
2. **Matrix.** Who it addresses × when it applies. Point to the thin cells (below).
3. **By role.** "If I'm a student, what are my AI policies?" Sorted into Do, Don't, May, Know.
4. **CS course policies.** 2,238 statements from 471 syllabus passages at 135 universities → **229 course policies** (165 rules, 35 recommendations, 29 facts).
5. **Method and reliability.** Coder agreement and the decision log (69 decisions).
6. Each page has a link to its CSV, so advisors can edit and send rows back.

## What it already shows (talking points)
- **Little is binding at the top.** About a fifth of what universities publish about AI is a rule (21%). Computing units are the exception: 45% rules.
- **Most universities hand the decision to instructors.** 79% of university-wide documents delegate.
- **CS courses are stricter than their universities.** Where the university delegates, 37% of CS course passages ban AI outright.
- **Rules loosen across the degree.** AI is banned in 48% of CS1 passages, 44% of CS2, 34% of algorithms and 11% of software engineering.
- **Thin cells are findings.**
  - Assessment is the least-addressed stage: 16 of 675 institutional policies (2.4%).
  - Staff and administrators almost never appear in course policies: 2 of 229.
  - Student policies are mostly about doing the work (71% institutional, 89% course). Almost nothing tells students what to do before a course starts.
- **School and computing units add little that is new.** Only 10 of 675 policies appear nowhere in a university-wide document.
- **Course-only practices exist:** asking AI for explanations instead of code, the warning that AI homework hurts exam readiness, AI for test cases, sharing AI sessions.
- **Reliability.** Coder agreement α = 0.82–0.89 on actor, topic, force and stage. Course coding α = 0.868. Stance is weaker (0.72), so stance results are tentative.

## CS vs. university and school (one-slide summary)
| | University-wide | School or college | Computing unit | CS course syllabi |
|---|---|---|---|---|
| Share of statements that are rules | 21% | 13% | 45% | 72% of course policies are rules |
| Main addressee | instructors 39% | instructors 50% | instructors 46% | students 80% |
| Staff and administrators | 15% | 1% | 3% | 1% |
| About doing the work | 37% | 38% | 36% | 72% |
| Before the course starts | 24% | 19% | 23% | 1% |
| About assessment | 2% | 4% | 3% | 5% |

- Universities and schools set up the system and advise. CS departments and syllabi set rules for students on the work itself.
- Documents that take a position (not delegate): 21% university-wide vs. 74% of computing-unit documents.
- CS is stricter: 37% of CS syllabi ban AI where the university delegates; bans fall from 48% (CS1) to 11% (software engineering).
- CS talks about code: line limits on AI code, coding agents, AI for tests and documentation, explanations instead of code.
- CS leaves out governance, faculty support, AI literacy, tool approval and research (14 common institutional topics never appear in syllabi).

## Decisions to ask the advisors
1. **Is 675 + 229 the right size for the synthesized policy set?** All stay as policies; a core view could show those at 5+ universities.
2. **How to run the human review on a sample.** Proposal in the report (section 5): every policy merged from 5+ versions, plus about 10% of the rest drawn evenly across groups and stages.

Conflicting policies are handled by direction (Do / Don't / May / Know on the By role page), so they are no longer a separate question.

## The shareable report
- On the site: the **Report** tab (second tab). It has a printable version and a Word download.
- Files: `v2/site/report.html` and `v2/exports/AI_Policy_Atlas_report.docx`.
- It holds status, pipeline, numbers, findings, CS vs. university, the two decisions, and all 675 + 229 policies grouped by who and when. No method section.

## Still to do
| item | status |
|---|---|
| Human review of 675 institutional + 229 course policy sentences | not started; needs a reviewer plan |
| Compare institutional and course policies side by side (D43) | partly done at the topic level; not yet at the policy level |
| Private GitHub repo | ready to create; waiting on your OK |
| Public site | later, only with your approval |
| Background workers | need `claude auth login` again before the next large run |

## Where things are
- Project folder: `~/Documents/Current-Research/AI in education policy guidelines`
- Site: `v2/site` (CSVs in `v2/site/data/csv`)
- Status and findings: `v2/STATUS_AND_FINDINGS.md`
- Definitions: `v2/DEFINITIONS.md`
- Decision log: `v2/METHODS_DECISIONS.md`
