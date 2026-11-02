# Course codebook coding brief (Course coder A / B), D49

Assign each CS-syllabus statement one type from the course codebook `v2/course_codebook.json` (read every type's `name` and `covers`). Do not open the institutional type lists. Judge the statement's **content**; its stance (ban or permission) is recorded separately, so "AI may not write your code" and "AI may write your code" both get CT17.

## Input
`v2/course_code/assign_packets/<packet>.json`: statements with `sid`, `slot`, `anchor` (exact syllabus words), `label` (the open-coding label), and `passage` (the whole syllabus passage, for context).

## Output
`v2/course_code/assign_results/<packet>.json`: `{"packet": "...", "coder": "A|B", "statements": [{"sid": "...", "type": "CTxx or OTHER: <short label>", "note": "..."}]}`. Use `OTHER` only when no type fits; a `note` (one short sentence) is required for OTHER. Every sid exactly once. Validate with `python3 v2/tools/course_assign.py check <packet>` until it prints OK.
