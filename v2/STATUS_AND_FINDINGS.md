# AI policy atlas v2: status and findings (2026-11-02)

Decision numbers (Dxx) point to `v2/METHODS_DECISIONS.md` (D59 and later are in `v2/decisions.json`). The step-by-step log is `PROVENANCE.md`.

## 1. How many policies, at which level

342 US universities (178 R1, 121 R2, 14 liberal-arts colleges, 29 other).

| level | universities with a document | documents | coded statements | about AI | share of AI statements |
|---|---|---|---|---|---|
| University-wide | 327 | 707 | 23,094 | 22,624 | 94.4% |
| School or college | 20 | 29 | 643 | 619 | 2.6% |
| Computing unit (CS, CSE, EECS, ECE and CS-related departments) | 32 | 38 | 799 | 717 | 3.0% |
| **Institutional total** | 342 | 774 | 24,536 | 23,960 | 100% |
| CS courses (six slots, C1–C6), coded and compared | 135 with an AI passage | 828 syllabi | 2,238 statements from 471 AI passages | | separate layer |

- **Unit.** The table counts statements, the coding unit. The policy set (675 institutional, 229 course) is in section 4.
- **Not about AI, later.** Another 12 statements were found not to be about AI when UNCOVERED statements were sorted (D64): 9 university-wide, 2 computing unit, 1 school. That leaves 23,948 statements about AI.
- **University-wide dominates.** Almost all AI policy is written university-wide. Department-level CS policy exists at only 32 of 342 universities, so CS policy is studied bottom-up from courses (D41, D42).
- **Course layer coverage:** a department profile needs current public syllabi for at least 3 of the 4 frame courses. 55 universities have one, 267 do not, and 20 have no CS program.
- **Course slots:** 1,932. That is 322 universities with a CS program, times 6 frame courses.
  - 996 not found;
  - 314 public with AI policy;
  - 240 outdated (Fall 2022 or earlier, before ChatGPT);
  - 173 public with no AI mention;
  - 70 undated;
  - 68 have no such required course;
  - 62 not public;
  - 9 only point to a higher-level policy.
- **Profile rule still uses C1–C4:** those 1,288 slots are the ones behind the 55, 267 and 20 above.

### Why these courses (course frame, D41, D53)

| slot | course | why it is in the frame |
|---|---|---|
| C1 | CS1 | Novice programming, where AI most threatens learning |
| C2 | CS2 | Students are still building fundamentals |
| C3 | Algorithms (else systems) | Proofs and analysis rather than code |
| C4 | Software engineering (else capstone) | Team and professional practice, where AI tools are often expected |
| C5 | AI / machine learning (added) | AI is the subject as well as a tool |
| C6 | Upper-level systems or security (added) | Code-heavy work beyond the intro sequence |

- **Comparable:** every department contributes the same courses, which are required or nearly universal in US CS majors.
- **Follows the degree:** the courses run from novice to professional, so we can ask whether AI rules loosen as students advance.
- **No cherry-picking:** a fixed frame stops us choosing courses because they post AI policies.
- **Small enough to collect:** every extra course is another search at 342 universities.
- **Left out but kept:** other electives, non-major intro courses and graduate courses are outside the frame. Every course seen but not collected is in the "Out of frame" sheet (1,077 rows), so it can be coded later.
- **Profiles:** a department profile still uses C1–C4.

## 2. What we did

1. **Collected** every university, school and computing-unit AI policy document at 342 universities.
   - Every computing unit was then searched a second time (D36, D40). That added 20 documents at 14 universities.
   - Two Cloudflare-blocked universities were collected in the browser, with each saved text verified by hash.
2. **Screened** 818 documents: 777 included, 19 excluded and 22 deferred.
3. **Coded** every policy statement, rationale first.
   - Two independent coders (A and B), then a reconciler (TACT; Claude Sonnet).
   - All original wording is cut from the saved document by a script and checked. No AI-written text appears in any source column.
