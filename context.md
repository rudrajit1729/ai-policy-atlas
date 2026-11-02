# Context: Computing AI Policy Atlas

Read this first. It tells a new conversation what this project is, what has been done, and where everything lives. The step-by-step log of what was done and when is in `PROVENANCE.md`.

## The project

A paper and an interactive dashboard that collect the generative-AI policies computing departments and courses at North American universities have published, and reconcile them into a shared set of guidelines. The method follows Amershi et al., "Guidelines for Human-AI Interaction" (CHI 2019): gather many sources, keep their statements verbatim, cluster similar statements, name each cluster, and organize the clusters several ways (by theme, by course-lifecycle phase, by who the rule addresses). The use case is an institution writing or revising its own AI policy.

PI: Rudrajit Choudhury (Oregon State University).

## Scope decisions (from the PI)

- **Geography:** USA and Canada. Mexico was dropped on 2026-10-05.
- **Units:** anything computer-science-like, including CS, CSE, EECS, ECE (computing courses), information science, iSchools, informatics, AI departments, data science, software engineering, and computing colleges.
- **Levels** (`university-general` added 2026-10-05 per the PI; see the note after this list):
  - `department`: a department, school or college policy.
  - `course`: a course syllabus policy, at most 3 per university, preferring intro courses.
  - `university-computing`: a university document, included only if it has a computing-specific section.
  - Fallback order per institution (PI, 2026-10-05): (1) CS → (2) CS-related unit (iSchool, informatics, AI, data science) → (3) `school-general` (e.g. College of Engineering) → (4) `university-general`. Only the best tier present is kept.
- **Content:** all AI-use provisions. That covers student use (code and writing), faculty and TA use (grading, feedback, materials), use categories or levels, disclosure, assessment, enforcement, rationale, and equity, privacy and IP. Writing-integrity rules are only one part.
- **Verbatim rule:** policy text is never paraphrased.
  - Each coded statement is an exact quote of at most 15 words, matched character for character against the live page by `tools/verify_build.py`.
  - Each quote carries a `#:~:text=start,end` link that opens the original page with the full passage highlighted.
  - Any text that isn't a quote, such as labels, summaries and pattern write-ups, is shown as analyst annotation.
  - The 15-word cap is a copyright constraint on republishing other institutions' text.

## Where things are

| Path | What it is |
|---|---|
| `tools/AGENT_BRIEF.md` | Research brief every corpus-building agent followed (inclusion rules, codebook, output schema, scope addenda). |
| `tools/fetch_text.py` | Fetches a page as exact plain text (HTML, PDF, .docx, Google Docs via txt export). |
| `tools/verify_build.py` | Merges `corpus/raw/*.json`, re-fetches every source (Wayback fallback for dead pages), verifies every quote, and writes `corpus/corpus.json` + `corpus/verification_report.md`. |
| `corpus/raw/*.json` | One file per search group (northeast, west, midwest, south, canada, liberal-arts, sweep, adjacent-units, and later pass2-*). |
| `corpus/browser_verified.json` | JavaScript-only pages verified in a real browser instead of by curl. |
| `corpus/corpus.json` | Merged, verified corpus that the dashboard reads. |
| `corpus/synthesis_base.json` | Themes, lifecycle phases, actors and codebook. |
| `corpus/synthesis.json` | Reconciled guidelines (clusters of statement IDs + exemplar), patterns, tensions and gaps (written after the corpus is complete). |
| `tools/reconcile.py` | Guideline definitions + rule-based assignment; applies `corpus/reconcile_overrides.json`; writes `corpus/synthesis.json` and `corpus/reconcile_review.md`. |
| `corpus/patterns.json`, `corpus/method.json` | Consensus, tension and gap write-ups (statement IDs as evidence) and the Method tab text. |
| `exports/*.csv` | Paper-ready tables (`tools/export_csv.py`). |
| `dashboard/template.html` | Dashboard source; `tools/build_dashboard.py` injects the data into `dashboard/index.html`. |

To rebuild from scratch:

```bash
python3 tools/verify_build.py && python3 tools/reconcile.py && python3 tools/export_csv.py && python3 tools/build_dashboard.py
```

## Status (update this section every time)

_Last updated: 2026-10-05 (end of session 1)_

- **Corpus complete for this round:** 554 documents from 408 institutions (USA 459 docs, Canada 95); 3346/3353 statements verified exact. The 7 unverified are SFU CMPT 120, which is unreachable and not archived.
- **Frames fully searched:**
  - Every Carnegie 2025 R1/R2 US university (326).
  - Every Universities Canada member with a computing degree (69 in frame).
  - Plus earlier passes covering liberal-arts colleges, HBCUs/MSIs, community colleges and other institutions.
  - Health-sciences-only institutions are out of frame.
