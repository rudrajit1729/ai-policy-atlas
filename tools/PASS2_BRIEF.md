# Pass 2 brief: coverage completion (run in a fresh Claude Code session)

You are continuing a research project. First read `context.md`, then `tools/AGENT_BRIEF.md` (including all addenda at the end). Every rule in `AGENT_BRIEF.md` applies: inclusion criteria, ≤15-word verbatim excerpts with `frag_start`/`frag_end`, codebook, output schema, USA and Canada only, and CS-like units including iSchools, data science and AI. Ignore its note that the web-search budget is exhausted. This session has a fresh, larger budget (1000 searches). Use WebSearch freely.

## Why pass 2 exists
Pass 1 hit a 200-search cap, so many institutions were checked only by browsing their sites ("browse-only") or came back "none-found" without a real search. Pass 2 re-searches those properly and widens coverage.

## Inputs
- `corpus/pass2_targets.json` has two lists. `research_again` holds institutions to re-search with WebSearch (browse-only or none-found in pass 1). `new_institutions` holds institutions not yet checked.
- `corpus/known_urls.txt` lists URLs already in the corpus. Do not add these again, and do not add a second document whose policy text is identical to one already included from the same institution.

## How to run
Split the targets into 6 roughly equal batches and run 6 general-purpose subagents in parallel (Agent tool), one batch each. Tell each subagent to read `tools/AGENT_BRIEF.md` and this file, and to write `corpus/raw/pass2-<n>.json` (n = 1..6) using the same schema as `AGENT_BRIEF.md`, with `"group": "pass2-<n>"`. Each subagent must:
1. For each institution, run at least 2 targeted searches, for example:
   - `"<university>" "computer science" ("generative AI" OR ChatGPT OR Copilot) policy`
   - `site:<domain> syllabus "generative AI"`
   - `site:<domain> "AI policy" (CS OR "computer science" OR informatics OR "data science")`
2. Fetch every included document with `python3 tools/fetch_text.py "<url>" p2-<slug>` and copy excerpts only from the saved text.
3. Record EVERY institution it checked in `searched_universities`, with result `included`, `none-found`, `only-generic-university-policy` or `inaccessible`. Put `"pass2"` in the notes.
4. Validate its own JSON and its exact-substring matches before writing the file.

After all 6 finish, run `python3 tools/verify_build.py` and write a short summary of pass-2 additions to `corpus/pass2_summary.md` (documents added, institutions added, and anything odd). Do not edit `corpus/synthesis*.json`, the dashboard, `context.md` or `PROVENANCE.md`. The main session does that.
