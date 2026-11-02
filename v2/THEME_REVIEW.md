# Theme review brief (Theme reviewer role), D34 / D37 / D38 / D45

Purpose: read every coded policy statement once more, now that the type list has grown from the data (P01–P127), and record four judgments per statement. A later synthesis step uses your judgments to rename, split, merge and add types and to build themes bottom-up. You do NOT edit the coded files and you do NOT rename types yourself.

Read first: `v2/DEFINITIONS.md` and the type list `v2/policy_types.json` (every type's `name` and `covers`). Read `v2/CODEBOOK.md`, section "Verbatim and honesty rules".

## Input
A packet `v2/theme_review/packets/<packet>.json`: `{"packet": ..., "current_type": "P24" or "UNCOVERED", "units": [...]}`. Each unit has `uid`, `university`, `layer`, `passage` (the original wording, cut by script from the saved document), `policy` (the coder's AI-normalized statement; empty means the passage states it), `why` (the coder's rationale), `actor`, `modality`, `fit_note`, `uncovered_note`.

Judge each statement from its `passage` first; use `policy` and `why` only to understand the coder's reading. If they disagree with the passage, the passage wins.

## For every unit, record
1. `about_ai`: `yes` if the statement talks about AI, directly or because it sits inside AI-specific rules (e.g. "Categories of permitted use include ..." in an AI policy is about AI even without the word). `no` only if it is a general rule that would read the same with AI removed from the document (a general misconduct sanctions ladder, a generic appeals process, a generic honesty value). When unsure, `yes`.
2. `binding`: what kind of statement it is.
   - `rule`: the institution, unit or course states its own requirement, prohibition or permission (must, may not, may).
   - `template`: sample or model language offered for instructors to adopt, or other institutions' statements quoted as examples.
   - `recommendation`: advice or a suggestion (should consider, we recommend, best practice).
   - `description`: a statement of fact, background, rationale or context that sets no rule.
3. `type`: does `current_type` fit the statement's **content** (ignore modality and actor: "require a syllabus statement" and "recommend a syllabus statement" are the same content)?
   - `keep` if it fits.
   - `Pxx` if another existing type fits clearly better (for UNCOVERED units: the existing type that now fits, if any).
   - `NEW: <short content label>` if no existing type fits. Use the same wording for the same idea across units, so they can be grouped.
4. `note`: one short sentence, required when `type` is not `keep` or `about_ai` is `no`; otherwise optional.

## For the packet as a whole, record `subgroups`
Do the statements in this packet fall into clearly different content groups (signs the type should be split)? List each group: `{"label": "...", "definition": "...", "uids": [...]}`. Use only groups with at least 5 units; leave the list empty if the type is coherent. Also give `name_suggestion`: a content-only name for the type as you see it in this packet (no "require", "should", "students", "instructors" unless the actor is the content), and `coherence`: `coherent` | `mostly coherent` | `mixed`.

## Output
Write `v2/theme_review/tags/<packet>.json`:
```json
{"packet": "...", "current_type": "...", "coherence": "...", "name_suggestion": "...",
 "subgroups": [{"label": "...", "definition": "...", "uids": ["..."]}],
 "units": [{"uid": "...", "about_ai": "yes|no", "binding": "rule|template|recommendation|description", "type": "keep|Pxx|NEW: ...", "note": "..."}]}
```
Every uid in the packet must appear exactly once. Do not copy passages into the output. Validate with `python3 v2/tools/theme_review.py check <packet>` and fix every error until it prints OK.

## MIXED packets
Packets named `MIXED_...` hold units from many types (`current_type` is `MIXED`). Judge each unit against its own `current_type` field. Skip `subgroups`, `coherence` and `name_suggestion` (write `"subgroups": []`).

## Split packets (step 2, D47)
Packets in `v2/theme_review/split_packets/SPLIT_<type>_NN.json` hold every statement now assigned to a type that the synthesis splits. The packet gives `split_type`, `why` (what the split separates), and `options` (type id, name, covers). For each unit, read its `passage` first and choose the one option whose **content** fits best (ignore modality and actor). If `other_allowed` is true and none of the options fits, you may give another existing type id from `v2/policy_types_v3.json` or `NEW: <short content label>`.

Write `v2/theme_review/split_tags/<packet>.json`: `{"packet": "...", "units": [{"uid": "...", "type": "<option id>", "note": "..."}]}`. A `note` (one short sentence) is required when the unit leaves `split_type`. Every uid exactly once. Validate with `python3 v2/tools/theme_apply.py check <packet>` until it prints OK.