4. **Kept the type list open (D33).** New types were added between batches whenever a pattern appeared at 3 or more universities, growing it from 65 to 127.
5. **Theme review (D46, D47).** Every one of the 24,536 statements was read again against the full list. Each got three tags (about AI, binding, final type), and the codebook was rebuilt from what the review found:
   - content-only names;
   - 12 new types;
   - one type retired;
   - 15 themes.
6. **Agreement (D48).** Krippendorff's α between the two coders.
7. **Course layer (D41, D49, D56, D61).** Collected syllabi on a fixed frame (C1–C6) at all 342 universities: 828 syllabi, 471 AI passages at 135 universities. Coded with its **own** codebook (2,238 statements, 50 types, α = 0.868), then compared with the institutional layer.
8. **Policies (D59–D68).** Grouped the coded statements into policies, one actor group and one action each, and merged policies that say the same thing. Done for both the institutional and the course layer: 1,062 and 317 synthesized items. Then split by kind (D66, D67): the **policy set** is rules, recommendations, and facts and warnings (675 institutional, 229 course). Templates, descriptions and reasons, definitions and resources are kept as other coded text and not counted (section 4).
9. **Atlas website (D68).** One local multi-page site (`v2/site/index.html`) with a CSV behind each page. It replaces the claude.ai findings page.

## 3. What we found

### What institutions actually write (binding tag, statements about AI)
| level | rule | recommendation | description | template |
|---|---|---|---|---|
| University-wide | 21% | 33% | 28% | 19% |
| School or college | 13% | 28% | 28% | 31% |
| Computing unit | **45%** | 23% | 27% | 5% |

(After the audit correction, D54.)

- **Little is binding at the top.** About a fifth of what universities publish about AI is a rule. The rest is advice, background or sample syllabus text.
- **Schools mostly offer sample text.** Nearly a third of their statements are templates.
- **Computing units write rules.** Almost half of what they publish is binding rules (45%), and they rarely offer templates.

### Where documents stand (document stance)
- **University-wide:** 557 of 707 documents (79%) hand the decision to instructors. 78 restrict, 60 permit, 9 encourage and 3 prohibit.
- **Computing units take a position more often:** of 38 documents, 13 permit, 10 restrict, 3 prohibit, 2 encourage and 10 delegate.
- This is the first sign of the higher-ed versus CS difference that D43 asks about.

### Types and themes
- **Types:** 139 types are in use, each named only by its content. Whether a statement requires, allows or bans something is carried by separate tags.
- **Unplaced statements:** 246 statements remain UNCOVERED, at 116 universities. Of the 348 first left over, 90 were placed in policies and 12 were found not about AI (D64). The 246 that remain are 226 rare policies kept as candidates and 20 that are not a policy.
- **Not about AI:** 588 statements (2.4%) don't talk about AI. They are kept but not quoted or counted.
- **15 themes** (typed statements about AI, 23,702 in all, including the 90 placed; number of universities):

| theme | statements | universities |
|---|---|---|
| T01 Default stance and who decides | 2,576 | 313 |
| T02 Communicating and learning the rules | 2,776 | 312 |
| T15 Governance and the policy itself | 2,447 | 301 |
| T08 Detection, misconduct and due process | 2,089 | 290 |
| T05 Disclosure and attribution | 2,014 | 286 |
| T06 Ownership, understanding and verification | 1,978 | 282 |
| T12 Data, privacy, security and approved tools | 2,683 | 255 |
| T11 Faculty and staff use of AI | 1,389 | 250 |
| T09 Why: learning, careers and values | 930 | 245 |
| T13 Ethics, equity and access | 923 | 226 |
| T04 AI in producing submitted work | 909 | 219 |
| T10 AI literacy and teaching AI use | 712 | 213 |
| T07 Assessment design | 949 | 188 |
| T03 AI as a learning aid | 892 | 186 |
| T14 Research and scholarship | 435 | 111 |

- **Most common types (by number of universities):**
  - instructor or assignment decides AI use (278);
  - AI rules stated in the syllabus (266);
  - disclosing AI use (260);
  - AI misuse as academic misconduct (258);
  - verifying AI output (249);
  - keeping sensitive data out of AI tools (232).
