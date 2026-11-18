# Brief: verify each policy against its sources before the documents go to coauthors

Each policy in your batch file is shown with its current STANCE, STAGE, TAG, THEME LABEL and DIRECTIVE, and the statements behind it (university, where it comes from, how each statement was coded, and the original words). The PI found a policy filed under Prohibit / Before the course whose sources are mostly not prohibitions and are about assessment. Check every policy in your batch the same way. Judge from the original words of the statements.

Check five things:

1. ACTOR. Do the statements address this actor (students or instructors)? If most of the statements address someone else, flag it.

2. STAGE: when does the actor do what the policy asks?
   - before-course: designing the course, its assignments and exams, choosing tools, writing the syllabus or policy, institutional set-up.
   - course-start: telling students the rules at the start (syllabus statement, first-day discussion).
   - during-work: while students do assignments, projects, studying, coursework; instructors' own use of AI in teaching.
   - during-assessment: exams, quizzes, grading, what counts when work is assessed.
   - when-misuse: suspicion, detection, reporting, sanctions.
   - over-time: reviewing and revising policy, keeping up, evidence.
   - background: facts and context, not tied to a moment.
   Flag a stage only when the statements clearly put the act at another stage. Designing an exam format is before-course; grading and what counts in grading is during-assessment.

3. STANCE of the policy as a whole: what does it do about AI use?
   - prohibit: AI is not allowed (for this thing).
   - restrict: AI is allowed only for listed uses, or only under a stated limit.
   - permit: AI is allowed under conditions such as disclosure.
   - encourage: AI use is invited or promoted.
   - require: something is required when AI is used (or AI use is required).
   - delegates: the instructor or assignment decides.
   - none: a duty that holds whatever the stance on AI use (for example, verify output, tell students the rules), with no position on AI use itself.
   - context: a fact or warning that asks nothing.
   The current stance came from a rule (the most common non-neutral statement stance if at least a quarter of statements have one). That rule can mislabel a policy whose statements are mostly neutral: one "prohibit" statement among six neutral ones should usually make it "none". Flag a stance only when the statements as a whole clearly support another one.

4. TAG: expected (the actor should or must do it), choice (the actor may do it, or not), fact. Flag only clear errors.

5. WORDING. Does the DIRECTIVE or the THEME LABEL say more than the statements do (stronger force, wider scope, a detail no statement gives) or miss their point? The theme label covers a group of policies, so judge only whether it misstates this policy. Flag overstatements and propose a faithful rewording (same style: the directive in second person; the label starting with the actor and "should" or "may").

OUTPUT: JSON file verify_<batch>.json in this folder: a list of findings, one per policy that needs a change, nothing for policies that are fine:
{"pid": "...", "field": "actor|stage|stance|tag|directive|label", "current": "...", "proposed": "...", "evidence": "<quote the deciding words from the statements, with university>", "confidence": "high|medium"}
Be conservative: propose a change only when the statements clearly support it. Then reread each finding against its statements once more and drop any you cannot defend with a quote. Reply "done" with the number of policies checked and the number of findings by field.
