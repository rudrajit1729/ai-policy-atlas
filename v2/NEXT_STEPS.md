# AI Policy Atlas: where it stands and what comes next (2026-11-18)

## Where it stands
First pass done: every source collected, coded and organized so the team can review it.
- **Corpus:** 774 university-wide, school and department documents from 342 US universities; 24,536 statements coded, 23,948 about AI. CS syllabi: 471 AI passages at 135 universities, 2,238 statements.
- **Policy set:** 675 institutional and 229 CS course policies (rules, recommendations, options, facts and warnings), each traceable to the statements and sources behind it.
- **By role:** students, instructors, staff and administrators, everyone. Each role is organized by stance, then course stage, then theme, with near-duplicates shown as one lead policy with variants. General academic-integrity rules that AI documents restate without being about AI (45) are left out of the role views.
- **Reliability so far:** coder agreement α 0.82 to 0.89 on actor, topic, force and stage; course coding α 0.868; theme grouping by three independent coders, adjusted Rand 0.74.
- **Website:** https://rudrajit1729.github.io/ai-policy-atlas/ (repository: https://github.com/rudrajit1729/ai-policy-atlas).
- **Printouts:** `v2/exports/print/1_Instructor_AI_Policies.pdf`, `2_Student_AI_Policies.pdf` (sources on the website). Word versions with source tables in the appendices: `v2/exports/*_AI_Policies.docx`.

## Proposed first paper: instructors
Instructors are the right first paper: 249 institutional policies is a manageable set, and instructors are the ones who write the course AI policies.
1. **What institutions ask of instructors** (249 policies, 303 universities): by stance and course stage. Headline: most are cross-cutting duties, not stances (132 of 249); 205 ask instructors to do something (must/should), 38 leave the choice to them (may) and 6 are context; policies cluster before the course (96) and at its start (55); 252 universities leave the AI decision to instructors.
2. **What instructors then ask of students in CS syllabi** (173 course policies for students): 133 of 173 ask students to do something (must/should) and 40 leave the choice to them (may); more prohibitive (Prohibit 45, Require 39).
3. **What syllabi ask of instructors themselves:** almost nothing (13 policies at 19 universities). Instructors write the syllabus, so they rarely bind themselves; obligations on instructors come from the institution.
4. **The gap between the two layers:** what institutions delegate to instructors versus what instructors pass on to students, stage by stage (e.g. assessment is thin at both levels: Allowed with conditions and Encourage fill the during-the-course column and are almost empty during assessment, so instructors and students are left to work out what allowed or encouraged use means when work is graded).

## Changes after meeting Peggy (2026-11-18)
- Each document now opens with who it is for and who writes the policies.
- Tags: must/should (rules and recommendations together: the reader is asked to do it) versus may (an option: the choice is left to the reader). Options are read from each policy's directive ("you may", "you need not"); a "may ... only" or "may ... but must" stays must/should.
- Facts and warnings are pulled out of the stance rows into their own Context row, since they ask nothing of the reader.
- The matrix is called the bird's-eye view; columns are when in the course a policy applies ("While students work" is now "During the course"); each cell lists every theme, tagged must/should or may, and says who "you" is.
- "Duties and facts" is now "Cross-cutting duties": things the reader must or should do whatever the stance.
- Empty cells are reported as findings under each matrix.
- Date accessed: sources collected in October 2026; every source link checked on 2026-11-18 (v2/linkcheck/).

## What I would change in the next two weeks (no input needed from you unless noted)
1. **Human review sample** of the instructor policies first: every lead with variants (check the variant notes) and a stratified 10% of the rest. Needs: one or two coauthors to check against sources.
2. **Instructor CS course layer is sparse** (13 policies). Report it as a finding rather than pad it; consider adding department-level documents that address CS instructors.
3. **Conflicts:** list policies that point in opposite directions for the same act (e.g. "do not use AI detectors" vs "you may use detection tools"), per role. The stance-by-stage matrix already puts them side by side.
4. **CS1 coverage:** one course per curriculum role per university; 160 of 322 CS1 syllabi not findable. State as a limitation; consider a second pass for non-major intro courses (1,077 courses logged but not collected).
5. **Course progression:** report AI ban rates by course slot (CS1 48%, CS2 44%, algorithms 34%, software engineering 11%; AI/ML 37%, systems or security 39%), with counts.
6. **Wording pass** (Margaret pass) on the instructor document once the review is done.
7. **Website:** add a short "How to use this site" page and a search box for policies.

## Feedback from coauthors
Please add notes below or reply by email. Useful feedback: a policy that misstates its sources, a theme name that is unclear, a variant that is really a different policy, a missing source.

| Who | Page or policy ID | Comment | Suggested change |
|---|---|---|---|
| | | | |
