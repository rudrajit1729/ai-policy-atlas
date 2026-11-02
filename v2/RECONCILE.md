# v2 reconciliation brief (Reconciler role)

Read all of `v2/CODEBOOK.md`. Two coders independently coded the same documents: `<RUN_DIR>/coderA/<slug>.json` and `<RUN_DIR>/coderB/<slug>.json`. `<RUN_DIR>` is given in your task (`v2/dryrun` for the dry run, `v2/run` for the full run). Produce the consensus coding at `v2/inst/<slug>.json`.

For each document:
1. **Align units.** Two units match when they cover the same source passage and the same rule (overlapping or adjacent anchors). A unit found by only one coder is checked against the source text: keep it if it is a real policy statement, drop it if not.
2. **Resolve disagreements by re-reading the source text, and write the resolution rationale first.** For every unit where the coders disagreed, or that only one coder found, set `resolution_why` on the final unit: what each coder said, what the source says, and why the final code follows from it. Keep the stronger of the two coders' `why`, or rewrite it so it matches the final codes. This covers actor, phase, modality, policy_type, stance, and the wording of normalized policies. The final normalized `policy` must be faithful to the passage. Prefer `null` (anchor-only) when the anchor alone states the rule.
3. Keep every `fit_note` and `uncovered_note` from either coder (merge them if both wrote one); never drop one silently. Merge `new_types`: deduplicate them, and map each one to an existing type if it really fits.
4. Write `v2/inst/<slug>.json` in the CODEBOOK format and run `python3 v2/tools/validate_inst.py v2/inst/<slug>.json` until it prints OK.

Also write `<RUN_DIR>/agreement_<slug>.json` containing:

`{"documents": n, "units_A": n, "units_B": n, "matched": n, "only_A": n, "only_B": n, "kept_only_A": n, "kept_only_B": n, "agree_actor": share, "agree_phase": share, "agree_modality": share, "agree_policy_type": share, "agree_stance_docs": share, "notes": "the main kinds of disagreement and how you resolved them"}`

The shares are computed over matched units, or over documents for stance.
