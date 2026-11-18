# Brief: second, independent check of proposed corrections

A first verifier read each policy against a sample of its statements and proposed corrections. You see each flagged policy with ALL its statements and the findings. Decide each finding independently from the statements, not from the verifier's argument.

Definitions (same as the verifier's):
- STAGE = when the actor does what the policy asks. before-course: designing the course, assignments and exams, choosing tools, writing the syllabus or policy, set-up. course-start: telling students the rules at the start. during-work: while students do coursework or study; instructors' own AI use in teaching. during-assessment: exams, quizzes, grading, what counts when work is assessed. when-misuse: suspicion, detection, reporting, sanctions. over-time: reviewing and revising policy, keeping up. background: facts and context.
- STANCE of the policy as a whole: prohibit (AI not allowed), restrict (AI only for listed uses or under a stated limit), permit (AI allowed under conditions such as disclosure), encourage (AI use invited or promoted), require (something required when AI is used, or AI use required), delegates (the instructor or assignment decides), none (a duty that holds whatever the stance on AI, with no position on AI use itself), context (fact or warning).
- TAG: expected (should or must), choice (may, or not), fact.
- DIRECTIVE: second-person rewrite of the policy; must not say more than most statements say (force, scope, added details), nor miss their point.
- LABEL: the theme label shown for this policy; it starts with the actor and "should" (expected) or "may" (choice). A label finding means this policy is misfiled or the label misstates it.

For each finding decide:
- ACCEPT: the statements as a whole clearly support the proposed value.
- MODIFY: a change is needed but the proposal is not right; give your value.
- REJECT: the current value is defensible from the statements.
Judge by what most statements say; a detail stated by one source among many is not the policy's point. Be conservative: when the current value is defensible, REJECT.

OUTPUT: JSON file review_<N>.json in this folder (N = your file number): {"<fid>": {"decision": "ACCEPT|MODIFY|REJECT", "value": "<final value if ACCEPT or MODIFY>", "why": "<one sentence citing statements>"}} for every finding id in your file. Check with a script that every fid in your file is present. Reply "done" with counts of ACCEPT, MODIFY and REJECT.
