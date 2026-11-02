# Audit brief (Auditor role, Claude Opus), D50

Purpose: estimate how often the coded data is wrong. You check a sample of coded statements against their source and record, field by field, whether each code is right. You do not edit any coded file.

Read first: `v2/DEFINITIONS.md`, `v2/CODEBOOK.md` (sections on unit fields and "Verbatim and honesty rules"), `v2/THEME_REVIEW.md` (binding and about-AI definitions), and the final type list `v2/policy_types_v3.json` (each type's `name` and `covers`; ignore types marked `retired`).

## Input
`v2/audit/packets/<packet>.json`: units with `uid`, `university`, `layer`, `doc_title`, `passage` (original wording, cut by script), `context` (about 1,400 characters of the saved document around the passage), and the codes to check:
- `policy`: the AI-normalized statement (empty = the passage states it);
- `actor`, `phase`, `modality`, `unit_stance` (values defined in CODEBOOK.md);
- `about_ai` (yes/no), `binding` (rule/template/recommendation/description), `final_type` (id and name).

## For every unit and every field, decide
- `ok`: the code is right, or a reasonable coder could defend it from the passage and context.
- `wrong`: the code is clearly not supported; give the `correct` value (for `final_type`, an id from the v3 list or `UNCOVERED`; for `policy`, write `correct` as one sentence describing the error rather than a rewrite).

For `policy`, judge fidelity: wrong only if the normalized statement adds, drops, softens or strengthens something the passage says, or merges two rules. For `final_type`, judge content fit only (ignore modality and actor). Be strict but fair: "I would have chosen differently" is `ok` if the code is defensible.

Also give `unit_ok`: `yes` if every field is ok, else `no`, and `why`: one or two sentences, required when any field is wrong.

## Output
Write `v2/audit/results/<packet>.json`:
```json
{"packet": "...", "units": [{"uid": "...",
  "fields": {"policy": {"verdict": "ok|wrong", "correct": "..."}, "actor": {...}, "phase": {...}, "modality": {...},
             "unit_stance": {...}, "about_ai": {...}, "binding": {...}, "final_type": {...}},
  "unit_ok": "yes|no", "why": "..."}]}
```
`correct` is required only when the verdict is `wrong`. Every uid exactly once. Validate with `python3 v2/tools/audit.py check <packet>` until it prints OK.
