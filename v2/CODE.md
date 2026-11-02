# v2 coding brief (Coder role)

Read all of `v2/CODEBOOK.md` and `v2/policy_types.json` (read it again at the start of each university, because types can be added between batches). You are one of two independent coders. Do not look at the other coder's output.

For each assigned university:
1. Read `v2/collect/<slug>.json`. Code **only documents with `"screen": "include"`**; skip excluded and deferred ones. Read the saved text (`text_file`) of every included document. Read each one completely, top to bottom.
2. Code every document completely, following CODEBOOK.md: set the document fields (`stance`, `tiers`, `summary`) and code every policy unit. Do not skip policies because they look similar to ones in another document. Each document is coded on its own.
3. Write the result in the CODEBOOK output format to the output path given in your task. Copy the university and document metadata (id, layer, unit, course, title, url, date_or_term) from the collect file.
4. Run `python3 v2/tools/validate_inst.py <your output file>` and fix every error it reports. Every anchor must be an exact substring of the saved text and at most 15 words. Repeat until it prints OK.
