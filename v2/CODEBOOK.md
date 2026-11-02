# v2 codebook: coding AI-use policies in US computing education

This file is shared by every agent that collects or codes documents. Read all of it. The project context is in `../context.md`.

## Unit of analysis

The **university**. For each university we collect every layer that exists and keep the layers separate:

| layer | what it is | rule |
|---|---|---|
| `university` | The official university-wide AI policy or guidance: provost or academic affairs, the academic-integrity office, an official syllabus-statement policy, or the teaching center's official guidance. | Always collect, for every university. |
| `school` | A school- or college-level policy covering computing, e.g. a College of Engineering or College of Arts & Sciences AI policy. | Collect if it exists. |
| `computing` | A computing unit's policy. CS, CSE, EECS and ECE count. So do CS-related units: informatics, information science/iSchool, AI, data science, software engineering, and combined units such as UCI's ICS. **Collect every such unit**, including CS-related units at universities that also have a CS department. | Collect all that exist. |
| `course` | AI policies in syllabi of computing courses (CS and CS-related). | Add-on layer: up to 3 per computing unit, preferring intro and core courses. Never used to characterize the university as a whole. |

## Document-level fields

- `stance_why`: written first. Why the document has this stance, citing its words.
- `stance`: exactly one of
  - `prohibit`: AI use is banned for the work the document governs.
  - `restrict`: AI is banned unless explicitly permitted, or permitted only for narrow listed uses.
  - `permit`: AI is allowed with conditions such as disclosure or limits.
  - `encourage`: AI use is welcomed or recommended.
  - `require`: AI use is built into the work or required.
  - `delegates`: the document sets no stance itself and hands the decision to instructors, courses or assignments. Most university-wide guidance falls here.
- If a document offers tiers or templates, set `stance` to `delegates` and list the tiers in `tiers`.

## Policy units: the core of the coding

Code **every** policy the document states. A policy is any statement that requires, forbids, permits, recommends or explains something about AI use, by anyone, in teaching or learning. That includes rationale, definitions of misuse, enforcement, disclosure, privacy, equity, faculty use, review cycles, and so on. Do not sample: a 4-page policy can yield 30 or more units. Skip only navigation, boilerplate unrelated to AI, and exact repeats within the same document.

Fields for each unit, **in this order** (rationale first, as in TACT Stage 4):

- `why`: **written before any code.** One to three sentences explaining why this passage is a policy and why it gets the actor, phase, modality and policy type you are about to assign. Cite the passage's own words in quotation marks. Writing the rationale first keeps the reasoning checkable and stops a code from being chosen first and justified afterward.

- `anchor`: a contiguous, character-exact quote from the fetched text, **at most 15 words**. Choose the most load-bearing span of the sentence or passage.
- `frag_start` / `frag_end`: the exact first 3–6 and last 3–6 words of the full sentence or passage, used to build the highlight link.
- `policy`:
  - If the anchor alone fully states the policy, set `policy` to `null`. The anchor then is the policy text.
  - Otherwise write a normalized statement in plain present tense. Keep the institution's own key words and do not add, soften or strengthen anything. One policy per unit. Never merge two distinct rules.
- `actor`: who the policy is addressed to or binds. Exactly one of `student`, `instructor`, `ta-staff`, `admin` (department, college, university office), `all`.
- `phase`: exactly one of
  - `before-course`: course and policy design, institutional set-up.
  - `course-start`: communicating expectations.
  - `during-work`: assignments, projects, studying.
  - `during-assessment`: exams, quizzes, in-class evaluation.
  - `when-misuse`: suspicion, detection, sanctions, amnesty.
  - `over-time`: review, revision, evidence.
  - `general`: definitions, principles, scope.
- `modality`: exactly one of `must`, `must-not`, `may`, `should`, `should-not`, `informs` (rationale, facts, definitions).
- `policy_type`: one id from the type list (`policy_types.json`). Do not invent ids. The list is **provisional and grows with the data** (D33): between batches, recurring UNCOVERED notes become new types.
  - If the unit says what a type's definition and members say, assign that type.
  - If it fits **only partly**, assign the nearest type and write `fit_note`: what this unit says that the type does not capture.
  - If it fits **no** type, use `UNCOVERED` and write `uncovered_note`: what the policy is, in one plain sentence. **Prefer UNCOVERED over a stretched fit.** A new kind of policy that is forced into an old type is lost; an UNCOVERED unit is counted and can become a new type.
  - (During the dry run only, `NEW:<short name>` was allowed.)
- `unit_stance`: the position this single policy takes on AI use, independent of the document's overall stance. Exactly one of `prohibit`, `restrict`, `permit`, `encourage`, `require`, `neutral` (rationale, definitions, procedures).
- `topics`: 1–3 codes from the codebook in `AGENT_BRIEF.md` (for example `disclosure-citation`, `code-generation`, `privacy-data`).

## Code once, for every later analysis
Each unit is coded **once**, with every tag above: actor, phase, modality, unit_stance, policy_type, topics. Its document's layer and stance are attached to it as well. Later analyses (other matrices, other groupings) regroup these tags and never recode. So:
- `policy_type` is the **single** group where the policy belongs: the place a reader looking for this rule would expect to find it. If two types seem to fit, the `why` must say which one you chose and why the other does not fit as well.
- Grouping uses **constant comparison**. Before assigning a type, compare the unit with that type's definition and with policies already coded under it. Assign it there only if it says the same thing. Otherwise use `UNCOVERED` with a note. UNCOVERED notes and fit notes are reviewed between every batch; recurring patterns become new types, and every new or candidate type is recorded in `v2/CODEBOOK_MEMO.md`. After all coding, a theme review reads every unit of every type and may split, merge or create types and themes (D34). Terms are defined in `v2/DEFINITIONS.md`.

## Verbatim and honesty rules

- Never invent a policy. Every unit must be traceable to its anchor in the fetched text.
- A normalized `policy` must not go beyond what the source passage says. If you are unsure, keep `policy: null` and choose a fuller anchor.
- Fetch with `python3 tools/fetch_text.py "<url>" v2-<slug>` (run from the project root) and quote only from the saved text.

## Output: one JSON file per university at `v2/inst/<univ-slug>.json`

```json
{
  "university": "Full official name", "slug": "...", "state": "OR", "type": "R1|R2|liberal-arts|HBCU|MSI|community-college|other",
  "searched": {"university": "found|none-found|inaccessible", "school": "...", "computing": "...", "course": "..."},
  "documents": [
    {"id": "<slug>-<short>", "layer": "university|school|computing|course", "unit": "office/department/course name",
     "course": "CS 161 or null", "title": "...", "url": "...", "date_or_term": "...", "stance": "...", "tiers": [],
     "summary": "2-3 sentences in your own words (analyst annotation)",
     "stance_why": "...",
     "units": [ {"why": "rationale citing the passage, written first", "anchor": "...", "frag_start": "...", "frag_end": "...",
                 "policy": "... or null", "actor": "...", "phase": "...", "modality": "...",
                 "policy_type": "P19 | UNCOVERED", "uncovered_note": "only when UNCOVERED", "fit_note": "only when the type fits partly", "topics": ["..."]} ]}
  ],
  "new_types": [{"name": "...", "definition": "..."}],
  "notes": "anything a reviewer should know"
}
```
