# Brief: refine the role policy lists (round 2)

The input lists, for one or two roles, every policy in the AI policy set, organized as CELLS (role | level | stance | course stage), then GROUPS (themes made by a three-coder council), then policies. Each policy line: ID | directive to the reader | kind | N universities. Lines marked [NO-AI-WORD] never mention AI; their source wording follows.
Levels: inst = university, school and department documents; course = CS course syllabi. Stances: prohibit, restrict (only listed uses), permit (allowed with conditions), encourage, require, delegates (instructor decides), none (duties and facts: sets a duty or states a fact without allowing or restricting AI).

The PI's complaints you are fixing:
1. Theme names are vague or awkward ("Keeping data out of AI tools": what data? "Understanding and owning submitted work", "AI as a study aid", "Doing one's own thinking", "AI as assistive technology", "Ethical AI use in research"). A reader should know from the name alone what the policies ask.
2. Inside a theme there is redundancy: several policies say essentially the same thing. Merge those.
3. Some policies do not read as AI policies (e.g. "Do not use unauthorized notes or devices during an exam").

## Task A: merge near-duplicates (within a group only)
Inside each group (or each small cell without groups), merge policies that ask the same group to do the same thing, judged three ways:
- semantic: they say the same thing in different words;
- latent: they express the same underlying requirement even if worded at different levels of detail;
- contrastive: before merging, look for any difference that matters: force (must / should / may / must not), condition or exception (only if, unless, with permission), object (personal data vs course materials vs research data), actor, or stage. If any such difference exists, do NOT merge; keep them as separate items.
For each merged item write one directive that covers exactly what the merged policies say, no more and no less: keep the strongest shared force only if all share it (if force differs, don't merge), keep every condition, use the union of example lists only when the examples are of the same thing. Never merge across groups or cells. Never drop a policy ID.
Expect modest merging: many groups have no duplicates. Do not merge just because policies share a topic.

## Task B: rename group labels
Rename every group label so it says specifically what the policies ask or concern, in 3 to 8 plain words, sentence case, no colons. Prefer verb phrases for actions ("Keep personal and confidential data out of AI tools", "Use AI to study and practice, not to do graded work") and plain noun phrases for facts ("What AI output gets wrong"). Name the object specifically. No jargon ("latent", "agentic"), no vague words ("issues", "considerations", "matters", "ethics standards"). The same idea in different cells should keep the same label. Groups with one policy keep a label too.

## Task C: AI link for [NO-AI-WORD] policies
For each [NO-AI-WORD] policy, read its source wording and classify:
- "context": the sources are about AI (e.g. prompts, AI logs, assessment redesign in response to AI, devices or resources including AI). Rewrite the directive so the AI link is explicit, using only what the sources say (e.g. "Do not use AI or other unauthorized resources, such as notes, devices or the internet, during an exam; doing so is cheating.").
- "general": a general academic-integrity or procedural rule that an AI document restates without being about AI (e.g. report-form deadlines, group responsibility for violations). Keep the directive unchanged.
Give a one-line reason citing the source wording.

## Output (valid JSON, exactly this shape)
{
 "cells": {
  "<cell key exactly as in the input, e.g. student|inst|restrict|during-work>": [
     {"label": "<new group label>", "old_label": "<label in input, or '(no groups: small cell)'>",
      "items": [{"pids": ["P50.06"], "directive": "<directive; unchanged text if not merged and not rewritten>"},
                {"pids": ["P52.04", "P49.04"], "directive": "<merged directive>", "why": "<what makes them the same; what you checked>"}]}
  ]
 },
 "ai_link": {"<pid>": {"class": "context|general", "directive": "<rewritten directive for context; unchanged for general>", "why": "..."}}
}
Every cell in the input must appear; every policy ID exactly once in its cell; groups keep their membership (you may not move a policy between groups). Order groups and items by total universities, largest first (use the N universities given; for a merged item use the largest of its policies).
Before finishing, run a script that checks the shape, that every input ID appears exactly once in its cell and in its original group, and that every [NO-AI-WORD] ID has an ai_link entry. Then reread every merge once, contrastively, and undo any that hides a difference.

Directive style: second person to the reader of that role ("Do not ...", "You may ...", "If you do research, ..."), plain American English, no em dashes. Facts stay statements.

## Prose (only if your task says so)
For the roles "staff" and "all", also write paragraphs in the same style used for students and instructors: per level, an "intro" (3 to 5 sentences: where along the course the policies sit, which stances dominate, with counts) and one paragraph per stance present (2 to 4 sentences; 1 or 2 if 3 or fewer policies): what the policies ask, claim first, citing policy IDs in parentheses with "N universities". Every number must come from the input (policy counts per stance and stage can be counted from the input; universities per policy are given). No hype words (crucial, robust, landscape, nuanced, comprehensive, notably, underscores, highlights, delve, pivotal), no em dashes, no "not X but Y", no rhetorical questions. Describe only what the policies say. Put it in the JSON as "prose": {"staff": {"inst": {"intro": "...", "stances": {"<stance id>": "..."}}, "course": {...}}, "all": {...}}.
