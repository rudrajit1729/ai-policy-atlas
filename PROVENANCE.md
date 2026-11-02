# Provenance log

Append-only record of how the corpus and synthesis were produced: who or what did each step, with which inputs, and what came out. Newest entries at the bottom.

## 2026-10-05: Pass 1 corpus collection

- **Setup.** Claude (Opus 5.5, Claude Code desktop) created `tools/fetch_text.py`, the verbatim fetcher (curl + BeautifulSoup/pypdf). Fetched text is cached in the session scratchpad and is not part of the corpus.
- **Brief.** Claude wrote `tools/AGENT_BRIEF.md`, covering inclusion criteria, the excerpt rules (≤15 words, contiguous, exact), the starter codebook (22 codes), phase and actor codes, and the output schema.
- **Search agents.** Seven Claude subagents were launched in parallel: northeast, west, midwest, south, canada-mexico, liberal-arts and sweep. Each had a named list of institutions to check.
- **PI scope changes during the run.** Each one was appended to the brief and sent to the running agents.
  1. Capture all AI-use provisions: faculty and TA use, use categories and levels, disclosure, and writing as well as code (the `use-categories-levels`, `writing-assistance`, `faculty-grading-feedback`, `faculty-course-materials` and `research-use` codes were added).
  2. Include computing-adjacent units (iSchools, information science, informatics, AI, data science, software engineering). An eighth agent, `adjacent-units`, was launched for these.
  3. Drop Mexico. `verify_build.py` also filters out any non-USA/Canada document.
- **Search cap hit.** The session's web-search cap (200 calls, shared by all agents) ran out early. Agents switched to browsing department and course sites directly and marked those schools "browse-only".
- **Agent results** (each agent validated its own JSON and exact-substring matches before writing):

  | Group | Documents | Statements | Institutions |
  |---|---|---|---|
  | south | 18 | 101 | 12 |
  | midwest | 13 | | 7 of 18 |
  | liberal-arts | 22 | 127 | 14 |
  | sweep | 12 | | 11 |
  | northeast | 28 | 169 | 20 |
  | canada | 18 | 111 | 8 |

  `canada-mexico.json` was renamed to `canada.json`.
- **Verification** (`tools/verify_build.py`): every source was re-fetched independently, every quote located, its exact page characters substituted (curly quotes and so on), and a text-fragment deep link built. Fixes along the way:
  - Google Docs were read through their `export?format=txt` endpoint (Bucknell CSCI 203, Purdue CS 252).
  - The .docx syllabus (UF COP 3530) was parsed with python-docx.
  - The Williams CS 334 URL was moved from `dept.cs.williams.edu` (TLS certificate name mismatch) to `www.cs.williams.edu` (same page, valid certificate).
  - ASU CSE 110 is JavaScript-rendered. All 6 quotes and 12 link anchors were checked against the rendered page in Claude's built-in browser and recorded in `corpus/browser_verified.json`.
  - UBC CPSC 110 refuses live connections, so it was verified against the Internet Archive snapshot. The dashboard links there.
  - **Result:** 111 documents from 71 institutions, 675/675 statements verified exact, 0 over 15 words.
- **Global setting.** At the PI's request, Claude added `"env": {"CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION": "1000"}` to `~/.claude/settings.json` for future sessions.

## 2026-10-05: Pass 1 complete (west and adjacent-units merged)

- **West** (17 documents, 10 universities, including 3 Oregon State documents) and **adjacent-units** (18 documents, 13 iSchool, data-science and ML units) were merged.
- **Verifier fixes:**
  - Published Google Docs (`/d/e/.../pub`) are now fetched as HTML. The earlier rewrite broke UW Allen School's shared policy.
  - Text-fragment links now start the highlight at the quote itself whenever the agent's `frag_start` words also occur in an earlier sentence. This fixes over-long highlights flagged by the west agent.
- **Result:** 146 documents from 83 institutions; 902/902 statements verified exact.

## 2026-10-05: Pass 2 launched

- `tools/make_pass2_targets.py` wrote `corpus/pass2_targets.json` (143 institutions or units to re-search: browse-only or none-found in pass 1; 94 new institutions: more R1/R2s, Canadian universities, HBCUs/MSIs, community colleges) and `corpus/known_urls.txt`.
- Pass 2 runs as a separate headless Claude Code session (`claude -p`, with WebSearch, WebFetch, file tools, python3 and curl allowed) following `tools/PASS2_BRIEF.md`. It picks up the 1000-search setting.
- Output goes to `corpus/raw/pass2-*.json` and the run log to `logs/pass2_run.json`.

## 2026-10-05: Reconciliation (on the 902 pass-1 statements)

- **Guidelines.** Claude acted as reconciler and defined 55 guidelines in 12 themes (`tools/reconcile.py`). Each has an analyst-written label, a theme, a lifecycle phase, an addressee, and one verbatim exemplar statement.
- **First assignment.** An explicit rule over each statement's primary code and wording (`rule()` in `tools/reconcile.py`).
- **Manual review.** Claude read every cluster in `corpus/reconcile_review.md` and moved 203 misassigned statements. Each move is recorded in `corpus/reconcile_overrides.json` (statement id → guideline id).
- **Label changes from the review:**
  - G16 became "Allow AI-generated code under stated conditions".
  - G19 became "Do not have AI produce the work you submit".
- **Cross-cutting analysis** (`corpus/patterns.json`): 6 consensus patterns, 10 tensions (each with two sides quoted verbatim) and 6 gaps.
- **Method text:** `corpus/method.json`.
- **Exports:** `exports/documents.csv`, `exports/statements.csv` (one row per verbatim statement, with its guideline) and `exports/searched_institutions.csv`.
- **Dashboard:** built by `tools/build_dashboard.py`. A local preview showed no console errors, and custom groupings (create, move, save) were exercised. The test grouping was then cleared.

## 2026-10-05: Pass 2 merged and verified

- **Pass 2 results** (headless session, 6 subagents, 1000-search budget; see `corpus/pass2_summary.md`): +109 documents, +54 institutions, +515 statements. Totals: 255 documents, 137 institutions, 1417 statements.
- **Fetcher fixes:**
  - `fetch_text.py` no longer strips `<form>`, `<header>`, `<nav>` or `<footer>` content. ÉTS and UVic put their whole course plan inside `<form>`, and ÉTS puts its policy inside a header `<option>`. Verification only needs the quote to be present, so the extra page chrome is harmless.
  - `verify_build.py --refetch id1,id2` bypasses the cache for the named documents.