- **New types found in the data:**
  - translation;
  - AI feedback on one's own work;
  - signs of AI-written work;
  - AI capabilities and limits;
  - status of the guidance (advisory or binding);
  - accountability for AI-assisted output;
  - careers as a reason to learn AI;
  - environmental cost;
  - labor and consent behind AI;
  - AI records and public-records duties;
  - "AI is here to stay";
  - purpose and context of the policy.

### How reliable the coding is
- **Agreement between coders (Krippendorff's α):**
  - actor 0.89;
  - policy type 0.88;
  - modality 0.88;
  - phase 0.82;
  - statement stance 0.72;
  - document stance 0.72 (raw agreement 90%).
- The first four meet the 0.80 threshold. Stance supports tentative conclusions only.
- **Splitting sentences:** the coders split sentences into statements the same way 68% of the time. The reconciler resolved the rest against the source.
- **Themes check:** 47 of 128 types co-occur most with their own theme, against about 7% by chance. The rest follow document genre, so themes stay content groupings and genre is a second lens.
- **Opus audit (D50, D52, D54):** 510 statements were checked, including a representative 300.
  - Error rates on the 300:

    | field | error rate |
    |---|---|
    | binding | 11.0% |
    | final type | 7.3% |
    | statement stance | 3.0% |
    | normalized statement | 2.7% |
    | modality | 1.0% |
    | actor | 0.3% |
    | about AI | 0.3% |
    | phase | 0% |

  - Two systematic errors were found and fixed by a targeted pass over 4,259 statements:
    - sample syllabus text tagged "rule" instead of "template";
    - generic honor-code text in department documents counted as AI policy.
  - Binding error fell to 5.3% on the same sample (optimistic).
  - **Fresh audit (Claude Opus, not GPT).** 300 new statements, drawn after the correction (seed 20261027). Binding error is 8.0%, down from 11.0% before the correction. The other fields:

    | field | error rate |
    |---|---|
    | final type | 6.0% |
    | normalized statement | 5.0% |
    | statement stance | 4.0% |
    | about AI | 2.0% |
    | modality | 1.0% |
    | actor | 0.7% |
    | phase | 0% |

    At least one field was wrong in 21.3% of the 300 statements.
  - **GPT critique (Codex), complete (5 of 5 batches, 167 items):** GPT agrees with Opus on 87% of the corrected fields (126 of 145), including 50 of 55 binding corrections. It sides with the original coding on 18 fields and with neither on 1. It flags 5 of 38 Opus confirmations (13%).

### CS courses compared with institutions (D49, D56, D61)
- **Separate codebook.** The course layer was coded with its own codebook: 50 types built from the syllabus passages, before any comparison. It now covers all six slots (C1–C6): 2,238 statements from 471 AI passages at 135 universities. Agreement between coders: α = 0.868 (559 statements, 87.3% raw agreement).
- **Mostly aligned.** 91% of course statements fall in types institutions also write about, and 4% in related but more specific types (line caps on AI code, coding agents, AI for documentation, comments and formatting, AI for search and reference).
- **Course-only practices.** 3% have no institutional counterpart (66 statements):
  - ask AI for explanations, not code (16 universities);
  - AI homework hurts exam readiness (14);
  - AI for test cases (5);
  - sharing AI sessions (3).
- **Rules loosen across the degree.** AI is banned in 48% of CS1 passages, 44% of CS2, 34% of algorithms and 11% of software engineering. AI/ML (37%) and systems or security (39%) are the other two slots.
- **Courses are stricter than their universities.** Where the university leaves the decision to instructors, 37% of CS course passages ban AI outright (134 of 362).
- **Never in syllabi.** 14 institutional types, each at 100 or more universities, have no course counterpart. They include faculty support, policy review, definitions, values and principles, sample language, AI literacy, tool approval, research and learning objectives. They also include AI rules stated in the syllabus, explaining and finding the course rules, the purpose of the policy document and how the policy was made.

## 4. Policies (D59–D68)

A statement is one coded sentence. A policy is what readers need: one actor group asked to do one thing, with the statements that say it (D59, D60). Policies that say the same thing in other words are merged (D62).

**The policy set (D67, D68)** is rules, recommendations, and facts and warnings about AI. It is the only thing counted in the tables and findings below. Templates, descriptions and reasons, definitions and resources are **other coded text**: kept, shown on their own page of the atlas, never counted in the policy set.

### How the policy set was built (pipeline)
1. 24,536 statements coded.
2. 23,948 about AI. 588 not about AI are kept but set aside.
3. 23,702 have a topic. 246 are set aside: 226 rare one-offs and 20 that state no policy (D64). 90 of the 348 first left over were placed in policies.
4. 1,562 groups within a topic.
5. 1,430 after must and should are merged.
6. **1,062 after the same policy is merged across topics.** These are all synthesized items, the step before the split (D62).
7. **675 policy set.** 387 are set aside as other coded text: 162 templates, 123 descriptions, 102 reasons, definitions or resources (D66, D67).

The course layer: 2,238 statements, 100 not about AI set aside (19 groups); 390 groups within a course topic; **317 synthesized items** after merging across topics; **229 course policy set**. 88 are set aside as other coded text: 76 descriptions, 12 reasons, definitions or resources.

### Counts
- **Institutional policy set: 675.** 611 rules and recommendations (207 rules, 404 recommendations) and 64 facts and warnings.
  - 13,095 statements stand behind them.
  - 151 (22.4%) merge two or more parts; the parts and a one-line reason are kept for review.
  - 114 (16.9%) span 2 or more types, so they are listed under each type.
  - 74 (11.0%) have the stage "background" (a definition, scope, reason, value or fact with no time of action).
- **Course policy set: 229.** 200 rules and recommendations (165 rules, 35 recommendations) and 29 facts and warnings.
  - 1,717 statements stand behind them.
  - 34 (14.8%) have the stage "background".
  - 33 (14.4%) merge two or more parts; 24 (10.5%) span 2 or more course types.
- **Before the split (all synthesized items).** Institutional 1,062: 238 (22.4%) merge two or more parts, 173 (16.3%) span 2 or more types, 176 (16.6%) have the stage background. Course 317: 46 (14.5%) background, 42 (13.2%) merged, 30 (9.5%) span 2 or more course types.
- **UNCOVERED statements (D64).** Of 348 left over after the type review:
  - 90 (25.9%) were placed in an existing policy;
  - 12 (3.4%) were found not about AI and are no longer counted;
  - 20 are not a policy (no rule, recommendation, reason or fact);
  - 226 are unique: rare policies kept as candidates.
  - 246 remain UNCOVERED (70.7% of the 348): the 226 unique and the 20 not a policy.
- **Actor groups (D65).** Four: students; instructors; staff and administrators (TAs, staff and administrators combined); everyone. The coded actor is kept.
- **Stage.** Seven: before course, course start, during work, during assessment, when misuse is suspected, over time, background. Policies coded "general" were given a stage or background (D62).
- **Who the 675 address:** 266 instructors (39.4%), 168 everyone (24.9%), 139 students (20.6%), 102 staff and administrators (15.1%).
- **When:** 255 during work (37.8%), 162 before course (24.0%), 74 background (11.0%), 65 when misuse (9.6%), 63 course start (9.3%), 40 over time (5.9%), 16 during assessment (2.4%).

### Distribution by level, actor group and stage
How to read it: a policy counts at a level when at least one statement from that level supports it. A policy can sit at several levels, so the levels add up to more than 675 (665 + 130 + 152). Course policies are separate. Cells are numbers of distinct policies in the policy set, placed by each policy's own actor group and stage. Counting all 1,062 synthesized items instead gave 221 university-wide student policies about work; the policy set gives 94.

University-wide (665 policies)

| actor group | before course | course start | during work | during assessment | when misuse | over time | background | total |
|---|---|---|---|---|---|---|---|---|
| Students | 2 | 6 | 94 | 3 | 11 | 2 | 15 | 133 |
| Instructors | 101 | 56 | 42 | 11 | 36 | 10 | 6 | 262 |
| Staff and administrators | 47 | 1 | 21 | 0 | 7 | 19 | 7 | 102 |
| Everyone | 10 | 0 | 92 | 1 | 10 | 9 | 46 | 168 |
| **All** | **160** | **63** | **249** | **15** | **64** | **40** | **74** | **665** |

School or college (130 policies)

| actor group | before course | course start | during work | during assessment | when misuse | over time | background | total |
|---|---|---|---|---|---|---|---|---|
| Students | 1 | 1 | 27 | 1 | 2 | 1 | 4 | 37 |
| Instructors | 23 | 17 | 7 | 4 | 10 | 1 | 3 | 65 |
| Staff and administrators | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| Everyone | 1 | 0 | 14 | 0 | 0 | 1 | 11 | 27 |
| **All** | **25** | **18** | **49** | **5** | **12** | **3** | **18** | **130** |

Computing unit (152 policies)

| actor group | before course | course start | during work | during assessment | when misuse | over time | background | total |
|---|---|---|---|---|---|---|---|---|
| Students | 1 | 1 | 36 | 1 | 5 | 0 | 6 | 50 |
| Instructors | 29 | 15 | 8 | 3 | 10 | 2 | 3 | 70 |
| Staff and administrators | 4 | 0 | 0 | 0 | 0 | 1 | 0 | 5 |
| Everyone | 1 | 0 | 10 | 0 | 1 | 1 | 14 | 27 |
| **All** | **35** | **16** | **54** | **4** | **16** | **4** | **23** | **152** |

CS courses (229 policies)

| actor group | before course | course start | during work | during assessment | when misuse | over time | background | total |
|---|---|---|---|---|---|---|---|---|
| Students | 0 | 6 | 163 | 10 | 2 | 3 | 0 | 184 |
| Instructors | 2 | 2 | 1 | 1 | 2 | 0 | 5 | 13 |
| Staff and administrators | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 2 |
| Everyone | 0 | 1 | 0 | 0 | 0 | 0 | 29 | 30 |
| **All** | **2** | **9** | **166** | **11** | **4** | **3** | **34** | **229** |

### Thin cells are findings
- **Assessment is the least-addressed stage.**
  - Only 16 of 675 institutional policies (2.4%) are about assessment. The next thinnest stage, over time, has 40 (5.9%).
  - By level: university-wide 15 of 665 (2.3%), school or college 5 of 130 (3.8%), computing unit 4 of 152 (2.6%).
  - No institutional policy asks staff and administrators anything during assessment.
  - Statements agree: 131 of the 13,095 statements behind the policy set (1.0%) are about assessment; across all 23,948 statements about AI it is 247 (1.0%).
  - In courses it is 11 of 229 (4.8%), more than before course (2), over time (3) and when misuse (4), but far below during work (166, 72.5%).
- **Staff and administrators are rarely addressed in courses.**
  - 2 of 229 course policies (0.9%), against 102 of 675 institutional policies (15.1%).
  - Both are about work. Six of the seven stages have none.
- **Student policies concentrate while working.**
  - Institutionally, 99 of 139 student policies (71.2%) are about work. By level: university-wide 94 of 133 (70.7%), school or college 27 of 37 (73.0%), computing unit 36 of 50 (72.0%).
  - In courses it is 163 of 184 (88.6%), and that one cell is 71.2% of all 229 course policies.
  - Students, before the course starts: 2 institutional policies (1.4% of student policies) and none in courses.
- **School and computing units add few policies.**
  - They hold 130 (19.3%) and 152 (22.5%) of the 675, but only 10 (1.5%) appear nowhere in a university-wide document: 1 school only, 9 computing only, none at both.
  - 457 policies (67.7%) are university-wide only.
  - Their grids are thinner: 9 of 28 cells are empty at school or college and 8 at computing unit, against 2 at university-wide.

## 5. Definitions and how things are presented

- **Policy unit (statement):** one policy a document states, coded once. 24,536 in total. It is the unit the coding is counted in.
- **Policy (D59–D62):** one actor group asked to do one thing, merged across wording, strength and type, and backed by the statements that say it. Shown with its original wordings.
- **Synthesized item:** a policy as it stands after merging, before the split by kind. 1,062 institutional and 317 course. Not the result; the step before it.
- **Policy set (D67, D68):** the synthesized items that are rules, recommendations, or facts and warnings. 675 institutional (611 rules and recommendations, 64 facts) and 229 course (200, 29). It is what every count, table and chart refers to.
- **Other coded text (D66, D67):** templates (sample syllabus language), descriptions, and reasons, definitions and resources. Kept, shown on their own page, never counted in the policy set. Institutional 162 templates, 123 descriptions, 102 reasons, definitions or resources; course 76 descriptions, 12 reasons, definitions or resources.
- **Merged policy (D62):** a policy that combines parts saying the same thing in other words. Different actions, objects, conditions or directions stay separate. In the policy set: 151 institutional, 33 course.
- **Background:** a policy that is a definition, scope, reason, value or fact with no time of action. Its stage is background. In the policy set: 74 institutional and 34 course.
- **Layer:** university-wide, school or college, computing unit, or course.
- **Anchor and source passage:** the original wording, cut by script from the saved document and verified. Anchors are 15 words or fewer for anything published.
- **AI-normalized statement:** a plain restatement of the policy written by a coder. It is labelled as AI-written.
- **AI rationale:** the coder's reason for the codes, written before the codes were chosen.
- **Actor:** who the policy addresses. Coded as student, instructor, TA or staff, admin, or all.
- **Actor group (D65):** the four shown: students; instructors; staff and administrators (TA or staff and admin combined); everyone.
- **Phase:** when it applies, as coded (before the course, course start, during work, during assessment, when misuse is suspected, over time, general). It is kept in the data.
- **Stage (D62):** the phase as shown. The same, except coded "general" became a stage or background.
- **Modality:** must, must not, may, should, should not, or informs.
- **Statement stance:** prohibit, restrict, permit, encourage, require, or neutral.
- **Binding:** rule, template, recommendation, or description.
- **About AI:** yes or no. Statements that are not about AI are kept but not quoted or counted.
- **Final type:** one of 139 content-only types, or UNCOVERED.
- **UNCOVERED outcomes (D64):** placed in a policy, unique (a rare policy kept as a candidate), not a policy, or not about AI (no longer counted).
- **Theme:** one of 15 content groupings of the types.
- **Presentation:** each statement row shows its original wording, a highlight link to the source, the AI rationale and normalized statement (labelled as AI), every tag, and its AI-coding provenance.
- **Where it lives (D68):** the atlas is a local multi-page website, `v2/site/index.html`, opened with `Open AI Policy Atlas.command`. Pages: Overview (status, pipeline diagram, heatmaps, thin-cell findings), Policy set, CS course policies, Matrix, Other coded text, Universities, CS course coverage, Draft a policy, Policy label, and Method and reliability. Each page links to the CSV files behind it in `v2/site/data/csv` (written by `export_site_csv.py`), so collaborators can edit and return them. The claude.ai findings page is superseded by the site. Older files still exist: `v2/exports/atlas_v2.xlsx`, `v2/exports/course_layer.xlsx`, `v2/positions/final.json`. The full glossary is `v2/DEFINITIONS.md`.

## 6. Next

1. **Human review** of the policy set sentences: 675 institutional and 229 course. The other coded text (387 and 88) is kept for reference and not reviewed as policy.
2. **Compare institutional and course policies (D43).** Higher education and CS side by side, by type, actor group and stage, on the policy set.
3. **Review the local atlas site with advisors (D68).** Collaborators edit the per-page CSVs in `v2/site/data/csv` and return them.
4. **Public site and private GitHub repo (D51).** Only with the PI's approval. The site lets people browse real policies, record their decisions, and generate a syllabus statement or department guideline. Rendered locally first; nothing is published without the PI.

## Known gaps (2026-11-02)
- **Resolved: 9 course passages not coded.** Each passage now has a section-specific id. The 9 passages were coded (71 statements) and assigned to the codebook by two coders; 71 statements were placed (69 into existing course policies, 2 into new ones). All 471 passages are coded.
- **Matrix by direction (PI, for later).** A view of what to do vs. not to do that surfaces conflicting policies (e.g. "students may" vs. "students must not" for the same act). The By role page already sorts each role's policies into Do, Don't, May and Know (D69).
