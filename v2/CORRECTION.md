# Correction pass brief (Correction reviewer role), D52

The Opus audit found two systematic errors in the theme-review tags. You re-judge two tags for each statement in a packet, using the surrounding text. You do not edit any coded file.

Read first: `v2/THEME_REVIEW.md` (definitions of `binding` and `about_ai`).

## Input
`v2/correction/packets/<packet>.json`: units with `uid`, `layer`, `doc_title`, `passage` (original wording), `context` (about 1,400 characters of the document around it), the current `binding` and `about_ai`, and `check` (which of the two the audit flagged for this group of statements).

## The two errors to look for
1. **Template tagged as rule.** A sentence that sits inside a sample or model syllabus statement offered to instructors ("Sample statement", "Option 2: AI permitted with attribution", "You may adapt the following"), or that quotes another institution's policy as an example, is a `template`, even when it is worded as a command ("Students must cite..."). It is a `rule` only if the document's own institution, unit or course sets it. Use the context and the document title to decide whose rule it is.
2. **Generic honor-code text tagged as about AI.** In school and department documents, general academic-integrity text (sanction lists, "ask your instructor if unsure about acceptable behavior", collaboration rules, appeals, "the instructor has the final say") is `about_ai: no` when it would read the same if AI were removed from the document. It is `about_ai: yes` when it sits inside AI-specific rules or clearly applies to AI use. When unsure, `yes`.

Judge both tags for every unit, not only the flagged one; keep the current value when it is right.

## Output
Write `v2/correction/results/<packet>.json`: `{"packet": "...", "units": [{"uid": "...", "binding": "...", "about_ai": "...", "note": "..."}]}`. A `note` (one short sentence) is required when either value changes. Every uid exactly once. Validate with `python3 v2/tools/correction_pass.py check <packet>` until it prints OK.