- **Verification:** 1410/1417 statements verified exact. The 7 unverified statements all belong to SFU CMPT 120 (opencoursehub.cs.sfu.ca times out over HTTPS and has no Internet Archive snapshot). They are kept but flagged "unverified" on the dashboard.
- **French:** documents are auto-tagged `language: fr` (8 Québec documents) and shown with a "French" tag. Quotes stay in the original French.
- **Reconciliation of the 515 new statements:** each was reviewed by guideline cluster, adding 157 overrides (360 in total).

## 2026-10-05: PI scope change, university-wide fallback (scope addendum 3)

- The PI asked to include a university's general AI policy when it has no computing-specific one, and to keep searching until coverage is complete. If a session's quota runs out, the search continues in a new session.
- Added level `university-general`. `verify_build.py` drops it for any institution that also has a computing document.
- **Pass 3** is three parallel headless sessions (`tools/PASS3_BRIEF.md`), each with its own 1000-search budget:
  - **Track U:** 128 institutions with no computing document get their university-wide policy; previously blocked sources are retried.
  - **Track R:** every remaining Carnegie R1/R2 institution in the US (the frame is saved to `corpus/frame_us_r1r2.json`).
  - **Track C:** every remaining Canadian university with a computing degree (`corpus/frame_canada.json`).

## 2026-10-05: Jev as probabilistic second coder (PI request)

- **What it scores** (`tools/jev_score.py`), using TypeSafe Jev (pinned `jev-1.13.0`):
  - Stage A: for each statement, a Choice over the 55 guidelines plus "none_fit". Option descriptions come from `corpus/guideline_defs.json`.
  - Stage B: for each guideline, a Choice over the groups of each built-in grouping (theme, phase, actor).
- **Order bias:** every Choice is asked in forward and reversed option order within the same request, and the two distributions are averaged. The docs note that Jev can lean toward the first option.
- **Outputs:**
  - `corpus/jev_scores.json`: per-statement full distributions and per-guideline group distributions, plus agreement, Cohen's κ and order stability.
  - `corpus/jev_disagreements.md`: analyst-vs-Jev disagreements for review.
  - `corpus/jev_cache.jsonl`: every API response, so re-runs only pay for new statements.
- **Dashboard:**
  - A "Jev p" chip on every statement.
  - A "Jev p this guideline belongs in this group" line on every guideline card.
  - A "Jev vs analyst" filter.
  - A second-coder paragraph on the Method tab.
- **Status:** BLOCKED on a TypeSafe API key. None is set on this machine, and the PI needs to create one at console.typesafe.ai.

## 2026-10-05: Dashboard published (version 1, pass-2 corpus)

- **Artifact:** https://claude.ai/artifact/5aatUzCWHgdcziLS3sGtb9 (private to the PI until shared).
- **Capabilities:** `db` (custom groupings saved in collection `schemes`, shared with collaborators) and `user`.
- **Check:** the `schemes` collection is empty after publish, as expected. A local preview showed no console errors.
- **Next:** republish to the same file path after pass 3 and the Jev scoring.

## 2026-10-05: Pass 3 relaunch

