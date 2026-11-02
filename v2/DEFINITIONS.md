# Definitions: what each term in this study means

Every count, column and chart in the atlas uses these terms in exactly these senses. The paper's method section uses them too. If a term changes, change it here first and record the change in `v2/decisions.json`.

## Units of the corpus, from largest to smallest

| term | definition | example |
|---|---|---|
| **University** | One US institution in the sampling frame (`v2/queue.json`, 342 institutions). Each one is the unit we describe and compare. | Oregon State University |
| **Layer** | The organizational level that issued a document: `university`, `school` (a college within the university), `computing` (CS, CSE, EECS, ECE, or a CS-related unit such as informatics, an iSchool, AI or data science), or `course` (a CS syllabus in one of six frame slots, C1–C6; coded with its own codebook, D49). Layers are kept apart and never merged. | College of Engineering = `school` |
| **Document** | One web page, PDF or file that states AI policy or guidance, saved as text and screened for inclusion (D30). A university can have several documents in each layer. | OSU EECS "Guidance for drafting AI-use policies" |
| **Policy unit** (also "statement", "coded policy" or "data point") | One distinct statement in a document that requires, forbids, permits, recommends or explains something about AI use. This is the unit of coding: one row in the Excel `Policies` sheet. A document yields as many units as it has distinct statements. The 24,536 institutional statements are policy units. Since D59 the word "policy" alone means the merged **Policy** defined below. | "Students must disclose any use of AI tools." |

## Parts of a policy unit

| term | definition |
|---|---|
| **Anchor** | The original wording: a contiguous, character-exact quote of at most 15 words from the saved document. A script checks that it occurs in the source. |
| **Source passage** | The full sentence or passage around the anchor. A script cuts it from the saved text; it is never typed by AI. |
| **AI-normalized policy statement** | A plain-language restatement of the unit, written only when the anchor alone does not state the policy. It may not add to, soften or strengthen the source. When it is blank, the anchor is the policy. |
| **AI rationale** (`why`) | Written before any code is chosen. It says why the passage is a policy and why it gets its codes, quoting the source. |
| **Tags** | The codes every unit receives once: actor, phase, modality, unit stance, policy type and topics (definitions below). |

## Codes on each unit

| code | question it answers | values |
|---|---|---|
| **Actor** | Whom does the policy address or bind? Coded as five values; shown as four **actor groups** (D65, below). | student, instructor, ta-staff, admin, all |
| **Phase** | When in the course or institutional cycle does it apply, as coded? Still in the data. Shown as the **stage** (below). | before-course, course-start, during-work, during-assessment, when-misuse, over-time, general |
| **Modality** | How strongly is it stated? | must, must-not, may, should, should-not, informs |
| **Unit stance** | What position does this single statement take on AI use? | prohibit, restrict, permit, encourage, require, neutral |
| **Policy type** | Which recurring kind of policy is it? (See next section.) | one id (P01, P02, …) or UNCOVERED |
| **Topics** | What subject matter does it touch? | 1–3 topic codes |

## Levels of grouping, from smallest to largest

| term | definition |
|---|---|
| **Policy type** | A group of policy units that say the same thing, possibly in different words, at different universities. Each type has a name and a "covers" definition in `v2/policy_types.json`. A unit belongs to exactly one type. Types are built by constant comparison: a unit joins a type only if it says what that type's members say. Types are **provisional until all the data has been seen** (D33). |
| **UNCOVERED** | A unit that does not say what any existing type says. It is never forced into a type. Its note says what it is, and recurring UNCOVERED notes become new types. Each one ends in one of four outcomes (D64): **placed** (it states an existing policy, same meaning and actor, so it joins that policy); **unique** (a rare policy seen at 1 or 2 universities, kept as a candidate, still UNCOVERED); **not a policy** (it states no rule, recommendation, reason or fact, still UNCOVERED); **not about AI** (no longer counted). Of 348: 90 placed, 226 unique, 20 not a policy, 12 not about AI; 246 remain UNCOVERED. |
| **Fit note** | A note a coder writes when the chosen type fits only partly, saying what the type misses. Fit notes show where a type may need splitting. |
| **Candidate type** | A recurring pattern seen in UNCOVERED units or fit notes that does not yet meet the bar for a type (D33), kept in `v2/CODEBOOK_MEMO.md` so it is never lost. |
| **Theme** | A group of related policy types (for example "Disclosure and attribution"). Themes are the highest level of the analysis and are finalized only after the theme review of the full corpus (D34). |
| **Representative statement** | One statement per type that summarizes what all its members say. Where a verbatim anchor already captures it, the verbatim is used. |

## Policies (D59–D68)

