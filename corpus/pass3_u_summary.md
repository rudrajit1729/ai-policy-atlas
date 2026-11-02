# Pass 3, Track U summary: university-wide fallback (with addendum 4 tiers)

_Written 2026-10-05._

Files: `corpus/raw/pass3-u-2.json` (an earlier run, 4 institutions) and `corpus/raw/pass3-u-7.json` … `pass3-u-13.json` (this continuation). Batches 7–12 were first run under addendum 3. They were then re-run against **Scope addendum 4** (tiers 1 CS → 2 CS-related unit → 3 `school-general` → 4 `university-general`). Each re-run checked tiers 2 and 3 for every Tier-4 or none-found institution. Where a higher tier turned up, the university-general document moved to `excluded` with the reason "superseded by Tier N document (addendum 4)". Every document summary starts with "Tier N.". Every file validates: excerpts are exact substrings of the fetched text, at most 15 words; no duplicate URLs; no URL from `known_urls.txt`.

## Documents added

**136 documents** across the Track U files.

| Tier | Level | Docs |
|---|---|---|
| Tier 1 | course | 45 |
| Tier 1 | university-computing (UCSC, UAB, Regina, Vanderbilt) | 4 |
| Tier 2 | course (Georgia State CIS 3001), department (Utah ECE) | 2 |
| Tier 3 | school-general (Emory College, Iowa CLAS) | 2 |
| Tier 4 | university-general | 83 |

Notable new Tier-1 finds: earlier passes had marked these institutions as having no computing policy. VCU (CMSC 210/357/413), UTSA (CS 1063/1083/2113), USF (CAP 4111, CDA 4621, CIS 4219), NJIT (CS 490, 485, 698 from archived Digital Commons), UNT (CSCE 1030/3201), Austin CC (COSC 1436/1336, ITSE 1302), McMaster, Windsor, Temple, DePaul, GWU, Cincinnati, UC Riverside, UC Davis, Haverford, Northwestern, Montana State, Baylor, UCSB, Valencia, FAMU, FIU, Dalhousie, Lafayette, Brock, Mississippi State, UNLV, Tennessee COSC 202.

## Institutions added

119 institutions now have a document from Track U: 32 at Tier 1, 2 at Tier 2, 2 at Tier 3 and 83 at Tier 4.

- **none-found (5):** Morgan State, Spelman, Tuskegee, Foothill College, Miami Dade College.
- **Sub-unit targets already covered (3, recorded in `pass3-u-13.json`):** UMD iSchool, Rutgers SC&I and UT Austin iSchool. Their universities already have Tier-1 CS documents, so nothing was added.
- **Indiana:** Indiana appears twice in the targets (Luddy). It is handled once, as Indiana University Bloomington (Tier 4).

**Blocked-source retries:**
- **Tennessee COSC 202:** recovered from the Spring 2024 Wayback PDF. Included.
- **NJIT:** CS 301/332/375/450/786 are still blocked and were never archived. Three other archived Fall 2024 CS syllabi were included instead.
- **Brock:** COSC 1P02 was included from the Wayback copy. COSC 3P71 has no AI text.
- **Bellevue:** the archived software-development AI page is marketing, not policy. The eLearning "AI for Students" page was used instead (Tier 4).
- **Idaho:** archived CS syllabi have no AI text. The CETL AI Guidelines page was used instead (Tier 4).
- **Nebraska CSCE 310H:** behind Google sign-in and not archived. The teaching center's page was used instead (Tier 4).
- **SFU CMPT 120:** no alternate copy exists (no Wayback, archive.today, PDF or mirror). It is recorded in `pass3-u-10.json` `excluded` and searched as `inaccessible`. The 7 statements in `sfu-cmpt120` stay unverifiable.

## Frame size and coverage

The frame is the 128 entries in `corpus/pass3_university_targets.json` (127 unique after merging the duplicate Indiana entry), plus the SFU retry. Every target is recorded in `searched_universities` with "pass3" in its notes: 119 included, 5 none-found, 3 sub-units covered by existing CS documents.

## Calls for the PI or main session to review

- **Generous `university-computing` codings:** UCSC (its teaching-center guide samples UCSC computing courses), UAB (provost report with "Computer Code" sample statements), Regina (a coding sample assignment) and Vanderbilt (one ECE professor's policy among other samples). Each could be downgraded to Tier 4.
- **Borderline Tier 2:**
  - Georgia State CIS 3001 is an information-systems course in the business college.
  - Utah's ECE department page was used because no Kahlert School of Computing policy was found.
- **Thin or weak sources:** Brock COSC 1P02 (its only rule covers AI-written emails), Hampton (task-force recommendations), Montana State's teaching center page ("not official"), and Stevens (mostly data classification). Montana is now Tier 1, so its teaching center page no longer applies.
- **Text from Wayback snapshots, recorded as `curl`:** about 15 documents. Examples: Caltech, Bowie State, UC Davis OSSJA (superseded), Oklahoma State, Jackson State, the NJIT syllabi, UNLV, Baylor, Idaho, De Anza, Gonzaga and Bellevue. Some keep the live URL in `url`. `verify_build.py`'s Wayback fallback should cover them.
- **Simple Syllabus text:** the UTSA, USF, Valencia and FAMU syllabi come from the public Simple Syllabus JSON endpoint. Their `url` points at the public view page, which renders only with JavaScript, so the verify step may need `browser_verified.json` entries or the JSON URLs.
- **Text-fragment links won't highlight:** the VCU syllabi are Google Drive download links, so `#:~:text=` highlighting does not work on them.

## UNFINISHED

None. Every target was completed. Possible upgrades that could not be fetched:
- **SDSU:** library-hosted CS 150/160/210/250 syllabi are blocked by a bot check.
- **San Francisco:** CS 315 is on Simple Syllabus and CS 272 on Notion; neither is readable without JavaScript.
- **NEIU:** the College of Business and Technology AI syllabus examples need a Google sign-in.
- **UW–Milwaukee:** the SOIS sample syllabi are on SharePoint and need a login.
- **Indiana Luddy and Bellevue:** course pages returned empty or 403.
- **KU, SMU, Auburn and Loyola:** syllabus search on their Simple Syllabus sites is not public.
