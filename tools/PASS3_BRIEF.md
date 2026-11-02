# Pass 3 brief: complete coverage + university-wide fallback (run in a fresh Claude Code session)

Read `context.md`, then `tools/AGENT_BRIEF.md` including ALL addenda (especially addendum 3, which adds the `university-general` level). All verbatim and schema rules apply. USA and Canada only. This session has a fresh budget of 1000 web searches; use WebSearch freely.

You are one of three pass-3 sessions running at the same time. Do ONLY your track (given in the prompt), and write ONLY the files named for your track. Do not edit `corpus/corpus.json`, synthesis files, the dashboard, `context.md` or `PROVENANCE.md`.

## Tracks

### Track U: university-wide fallback
Input: `corpus/pass3_university_targets.json` lists institutions or units already searched that have no computing-specific document. For each one:
1. Re-check quickly (2 searches) for a computing-specific AI policy (department, school, college or computing course). If you find one, include it as usual.
2. Otherwise find the official university-wide AI policy or guidance and include it as `level: "university-general"`. `candidate_urls` lists pages earlier agents saw and excluded as generic; start there.
3. If the university publishes nothing, record `none-found`.

For sub-unit entries such as "University X — School of Y", one university-general document per university is enough.

Also retry these previously blocked sources through other routes (an Internet Archive snapshot, a mirror, a PDF copy):
- NJIT Digital Commons CS syllabi (CS 301, 332, 375, 450, 786)
- Tennessee COSC 202
- Bellevue College
- Brock
- Idaho CS
- Nebraska CSCE 310H
- SFU CMPT 120 (opencoursehub.cs.sfu.ca)

Output: 6 parallel subagents → `corpus/raw/pass3-u-<n>.json`.

### Track R: US research universities (sampling frame)
1. Build the frame: the Carnegie Classification R1 and R2 lists, 2025 classification. Fetch an authoritative list, such as the Wikipedia "List of research universities in the United States" or carnegieclassifications.acenet.edu. Save it as `corpus/frame_us_r1r2.json` (`name`, `tier`, `state`).
2. Drop institutions already covered. Match names in `corpus/covered_institutions.txt` loosely ("UC Berkeley" = "University of California, Berkeley").
3. For each remaining institution: look for computing-specific documents first, applying the AGENT_BRIEF levels and caps. If there are none, fall back to `university-general`.

Output: 6 parallel subagents → `corpus/raw/pass3-r-<n>.json`.

### Track C: Canada (sampling frame)
1. Build the frame: all Universities Canada member institutions that offer a computer science or computing degree. Save it as `corpus/frame_canada.json`.
2. Drop institutions already covered, using the same loose matching against `corpus/covered_institutions.txt`.
3. Run the same procedure as Track R. French-language documents are in scope: keep excerpts verbatim in French.

Output: 4 parallel subagents → `corpus/raw/pass3-c-<n>.json`.

## Every track
- Fetch every included document with `python3 tools/fetch_text.py "<url>" p3<track>-<slug>`. Copy excerpts only from the saved text. Each subagent validates its own JSON and exact-substring matches before writing.
- Record EVERY institution checked in `searched_universities`. Mark it `included`, `none-found`, `only-generic-university-policy` (only if you could not fetch that policy) or `inaccessible`, and put `"pass3"` in the notes.
- Skip URLs already listed in `corpus/known_urls.txt`.
- When done, write `corpus/pass3_<track>_summary.md` with these sections: documents added, institutions added, frame size and coverage, and UNFINISHED (any institutions not completed because the search quota ran out, or for any other reason).

## Continuation rules (added after the first launch)
- Run subagents in the FOREGROUND: call the Agent tool with `run_in_background: false`, and launch several in one message so they still run in parallel. Background subagents are killed when a headless session ends.
- Before starting, read any existing `corpus/raw/pass3-<track>-*.json` files and skip institutions they already record in `searched_universities`. Write new files with numbers that do not collide, for example `pass3-u-7.json` onward.
