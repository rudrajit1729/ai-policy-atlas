# Computing-layer recheck brief (Recheck role)

The first collection found a computing-unit AI policy at only 24 of 342 universities. Your job is to test whether that number is real or the result of searching too lightly. Search **only** the computing layer (and the school or college that contains it), and search it thoroughly. Read `v2/CODEBOOK.md`, sections "Unit of analysis" and "Verbatim and honesty rules". You do NOT code policies.

For the assigned university:
1. **List every computing unit.** Include CS, CSE, EECS, ECE, informatics, information science or iSchool, AI, data science, software engineering, computational science, and combined units (e.g. UCI ICS, Georgia Tech College of Computing). Include the school or college that contains each one. Use the university's own directory or college pages to make the list.
2. **Search each unit's own website for an AI policy that applies across the unit** (not one course). Look in all of these places:
   - pages titled or mentioning "AI policy", "generative AI", "ChatGPT", "LLM", "use of AI";
   - academic integrity, honor code, or "collaboration policy" pages of the unit;
   - undergraduate and graduate student handbooks (often PDFs);
   - instructor, faculty or TA resources, and teaching guidelines;
   - default or common syllabus statements, and course-policy templates the unit gives instructors;
   - curriculum or committee pages and department announcements that state a rule. A news item counts only if it states the unit's policy and no better source exists.
   Use WebSearch with `site:<unit domain>` queries and WebFetch the unit pages. Run at least 4 searches per unit.
3. A document qualifies if it states rules or guidance on AI use for **the whole unit**, or for a group of its courses (e.g. all intro courses). A single course's syllabus does not qualify; note its URL in `course_examples` and do not fetch it.
4. Fetch each qualifying document with `python3 tools/fetch_text.py "<url>" v2-<slug>-<short>` from the project root, and check that the saved text contains the AI policy.
5. Write `v2/recheck/<slug>.json`:
```json
{"slug": "...", "university": "...",
 "units_searched": [{"unit": "School of Computer Science", "layer": "computing|school", "site": "https://...",
                     "queries": ["site:cs.x.edu generative AI policy", "..."], "pages_checked": ["https://..."],
                     "result": "found|none-found|inaccessible", "note": "..."}],
 "documents": [{"id": "<slug>-<short>", "layer": "computing|school", "unit": "...", "title": "...", "url": "...",
                "date_or_term": "...", "text_file": "...", "quality": "good|thin|partial", "quality_note": "...",
                "in_first_collection": true}],
 "course_examples": ["https://... (course syllabus with an AI policy; not collected)"],
 "notes": "..."}
```
Set `in_first_collection` by checking `v2/collect/<slug>.json`. Do **not** edit `v2/collect/`. A "none-found" result must list the queries and pages you checked, so that a reader can audit it.
