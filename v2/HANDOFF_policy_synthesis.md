# Handoff prompt: from policy topics to actual policies

Paste this into a new Claude Code chat opened in this project folder.

---

You are continuing the AI Policy Atlas project (US university and CS-course generative AI policies). Work as chief of staff for the PI with autonomy, and keep usage low (see "Working rules").

**Read first:** `context.md` (project state), `v2/STATUS_AND_FINDINGS.md` (numbers and findings), `v2/PAPER_OUTLINE.md`, `v2/DEFINITIONS.md`, and the last 40 lines of `PROVENANCE.md`. Decisions are in `v2/METHODS_DECISIONS.md` (D01–D58).

## The problem the PI raised
In the app (`v2/site/index.html`, data from `v2/tools/build_v2.py`, served with launch config `atlas-v2` on port 8792), a matrix cell, a Policies card or a draft section shows a **policy type**. A type is a topic: for example "Verifying AI output", "Asking when unsure about AI use", "Explaining and defending one's own work". It does **not** show the policy itself. Each type holds many statements (P31 has about 970), and they are not all the same policy: some require verification, some only warn that AI is often wrong, some ask instructors to teach verification. The PI wants to see:
1. **The distinct policies inside each type.** Each one is a short policy sentence that reads like a policy ("Students must check AI output against a reliable source before submitting it"), not like a text synthesis or a topic name.
2. **The original wordings that support each policy.** These are the verbatim anchors from `v2/site/data/policies.json`, with university, link and count. Every policy must be tethered to real wording.
3. The same grouping in the matrix drawer, the Policies tab, the Draft a policy examples, and the Excel file (`v2/exports/atlas_v2.xlsx`, rebuilt by `v2/tools/export_xlsx.py`).

## Suggested approach (agree it with the PI before running it at scale)
- **Level below the type:** add a "policy position" level under each type (D43 calls this guideline synthesis).
  - For each type, cluster its statements (about-AI only, `v2/theme_review/final_assignments.json`) into positions.
  - Use the existing tags: `unit_stance`, `modality` and `actor` already separate "must verify" from "AI can be wrong" from "instructors teach verification".
  - A cheap first cut is deterministic: type × modality group × actor.
  - Then a Sonnet pass writes one plain policy sentence per position and picks the 3 most representative original wordings.
  - Each position records its supporting statement ids, so nothing is untethered.
- **No invented policy text.**
  - The policy sentence is AI-written and labelled as such.
  - It must only restate what its supporting original wordings say.
  - A script checks that every position has supporting ids and that every shown quote is verbatim in the saved text (reuse `export_xlsx._find`).
- **Pilot first:** try 3 types (P31, P10, P30) and show the PI before running all 139 types.
- **Then the app:** show "policy sentence → supporting original wordings (N universities)" everywhere a type is shown today, in lifecycle order (D55).

## Open items to finish or check
- **Fresh audit and C5/C6:** a fresh Claude Opus audit of 300 new statements (`v2/audit2`) and the remaining C5/C6 course collection (Sonnet) were running when this chat was opened. `python3 v2/tools/finalize_codex.py` summarizes both and rebuilds the course Excel, app data and findings page in one call.
- **GPT critique:** batch 5 of the GPT critique of the Opus audit runs on Codex at 21:55 PT (`v2/tools/codex_run.py critique`).
- **Findings page:** private artifact https://claude.ai/artifact/N3FdLuxHJzbyk4uJnXstjc, built from `v2/site/findings_template.html` + `v2/tools/build_site_data.py` + `v2/tools/build_findings_page.py`.
- **Nothing is published to GitHub.** Ask the PI before any push.

## Working rules (PI)
- **Original wording:** never put AI-written text in an original-wording field. Label AI-written text as AI.
- **Usage:**
  - Bulk work goes to background workers: `claude -p --model sonnet` via the existing drivers, or the Codex CLI at `/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex`, which uses the PI's ChatGPT plan, not Claude.
  - The main chat launches and wraps up with one-call scripts, and does not poll.
  - Check `mcp__ccd_session_mgmt__get_usage` before large runs and tell the PI the expected cost.
  - The PI's weekly cap was 60% for the week ending Sat 2026-10-31 20:00Z.
- **Records:** keep `PROVENANCE.md`, `context.md` and `v2/decisions.json` (render with `v2/tools/render_decisions.py`) current.
- **Writing:** write to the PI plainly and briefly.
