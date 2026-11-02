# Paper outline (bullets, for discussion), revised 2026-11-02

## Working title
- Generative AI Policy, from the University to the CS Classroom: A Synthesis of Policies across US Higher Education

## The gap
- **No shared vocabulary.** Universities have no common language for how they integrate generative AI into teaching and curricula. Each writes its own documents, in its own terms, and nobody can compare them.
- **No CS view.** Without a shared vocabulary, there is no way to see where a discipline like CS sits relative to the institution around it.

## Research questions
- **RQ1:** What are the generative AI policies of US higher education: what do they cover, who do they address, and how binding are they?
- **RQ2:** Taking CS as a specific case, how do CS course policies differ from institutional policy, and what can each learn from the other?

## Data and method
- **Universities:** 342 US universities (178 R1, 121 R2, 14 liberal-arts colleges, 29 other).
- **Policy documents:** 774, at three levels: university-wide (327 universities), school or college (20), computing unit (32).
- **Course frame:** the same six CS courses at every university, taken from the official catalog:
  - CS1;
  - CS2;
  - algorithms;
  - software engineering;
  - AI/ML;
  - systems or security.
  - 828 syllabi collected; 471 AI passages at 135 universities.
- **Statement-level coding:**
  - every policy statement is coded once (24,536 statements);
  - two coders work independently, then a reconciler resolves disagreements;
  - every statement keeps the institution's exact words, cut from the saved document and checked by script.
- **Building the vocabulary:**
  - the list of policy types started small and grew whenever the data showed a new kind of policy at three or more universities;
  - after all statements were coded, every statement was re-read against the full list;
  - the result is 139 policy types named by what they are about, grouped into 15 themes along the course lifecycle;
  - this is the shared vocabulary the paper proposes.
- **CS courses:** coded with their own vocabulary, 50 types built from the syllabi alone, before any comparison with institutional policy. 2,238 statements from all six slots.
- **Policies (D59–D68):**
  - statements are grouped into policies: one actor group and one action each, merged across wording, strength and type;
  - pipeline: 24,536 statements, 23,948 about AI, 23,702 with a topic, 1,562 groups, 1,430 after must and should merged, 1,062 synthesized items after merging across topics, 675 in the policy set;
  - the policy set is rules, recommendations, and facts and warnings: 675 institutional (611 rules and recommendations, 64 facts; 151 merge parts, 114 span 2 or more types) and 229 course (200, 29);
  - set aside as other coded text, kept and never counted: institutional 162 templates, 123 descriptions, 102 reasons, definitions or resources; course 76 descriptions, 12 reasons, definitions or resources;
  - four actor groups: students, instructors, staff and administrators, everyone;
  - seven stages: before course, course start, during work, during assessment, when misuse, over time, background;
  - of 348 leftover (UNCOVERED) statements, 90 were placed in policies and 12 were found not about AI; 246 remain.
