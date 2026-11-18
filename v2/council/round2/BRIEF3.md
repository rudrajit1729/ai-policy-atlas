# Brief: cluster near-duplicate policies inside each group (round 3)

The PI reads the lists and sees redundancy: inside a group, several policies make the same point with small differences. An earlier pass refused to merge them because they differ in force, scope or condition, which was right: they must not be collapsed into one sentence. Instead, cluster them and show the differences.

INPUT lines: cells (role | level | stance | stage), groups (with their final labels), and policies: ID | directive | kind | N universities.

TASK: inside each group, cluster the policies that make the same point (semantically, or latently: the same underlying requirement at a different level of detail). For each cluster:
- the lead is the policy stated by the most universities;
- every other member is a variant with a short note (2 to 8 words) saying exactly how it differs from the lead, contrastively: scope ("homework only", "graded work only", "research data"), force ("should, not must", "may, not must"), condition ("only with instructor permission", "when in doubt"), object ("course materials, not personal data"), or added detail ("also names transcripts"). The note must be checkable against the two directives; do not invent differences.
- Singletons are fine. Do not cluster policies that only share a topic but ask different things (e.g. "keep personal data out" and "use approved tools" are different points). Never cluster across groups. Never change directives or labels. Every policy ID appears exactly once.

OUTPUT (valid JSON): {"cells": {"<cell key>": [{"label": "<group label as given>", "items": [{"lead": "<pid>", "variants": [{"pid": "<pid>", "differs": "<note>"}]}]}]}}
Keep group order as given; order items by the lead's universities, largest first. Run a script to check every input ID appears exactly once in its own group, then reread every variant note against the two directives and fix any that is wrong or vague. Reply "done" with the number of clusters that have variants and the number of variants.
