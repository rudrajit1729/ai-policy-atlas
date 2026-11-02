# v2 worker brief (one headless session handles a list of universities)

You orchestrate the TACT-style pipeline for each university in your list. You do no coding yourself; you dispatch subagents and check their outputs. Project root: the current directory.

For each university slug in your list, in order:
1. **Skip check.** If `v2/inst/<slug>.json` exists and `python3 v2/tools/validate_inst.py v2/inst/<slug>.json` prints OK, skip to the next slug.
2. **Collector** (one foreground subagent, `run_in_background: false`). Prompt: "You are the COLLECTOR. Read v2/COLLECT.md and follow it for the university '<name>' (slug <slug>). Its known URLs from an earlier pass are in v2/queue.json under that slug. Write v2/collect/<slug>.json." Skip this step if `v2/collect/<slug>.json` already exists.
3. **Coder A and Coder B** (two foreground subagents launched in the SAME message, so they run in parallel). Prompt for each: "You are CODER <A|B>, an independent coder; another coder codes the same documents separately and you must not read their output. Read v2/CODE.md and follow it exactly, including all of v2/CODEBOOK.md (rationale `why` first for every unit and `stance_why` for every document) and the closed type list v2/policy_types.json. University: <slug>. Write v2/run/coder<A|B>/<slug>.json and validate it with `python3 v2/tools/validate_inst.py v2/run/coder<A|B>/<slug>.json` until it prints OK. Do not read v2/run/coder<B|A>/." Skip a coder whose output already validates.
4. **Reconciler** (one foreground subagent). Prompt: "You are the RECONCILER. Read v2/RECONCILE.md and follow it with RUN_DIR = v2/run for university <slug>. Write v2/inst/<slug>.json (validate until OK) and v2/run/agreement_<slug>.json."
5. Run `python3 v2/tools/export_xlsx.py` so the Excel record includes this university.

Rules:
- Always launch subagents in the FOREGROUND (`run_in_background: false`). Background subagents are killed when a headless session ends.
- If a subagent fails (API or network error), retry it once. If it fails again, append the slug and the error to `v2/run/failed.txt` and move on.
- Never edit `v2/CODEBOOK.md`, `v2/policy_types.json`, briefs or tools.
- At the end, print one line per slug: done, skipped or failed.
