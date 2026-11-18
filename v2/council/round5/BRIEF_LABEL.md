# Brief: write theme labels that name the actor and match the tag

INPUT: groups.txt (same folder): 311 groups. Each has a KEY, the ACTOR (who the policies address), a TAG, the stance and stage, the OLD THEME label, and its POLICIES (ID: directive).

TAG meaning, from a coding of every policy by three independent coders:
- asked: the actor is asked to do it (must and should treated alike).
- choice: the actor may do it, or not; it is left to them.
- fact: a fact or warning that asks nothing of anyone.

The PI's complaint about the old labels: "Assess students' own work, not AI output" does not say who must do it; a label must name its actor. And a label must not mix an ask with an option ("Teach basics without AI, then allow more": the "allow more" part is an option, not an ask).

TASK: write one new label per group.
- asked: start with the ACTOR, then "should" or "should not": "Instructors should assess students' own work, not AI output." Use "should" even when the policies say must.
- choice: start with the ACTOR, then "may": "Instructors may use AI to draft course materials."
- fact: a plain statement of the fact, no actor needed: "AI output can be wrong or fabricated."
- Everyone: "Everyone should ..." / "Everyone may ...". Staff: "Staff and administrators should ...".
- The label must cover every policy in the group and add nothing they do not say. Keep the OLD THEME's point and wording where it is accurate. 6 to 16 words, one sentence, ending with a period. No "etc.", no semicolons.
- Inside an asked label, no "may" or "can" clause that gives the actor an option; inside a choice label, no "should" or "must".
- If a group's policies are about someone acting on another group (e.g. instructors telling students), the actor is still the ACTOR given: "Instructors should tell students which AI uses are allowed."

OUTPUT: JSON file labels.json in this folder: {"<KEY>": "<label>"} for all 311 keys, copied exactly. Run a script to check: every key present once; asked labels start with the actor followed by " should"; choice labels start with the actor followed by " may"; no fact label starts with an actor name. Then reread every label against its policies and fix any that overstate, understate or mix tags. Reply "done" with the number of labels and 10 example labels (old theme -> new label).
