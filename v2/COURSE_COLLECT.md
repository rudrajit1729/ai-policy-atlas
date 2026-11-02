# Course-layer collection brief (Course collector role), D41

Purpose: build the CS **course layer** systematically so it can later be analyzed bottom-up. Department-level AI policy is sparse; most CS-specific AI rules live in syllabi. One or two courses chosen at random do not represent a department, so every university uses the **same fixed course frame**. You collect and save documents only. You do NOT code policies.

Read `v2/CODEBOOK.md`, section "Verbatim and honesty rules".

## 1. Identify the CS program
Use the university's primary computer science degree program (the BS/BA in Computer Science, or the nearest equivalent such as CSE, EECS-CS, or Computing). If the university has no CS or computing bachelor's program (e.g. a medical or health-science university), write `"program": null`, explain in `notes`, and stop.

## 2. Identify the four frame courses from the official catalog or degree requirements
Use the catalog or degree-requirements page, not search results, and record its URL.

| slot | rule |
|---|---|
| `C1` | **CS1**: the first programming course required for the CS major. |
| `C2` | **CS2**: the next required programming course after C1 (often data structures). |
| `C3` | The required **algorithms** course. If the major requires none, the required **systems** course (computer organization, systems programming). |
| `C4` | The required **software engineering** course. If none, the required **capstone** or senior design course. If neither is required, write `"course": null`. |
| `C5` | The **AI / machine learning** course: the required AI or ML course if the major requires one; otherwise the undergraduate introduction to AI or to machine learning that the department offers most often (check the catalog and recent schedules). If the department offers neither, write `"course": null`. Note in `note` whether it is required or an elective. |
| `C6` | An **upper-level systems or security** course, different from C3: the required operating systems or computer systems course if the major requires one and C3 is not already it; otherwise the required computer security course; otherwise the upper-level operating systems, networks or security elective offered most often. Note in `note` whether it is required or an elective. |

If the degree offers alternatives (e.g. a choice of two CS1 courses), take the one most students take (the default listed first) and note the alternatives.

## 3. Find the most recent public syllabus for each frame course
- Search the department site, course website (often `<dept-domain>/courses/...`, GitHub Pages, personal pages), the public syllabus repository (Simple Syllabus, Concourse, syllabus banks), and the catalog. Run at least 3 searches per course, e.g. `"<course number>" syllabus`, `"<course number>" "generative AI" OR ChatGPT OR "AI policy"`, and `site:<dept-domain> <course number>`.
- Prefer the most recent term, 2025–26 or later. Search for the current offering by name and year (e.g. `"CS 161" 2026`, `"CS 161" "Fall 2025"`), including instructor and course websites, before settling for an older version.
- **Date every syllabus.** Set `year` to the calendar year the term starts (Fall 2025 → 2025, Spring 2026 → 2026). Find it in the text, the URL or the page. If no date can be established, set `"undated": true` and `year: null`. Set `older: true` if the term is before 2025–26.
- ChatGPT was released at the end of November 2022, so a syllabus from **Fall 2022 or earlier** cannot tell us anything about AI policy. If the newest public syllabus you can find predates Spring 2023, keep it, but set the course `status` to `outdated`.
- If several sections in the same term have different syllabi, collect up to 3 and note how many exist.
- Fetch each syllabus with `python3 tools/fetch_text.py "<url>" v2c-<slug>-<slot>[-n]` from the project root, then read the saved text.
- Set `status` for every course. `public-*` statuses apply only to syllabi from Spring 2023 or later:
  - `public-ai-policy`: a public syllabus that has an AI section or statement;
  - `public-no-ai`: a public syllabus that does not mention AI;
  - `public-generic-only`: the syllabus only points to a university or department AI policy without its own rule (still collect it);
  - `outdated`: the newest public syllabus is from Fall 2022 or earlier (pre-ChatGPT); keep it and record its year;
  - `undated-only`: the only public syllabus has no date that can be established;
  - `not-public`: a syllabus exists but is behind a login (LMS, Canvas);
  - `not-found`: nothing was found after the required searches.
- For a `public-ai-policy` or `public-generic-only` syllabus, give `ai_start` and `ai_end`: the **exact** first 5–8 words and last 5–8 words of the syllabus's whole AI-related passage. If the AI rules are scattered, give one pair per passage in `ai_passages`. A script cuts the verbatim text between them, so copy the words exactly from the saved text.
- Do not record instructor names.

## 4. Write `v2/course/<slug>.json`
```json
{"slug": "...", "university": "...",
 "program": {"name": "BS Computer Science", "unit": "Department of Computer Science", "requirements_url": "https://..."},
 "courses": [
   {"slot": "C1", "course": "CS 161", "title": "Introduction to Computer Science I", "catalog_url": "https://...", "alternatives": [],
    "status": "public-ai-policy|public-no-ai|public-generic-only|not-public|not-found",
    "searches": ["\\"CS 161\\" syllabus oregon state", "..."],
    "syllabi": [{"id": "<slug>-C1", "url": "https://...", "term": "Fall 2026", "year": 2026, "undated": false, "older": false, "section": "001 or all",
                 "text_file": "...", "ai_passages": [{"ai_start": "...", "ai_end": "..."}]}],
    "sections_in_term": 1, "note": "..."}
 ],
 "notes": "..."}
```
Every one of C1–C4 (and C5–C6 once added, D53) must appear, even when its status is `not-found` or `not-public`. Validate with `python3 v2/tools/validate_course.py v2/course/<slug>.json` and fix every error it reports until it prints OK.

## Adding C5 and C6 to an existing file (D53)
For a university whose `v2/course/<slug>.json` already has C1–C4: keep C1–C4 exactly as they are, identify C5 and C6 from the catalog with the rules in section 2, and run section 3 for each (at least 3 searches, date every syllabus, set a status, give `ai_start` / `ai_end` for AI passages). Append the two entries to `courses`. If `program` is null, change nothing. Validate with `python3 v2/tools/validate_course.py --slots C1,C2,C3,C4,C5,C6 v2/course/<slug>.json` until it prints OK.
