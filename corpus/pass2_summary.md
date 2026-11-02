# Pass 2 summary (2026-10-05)

Pass 2 re-searched the institutions pass 1 had only browsed and added new ones. `corpus/pass2_targets.json` listed 227 unique institutions once duplicate names were merged (for example "Penn State" and "Pennsylvania State University", or "LSU" and "Louisiana State University"). Six parallel subagents each took about 38 of them. Sub-units of one university went to the same batch so the cap of 3 courses per university could be enforced. Each institution got at least 2 targeted WebSearches. The outputs are `corpus/raw/pass2-1.json` to `pass2-6.json`.

## Totals

| | Before pass 2 | After pass 2 | Added |
|---|---|---|---|
| Documents | 146 | 255 | **109** |
| Institutions | 83 | 137 | **54** |
| Excerpts | 902 | 1417 | **515** |
| Verified exact | 902 | 1392 | 490 |
| Unverified | 0 | 25 | 25 (see below) |
| Over 15 words | 0 | 0 | 0 |

The 109 new documents break down as follows:
- **Level:** 99 course, 8 department, 2 university-computing.
- **Country:** 84 USA, 25 Canada.
- **Stance:** 48 permit-with-conditions, 43 prohibit-by-default, 7 tiered, 4 encourage, 4 instructor-discretion, 3 mixed.

No new codes were proposed. Seventeen institutions already in the corpus gained documents: BU, Brown, Harvard, MIT, NYU, Purdue, RIT, Alberta, Arizona, UBC, Chicago, Hawaii, Michigan, Oregon, Pitt, Toronto and UVA.

### Results by batch (`searched_universities`)

| Batch | Documents | Included | Generic university policy only | None found | Inaccessible |
|---|---|---|---|---|---|
| pass2-1 | 20 | 14 | 14 | 11 | 0 |
| pass2-2 | 23 | 14 | 12 | 11 | 1 |
| pass2-3 | 22 | 13 | 17 | 7 | 1 |
| pass2-4 | 13 | 9 | 16 | 12 | 1 |
| pass2-5 | 13 | 11 | 21 | 5 | 1 |
| pass2-6 | 18 | 13 | 17 | 7 | 0 |
| **Total** | **109** | **74** | **97** | **53** | **4** |

Rows count institution entries. A university and its sub-unit, such as Drexel and Drexel CCI, can both be marked included for the same documents. The two agents in batches 1 and 3 each added one extra row for a parent university.

### New institutions (54)

Boise State, Bowdoin, Bryn Mawr, Cal Poly SLO, City College of San Francisco, Colorado School of Mines, Colorado State, Drexel, Florida State, Georgetown, Illinois Tech, James Madison, Kansas State, Marquette, McGill, NC State, Old Dominion, Penn State, Polytechnique Montréal, Portland State, San José State, Santa Clara, SFU, Smith, Texas A&M, Texas Tech, UT Dallas, Toronto Metropolitan, CU Boulder, UConn, Houston, Miami, Minnesota, Nevada Reno, New Brunswick, New Mexico, Notre Dame, Oklahoma, Rhode Island, Saskatchewan, South Carolina, UTEP, Vermont, Victoria, Université de Montréal, Sherbrooke, UQAM, WashU, Western Washington, Wilfrid Laurier, William & Mary, WPI, York, ÉTS.

## Things that need attention

1. **25 unverified excerpts in 5 documents that were read with WebFetch.** `verify_build.py` could not match them.
   - **`uvic-csc110`, `uvic-csc226`, `uvic-csc361`:** the UVic course-outline site is JavaScript-only, so curl gets no outline text.
   - **`ets-log430`:** ÉTS wraps the whole course plan in a `<form>` element. `fetch_text.py` strips forms, so the plan text never reaches the check. The agent confirmed the wording against the raw HTML. Options: change `html_to_text` to keep `form` content, or add the document to `browser_verified.json`.
   - **`sfu-cmpt120`:** curl to opencoursehub.cs.sfu.ca fails with exit 35, an SSL error.

   The fix for all five is to verify them in a real browser and add them to `corpus/browser_verified.json`, or else drop them.
2. **Sources that blocked the fetch.** Each of these probably holds relevant policies:
   - NJIT Digital Commons, which has CS 301, 332, 375, 450 and 786 with AI policies (Cloudflare).
   - Tennessee COSC 202 (403 and a certificate error).
   - Bellevue College (Cloudflare and 403).
   - Brock course outlines (403).
   - Idaho CS course servers (timed out).
   - Laval course plans (behind a login).
   - McMaster outlines (image-only or behind a login).
   - Nebraska CSCE 310H (Google login).
3. **Pass 1 was wrong about Arizona.** It marked the University of Arizona College of Information Science integrity page as having no AI text. The page does have AI text, and pass 2 added it.
4. **Course caps were already exceeded in pass 1** and were not changed here: CMU 5, Berkeley 5, Georgia Tech 4, UCSD 4, UIUC 4, UW 4. Pass 2 respected the caps and skipped capped schools. Several of those schools had more AI policy text available.
5. **`corpus/known_urls.txt` is incomplete.** For example, it has no entries for Pitt, NYU or Toronto. The agents checked `corpus/raw/*.json` directly, so no duplicates got in: the merge found no URL collisions.
6. **Borderline inclusions** for the PI to review:
   - **Template wording:** CCSF CS 110A mentions AI only inside its definition of cheating. Texas Tech CS 4366, Laurier CP164, UNR CS 474/674 and Pitt CS 0445 largely reuse university template wording.
   - **One sentence on AI:** Portland State's CS graduate handbook says only that AI rules vary by course.
   - **Source questions:**
     - Polytechnique LOG2990 comes from a teaching-support template folder and may be a sample course plan.
     - Bowdoin CSCI 2330 is a Wayback snapshot (the live host returns 503), and the archive URL is stored as `url`.
     - Santa Clara's "AI Squared" page is engineering-school guidance with a CSE section, coded `university-computing`.
     - The UNB document is one instructor's policy across all their courses, coded `course`.
   - **Older terms:** Texas A&M CSCE 420 and 312, Georgetown COSC-3450, McGill COMP 480 (a draft) and Houston COSC 4368 are from 2023–2024.
   - **PDF extraction artifacts:** the extracted text of Mines CSCI-561 has "Y ou" and ligatures, and William & Mary CSCI 304 has broken words. Excerpts match, but the deep-link highlights may fail on the live PDF. PDF links do not get text fragments anyway.
7. **French-language documents:** Université de Montréal EBSI, Polytechnique LOG2990, Sherbrooke IFT 339 and IFT 615, UQAM INF1120, INF2050 and INF3105, and ÉTS LOG430. The dashboard may need a language tag or a note.
