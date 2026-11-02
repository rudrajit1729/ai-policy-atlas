# Pass 3, Track C (Canada sampling frame): summary

_2026-10-05. Outputs: `corpus/frame_canada.json`, `corpus/raw/pass3-c-1.json` … `pass3-c-4.json`. All four files pass an exact-substring check against the cached text in `.cache/text/p3c-*.txt`. Every document was fetched by curl; none relies on `webfetch`, and no URL appears in `corpus/known_urls.txt`. Scope addendum 4 (tier fallback order) was applied after the first sweep: every institution that had fallen back to `university-general` was re-checked at tiers 2 and 3, and every summary is prefixed "Tier N:"._

## Documents added

37 documents.

| Level | n | Tier |
|---|---|---|
| course | 14 | 1 |
| department | 1 | 1 |
| school-general | 1 | 3 |
| university-general | 21 | 4 |

No tier-2 documents (iSchool, data science or software engineering units) were found at any of these institutions.

- **Tier 1, computing course or department (8 institutions):**
  - Winnipeg: ACS-1903, ACS-1904, ACS-3931
  - Mount Royal: COMP 3309
  - Vancouver Island: two CSCI 159 sections and CSCI 161
  - Acadia: Jodrey School of Computer Science academic integrity page
  - Saint Mary's: CSCI 1226, CSCI 2341
  - StFX: CSCI 161
  - UQAC: 8INF972
  - UQO: CYB6023
  - TÉLUQ: INF 1420, INF 1901
- **Tier 3, school-general (1):** Brandon, Faculty of Science Course Outline Policy (Dec 2024).
- **Tier 4, university-general (21):**
  - Alberta: Athabasca, Concordia Edmonton, MacEwan, Lethbridge
  - British Columbia: Capilano, KPU, Trinity Western, UNBC, UFV
  - Prince Edward Island: UPEI
  - Nova Scotia: Cape Breton
  - Ontario: Algoma, Lakehead, Nipissing, RMC
  - New Brunswick: Moncton
  - Quebec: Bishop's, HEC Montréal, UQAR, UQTR, UQAT

## Institutions added

39 institutions checked: 31 included, 8 none-found.

- **None-found, in frame (3):**
  - The King's University (AB)
  - Mount Allison (NB): guidelines are still being drafted.
  - Laurentian (ON): draft guidelines went to Senate in May 2025 but were never published in English or French.
- **None-found, out of frame after verification (5):** St. Mary's University Calgary, Université de Saint-Boniface, Royal Roads, Mount Saint Vincent, Redeemer. None offers a computing degree.

## Frame size and coverage

- **Members:** Universities Canada has 97 members, from univcan.ca, accessed 2026-10-05.
- **In frame:** 69 offer a computing degree. All 9 "verify" entries are now resolved in `frame_canada.json`: 4 yes, 5 no.
- **Coverage:** 35 were covered before pass 3 and 34 were searched in this pass, so 69/69 (100%) of the frame has been searched. 66/69 have at least one document in the corpus.

## Notes for the PI

- **Capilano is a borderline frame member.** It has no standalone CS degree, only a BSc (General) with a Computational Sciences concentration. Drop it if the frame should be CS-degree-only.
- **Brandon's Tier 3 document is thin.** It has one sentence recommending an AI statement in course outlines. The Senate Academic Integrity Policy has a fuller AI section but now sits in `excluded`. That follows addendum 4's first-tier-that-exists rule. Revert to the Senate policy if Tier 3 should require substantive AI rules.
- **Athabasca's only official guidance is a provost news post (Aug 2023)** of interim rules. It is included as university-general even though news items are normally excluded.
- **Nipissing's PDF is behind Cloudflare.** The document URL is a web.archive.org snapshot (Sept 2024).
- **Some PDF extractions have broken spacing,** at Mount Royal, UQAR and UQTR. Excerpts keep the cached text exactly as extracted.
- **UQO and TÉLUQ's Tier 1 documents are not intro courses.** UQO's is a cybersecurity graduate course: of about 160 public computing plans, only one instructor's had an AI clause. TÉLUQ's are an HCI course and an AI course.

## UNFINISHED

None.
