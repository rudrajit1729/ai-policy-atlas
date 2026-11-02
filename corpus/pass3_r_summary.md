# Pass 3, Track R (US R1/R2 sampling frame): summary

_2026-10-05. Outputs: `corpus/frame_us_r1r2.json`, `corpus/raw/pass3-r-1.json` … `pass3-r-6.json`. All six files pass a check covering schema, codebook values, the 15-word cap, and exact substring matches (whitespace/quote-folded, same fold as `verify_build.py`) of every `text`, `frag_start` and `frag_end` against the cached text in `.cache/text/p3r-<id>.txt`. Scope addendum 4 (tier fallback order) arrived after the first sweep. Every institution that had fallen back to `university-general` was then re-checked at tiers 2 and 3 with 2–4 searches each, and every document summary states its tier ("Tier N")._

## Documents added

134 documents, 895 excerpts.

| Level | n | Tier |
|---|---|---|
| course | 21 | 1 |
| department | 1 | 1 |
| university-computing | 1 | 1 |
| course | 2 | 2 |
| department | 2 | 2 |
| school-general | 0 | 3 |
| university-general | 106 | 4 |

- **Tier 1, computing course or department (19 institutions, 24 documents):**
  - UC Merced: CSE 176
  - UMKC: Provost sample-statements page that reproduces the CS program's statement (`university-computing`)
  - LMU: CMSI 3300
  - TCU: COSC 10403, COSC 30203/30253
  - UNC Wilmington: CSC 365
  - Wright State: CEG 4350/5350
  - Appalachian State: CS 3435
  - CUNY Hunter: CSci 127
  - Clark: CSCI 103
  - Lamar: COSC 3306
  - Texas State: two CS 3358 sections
  - Akron: 3460 HCI
  - Miami (OH): CSE department academic integrity guidelines
  - Rowan: CS 04.113
  - UMSL: CMPSCI 4390/5390, which has a per-activity AI table, allows agentic coding tools and ends with an oral final
  - East Texas A&M: AI 500
  - UT Arlington: CSE 1310
  - Memphis: COMP 1900, COMP 4745/6745, COMP 7118
  - UT Tyler: COSC 1337, COSC 3315
- **Tier 2, CS-related unit (4):**
  - UTHealth Houston: McWilliams School of Biomedical Informatics
  - UNC Greensboro: ISM 671, an information systems course in the business school (borderline; see notes)
  - OHSU: BMI 510/610 biomedical informatics
  - University of San Diego: MS Applied Data Science handbook
- **Tier 3, school-general:** none. No Engineering or Science college AI policy was found at any of these institutions.
- **Tier 4, university-general (106):** all other included institutions. Each `unit` field names the publishing office.

Only 2 documents are marked `verbatim_source: "webfetch"`: UNMC Policy 8020 and Icahn's AI policy PDF. Both block the browser user agent that `fetch_text.py` sends but answer a plain curl. Their excerpts were checked against text extracted from that plain-curl copy (see the verification risks below).

## Institutions added

146 institutions checked; every one is recorded in `searched_universities` with "pass3" in the notes.

| Result | n |
|---|---|
| included | 129 (19 at Tier 1, 4 at Tier 2, 106 at Tier 4) |
| none-found | 9 |
| inaccessible | 5 |
| only-generic-university-policy | 3 |

- **None-found:** Delaware State, OU Health Sciences Center, Texas Southern, UT Health San Antonio, Tulsa, Baylor College of Medicine, South Carolina State, Rockefeller, Louisiana Tech.
  - UT Health San Antonio merged into UTSA in 2025, and UTSA's guidance is already in `pass3-u-10`.
- **Inaccessible:** Albert Einstein, SUNY Upstate, UT Southwestern (VPN required), OSU Center for Health Sciences (403), Eastern Michigan (Cloudflare on all of emich.edu).
- **Only-generic, not fetchable:** Catholic University (AI Policy, May 2026, blocked by Cloudflare), AFIT (GenAI Teaching Guidebook, blocked by Cloudflare), Wichita State (syllabus-policy page, blocked by Incapsula).

## Frame size and coverage

- **Frame:** 326 institutions, 187 R1 and 139 R2, from the Carnegie 2025 list via Wikipedia's "List of research universities in the United States". `covered_as` in `corpus/frame_us_r1r2.json` maps frame names to corpus names.
- **Already covered before pass 3:** 180 institutions (153 R1, 27 R2). Loose matching was checked by hand. Look-alikes such as Baylor University vs Baylor College of Medicine, and UC San Diego vs University of San Diego, were kept separate.
- **Remaining institutions searched in this track:** 146 (34 R1, 112 R2).
- **Result:** all 326 frame institutions have now been searched.
  - Track R included a document for 129 of the 146 (30 of 34 R1; 99 of 112 R2).
  - The 17 without a document are mostly medical or health-science institutions or sites blocked to automated fetching.
- **Tiers among Track R institutions:** Tier 1 (19) + Tier 2 (4) = 23 of 129 included institutions (18%) have a computing-specific document; 106 rely on the university-wide fallback.

## Notes for the merge and review

- **Shared URL:** IU Indianapolis's Tier-4 document uses `teaching.iu.edu/resources/generative-ai/policies.html`, the same URL as `iu-teaching-genai-policies-guidance` in `pass3-u-7` (filed under IU Bloomington). Bloomington has computing documents, so `verify_build.py` should drop the Track U copy, leaving only the Indianapolis one. The two doc ids differ.
- **Verification risks for `verify_build.py`.** It refetches pages with the browser user agent:
  - UNMC and Icahn block that user agent, so their quotes may show as unverified.
  - Georgia Southern and UM-Dearborn were read from Wayback snapshots. Their `url` field is the original page.
  - UMass Chan returned a challenge page to the default user agent; its PDF was fetched with a shorter user agent.
  - USD's handbook PDF has run-together words. Two `frag_end` values contain them ("forindependent", "oftheir").
- **Borderline calls for the PI:**
  - UNC Greensboro ISM 671 counted as Tier 2. Revert UNCG to Tier 4 if business-school information systems should not count as CS-related.
  - UMKC's provost page is `university-computing` (Tier 1).
  - Several Tier-4 documents come from a medical school or program rather than the whole university, because the institution has no computing unit: UCSF, LSUHSC, Weill Cornell, Loma Linda (stance `mixed`), UMass Chan.
  - Some Tier-4 sources are thin or hosted by a library or IT office: ACU, BGSU, SUNY ESF, Tennessee State, Virginia State, Southern University, Clark Atlanta, SIU (Faculty Senate text on a library guide).
  - UMass Dartmouth's Faculty Senate PDF comes from a third-party copy (New Bedford Light).
- **Worth retrieving by hand in a browser:**
  - Montana CSCI 150 syllabus (ScholarWorks; 403 to curl and WebFetch, not archived). If retrieved, Montana moves to Tier 1.
  - FAU COP 3035C syllabus (server error, no archive). If retrieved, FAU moves to Tier 1.
  - Eastern Michigan's Faculty Development Center AI guidance.
  - The policies of Catholic University, AFIT and Wichita State.
- **Leftover files:** probe and scratch text files (`p3r-test-*`, `tmp-*`, `p3r-x-*`, ids that were later renamed) remain in `.cache/text/`. They are not referenced by any raw file and can be deleted.

## UNFINISHED

None. All 146 remaining frame institutions were searched to completion (search quota was not exhausted).