| term | definition |
|---|---|
| **Policy** (D59, D60) | One actor group asked to do one thing, with the statements that say it. Fine groups that ask the same actor for the same action merge across force (must, should, may). Different actors, actions or objects, and prohibitions versus permissions, stay separate. Each policy has one plain sentence, an actor group, a stage (or background), a kind (action or background) and its original wordings. Not to be confused with a policy unit (statement). The count that matters is the **policy set** below: 675 institutional and 229 course. |
| **Synthesized item** (D62, D66) | A policy as it stands after merging, before the split by kind. 1,062 institutional and 317 course. These were earlier called "policies" and counted as the result; they are the step before the policy set. |
| **Policy set** (D67, D68) | The synthesized items that are **rules, recommendations, or facts and warnings** about AI. Institutional 675 (611 rules and recommendations, of which 207 rules and 404 recommendations, plus 64 facts); course 229 (200 plus 29; 165 rules, 35 recommendations). Every count, table and chart in the atlas and the paper is on the policy set. |
| **Other coded text** (D66, D67) | Synthesized items that are not in the policy set: **templates** (sample syllabus language), **descriptions** (background that sets no rule), and **reasons, definitions and resources**. Kept, shown on their own page of the atlas, never counted in the policy set. Institutional 162 templates, 123 descriptions, 102 reasons, definitions or resources (387 in all); course 76 descriptions, 12 reasons, definitions or resources (88 in all). Definitions and resources are not analysed further. |
| **Fact and warning** (D66, D67) | Background text that states a fact or warning about AI and explains why rules exist. It is kept beside the rules and recommendations in the policy set. 64 institutional, 29 course. |
| **Merged policy** (D62) | A policy built from parts that say the same thing in other words, judged by semantic equivalence (same requirement, permission, prohibition or fact) and latent equivalence (same intent and act asked of the same people). Different actions, objects, material conditions or directions stay separate. It is listed under each of its types. The parts and a one-line reason are kept for review. In the policy set, 151 institutional policies merge parts and 114 span 2 or more types (before the split: 238 and 173 of 1,062). |
| **Stage** (D62) | When a policy applies, as shown: before course, course start, during work, during assessment, when misuse is suspected, over time, or background. It replaces "phase" wherever a value is shown. The coded phase still exists, and "general" is the only coded value that is not a stage: each policy coded "general" was given a stage or background. |
| **Background** | A policy that is a definition, scope statement, reason, value or fact with no time of action. Its stage is "background" and its kind is background rather than action. In the policy set, 74 institutional and 34 course policies have this stage (before the split: 176 of 1,062 and 46 of 317). |
| **Actor group** (D65) | Who a policy is shown as addressing: **students**; **instructors**; **staff and administrators** (coded ta-staff and admin combined, because each is small); **everyone** (a rule addressed to the whole community rather than one role, kept separate because it binds all roles at once). The coded actor is kept as `actor_coded`. |
| **Course policy** (D63) | A policy built from course statements (course codebook, D56) with the same rules as institutional policies, then merged across course types. Statements not about AI are set aside. 317 synthesized items, 229 in the course policy set. |

## Document-level codes

| term | definition |
|---|---|
| **Document stance** | The document's overall position: prohibit, restrict, permit, encourage, require, or delegates (it hands the decision to instructors or courses). |
| **Tiers** | Named levels of AI use that a document offers instructors (for example "no AI / some AI / full AI"). |
| **Screen** | Whether the document passed inclusion screening: include, exclude, or review (D30). Only included documents are coded. |
| **Quality** | The collector's label for the document: good, thin, generic, superseded, partial. |

## Process terms

| term | definition |
|---|---|
| **Coder A / Coder B** | Two independent Claude Sonnet agents that code the same documents without seeing each other's work. |
| **Reconciler** | A third agent that aligns the two codings, resolves disagreements against the source and records why. |
| **Agreement** | The share of matched units on which A and B gave the same code, and Krippendorff's α computed over the full run. |
| **Theme review** | The pass after all coding (D34) that reads every unit of every type and every UNCOVERED unit, and splits, merges or creates types and themes where the data supports it. |
| **Audit** | The Opus review of the final coding, critiqued by GPT (Codex). Each change is logged as an override. A second, fresh Opus audit of 300 new statements checked the corrected coding. |

**About AI (D45).** Whether a coded statement talks about AI, directly or through its AI context. A statement that is not about AI (for example a general misconduct sanction ladder inside an AI page) is kept in the data but not quoted and not counted; its original-wording cells read "Not about AI (kept, not quoted)". Before the theme review only statements a coder flagged are marked; the theme review judges every statement (field `about_ai`, the D38 `ai_specific` tag).

**Binding (theme review, D38/D46).** What kind of statement a policy unit is (statement level; the kind of a whole policy is set in D66, and only rules, recommendations and facts and warnings are in the policy set): `rule` (the institution, unit or course states its own requirement, prohibition or permission), `template` (sample language offered to instructors, or other institutions' statements quoted as examples), `recommendation` (advice), `description` (fact, background or rationale that sets no rule).

**Final type (theme review, D47).** The type a statement holds after the theme review: the coded type if the reviewer kept it, a better existing type if moved, a new type created in the synthesis, or UNCOVERED. Type names are content-only; whether a statement requires, allows or bans is carried by modality, unit stance and binding.

**Theme (v3, D47).** One of 15 content groupings of the final types (T01–T15), built after all statements were reviewed.

**Document stance labels (D58).** The overall position of a document on student AI use, as shown in the app and the Excel file: **Prohibit** (AI is not allowed); **Only listed uses** (stored as `restrict`: AI is allowed only for specific uses the document lists, everything else is off limits); **Allowed with conditions** (stored as `permit`: AI is allowed in general, under conditions such as disclosure or citation); **Encourage** (the document invites or promotes AI use); **Instructor decides** (stored as `delegates`). No document takes the stance "require", so it is not shown.

**Where the atlas lives (D68).** A local multi-page website, `v2/site/index.html`, opened with `Open AI Policy Atlas.command`. Each page links to the CSV files behind it in `v2/site/data/csv`. The claude.ai findings page is superseded.

**Original wording and the policy statement.** Each statement is shown as a plain statement written by a coding agent, with the institution's original wording under it (cut by script from the saved document). When the original wording already states the policy plainly, only the original wording is shown. Each policy is shown as one plain sentence written by a Claude Sonnet worker from its grouped statements (D60), with up to 3 original wordings checked verbatim against the saved text.