- **Tiers:** 196 institutions at tier 1 (CS), 7 at tier 2 (CS-related unit), 3 at tier 3 (school/college), 202 at tier 4 (university-wide).
- **Reconciliation:** 57 guidelines; every statement reviewed (874 manual overrides). Patterns: 6 consensus, 11 tensions, 6 gaps.
- **Dashboard:** https://claude.ai/artifact/5aatUzCWHgdcziLS3sGtb9 (version 3), published from `dashboard/index.html`; republish the same file to keep the URL. Custom groupings live in its database collection `schemes`.
- **Probability scoring:** dropped by the PI on 2026-10-05; `tools/jev_score.py` is kept for the record only.
- **Rebuild pipeline after any new data:**

  ```bash
  python3 tools/verify_build.py && python3 tools/reconcile.py && python3 tools/export_csv.py && python3 tools/build_dashboard.py
  ```

  Then review the new `[rule]` statements in `corpus/reconcile_review.md`, add overrides to `corpus/reconcile_overrides.json`, and republish.
- **Possible next steps:**
  1. Second human coder on a sample, for inter-rater reliability.
  2. Retrieve the Montana CSCI 150 and FAU COP 3035C syllabi by hand (each would move its university to tier 1).
  3. Draft the paper sections from `exports/*.csv` and `corpus/patterns.json`.

## v2 (current work, started 2026-10-25): read this before continuing

**PI decisions (confirmed):**
- **Scope:** US only. ~342 institutions in `v2/queue.json`.
- **Layers per university**, kept separate:
  - `university`: always collected.
  - `school`: college, e.g. engineering.
  - `computing`: every CS unit plus CS-related units (informatics, iSchool, AI, data science, combined units like UCI ICS).
  - `course`: an add-on layer; **deferred for now (PI 2026-10-25)**.
- **Coding:** every policy in every document is coded **rationale-first** (TACT style: `why` before codes, `stance_why` per document). Each policy is a normalized statement plus a verbatim anchor of ≤15 words shown beside it, plus a highlight link. If the anchor alone states the policy, `policy` is null. Never invent policies.
- **Stance columns:** prohibit · restrict · permit · encourage · require · delegates.
- **Matrix:** two views, full actor › phase × stance, and actor × phase.
- **Policy-label builder:** a checklist that produces a profile plus similar universities.
- **Delivery:** a private GitHub repo under rudrajit1729 (ask the PI before pushing; render locally first) plus the claude.ai Artifact site (a standalone HTML app). The living Excel file is `v2/exports/atlas_v2.xlsx`, rebuilt after every university.
- **Autonomy (PI 2026-10-25):** Claude judges document quality, then codes, then runs the audit without asking. Surface only decisions that are genuinely the PI's, plus the 40% usage notification.
- **Run setup (PI 2026-10-25, latest):**
  - Use a cheaper model (Sonnet 5.5) for agents.
  - Run in batches.
  - **Collect documents first** (without the course layer), show the PI which documents are good, then code.
  - **Coding design (final, 2026-10-25):** Coder A ∥ Coder B (independent, rationale-first) → Reconciler, all on Sonnet. The PI left the choice to Claude. Reasons: each single coder missed 5–11% of the policies the other found in the dry run, and two independent codings are needed to report Krippendorff's α. A third coder is not needed because agreement was already 0.87–0.97.
- **Budget:** Max $200 plan. The weekly all-models limit resets Sat Oct 31 (shown as 2026-10-31T20:00Z). Check with `mcp__ccd_session_mgmt__get_usage` between batches and **stop new batches at 40% weekly use and send the PI a notification (PI, 2026-10-25)**. Usage was 3% when v2 started.

**Files:**
- `v2/CODEBOOK.md`, `v2/COLLECT.md`, `v2/CODE.md`, `v2/RECONCILE.md`, `v2/WORKER.md`: briefs.
- `v2/policy_types_v0.json`: P01–P57, seeded from the v1 groups. The closed list `v2/policy_types.json` is still to be written after the dry run.
- Excel (D31): ORIGINAL WORDING columns are script-cut and verified; columns are labeled "AI rationale" and "AI-normalized policy statement", and an "AI coding provenance" column gives the model, roles and audit status (PI preferred neutral wording over "AI-generated"); failures go to the Unverified sheet.
- `v2/tools/validate_inst.py` (provenance check; `--no-why` for the dry run), `build_v2.py` (site data), `export_xlsx.py`, `run_v2.py` (resumable driver).
- `v2/site/index.html`: the site. Serve it with launch config `atlas-v2` on port 8792.

