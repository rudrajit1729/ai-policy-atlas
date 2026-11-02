# Research brief: corpus of AI policies in CS education (North America)

Goal: build the corpus for a thematic synthesis (in the style of Amershi et al., "Guidelines for
Human-AI Interaction", CHI 2019) of policies/guidelines that North American universities use for
generative-AI use in **computing education** (CS, CSE, EECS, ECE, informatics/computing colleges).

## What counts (in scope)
- `department`: a CS/ECE/EECS/computing department, school, or college-level AI policy or guidance
  page (e.g. "Generative AI policy for CS courses", "Guidance for instructors on AI in CS courses").
- `course`: an AI policy inside a specific CS course syllabus / course website (intro programming,
  data structures, systems, etc.). At most 3 course documents per university; prefer intro
  programming courses and well-known courses with explicit, substantive AI sections.
- `university-computing`: a university-level document ONLY if it has a section specifically about
  programming/coding/computing courses.
Out of scope: generic university-wide AI statements with nothing computing-specific (list them in
`excluded`), news articles, blog posts, research papers.

## How to work
1. Find candidates with WebSearch (e.g. `"<university>" computer science "generative AI" policy`,
   `site:<cs domain> AI policy`, `"ChatGPT" OR "Copilot" syllabus site:<domain>`).
2. For EVERY document you include, fetch exact text with the helper (do not rely on WebFetch for
   wording; WebFetch may paraphrase):
   `cd "/Users/rudrajit/Documents/Current-Research/AI in education policy guidelines" && python3 tools/fetch_text.py "<url>" <slug>`
   then read the saved .txt file (path printed). If curl gets blocked/empty (JS-only page, login),
   you may use WebFetch to confirm content, but then set `"verbatim_source": "webfetch"`.
3. Only include publicly accessible documents (no login). Prefer the current/most recent version.

## Verbatim rules (critical)
- NEVER paraphrase policy text. Every `text` field must be a contiguous, character-exact substring
  of the fetched page text (whitespace differences are OK; do not fix typos, do not change quotes).
- Keep each `text` excerpt SHORT: at most 15 words, the most load-bearing words of one policy
  statement. If the statement is longer, choose the core contiguous span (do not stitch pieces).
- For each excerpt also give `frag_start` (the first 3-6 words of the FULL sentence/statement) and
  `frag_end` (its last 3-6 words), both exact substrings, so we can build a
  `#:~:text=start,end` deep link that highlights the full passage on the original page.
- At most 8 excerpts per document; choose the statements that actually set policy (rules,
  permissions, prohibitions, disclosure requirements, assessment/integrity consequences,
  rationale, instructor guidance, privacy/equity notes).

## Coding each excerpt
`topics` (1-3, from this starter codebook; add a new kebab-case code only if nothing fits and list
it in `new_codes`):
default-stance, instructor-discretion, syllabus-communication, permitted-uses, prohibited-uses,
code-generation, disclosure-citation, accountability-understanding, assessment-design,
exams-in-person, detection-tools, integrity-sanctions, learning-rationale, ai-literacy-career,
course-provided-tools, equity-access, privacy-data, instructor-staff-use, collaboration-analogy,
policy-evolution, ethics-bias-environment, intellectual-property.

`phase` (exactly 1): before-course (course/policy design, what instructors should decide),
course-start (communicating expectations to students), during-work (doing assignments/projects),
during-assessment (exams/quizzes/interviews), when-misuse (suspected violations, detection,
sanctions, amnesty), over-time (reflection, revision, review of policy).

`actor` (exactly 1): student, instructor, department, ta-staff.

`stance` for the document (exactly 1): prohibit-by-default, permit-with-conditions,
encourage, instructor-discretion, tiered (explicit levels/categories of use), mixed.

## Output
Write ONE JSON file to `corpus/raw/<GROUP>.json` (GROUP given in your task) with this shape:
```json
{
  "group": "<GROUP>",
  "searched_universities": [
    {"university": "...", "result": "included|none-found|only-generic-university-policy|inaccessible", "notes": "..."}
  ],
  "documents": [
    {
      "id": "<univ-slug>-<unit-or-course-slug>",
      "university": "Full name", "country": "USA|Canada|Mexico", "region": "state/province code",
      "unit": "e.g. Paul G. Allen School of CSE", "level": "department|course|university-computing",
      "course": "e.g. CS 106A (or null)", "title": "document title as shown",
      "url": "...", "date_or_term": "as stated on page, or null", "accessed": "2026-10-05",
      "verbatim_source": "curl|webfetch", "stance": "...",
      "summary": "2-3 sentences IN YOUR OWN WORDS describing what the document covers overall (analyst annotation, never presented as policy text)",
      "excerpts": [
        {"text": "...", "frag_start": "...", "frag_end": "...", "section": "heading or null",
         "topics": ["..."], "phase": "...", "actor": "..."}
      ]
    }
  ],
  "excluded": [{"university": "...", "title": "...", "url": "...", "reason": "..."}],
  "new_codes": [{"code": "...", "definition": "..."}]
}
```
Validate the file with `python3 -c "import json;json.load(open('<path>'))"` before finishing.
Final reply: just counts (documents included, universities with none found) and anything odd.

## Scope addendum (from the PI, mid-run)
Capture ALL kinds of AI-use provisions, not just writing/plagiarism statements. Look for and code:
- AI use by STUDENTS (code, writing reports/documentation, debugging, learning, exams)
- AI use by FACULTY / INSTRUCTORS / TAs (grading, feedback, generating course materials, detection)
- AI use CATEGORIES or LEVELS (e.g. "no AI / some AI / full AI", traffic-light, tiered tables)
- DISCLOSURE requirements (what to report, how to cite, prompts/transcripts)
- AI for WRITING as well as AI for CODE
Additional codes you may use: `use-categories-levels`, `writing-assistance`, `faculty-grading-feedback`,
`faculty-course-materials`, `research-use`. University-level AI documents that speak to instructor
syllabus statements or AI-use levels used in computing courses are in scope if the CS unit links to
or adopts them (note this in the summary).

## Scope addendum 2 (from the PI)
- Units in scope = anything computer-science-like: CS, CSE, EECS, ECE (computing courses), information
  science / iSchools / informatics, AI departments, data science schools/institutes, software engineering,
  computing colleges. Treat their department pages and their courses exactly like CS ones.
- Geography: USA and Canada only. DROP Mexico entirely (do not include Mexican institutions).

## Note: web-search budget exhausted
The session's WebSearch quota is used up. Do not retry WebSearch. Find documents by browsing directly:
department "undergraduate" / "academic integrity" / "policies" pages, course listing pages, course websites
(often <dept-domain>/~course, <course>.github.io, or linked from the department's course list), and site
search pages on the university's own domain via fetch_text.py or WebFetch. Record in searched_universities
notes which schools were checked only by direct browsing ("browse-only") so coverage can be redone later.

## Scope addendum 3 (from the PI, 2026-10-05)
- NEW LEVEL `university-general`: if an institution has NO computing-specific AI policy (no department, college,
  or computing-course document), include its official university-wide AI policy/guidance instead (provost or
  academic-affairs AI policy, academic-integrity office AI rules, official syllabus-statement guidance from the
  teaching center). Use `"level": "university-general"` and `"unit": "<office that published it>"`.
  Only if the university publishes nothing at all do you record it as none-found.
- If you find a computing-specific document, do NOT also add the university-wide one (the merge drops it anyway).
- Coverage must be complete: do not stop early. If your web-search quota runs out, write what you have, list
  the unfinished institutions in your summary under "UNFINISHED", and stop; the main session will continue them.

## Scope addendum 4: fallback order per institution (from the PI, 2026-10-05)
For each institution, include the FIRST of these that exists, and only that tier:
1. Computer science: a CS / CSE / EECS department, school or college policy, or CS course policies (levels `department`, `course`).
2. If there is no CS unit or no CS policy, a CS-related unit: information science or iSchool, informatics, AI, data science, software engineering, or computing-and-information schools such as UCI's ICS (levels `department`, `course`).
3. Otherwise, a school or college policy that covers computing programs, such as a College of Engineering or Faculty of Science AI policy: level `school-general`, unit = that school.
4. Otherwise, the university-wide AI policy: level `university-general`.
Record which tier you stopped at in the document summary ("Tier 1/2/3/4").
