# Course-layer open coding brief (Course coder role), D49

Purpose: build a codebook for CS course AI policies **from the syllabi alone**. Course passages are NOT coded with the institutional codebook: do not open `v2/policy_types*.json`, `v2/theme_review/` or `v2/CODEBOOK.md` type lists. You describe what each syllabus says in your own words; a later step groups your labels into a course codebook and only then compares it with the institutional layer.

Read `v2/DEFINITIONS.md` for general terms (statement, actor, modality, stance). Verbatim rules: anchors are copied exactly from the passage, never paraphrased.

## Input
`v2/course_code/packets/<packet>.json`: AI passages cut by script from CS syllabi, each with `pid`, `university`, `slot` (C1 CS1, C2 CS2, C3 algorithms, C4 software engineering, C5 AI/ML, C6 systems/security), `course`, `term`, and `text` (the verbatim passage).

## For each passage
1. `passage_stance`: the passage's overall position on student AI use: `prohibit`, `restrict` (allowed only in narrow ways), `permit` (allowed with conditions), `encourage`, `require`, `mixed` (different rules for different work), or `none` (mentions AI without a position).
2. Split the passage into **statements**: one rule, permission, condition, reason or procedure each. Never merge two rules; never invent one. For each statement:
   - `anchor`: an exact quote from `text`, 4–25 words, that states it (copy character for character).
   - `why`: one sentence on why this is a statement and why it gets the label and tags below (written first).
   - `label`: a short descriptive label in your own words, 2–7 words, naming what the statement is about (for example "AI allowed for debugging only", "must cite prompts used", "AI code earns zero credit"). Reuse the same wording for the same idea across statements and passages so labels can be grouped.
   - `actor`: `student`, `instructor`, `ta-staff`, `all`.
   - `modality`: `must`, `must-not`, `may`, `should`, `should-not`, `informs`.
   - `stance`: `prohibit`, `restrict`, `permit`, `encourage`, `require`, `neutral`.
   - `cs_specific`: `yes` if it concerns code, programming, debugging, autograders, tools like Copilot, or other computing practice; else `no`.

## Output
Write `v2/course_code/results/<packet>.json`:
```json
{"packet": "...", "passages": [{"pid": "...", "passage_stance": "...", "statements": [
  {"anchor": "...", "why": "...", "label": "...", "actor": "...", "modality": "...", "stance": "...", "cs_specific": "yes|no"}]}]}
```
Every pid exactly once. Validate with `python3 v2/tools/course_code.py check <packet>` (it checks every anchor against the passage) until it prints OK.
