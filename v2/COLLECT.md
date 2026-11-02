# v2 collection brief (Collector role)

Read `v2/CODEBOOK.md`, sections "Unit of analysis" and "Verbatim and honesty rules". You do NOT code policies. You find and fetch documents.

For each assigned university:
1. Use WebSearch and WebFetch to find, layer by layer:
   - the official **university**-wide AI policy or guidance;
   - any **school/college** AI policy covering computing;
   - **every computing unit** policy (CS/CSE/EECS/ECE and CS-related units such as informatics, iSchool, AI, data science, software engineering, or combined units like ICS);
   - **Course syllabi are DEFERRED (PI, 2026-10-25): do not collect course documents in this phase.** Set `searched.course` to "deferred".
   Start from the `known` URLs in the seed file; they came from an earlier pass. Prefer the current version of each document.
2. Fetch every document with `python3 tools/fetch_text.py "<url>" v2-<univslug>-<short>` from the project root, and check that the saved text actually contains AI policy text. If curl gets nothing (JavaScript-only, login), try the routes `fetch_text.py` already supports; otherwise record it as inaccessible.
3. Write `v2/collect/<univslug>.json`:
   `{"university", "slug", "state", "type", "searched": {"university","school","computing","course"} (found|none-found|inaccessible), "documents": [{"id","layer","unit","course","title","url","date_or_term","text_file"}], "notes"}`.
   `text_file` is the path that `fetch_text.py` printed.
Do not include news articles, research papers, or pages that merely link elsewhere. Follow the link to the real policy instead.

## Collection-phase quality notes (required)
For every document, add `"quality": "good|thin|generic|superseded|partial"` and `"quality_note"` to its entry in the collect file:
- `good`: substantive AI policy or guidance.
- `thin`: only one or two AI sentences.
- `generic`: an AI page with no rules (news, tool lists, workshops). Avoid collecting these at all where possible.
- `superseded`: an older version kept for the record.
- `partial`: AI text is only one section of a longer document.
Prefer the official, current document. One good university-level document beats five overlapping pages; collect overlapping pages only if each adds policy content.
