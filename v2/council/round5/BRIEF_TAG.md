# Brief: tag each policy as ASKED, CHOICE or FACT

You are one of three independent coders. Do not look for or read other coders' files.

INPUT: policies.tsv (same folder). One row per policy: pid, actor (who the policy addresses), level, stance, stage, theme, directive (the policy rewritten as a directive to the actor) and original_wording (up to three statements from university documents or syllabi, separated by " || ").

For each policy decide what it does to its actor, judging from the original wording first and the directive second:

- ASKED: the policy asks or expects the actor to do something or not to do something. Must, should, are expected to, are required to, are encouraged to, need to, do not, avoid, it is recommended that. Strong or soft, enforced or not: if the actor is being told what to do, it is ASKED. A permission limited by a condition the actor must meet ("you may use AI only with instructor permission", "you may use AI but must disclose it", "use AI only for X") is ASKED, because the point is the limit.
- CHOICE: the policy leaves it to the actor: the actor may do it or not, and either is fine. May, can, are free to, are allowed to, need not, are not required to, it is optional, at your discretion, it is up to you. "You may require students to disclose AI use" (said to instructors) is CHOICE: the instructor decides. "Students may use AI to brainstorm" is CHOICE for students.
- FACT: the policy describes, explains or warns, and asks nothing of the actor. "AI output can be wrong", "AI rules differ across courses", "violations may lead to sanctions" (a consequence the actor faces, not something they choose), "some instructors require AI logs".

Rules:
- Tag what the policy does to ITS actor (the actor column), not to anyone else.
- If the original statements disagree, tag what most of them do.
- "Encourage" stance does not decide the tag: "instructors are encouraged to teach AI literacy" is ASKED; "instructors may wish to try AI" is CHOICE.
- A sentence that combines an ask and an option ("Teach basics without AI, then allow more") is ASKED if the actor is told to do the first part; note the mix in "why".
- Do not guess from the theme label alone.

OUTPUT: write JSON to tags_<N>.json in this folder, where N is your coder number: {"<pid>": {"tag": "ASKED|CHOICE|FACT", "why": "<6 to 15 words, quoting the deciding word or phrase>"}} for every pid in policies.tsv (859). Run a script to check every pid is present exactly once with a valid tag. Then reread every CHOICE and FACT tag, and every ASKED tag whose directive or wording contains "may", "can", "optional" or "need not", and fix any you got wrong. Reply "done" with your counts of ASKED, CHOICE and FACT.