- **Reliability (Krippendorff's α):**
  - institutional coding: actor 0.89, type 0.88, modality 0.88, phase 0.82, stance 0.72;
  - course coding: 0.87.

## Findings: higher education (RQ1)
- **Policy is written at the top.** 94% of AI policy statements come from university-wide documents. Only 32 of 342 universities have a computing-unit policy.
- **Universities delegate.** 79% of university-wide documents leave the AI decision to each instructor.
- **Universities mostly advise.** About a fifth of what they publish is a binding rule. The rest is recommendation, background and sample syllabus text.
- **What they talk about** (themes, by number of universities):
  - who decides;
  - communicating the rules;
  - governance;
  - misconduct;
  - disclosure;
  - ownership and verification;
  - data and approved tools.
- **What they barely touch:** assessment. Only 1% of statements (247 of 23,948) say what happens during exams or other assessments. At the policy level, 16 of 675 (2.4%).
- **Who policies address and when** (the 675 in the policy set):
  - instructors 39%, everyone 25%, students 21%, staff and administrators 15%;
  - 38% are about work, 24% are before the course, 11% are background;
  - student policies concentrate while working (71% of them).
- **School and computing units add few policies.** Only 10 of 675 (1.5%) appear nowhere in a university-wide document.

## Findings: CS (RQ2)
- **CS units decide where universities delegate.**
  - 45% of what computing units publish is a binding rule, against about a fifth university-wide.
  - Most computing-unit documents take a position rather than handing the decision to instructors.
- **CS courses are stricter than their universities.** Where the university leaves the decision to instructors, 37% of CS course passages ban AI outright.
- **Rules loosen across the degree.** AI is banned in 48% of CS1 passages, 44% of CS2, 34% of algorithms and 11% of software engineering. AI/ML (37%) and systems or security (39%) fall in between.
- **What CS courses add that institutions do not:**
  - prompt AI for explanations, not code;
  - line caps on AI code ("rewrite it yourself");
  - turn off Copilot and editor autocomplete;
  - rules for coding agents;
  - AI for test cases;
  - "AI homework will cost you on the exam";
  - explain every line, checked in code interviews.
- **Course policies** (the 229 in the course policy set):
  - 80% address students and 72% are about work;
  - assessment gets 11 (4.8%), more than before-course (2), over-time (3) or when misuse (4), but far less than working (166);
  - staff and administrators get 2 (0.9%), against 15% of institutional policies.

## Comparison
- **Aligned on the core.** CS courses and universities agree on who decides, disclosure, own work, misconduct and verification. 91% of what syllabi say falls in topics universities also cover.
- **But stricter in CS.** While universities say "decide and disclose", CS1 says "don't use it".
- **Missing from syllabi.** 14 institutional types, each at 100 or more universities, never reach syllabi:
  - support for faculty;
  - policy review;
  - definitions;
  - values;
  - AI literacy;
  - tool approval and privacy;
  - learning objectives as the reason for a rule;
  - explaining and finding the course rules;
  - the purpose of the policy and how it was made.
- **What higher education can learn from CS:**
  - concrete, assessable rules (explain every line, oral checks, limits on AI code);
  - staging AI permission across a curriculum;
  - saying what happens in assessments.
- **What CS can learn from higher education:**
  - say why, from learning objectives;
  - address data, privacy and tool approval;
  - revisit the policy;
  - link students and faculty to institutional support.

## Contributions
- A shared vocabulary for generative AI policy in higher education: 139 content-named types in 15 lifecycle themes, built from 24,536 statements at 342 universities.
- A policy set: 675 institutional and 229 course policies (rules, recommendations, and facts and warnings), each one actor group and one action, with the original wording behind it. Templates, descriptions and reasons are kept as other coded text and not counted.
- A CS case built bottom-up from a fixed course frame, with its own vocabulary, compared with the institutional one.
- A local website (v2/site, D68): browse real policies along the course lifecycle, see how common each choice is, read the other coded text, edit the CSV behind each page, and draft a policy grounded in real wording. Public release only with the PI's approval (D51).

## Threats to validity (to write)
- **Access.** Many syllabi sit behind learning-management logins. Public availability is uneven and favors R1 and selective colleges.
- **AI-assisted coding.** Mitigated by:
  - two independent coders and a reconciler;
  - script-verified wording;
  - Opus audits (510 statements, then a fresh 300) with a GPT critique of the corrections (167 items).

  Binding error is 8.0% on the fresh sample. Stance agreement is tentative (α 0.72). Policy sentences and merges are AI-made and await human review.
- **Snapshot.** October 2026; policies change quickly.
- **Course frame.** Six courses per university, not electives or graduate courses. Courses seen outside the frame are kept for later coding.

## Figures and tables (draft list)
1. Pipeline: from 24,536 statements to the 675 institutional and 229 course policy set, with what each step set aside.
2. Policy by level: universities, documents, statements.
3. What institutions write: rule, recommendation, description, template, by level.
4. Document stance by level.
5. The 15 themes along the course lifecycle, with university coverage.
6. Who and when: the actor group × stage matrix of the policy set, by level and for courses, with the assessment gap.
7. CS course stance from CS1 to software engineering.
8. University stance against course stance.
9. Alignment: shared, partial, CS-only and institution-only topics.