- **What went wrong on the first launch:** all three tracks dispatched their subagents in the background. Headless `claude -p` stops waiting for background tasks after 600 s and terminates them, so only `pass3-u-2.json` was written.
- **What survived:** both sampling frames were saved. `corpus/frame_us_r1r2.json` lists 326 institutions (187 R1, 139 R2, from the Wikipedia table of the Carnegie 2025 classification; Carnegie's own site blocked the fetch). `corpus/frame_canada.json` lists the 97 Universities Canada members, 74 of which offer computing degrees.
- **The fix:** `tools/run_track.sh` sets `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0`. The brief now requires foreground (parallel) subagents and skipping institutions already recorded in existing `pass3-*` files. The runner retries up to 3 times on API or network errors; one relaunch hit `ENOTFOUND`.
- **Running now:** all three tracks, in parallel.

## 2026-10-05: Probability scoring dropped

- Jev became inaccessible. Asked about alternatives (Codex as second coder, repeated Claude sampling, an embedding classifier), the PI said probabilities are not needed.
- `tools/jev_score.py` and `corpus/guideline_defs.json` are kept for the record but not used.
- The dashboard's Jev features render nothing when no scores exist, so the published page is unchanged.

## 2026-10-05: Harvey Mudd AI Use Levels pilot added (PI decision)

- The PI approved including Harvey Mudd College's "Pilot Program: HMC AI-Use Course Policies (DRAFT)" (Google Doc). It is college-wide, not computing-specific, but Pomona College's CS AI Policy Tier System is modeled on it.
- Added in `corpus/raw/manual-additions.json` as `university-general` with `keep_with_computing: true`. That flag exempts it from the rule that drops university-wide documents for institutions that also have a computing document (HMC has CS 70).
- 8 excerpts were chosen by Claude from the fetched text; all 8 verified exact. One override: e7 ("Normalize struggle…") → G35.

## 2026-10-05: Hawaii ICS 314 excluded (PI decision)

- Removed via the new `corpus/exclude_docs.json`, which `verify_build.py` applies and records under `excluded`.
- Reason: the document frames AI as a course topic and learning outcome only, with no AI-use rules.
- Hawaii stays in the corpus through ICS 311.

## 2026-10-05: Fallback order per institution (scope addendum 4, PI)

- **Order:** (1) CS department or course policy; (2) CS-related unit (iSchool, informatics, AI, data science, software engineering; e.g. UCI ICS); (3) school or college policy covering computing (new level `school-general`); (4) university-wide (`university-general`).
- **Enforcement:** `verify_build.py` keeps only the best tier present per institution. The HMC pilot is exempt via `keep_with_computing`.
- **Running sessions:** the order was appended to `AGENT_BRIEF.md` and sent to the three running pass-3 sessions.
- **Planned after pass 3:** a check of every institution whose best tier is 4, to confirm that no tier-2 or tier-3 document exists.
- **Corpus at this point** (pass-3 files partly in): 330 documents from 207 institutions; 1915/1922 statements verified exact.

## 2026-10-05: Source tiers shown on the dashboard (PI request)

- `verify_build.py` assigns each document a `tier`:
  - 1: CS, including any unit named computer or computing, EECS, CSE, and `university-computing` documents.
  - 2: CS-related unit (information, informatics, data science, AI, iSchool, Heinz).
  - 3: `school-general`.
  - 4: `university-general`.
- **Interpretation recorded:** tiers 1 and 2 are kept together, because the PI earlier put all CS-like units in scope. Tiers 3 and 4 are fallbacks only.
- **Dashboard:** the Corpus tab has a "Source tiers" panel with institution counts per tier, and a tier label on every document row. The Method tab's scope section lists the four tiers.
- **Split at this point:** 148 institutions at tier 1, 3 at tier 2, 86 at tier 4. Tier 3 is still empty; the post-pass-3 check will look for school- or college-level policies for the tier-4 institutions.
- **Version 2 published** to the same Artifact URL. It includes the source-tier panel and the partially merged pass-3 data: 363 documents, 237 institutions, 2114 statements. Pass-3 statements are rule-assigned only; manual review is still pending.

## 2026-10-05: Track C (Canada) complete

- **Results:** 37 documents in `corpus/raw/pass3-c-1..4.json` (tier 1: 15; tier 3: 1; tier 4: 21). All 69 in-frame Canadian institutions have been searched; UNFINISHED: none. See `corpus/pass3_c_summary.md`.
- **Claude's decisions on the flags** (chief-of-staff mandate):
  - Capilano is kept in the frame (BSc with a Computational Sciences concentration).
  - Brandon's thin tier-3 document is kept, per the first-tier-that-exists rule.
  - Athabasca's provost post is kept as official interim policy, not as news coverage.

## 2026-10-05: Track R (US R1/R2) complete

- **Results:** 134 documents in `corpus/raw/pass3-r-1..6.json` (tier 1: 24; tier 2: 4; tier 4: 106). All 326 frame institutions have been searched; UNFINISHED: none. See `corpus/pass3_r_summary.md`.
- **Claude's decisions** (chief-of-staff mandate):
  - **Health-sciences-only institutions with no computing programs are out of frame** (UCSF, LSU Health Sciences, Weill Cornell, Loma Linda, UMass Chan, UNMC, Icahn). This mirrors the Canadian frame rule ("offers a computing degree"). Applied at the final merge.
  - **UNCG ISM 671 stays tier 2** (information systems counts as a CS-related unit).
  - **UMKC's provost page stays tier 1** (`university-computing`).
  - **Thin or library-hosted tier-4 sources are kept** as the official fallback.
- **Not retrievable automatically** (403 or server error): Montana CSCI 150 and FAU COP 3035C. If either is added, that university moves to tier 1.

## 2026-10-05: Track U complete; final merge (passes 1–3)

- **Track U:** 136 documents across 119 institutions (`pass3-u-2`, `-7..-13`; tier 1: 32, tier 2: 2, tier 3: 2, tier 4: 83). UNFINISHED: none.
- **Claude's decisions on Track U's flags:**
  - UCSC, UAB, Regina and Vanderbilt stay `university-computing`.
  - Georgia State CIS 3001 stays tier 2.
  - Utah ECE counts as tier 1.
  - Thin sources (Brock, Hampton, Stevens) are kept.
- **Out-of-frame rule:** institutions with no computing degree programs are dropped by name pattern via `corpus/out_of_frame.json` (UCSF, LSU Health, Weill Cornell, Loma Linda, UMass Chan, UNMC, Icahn). This removed 8 documents.
- **Fetcher routes added:**
  - Simple Syllabus pages are read through the public `api2/doc-full-page-get?code=` JSON.
  - Canvas pages through `/api/v1/courses/<id>/pages/<slug>`.
  - Google Drive viewer links through `uc?export=download`.
  - JSON responses are flattened to text.
- **Verification:** 554 documents from 408 institutions; 3346/3353 statements verified exact. The 7 exceptions are still SFU CMPT 120.
- **Tiers:** 196 institutions at tier 1, 7 at tier 2, 3 at tier 3, 202 at tier 4. 459 documents are from the USA and 95 from Canada.
- **Reconciliation:** all 1931 pass-3 statements were reviewed, adding 513 overrides (874 in total). Two guidelines were added:
  - G56 "Set an institution-wide framework for responsible AI use".
  - G57 "Talk with the student before escalating suspected misuse".
  - Most new detector statements were skeptical, so they moved from G40 to G39.
- **New tension pattern:** "Universities delegate; computing units decide". Tier-4 documents are 54% instructor-discretion and 26% tiered; tier-1 documents are 41% permit-with-conditions and 39% prohibit-by-default. G09 (syllabus statement) appears at 61% of tier-4 institutions vs 8% of tier-1; G19 (no AI-produced work) at 51% of tier-1 vs 12% of tier-4.
- **Dashboard version 3** published to https://claude.ai/artifact/5aatUzCWHgdcziLS3sGtb9. All tabs render in about 35 ms with no console errors.

## 2026-10-25: PI re-scope to v2 (decisions confirmed with the PI)

- **Scope:** US only; Canada is dropped. Frame: all ~340 US institutions found so far (R1/R2 plus liberal-arts colleges, HBCUs/MSIs and community colleges).
- **Unit of analysis:** the university. Every layer that exists is kept, and each is labeled:
  - university-wide policy, always collected;
  - school or college policy;
  - computing unit (CS/CSE/EECS/ECE; otherwise a CS-related unit such as an iSchool, informatics, AI, data science, or a combined unit like UCI ICS);
  - course or instructor policies, as an add-on layer that never defines a university on its own.
- **Coding depth:** every document is coded completely. Every policy it states becomes its own entry, written as a normalized statement kept as close to the original wording as possible, plus a short verbatim anchor (≤15 words) and a highlight link. These are policies, not new guidelines: identical or similar policies are grouped, never invented.
- **Analysis:**
  - a proper thematic analysis (codebook, themes, patterns);
  - an actor × lifecycle × document-stance matrix. Stance columns: Prohibit · Restrict (only with explicit permission) · Permit with conditions · Encourage · Require/integrate · Delegates to instructor;
  - a "nutrition label" builder (checklist → generated profile plus similar schools).
- **Delivery:** (superseded by D71) a private GitHub repo under rudrajit1729 (data, code, site, Excel workbook). The interactive site stays on the claude.ai Artifact link.
- **Versioning:** the v1 corpus and dashboard are kept as-is for the record. v2 lives in `v2/`.

## 2026-10-25: v2 dry run and full-run setup

- **TACT adaptation:** PI's TACT repository (`../AI-Council-Method/tact-release`).
  - Rationale-first coding: `why` per unit and `stance_why` per document, written before codes.
  - Closed codebook for the full run, with UNCOVERED plus a note.
  - Reconciler writes `resolution_why`.
  - Deterministic provenance check (`v2/tools/validate_inst.py`).
  - Independent coders that never see each other's output.
  - All agents are Claude instances (the PI asked for Claude sub-instances), not three model families.
- **Dry run:** 6 universities (Oregon State, UIUC, Georgia Tech, UC Irvine, Pomona, Howard), 44 documents.
  - Collector: one agent.
  - Coders A and B: three agents each, two universities per agent.
  - Reconcilers: three agents.
- **Network outage:** an `ENOTFOUND` outage at about 19:40 interrupted all running agents. They were resumed with their context; no saved file was lost.
- **Mid-run validator change:** the rationale requirement was added to the validator while dry-run coders were still working. Coder A2 then wrote post-hoc rationales (disclosed in its file notes). The dry run is calibration only, and running agents were told to validate with `--no-why`. All six universities will be recoded rationale-first in the full run.
- **Cost and time estimate given to the PI:**
  - About 420k tokens per university, so about 140–150M tokens for 342 universities.
  - About $600–$950 at Opus 5.5 API rates ($4/$20 per M), or about $350–$550 with Sonnet 5.5 coders. On a subscription this draws on plan usage limits instead.
  - 6–10 h wall-clock with about 15 parallel agents.
- **Full-run tooling (not launched yet):**
  - `v2/queue.json`: 342 US institutions (R1 178, R2 121, liberal-arts 14, other 29) with v1 seed URLs.
  - `v2/WORKER.md` and `v2/tools/run_v2.py`: resumable chunks of headless sessions, each running collector → coders A∥B → reconciler.
  - `v2/tools/export_xlsx.py`: the living Excel record `v2/exports/atlas_v2.xlsx`, rebuilt after every university.

## 2026-10-25: Run plan revised by the PI

- **Model:** Sonnet 5.5 for agents (`--model sonnet`).
- **Batches:** the driver defaults to one bounded batch per launch.
- **Collection before coding:** university, school and computing layers only. Course syllabi are deferred. Every collected document gets a quality label (good/thin/generic/superseded/partial) for the PI's review.
- **Coding:** one coder (rationale-first) plus one reviewer/reconciler per university.
- **Usage guard:** check `get_usage` after every batch. **Stop and notify the PI when weekly all-models usage reaches 40%.** Usage was 3% at the start.
- **Accidental launch:** a driver test briefly started the collect phase without a limit. It was killed within seconds and wrote no files. The default limit is now 36.
- **Calibration batch launched:** 12 universities, 3 sessions × 4.
- 2026-10-25: Added unit_stance and code-once/constant-comparison rules to CODEBOOK.md at the PI's request. Started CODEBOOK_MEMO.md.
- 2026-10-25: Final coding design: Coder A ∥ Coder B → Reconciler (Sonnet). The PI deferred the choice. Justified by dry-run coverage (one coder misses 5–11%) and the need for Krippendorff's α.
- 2026-10-25: Planned the final stage at the PI's suggestion: an Opus corpus audit by policy type. Overrides go to v2/audit/overrides.json with rationale; inst files are never edited.
- 2026-10-25 20:10: Calibration collection finished: 12 universities, 31 documents (19 good, 7 partial, 5 thin). Weekly usage still 3% (5-hour: 2%). Launched collection batch 2: 162 universities, 6 sessions × 6.
- 2026-10-25: The PI delegated document-quality screening, coding and the audit to Claude. Only genuine PI decisions get surfaced.
- 2026-10-25: Added inclusion-heuristic document screening (script + Claude decisions, logged to v2/screening_log.json) and a GPT/Codex adversary in the Opus audit (TACT-Full style). The PI was told that coded rows go to OpenAI.
- 2026-10-25: Created the decisions register (v2/decisions.json → METHODS_DECISIONS.md and an Excel Decisions sheet) at the PI's request, for writing the paper's methods.
- 2026-10-25: Screening run on 229 documents collected so far. 47 needed review: dry-run documents without quality labels, plus 3 edge cases (FIU code excluded: no AI text). Manual decisions are in v2/screening_decisions.json.
- 2026-10-25 21:25: Collection batch 2 done: 180/342 universities, 436 documents screened (396 include, 12 exclude, 22 deferred, 6 to review). Weekly usage 4%. Launched collection batch 3 (the remaining 162).
- 2026-10-25: Screening decisions written into the collect files; coders code only screen=include documents, and the validator enforces it. Dry-run reconciled files moved to v2/dryrun/inst (calibration only; recoded in the main run). Launching coding batch 1 (24 universities, Sonnet, Coder A ∥ B → Reconciler).
- 2026-10-25: Excel exporter made deterministic (D31): script-cut source passages and offsets, verified anchors, an Unverified sheet, flags for rationale quotes and paraphrase drift.
- 2026-10-25 22:00: Collection complete: 342 universities, 793 documents → 750 include, 21 exclude, 22 deferred after the manual review of 14 edge cases (Spanish AI terms added to the screener). Weekly usage 7%, 5-hour 19%.
  - Correction: the final screening tally after adding Spanish terms is 752 include / 19 exclude / 22 deferred.
- 2026-10-25 22:10: Coding batch 1 done: 24/24 universities reconciled and valid, 1603 policies. Weekly usage 7%→8% (about 1% per 24 universities; projected about 21% total). 5-hour window 23%. Next: coding batches of about 80, checking usage between them.
- 2026-10-25: At the PI's request, the Excel columns are relabeled AI-GENERATED and an 'AI PROVENANCE' column states which model and agent roles produced each row. It will be updated to mark audit status after the Opus + GPT audit.
- 2026-10-25: Excel labels changed to neutral wording at the PI's request: 'AI rationale', 'AI-normalized policy statement', 'AI coding provenance'.
- 2026-10-25 23:50: Coding batch 2 done: 104/342 reconciled, no failures. Weekly 14% (about 0.075% per university); projected about 32% after coding, close to the 40% cap once the audit is added. 5-hour window 52%. Launched batch 3 (70).
- 2026-10-25: UNCOVERED review at 104 universities: 175/6,449 units (2.7%), no cluster larger than 6. Type list stays closed for the rest of coding; clusters will be resolved at the audit (see CODEBOOK_MEMO).
- 2026-10-26 00:20: On PI feedback, withdrew D32 (closed type list). Added DEFINITIONS.md (D35); read all 204 UNCOVERED notes and added provisional types P66–P77 (D33), with candidates in CODEBOOK_MEMO; coders now write fit_note; full theme review planned after coding (D34). Batch 3 is still running, and its later chunks pick up the new types. Snapshot of the P01–P65 list: v2/policy_types_P01-P65_snapshot.json. Corpus so far: 119 universities, 260 documents, 7,485 policy units (university layer 7,166, school 129, computing 190).
- 2026-10-26 00:45: PI asked why the corpus is almost all university-wide. First collection: computing layer found at 24/342 universities (316 none-found), school layer at 17. v1 had only 19 department-level documents against 256 syllabi. Prepared the computing recheck (D36: RECHECK_COMPUTING.md, run_v2 --phase recheck, sample in recheck_sample.json); it launches after batch 3. Added candidate_types.json and an Excel TypeLog sheet (D37). Confirmed the theme review rereads every statement.
- 2026-10-26 07:05: Batch 3 done: 70/70 reconciled, 174/342 total. Weekly 20% (about 0.057% per university); 5-hour window 77%. Oklahoma State logged in failed.txt (Cloudflare blocks okstate.edu; re-collect with the browser later). Launched the computing recheck (26 universities).
- 2026-10-26 07:30: Review 2 (D38, D39): read all 124 UNCOVERED and 1,027 fit notes from batch 3. Added P78–P103 (103 types), broadened P65 and P69, promoted 3 candidates and added 11. Theme review will apply content-only type names and the ai_specific and binding tags.
- 2026-10-26 07:15: Recheck sample (D40): random 1/20 missed (SJSU iSchool). Purposive: Cornell College of Engineering missed (4 pages); UW added a research guideline and a CoE paragraph; CMU, Stanford, Michigan and Princeton confirmed none (course syllabi only). Merged 7 documents (all screened include); Cornell and SJSU moved to superseded for recoding. Correction: my 00:45 spot check matched files by prefix, so UW was wrongly listed as computing none-found. Scheduled after the 08:00Z reset: recheck all universities, merge, screen, coding batch 4 (60).
- 2026-10-26 07:20: PI: collect all CS-level documents (course layer stays deferred), start now, go faster. Recheck now runs with 10 workers and merges and screens after each chunk. Coding runs alongside on rechecked universities only (--require-recheck), not-yet-coded first.
- 2026-10-26 07:45: PI approved the systematic course frame (D41). Course syllabi are collected now (COURSE_COLLECT.md, validate_course.py, build_course_xlsx.py → v2/exports/course_layer.xlsx); coding deferred. Pilot of 20 launched.
- 2026-10-26 07:55: PI set the framing (D42): Part 1 = general higher-ed AI policy (top-down); Part 2 = CS bottom-up from the course frame, contrasted with Part 1.
- 2026-10-26 08:00: PI set the analysis plan (D43): synthesize guidelines separately for higher ed (top-down) and CS (course layer, bottom-up), then compare. Same level → one finding; differences → what each can learn from the other.
- 2026-10-26 08:20: Course pilot (20): 9/19 programs had 3+ public frame syllabi, but many 'public-no-ai' syllabi were pre-ChatGPT (2009–2022). Added statuses outdated and undated-only and a required year per syllabus (validator enforces); the 12 pilot files that fail are redone in the full run. Full course collection launched (6 workers). Usage: weekly 24%, 5-hour 20%.
- 2026-10-26 08:35: Full computing recheck done (342/342). 14 universities gained 20 documents; with the earlier sample, computing-unit policies are now at 30 universities (37 documents) and school policies at 19 (28 documents). 7 coded universities are queued for full recoding (Cornell, San José State, Arizona State, Colorado State, Northeastern, Rowan, Santa Clara). Manually included 3 review documents (Colorado State CS, Southern Connecticut CS, Iowa CLAS).
- 2026-10-26 08:40: Weekly usage rose to 28%. Paused course collection (64/342 collected, resumable) so coding finishes under the 40% cap; course collection resumes after coding or after the weekly reset. Launched coding batch 5 (the remaining 101, including 7 recodes) alongside batch 4.
- 2026-10-26 09:35: Batch 4 done (60/60). 282/342 coded. Weekly usage 37%. michigan-dearborn failed (Cloudflare blocked both university pages; 0 included docs) and joins oklahoma-state for browser re-collection. Batch 5 continues; checking usage every 10 universities, stop at 40%.
- 2026-10-26 09:55: Between-batch review 3 (D44): read all 230 UNCOVERED notes from 115 universities; added P104-P127 (24 types; snapshot v2/policy_types_P01-P103_snapshot.json); 20 new candidates; fit notes tallied by type for the theme review.
- 2026-10-26 10:25: Weekly usage reached 40% (the PI's cap). Stopped coding batch 5 and its workers. 314/342 universities coded (22,260 reconciled policies). The 28 not yet coded are listed in v2/run/todo_after_reset.txt; partial coder outputs for them stay in v2/run/coderA|B and are reused or overwritten on resume. Resume after the weekly reset (2026-10-31 20:00Z): python3 v2/tools/run_v2.py --phase code --model sonnet --workers 6 --chunk 3 --only $(cat v2/run/todo_after_reset.txt)
- 2026-10-26 17:35Z: PI raised the weekly cap to 60%. Resumed coding the 28 remaining universities (v2/run/todo_after_reset.txt).
- 2026-10-26 17:58Z: PI rule (D45): statements and documents not about AI are kept but not quoted and not counted. export_xlsx.py adds an 'about AI' column and a Screening sheet; 120 statements flagged by coder notes are marked now, the rest are judged in the theme review. A keyword test was rejected: 7,434 of 22,260 passages contain no AI word but most are AI rules in AI context.
- 2026-10-26 18:02Z: Re-collected oklahoma-state (3 ITLE pages) and michigan-dearborn (2 Digital Education pages) in the built-in browser; saved texts hash-verified against the browser's innerText; empty coded files moved to v2/run/superseded; recoding both.
- 2026-10-26 18:03Z: Weekly usage 41% (cap now 60%). Resumed course-layer collection (D41) alongside the last coding; files that fail validate_course.py are redone; stop at 58%.
- 2026-10-26 18:05Z: PI: statements not about AI move to their own NotAboutAI sheet (D45 applied in export_xlsx.py); Policies holds only AI statements. Sent the PI atlas_v2.xlsx (319 universities, 22,789 policies, 121 not about AI) and course_layer.xlsx (64 universities). 23 universities left to code; course layer 64/342.
- 2026-10-26 18:10Z: PI: run the theme review now. Wrote v2/THEME_REVIEW.md and v2/tools/theme_review.py (D46); built 201 packets covering 23,287 verified statements; piloting 2 packets (P24, UNCOVERED) before the full run.
- 2026-10-26: Course collector wrote v2/course/fordham.json, george-mason.json, george-washington.json (all validate OK). Fordham: C3 public-ai-policy (Fall 2025), C1/C2 outdated, C4 null (no SE or capstone required). George Mason: all four not-found, because cs.gmu.edu/media/syllabi URLs return 404 on fetch (site restructured; retry later). George Washington: C3 public-no-ai (Spring 2024), C2 undated-only, C1/C4 not-found (course pages 404 or absent).
- 2026-10-26 18:14Z: Theme-review pilot OK (P24 packet: 196/200 about AI, 181 keep, subgroups research disclosure / citation format / transparency principle; UNCOVERED packet: 81% now fit existing types P66-P127, 19% NEW labels). Launched the full review of the remaining 199 packets.
- 2026-10-26 18:33Z: CODING COMPLETE: 342/342 universities, 24,536 reconciled policies (151 marked not about AI). Built incremental theme-review packets for units coded after the review started.
- 2026-10-26 18:53Z: Theme review step 1 complete (24,536 units, 212 packets). Step 2 synthesis written to v2/theme_review/synthesis.json (content-only names for all types, 12 new types P128-P139, P18 retired, 120+ NEW labels mapped, 10 types sent to a split pass). Resolved: 20,286 keep, 3,062 moved, 817 NEW labels mapped, 371 stay UNCOVERED as candidates. Running split pass (23 packets).
- 2026-10-26 18:57Z: Theme review complete (D46/D47). Split pass 23 packets OK. Final: 24,536 statements; 23,994 about AI (542 not); binding: recommendation 32%, rule 28%, description 28%, template 12%; 138 types in use with content-only names; 12 new types P128-P139; P18 retired; 348 UNCOVERED; 15 themes T01-T15. Excel gains binding / final type / final theme columns and a Themes sheet; v2/policy_types_v3.json written.
- 2026-10-26: Course collector wrote v2/course/{michigan,michigan-dearborn,minnesota}.json, all validate OK. Texts saved as .cache/text/v2c-<slug>-<slot>.txt.
- 2026-10-26 19:47Z: Krippendorff's alpha computed (D48): actor .891, modality .881, policy_type .884, phase .816, unit_stance .723, doc stance .719; unitizing .684. Alpha sheet added to the Excel. Course layer: 341/342 collected and valid (558 syllabi, 338 AI passages verified, 55 universities with a 3-of-4 profile); southern-mississippi running.
- 2026-10-26 19:57Z: Course layer collection complete: 342/342.
- 2026-10-26 21:32Z: PI approved Opus audit + GPT critique (D50); course passages get their own codebook (D49); app after (D51). Wrote v2/STATUS_AND_FINDINGS.md, v2/AUDIT.md, v2/tools/audit.py; sampled 510 units (base 300 proportional by theme + oversamples). Piloting packet A01 with Opus.
- 2026-10-26 21:34Z: Audit pilot A01 OK (4/25 units with an error: 3 binding, 1 unit_stance). Launched the remaining 20 audit packets (Opus, 5 workers).
- 2026-10-26 21:36Z: Restructured v2/STATUS_AND_FINDINGS.md per PI (policies by level first, then method, findings, definitions, next); corrected course slots to 1,288 (322 universities with a CS program x 4). Built a private findings page (v2/site/findings.html from template + v2/site_data/summary.json via v2/tools/build_findings_page.py), published as a private artifact: https://claude.ai/artifact/N3FdLuxHJzbyk4uJnXstjc
- 2026-10-26 21:40Z: Opus audit done (D52): base n=300 unit error 21.7%; binding 11.0%, final_type 7.3%, others <=3%. Codex critique blocked (codex binary not installed; /Applications/ChatGPT.app has no codex). Launched targeted correction pass: 4,259 units, 22 packets (Sonnet). Backup: v2/theme_review/final_assignments_before_D52.json.
- 2026-10-26 21:48Z: Correction pass applied (D54): binding error 11.0% -> 5.3% on base sample. PI: add C5 AI/ML and C6 systems/security (D53); out-of-frame sheet (632 rows); 'new' chip replaced by an Origin column on the site. Piloting C5/C6 on 3 universities.
- 2026-10-26 21:51Z: C5/C6 pilot OK (oregon, kansas-state, williams-college; catalog-based, required/elective noted, C1-C4 untouched). Updated findings site (v2) with course-frame rationale, Origin column, audit table; STATUS_AND_FINDINGS.md updated. Launched C5/C6 collection for all universities (5 workers); stop at 58% weekly.
- 2026-10-26 21:57Z: Rebuilt the v2 prototype site data (build_v2.py) from the final codes (theme-review types/themes, binding, about-AI); matrix and policy-label tabs verified locally on full data (342 universities, 24,536 statements); site now hides not-about-AI statements. Not yet: document generator, course layer in the app, publish-size reduction (policies.json 15 MB).
- 2026-10-26 22:11Z: PI: matrix cells collapsible + linkable, chronological policies, fixed counts, readings on tables, course tab, then document generator; course coding in parallel. Wrote v2/tools/doc_dates.py (383/774 documents dated: 310 collector field, 73 document text; 391 undated). Course open coding (D49): v2/COURSE_CODE.md, v2/tools/course_code.py; coders may not read institutional type lists (tool allowlist restricts reads).
- 2026-10-26 22:16Z: App v1 local (D55): lifecycle ordering, collapsible + linkable matrix cells and policies, about-AI counts (23,960), readings on every view, CS courses tab, Draft a policy tab (template sentences + real examples, copy/download). Verified in local preview (port 8792): deep links, drawer, courses, draft; no console errors except optional patterns/method JSON.
- 2026-10-26 22:16Z: Weekly usage 57%: paused C5/C6 collection at 109/342 universities (resume after the 2026-10-31 reset with run_v2.py --phase course56) to keep budget for course coding.
- 2026-10-26 22:28Z: Course open coding complete: 1,765 statements from 386 passages (44% CS-specific), 1,478 distinct labels. Course codebook built inductively from the labels: v2/course_codebook.json (50 types CT01-CT50, 9 themes). Coding with it: coder A all, coder B 25% sample (441) for alpha.
- 2026-10-26 22:38Z: Course coding done (D56): course codebook alpha .878; comparison written (v2/exports/layer_comparison.json); course_layer.xlsx gains Course statements + Course codebook sheets; app CS courses tab shows course types and the comparison.
- 2026-10-26 23:52Z: Codex CLI found inside ChatGPT.app and smoke-tested (writes files, fetches). D57: Codex runs the GPT critique, a fresh 300-statement audit (v2/audit2, seed 20261027), and the remaining C5/C6 collection (213 universities).
- 2026-10-26 23:53Z: Consistency check: 23,960 statements about AI and 138 types agree across app, findings page, Excel; fixed per-university counts in the app to exclude not-about-AI; findings page rebuilt (course 386 passages) and republished (v3). Wrote v2/PAPER_OUTLINE.md (bullets). App open in the local preview (port 8792).
- 2026-10-26 23:57Z: Codex hit the PI's ChatGPT usage limit (resets 9:50 PM PT). Critique 4/5 batches done; fresh audit 0/12; C5/C6 8 universities done by Codex (205 remain). Jobs stopped; scheduled to resume at 21:55 PT.
- 2026-10-26 23:57Z: GPT critique (batches 1-4 of 5, 140 items): GPT agrees with Opus on 126 of 145 corrected fields (87%); sides with the original code on 18 (final_type 10/43, binding 4/55, policy 2/11, actor 1, modality 1); flags 1 of 11 Opus confirmations (about_ai). Summary: v2/audit/critique/summary_partial.json. Batch 5 resumes at 21:55 PT.
- 2026-10-27 00:21Z: PI review applied (D58): P140 split from P19; stance labels defined; require column dropped; statement + original wording display; lifecycle stages; richer matrix cells; draft as full document; outline revised. App, findings page (republished) and Excel rebuilt for consistency.
- 2026-10-27 00:24Z: PI asked for economy (remaining Codex work within 2-3% Claude usage). codex_run.py now stops cleanly at the ChatGPT usage limit; v2/tools/finalize_codex.py wraps up in one call. Status: critique 4/5, fresh audit 0/12, C5/C6 137/342 (205 left); Codex resumes 21:55 PT.
- 2026-10-27 00:38Z: PI: finish remaining work on Claude. Fresh audit (v2/audit2, 300 statements) by Claude Opus workers; C5/C6 (205 universities) by Sonnet workers; Codex keeps only critique batch 5 (cross-family) at 21:55 PT. One background chain, wrap-up by finalize_codex.py.
- 2026-10-27 03:50Z: Fresh Opus audit done (v2/audit2, 300 new statements, seed 20261027): any-field error 21.3%; binding 8.0%, final_type 6.0%, policy 5.0%, unit_stance 4.0%, about_ai 2.0%, others <=1%. So D54's 5.3% binding rate (re-measured on the corrected base sample) was optimistic; report 8.0% as the out-of-sample rate. C5/C6 course collection complete (342/342). Fixed finalize_codex.py auditor label (Claude Opus, not GPT) and ran it: course_layer.xlsx, app data and local findings page rebuilt (artifact not yet republished). Weekly usage 62% (over the PI's 60% cap): no new Claude batches until the PI says so. Critique batch 5 still waits for 21:55 PT on Codex; finalize_codex.py reruns after it.
- 2026-10-27 04:05Z: PI approved policy positions (D59): v2/tools/positions.py groups each type's statements by who is asked to do what, and when; Sonnet writes one AI-labelled policy sentence per position; ids kept; example wordings re-verified with export_xlsx._find. Pilot P31/P10/P30: 34 positions, 0 problems, no visible usage change (62%). Full run of the other 136 types launched; build_v2.py (positions.json + 'pos' per statement) and export_xlsx.py (Positions sheet + position columns in Policies) rebuild after it. App shows positions in Policies cards, matrix drawer and Draft examples.
- 2026-10-27 04:15Z: Policy positions complete (D59): 139 types, 1,562 positions; all 23,612 typed about-AI statements belong to exactly one position; 1,498 positions show 3 verified original wordings (14 have 1-2 because they hold 1-2 statements). 5 types first failed on lines placed twice; positions.py now keeps such a line in its best-matching position (logged as repaired). App (Policies cards, matrix drawer, Draft examples) and atlas_v2.xlsx (Positions sheet; position id + sentence columns in Policies) rebuilt and checked in the local preview. Weekly usage unchanged at 62%.
- 2026-10-27 04:57Z: Wrap-up done. Fresh Opus audit (300 new statements, after the D52 correction): binding 8.0%, final type 6.0%, policy 5.0%, unit stance 4.0%, about-AI 2.0%, modality 1.0%, actor 0.7%, phase 0%; any field 21.3% (v2/audit2/report.json). GPT critique complete (167 items; Opus upheld on 126 of 145 corrected fields). C5/C6 collected at 342/342. Course Excel, app data and findings page rebuilt.
- 2026-10-27 05:00Z: GPT critique complete (5/5 batches, 167 items): on 145 fields Opus corrected, GPT agrees with Opus on 126 (87%), sides with the original code on 18, proposes a third value on 1; flags 5 of 38 Opus confirmations (batch 5: 4 of 27, modality and statement stance). Findings page gains a fresh-sample column (n=300, Opus) and the critique summary (build_site_data.py + findings_template.html); republished as version 5 of https://claude.ai/artifact/N3FdLuxHJzbyk4uJnXstjc. Open: C5/C6 passages are collected but not yet coded with the course codebook. Weekly usage 62%.
- 2026-10-27 07:35Z: PI review of policy positions (D60): merge same-actor positions that ask for the same action across force; different actors stay separate; sentences name the actor and state the policy directly; app shows no 'AI-written' tag but who and how strongly (e.g. Students must 189, should 104); Excel README records that Sonnet wrote the sentences. positions.py consolidate: 1,562 fine positions -> 1,430 policies in 139 types (P65, P69, P109 needed a retry); a script check rejects mixed-actor merges; fine positions kept in v2/positions/positions_fine.json. App and atlas_v2.xlsx rebuilt and checked in the local preview. C5/C6 course coding running (85 new passages, open coding 3/5 packets).
- 2026-10-27 08:00Z: C5/C6 course coding complete: 85 new passages (C5 33, C6 52) open-coded (one packet redone after its worker tried to run a script; prompt now forbids scripts), 402 new statements assigned to the course codebook incrementally (course_assign.py packets now packs only new statements; coder B 25% of them, seed 20261026). Course layer: 471 AI passages at 135 universities, 2,167 statements, alpha (type) .870, agreement .874; OTHER 5% in C5, 2% in C6. compare_layers, course_layer.xlsx, app data and findings page rebuilt; findings page republished (version 6).
- 2026-11-02: PI asked for course policies, a cross-type merge of redundant policies, homes for stage-less policies and unplaced statements, combined staff/admin actors, the status on the site and no stale content. The headless claude CLI's login had expired (OAuth), so v2/tools/synthesis.py gained a file mode (SYN_MODE=files): prompts written to v2/positions/prompts, answered by in-session subagents (Sonnet for course grouping and placement, Opus for merges), validated by the same script checks. Results (D62-D65): institutional 1,430 -> 1,062 policies (238 merges, 173 span 2+ types, 176 background); course 390 grouped (19 not about AI) -> 315 policies (45 background); UNCOVERED 90 placed, 226 unique, 20 not a policy, 12 not about AI (5 loose placements kept unique). App (actor groups, stages, course policies), atlas_v2.xlsx (Positions, stage and actor-group columns, grouped Matrix), course_layer.xlsx (Course policies sheet) and findings page (Status section with distribution and thin-cell findings; refreshed steps, definitions, next) rebuilt and checked; findings page republished as version 7. About-AI count is now 23,948 everywhere.
- 2026-11-02: Docs refreshed by a subagent from the data files (STATUS_AND_FINDINGS.md, DEFINITIONS.md, PAPER_OUTLINE.md; originals backed up in the session scratchpad). Its checks found two stale points, fixed: build_site_data.py now takes type and about-AI from site/data/policies.json (so theme counts include the 90 placements and UNCOVERED reads 246) and dates summary.json by build day; the findings-page thin-cell note no longer claims assessment is the thinnest course stage (courses: before-course 1%, over-time 1%, assessment 6%). Findings page republished (version 8).
- 2026-11-02: PI (advisor meeting): show the synthesis pipeline and what is and is not a policy, keep every policy. D66: policy kinds (rule/recommendation/template/description/background) from statement binding or force; 221 background policies classified by a Sonnet subagent (fact 93, reason 69, definition 23, resource 21, rule 15 moved back). Findings page gains 'From statements to policies' (level definitions; pipeline 24,536 statements -> 23,948 about AI -> 23,702 with a topic -> 1,562 -> 1,430 -> 1,062 institutional policies; course 2,167 -> 390 -> 315; kinds table; background kinds with examples) and 'The policy set' (browser of all 1,062 + 315 policies, each opening to every statement with university and source link; data in policyset.json, 6.3 MB, published with the page). App shows each policy's kind and merge count. Findings page republished (version 9).
- 2026-11-02: D67 (PI): policy core = rules + recommendations (611 institutional, 199 course); facts kept beside; templates, descriptions and reasons/definitions/resources in their own tabs. Findings page policy-set browser now has tabs by kind with counts and a note per tab; pipeline table shows the core count. Republished (version 10).
- 2026-11-02: D68 (PI): the policy set is rules + recommendations + facts (institutional 675, course 228); templates, descriptions, reasons/definitions/resources moved to an 'Other coded text' page, never counted. Rebuilt v2/site/index.html as a multi-page local website: Overview (pipeline diagram with set-aside notes, policy-set heatmaps by level x group x stage, thin-cell findings), Policy set and CS course policies (sub-tabs, all collapsed), Matrix (counts distinct policies by each policy's group and stage), Other coded text, Universities, CS course coverage, Draft, Policy label, Method (findings.html?embed=1, one section per sub-page). New v2/tools/export_site_csv.py writes 11 CSVs (v2/site/data/csv) linked from each page. Launcher: 'Open AI Policy Atlas.command' (serves v2/site on port 8792). University-wide 'students while working' is 94 policy-set policies (the earlier 221 counted all kinds). The claude.ai findings artifact (v10) is now superseded by the local site.
- 2026-11-02: Excel and Method pages moved to the policy set (D68). atlas_v2.xlsx: PolicySet sheet (675) and OtherCoded sheet (387) replace Positions; Policies sheet gains a category column; Matrix sheet counts statements behind the policy set by their policy's group and stage. course_layer.xlsx: Course policies (228, policy set) and Course other coded (87). Findings/Method pages: 'Policy set' definition; Next cites 675 and 228. summary.json status gains policy_set and course_policy_set. Docs refresh to the policy set delegated to a subagent.
- 2026-11-02: Docs moved to the policy set by a subagent (STATUS_AND_FINDINGS.md, DEFINITIONS.md, PAPER_OUTLINE.md). Its checks found and I fixed: render_decisions.py skipped decisions with new section names (METHODS_DECISIONS.md now lists all 69); course passages that share an id across two sections were double-counted in the site (2,226 -> 2,167 statements; passages still shown, labels on the first only; 9 passages not yet coded, logged as a known gap). D69: 'By role' page (Do / Don't / May / Know per stage for each role; students 139 = 71 / 21 / 25 / 22); matrix-by-direction and conflicting policies logged as an open item for later.
- 2026-11-02: The 9 uncoded course passages are coded. Passage ids now get a section suffix (|s2) when a second section of the same course and term repeats the id (course_code.py, build_v2.py). Open coding by a Sonnet subagent (71 statements; the subagent reported 69, the file holds 71; check OK); course codebook assignment by two independent Sonnet coders (A: 71, B: 18); course alpha now .868 (559 pairs, 87.3% agreement). New synthesis.py course-place step: 69 statements placed in existing course policies, 2 new course policies (CNEW.c01, CNEW.c02). Course layer: 471/471 passages coded, 2,238 statements (2,138 in a policy, 100 not about AI), 317 course items, course policy set 229. Site, both Excel files, CSVs and findings data rebuilt; docs' course numbers refreshed by a subagent.

## 2026-11-02 Meeting brief and repo prep
- Wrote v2/MEETING_BRIEF.md (demo order, talking points, questions for advisors, open items). Added .DS_Store, __pycache__ and *.pyc to .gitignore. No git repo yet; private GitHub repo awaits PI approval.
- 2026-11-02 D70: tools/build_report.py writes v2/site/report.html (Report tab) and AI_Policy_Atlas_report.docx (site/data and exports): status, pipeline, numbers, findings, CS vs university/school, 2 advisor decisions, all 675 + 229 policies grouped by who and stage. MEETING_BRIEF decisions trimmed to 2.
- 2026-11-02 D71: PI asked to publish. Public repo https://github.com/rudrajit1729/ai-policy-atlas (main); site on GitHub Pages https://rudrajit1729.github.io/ai-policy-atlas/ via .github/workflows/pages.yml (deploys v2/site). Excluded: .cache/, logs/, .claude/. Root README.md added.
- 2026-11-02 D72: report lists tag each policy with a stance (rule in decisions.json); summary table of stance by institutional vs course added to section 3. Pushed; live site redeployed.