**Dry run status (6 universities: oregon-state, uiuc, georgia-tech, uc-irvine, pomona, howard):**
- Collect: done (44 documents).
- Coder A: done.
- Coder B: done except oregon-state and howard.
- Reconciled: georgia-tech and uc-irvine (agreement 0.87–0.97 per field, stance 1.0). uiuc and pomona are reconciling.
- Proposed new types to decide:
  - Human-written course communication (kept by the reconciler).
  - Instructor AI for feedback/grading.
  - Instructor AI familiarity.
  - Defer to external venue/sponsor rules.
  - Student right to respond to AI allegations.
  - Prescribed AI interaction protocol.
  - Decline to police AI use.
  - Instructor use of AI for teaching work.

**Decisions register:** add every study-design decision to `v2/decisions.json` (id, date, section, by, decision, rationale). Run `python3 v2/tools/render_decisions.py`, which writes `v2/METHODS_DECISIONS.md`; the Excel export adds a Decisions sheet. Write it methods-ready for the paper.
**Coding method (PI, 2026-10-25):** code each policy once with every reusable tag (actor, phase, modality, unit_stance, policy_type, topics, plus the document's layer and stance). There is one primary policy_type per policy, justified in its `why`. Grouping uses constant comparison; codebook changes go in `v2/CODEBOOK_MEMO.md`.

**Screening tool:** run `python3 v2/tools/screen_docs.py` after each collection batch. Review every 'review' document and add a manual decision with its reason to `v2/screening_decisions.json`. Only documents marked include get coded. Rules are D30 in decisions.json.
**Document screening (PI, 2026-10-25):** a deterministic script checks every collected document against the inclusion heuristics (AI policy text present, layer valid, not news/workshop/link list, not a duplicate or superseded, enough substance). Its result is cross-checked against the collector's quality label, Claude decides every flagged document, and decisions go to `v2/screening_log.json`. Every document that passes is coded exhaustively.
**Audit adversary (PI, 2026-10-25):** in the Opus audit, GPT (via the Codex MCP, `mcp__codex__codex_ask` or `codex_review`) critiques Opus's proposed corrections (TACT-Full adversary). Opus answers accept / partly accept / reject with a reason, and the exchange goes to `v2/audit/critique_log.jsonl`. This sends coded rows (anchors, tags, rationales) of public documents to OpenAI; the PI was told and may opt out.
**Final stage (PI suggestion, 2026-10-25): Opus corpus audit.** After all Sonnet coding and reconciliation, Opus agents audit the whole corpus by policy type: all units of a type across all universities. They verify every tag against the anchor and the type definition, move misplaced units, and propose merges or splits. Corrections go to `v2/audit/overrides.json` with a rationale for each; the coded inst files are never edited. `build_v2.py` and `export_xlsx.py` apply the overrides at build time.

**Progress as of 2026-10-25 21:30:**
- Dry run is done; its files are in v2/dryrun (calibration only).
- The codebook is closed (P01–P65).
- Collection: complete (342 universities, 793 documents).
- Screening: complete (752 include / 19 exclude / 22 deferred).
- Coding: 104/342 done after batch 2; weekly usage 14%; projected about 32% after coding (audit must fit under 40%). Batch 3 (70) launched 23:50.
- Weekly usage: 7% after collection.
- To resume, re-run the driver with the same commands; it is idempotent:
  - `python3 v2/tools/run_v2.py --phase collect --model sonnet --workers 6 --chunk 6 --limit 170`
  - `python3 v2/tools/screen_docs.py` (review new 'review' documents)
  - `python3 v2/tools/run_v2.py --phase code --model sonnet --workers 4 --chunk 3 --limit N`
  - Check `get_usage` between batches and stop at 40%.

**Next:**
1. Finish the dry run.
2. Write the closed `policy_types.json`.
3. Run the collection phase (no courses) in batches with Sonnet.
4. Produce a document review for the PI.
5. Run coder plus reviewer in batches.
6. Build the site, Excel and repo; ask the PI before any GitHub push.

## Open decisions for the PI

- ~~Harvey Mudd pilot~~: resolved 2026-10-05; included as an influential source (see PROVENANCE).
- ~~Hawaii ICS 314~~: excluded 2026-10-05 (no AI-use rules).

## Working agreement (this project only)

The PI asked Claude to act as chief of staff: run the work end to end and come back with finished results. Keep `context.md` and `PROVENANCE.md` current after every meaningful step.

### 2026-10-26 PI feedback: definitions and open-ended themes (D33–D35)
- `v2/DEFINITIONS.md` defines every term ("policy unit" = one coded statement = one data point). It is also the Definitions sheet in the Excel file.
- The type list is provisional and grows with the data. After every batch, read **all** UNCOVERED notes and fit notes, add a type for any pattern seen at 3 or more universities, and log smaller patterns as candidates in CODEBOOK_MEMO. P66–P77 were added at 119 universities.
- After coding and before the audit, run the theme review (D34): read every member of every type, split, merge or create types, reassign earlier units, and build themes bottom-up. Log every change as an override.
- Export columns are now looked up by header name (TYPE_COL, VER_COL); a hard-coded index briefly zeroed out the Policies sheet.

### Course layer: PI approved systematic collection (D41); coding deferred
PI's idea: we go top-down first (university → school → department). Where the department level is sparse, build a CS-level picture bottom-up from courses. It must be systematic, because one or two courses do not represent a university. Proposed design, to be decided once the full computing recheck reports how many universities have a computing-unit policy (25/342 at the start of the full recheck):
1. A fixed course frame at every university: CS1, CS2 or data structures, one required mid-level core course, and software engineering or capstone, each identified from the catalog.
2. The most recent offering; the coordinator's syllabus, or all sections if they differ.
3. Syllabi that are not public are logged as missing data, and coverage is reported as a limitation.
4. A department profile only when at least 3 of the 4 core courses are found; otherwise "insufficient".
5. A pilot on about 20 universities to measure syllabus availability before committing.

### Study framing (PI, 2026-10-26, D42)
- Part 1: general US higher-education AI policy, top-down (university, school and computing layers).
- Part 2: computing education, bottom-up from the fixed course frame (D41), contrasted with Part 1 (parallels and divergences). CS-specific school and department policies form the layer between the two.
- Course passages will later be coded with the same codebook and tags so the contrast holds.
- Analysis plan (D43): separate guideline syntheses for higher ed and CS, then compare; either outcome is a finding.

## Status 2026-10-26 10:25 (paused at the 40% weekly cap)
- Coding: 314/342 universities have coded files (312 with documents; oklahoma-state and michigan-dearborn are empty because Cloudflare blocked collection and need browser re-collection). 22,260 reconciled policies. 28 not yet coded: `v2/run/todo_after_reset.txt`.
- Type list: 127 types after between-batch review 3 (D44); 45 candidates.
- Course layer: 64/342 collected; 11 files fail the validator and will be redone.
- After the weekly reset (Sat 2026-10-31 20:00Z): finish the 28, re-collect the 2 Cloudflare universities, resume course collection, then the theme review (D34/D37/D38), α, audit.

## Status 2026-10-26 ~19:00Z
- Coding complete: 342/342 universities, 24,536 statements.
- Theme review complete (D46/D47): 138 types in use, content-only names, 12 new types, 15 themes; per-statement binding and about-AI tags. Files: v2/theme_review/, v2/policy_types_v3.json; Excel columns "final type", "binding", "final theme"; Themes sheet.
- Course layer collection continuing (cap: stop at 58% weekly; PI cap 60%).
- Next: Krippendorff's alpha (coder A vs B; also theme-review moves as a stability measure), Opus audit + Codex critique, site build (render locally first), course-passage coding, higher-ed vs CS guideline synthesis (D43).

## Status 2026-10-26 evening (hand-off)
- Next chat starts from `v2/HANDOFF_policy_synthesis.md`: add the "policy position" level under each type (distinct policies + supporting original wordings), pilot P31/P10/P30, then app + Excel.
- Running at hand-off: fresh Opus audit (v2/audit2), C5/C6 Sonnet collection; wrap up with `python3 v2/tools/finalize_codex.py`. GPT critique batch 5 on Codex at 21:55 PT.

**Policy positions (D59, 2026-10-27):** under each type, `v2/positions/positions.json` lists its distinct policies (who is asked to do what, and when), each with an AI-written policy sentence, supporting statement ids and 3 verified original wordings. Rebuild: `python3 v2/tools/positions.py run` (skips finished types) then `build_v2.py` and `export_xlsx.py`. Shown in the app's Policies cards, matrix drawer, Draft examples, and the Excel Positions sheet.

**Policies, final (D62-D65, 2026-11-02):** `v2/positions/final.json` is the source the app, both Excel files and the findings page read: 1,062 institutional policies (merged across types; stage or background; actor groups students / instructors / staff and administrators / everyone) and 317 course policies. Rebuild order: `python3 v2/tools/synthesis.py apply`, then `build_v2.py`, `export_xlsx.py`, `build_course_xlsx.py`, `build_site_data.py`, `build_findings_page.py`. The headless `claude` CLI login expired on 2026-11-02 (run `claude auth login` in a terminal to restore background workers); until then `SYN_MODE=files` writes prompts for in-session subagents.

**Website (D68, 2026-11-02):** the atlas is the local site `v2/site/index.html` (double-click `Open AI Policy Atlas.command`, or `python3 -m http.server 8792 --directory v2/site`). Policy set = rules + recommendations + facts (675 institutional, 229 course); other coded text on its own page. Rebuild after any data change: `synthesis.py apply`, `build_v2.py`, `export_site_csv.py`, `export_xlsx.py`, `build_course_xlsx.py`, `build_site_data.py`, `build_findings_page.py`, then `build_report.py` (Report tab, printable HTML and Word, D70).
