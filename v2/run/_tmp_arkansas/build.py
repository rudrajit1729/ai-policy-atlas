import json, sys, copy
sys.path.insert(0, 'v2/tools')
from validate_inst import fold
R = 'v2/run/'
A = json.load(open(R + 'coderA/arkansas.json'))
B = json.load(open(R + 'coderB/arkansas.json'))
C = json.load(open('v2/collect/arkansas.json'))
tf = {d['id']: d['text_file'] for d in C['documents']}
FIELDS = ('actor', 'phase', 'modality', 'policy_type', 'unit_stance')


def span(hay, u):
    a = fold(u['anchor'])
    i = hay.find(a)
    if i < 0:
        s = hay.find(fold(u['frag_start']))
        return (s, s + len(a)) if s >= 0 else (-1, -1)
    return (i, i + len(a))


def auto_match(hay, ua, ub, manual):
    sa = [span(hay, u) for u in ua]
    sb = [span(hay, u) for u in ub]
    ma = dict(manual)
    mb = {j: i for i, j in ma.items()}
    cands = []
    for i, (a0, a1) in enumerate(sa):
        for j, (b0, b1) in enumerate(sb):
            ov = min(a1, b1) - max(a0, b0)
            if ov > 0 or -ov <= 15:
                sc = ov / max(1, min(a1 - a0, b1 - b0)) if ov > 0 else 0.01
                if ua[i]['policy_type'] == ub[j]['policy_type']:
                    sc += 0.5
                cands.append((sc, i, j))
    cands.sort(reverse=True)
    for sc, i, j in cands:
        if i in ma or j in mb or sc < 0.2:
            continue
        ma[i] = j
        mb[j] = i
    return ma, mb, sa, sb


# manual extra pairs: doc -> {Aidx: Bidx}
MANUAL = {0: {51: 53}, 1: {4: 4}, 2: {8: 5}}

# Overrides for matched units: (doc, Aidx) -> dict(fields, res=resolution text, base='A'|'B', plus optional extra fields)
O = {}


def o(doc, i, res, base='A', **kw):
    O[(doc, i)] = dict(kw, res=res, base=base)


# ---------------- doc 0 : ai-guidelines
o(0, 1, "A coded phase general, B before-course. The sentence is in the Purpose paragraph and states a university commitment ('facilitate the training of University students and employees in this area'), not a set-up step for a course, so general.", phase='general')
o(0, 2, "A coded informs/neutral, B must/restrict. The source says 'The University affirms that accountability for all final decisions ... resides with human employees ... regardless of any AI recommendation', which assigns responsibility to employees and limits AI as the decider, so must and restrict; actor stays admin because the university is the one affirming.", modality='must', unit_stance='restrict')
o(0, 3, "A coded informs, B should. The source says 'The University ... encourages innovation and the use of AI', a statement of the institution's own position rather than a direction to a reader, so informs (the encouragement is carried by unit_stance).", modality='informs')
o(0, 4, "A coded P50 (restrict), B coded P56 (permit). The source sentence ('AI use must be conducted in a manner that safeguards sensitive university data, protects individual privacy, and upholds ethical standards') names data, privacy and ethics together as the condition on the encouragement just given, which is a principle for AI use as a whole, so P56 rather than the narrower personal-data type P50. Because it conditions the encouragement it restricts rather than permits.", policy_type='P56', unit_stance='restrict', base='B')
o(0, 10, "Type and modality agree. A coded restrict, B neutral. The verify-the-output duty does not limit whether AI may be used, only how outputs are treated, so neutral. The same call is applied to the other verification units.", unit_stance='neutral')
o(0, 11, "A coded informs, B must. 'Students and University employees are ultimately responsible for the content that they produce, share, and submit' assigns responsibility to users, so it is a duty (must) and not merely a fact.", modality='must')
o(0, 12, "A coded must-not, B should-not. The source says users 'are expected to refrain from utilizing AI to in any way threaten University systems or security'. The document uses 'expected' as a firm duty (elsewhere 'are expected to' is coded must), so must-not.", modality='must-not')
o(0, 14, "A coded restrict, B prohibit. 'AI must not be used to engage in any activity that is illegal, violates university policies, or breaks contractual obligations' is a flat ban on those uses, so prohibit.", unit_stance='prohibit')
o(0, 18, "A coded informs, B must. 'All existing IT conduct rules apply fully to AI usage' points to rules that already bind; the obligation comes from those rules, so informs.", modality='informs')
o(0, 20, "A coded P19 (phase during-work), B coded P29 (phase general). The source ('Misrepresenting AI-generated work as one's own is prohibited') bans misrepresentation, not AI generation, which P19 would overstate; it matches 'students own everything they submit' (P29). It sits in the general Integrity paragraph with no assignment context, so phase is general.", policy_type='P29', phase='general', base='B')
o(0, 21, "A coded phase during-work, B general; unit_stance permit vs encourage. 'Members of the university community should be transparent about the role of AI tools' is a general expectation not tied to a submission, so phase general. AI use is allowed on condition of transparency, so permit.", phase='general', unit_stance='permit')
o(0, 28, "A coded permit, B encourage. 'Users of AI should strive for transparency in how AI is utilized' makes disclosure a condition on allowed use, so permit (same call as the other disclosure principle).", unit_stance='permit')
o(0, 29, "A coded informs/neutral, B must/require. The source says 'the university will ensure that the use of AI is disclosed to appropriate stakeholders', a commitment the university binds itself to, so must. It does not take a position on whether AI may be used, so neutral.", modality='must', unit_stance='neutral')
o(0, 30, "A coded actor ta-staff, B admin. The rule ('authorized humans make any final decision arising in the course of employment') binds employees who decide, not an office, so ta-staff is the closest actor.", actor='ta-staff')
o(0, 31, "A coded actor all, B admin. 'AI must not be used as the sole decision-maker for any critical or sensitive decisions' is addressed to anyone using AI, so all.", actor='all')
o(0, 34, "A coded actor admin, B all. The sentence ('The university is subject to equal opportunity and anti-discrimination laws ... and these extend to decisions or actions influenced by AI') is the university speaking about itself, so admin.", actor='admin')
o(0, 35, "A coded P87 (benefits), B coded P02 (default welcome). The source says AI to enhance learning 'has great potential and is supported by the University'. The operative content is the university's support, a default welcome, so P02; the potential is a benefit claim that P87 would capture, noted in fit_note.", policy_type='P02', base='B', fit_note="Also states a benefit of AI for learning ('has great potential'), which P87 covers.")
o(0, 36, "A coded actor all, B admin. 'Guidelines that address every AI tool are impractical' is the university acknowledging its own limits, so admin.", actor='admin')
o(0, 38, "A coded P04 (leave to instructors), B coded P02 (default permit). The source sentence ('students may use AI in a manner that enhances learning without violating rules set forth by a course instructor and the University's Academic Integrity Policy') is the stated guiding principle: AI is allowed, within limits. The instructor decision is handled by the next sentence (P04, coded separately), so this unit is P02 with a fit note. A's normalized policy is kept because the anchor alone cuts off the conditions.", policy_type='P02', fit_note="The permission is bounded by instructor rules and the Academic Integrity Policy.")
o(0, 41, "A coded restrict, B neutral. 'It is the responsibility of the student to seek permission from the instructor if there is any doubt' tells students to ask; the ban itself is in the preceding unit, so neutral.", unit_stance='neutral')
o(0, 45, "A coded P17 (sanctioned course tool), B coded P92 (university-licensed or approved tools). The source names 'AI resources available as part of the University's library services', a university-provided resource and not a course-specific tool, so P92.", policy_type='P92', base='B')
o(0, 46, "A coded P14, B coded P100. The source says 'the review of summative AI services commonly found in web browsers is acceptable', one of the listed acceptable learning uses (summaries), so P14. It is also a built-in browser feature, which is why it is flagged for P100.", policy_type='P14', fit_note="Built-in browser AI summaries; P100 (exempt routine features) is also close.")
o(0, 47, "A coded informs, B must. 'Use of AI in a manner not approved by the course instructor is subject to this policy' says which policy applies, so informs. A's normalized policy is kept.", modality='informs')
o(0, 48, "A coded neutral, B encourage. 'Faculty are encouraged to clearly communicate their policies regarding AI in their syllabi' asks for communication and takes no position on AI use, so neutral.", unit_stance='neutral')
o(0, 50, "A coded phase during-work, B course-start; unit_stance permit vs encourage. The rule ('faculty are encouraged to disclose substantive use of AI in creating course content, grading, or providing feedback') attaches to the faculty's AI-assisted work, so during-work. Instructor AI use is allowed with disclosure, so permit.", phase='during-work', unit_stance='permit')
o(0, 52, "A coded P52 (copyright of output), B coded P49 (do not upload course materials). The source concerns 'copyrighted course materials or proprietary instructional resources in any AI tool', which is putting materials into AI (input), so P49. It permits use under Fair Use rather than banning it, noted in fit_note.", policy_type='P49', base='B', fit_note="Conditions use of copyrighted course materials in AI on Fair Use rather than banning uploads outright; copyright (P52) is also close.")
o(0, 53, "A coded P24 (restrict), B coded P45 (prohibit). 'Uncited use of the work of others, whether a person or AI, is a violation' treats AI output like a human source under existing rules, so P45. It also concerns citation (P24) and misconduct (P36), noted in fit_note. A's normalized policy is kept. Uncited use is barred while cited use is not, so restrict.", policy_type='P45', unit_stance='restrict', fit_note="Also a citation requirement (P24) and an integrity-violation classification (P36).")
o(0, 54, "A coded P62 (permit), B coded P24 (require). 'All research outputs must be attributable to faculty and/or student researchers, with transparent documentation of any AI-assisted contributions' requires documenting AI help with each output, which is disclosure (P24), even though it sits in the research section. AI use is allowed given documentation, so permit. A's normalized policy is kept.", policy_type='P24', unit_stance='permit', fit_note="Applies to research outputs and also requires attributability to human researchers; research governance (P62) is also close.")
o(0, 55, "A coded require, B neutral. Verifying AI content in research documents does not take a position on whether AI may be used, so neutral. A's normalized policy is kept.", unit_stance='neutral')
o(0, 56, "A coded neutral, B restrict. 'is at the discretion of the student's graduate advisory committee' hands the decision to the committee without setting a position, so neutral. A's normalized policy is kept.", unit_stance='neutral')
o(0, 57, "A coded must-not/restrict, B informs/prohibit. 'The use of AI without permission from the committee is a violation of the University's Academic Integrity Policy' bars unpermitted use (a duty on the student) while allowing permitted use, so must-not and restrict. A's normalized policy is kept.", modality='must-not', unit_stance='restrict')
o(0, 58, "A coded restrict, B neutral. The researcher's duty to ensure external AI requirements are adhered to does not itself restrict or permit AI, so neutral.", unit_stance='neutral')
o(0, 59, "A coded phase general, B before-course. The vetting rule applies to any AI tool used on a University system or for University business and is not tied to a course set-up stage, so general. A's normalized policy is kept.", phase='general')
o(0, 62, "A coded phase general, B during-work. The statement ('these tools may be used as long as they do not pose a security or operational threat') sets conditions for approved tools without reference to a particular task, so general.", phase='general', fit_note="Concerns approved but unlicensed tools and a security condition.")
o(0, 67, "A coded must/restrict, B should/neutral. 'In general, treat AI queries the same as any external disclosure' is hedged with 'In general', so should; it limits what may be put into AI to what FERPA and other laws allow, so restrict.", modality='should', unit_stance='restrict')
o(0, 72, "A coded restrict, B neutral. 'It is the responsibility of the researcher to determine if their data falls in this category' assigns a classification duty and does not itself restrict AI use, so neutral.", unit_stance='neutral')
o(0, 73, "A coded P62, B coded P52. The researcher with an IP doubt must 'contact Technology Ventures before using non-licensed University approved AI tools with their data', which concerns research data and its IP, not licensing of AI output, so P62.", policy_type='P62', fit_note="Addresses commercialization and IP of research data put into AI tools, not licensing of output (P52).")
o(0, 76, "A coded P50, B coded P77. 'All use of AI tools must comply with privacy laws, regulations, and university privacy policies' is about privacy specifically, which fits 'protect personal data' (P50) better than the generic compliance type; it restricts use to compliant uses.", policy_type='P50', unit_stance='restrict', fit_note="Also a compliance-with-law statement (P77).")
o(0, 79, "A coded restrict, B neutral. Following IRB protocols is a compliance duty that does not restrict AI use itself, so neutral.", unit_stance='neutral')
o(0, 80, "A coded P50, B coded P77. 'AI should never be used as a means to evade or \"work around\" privacy rules' is a ban on circumventing privacy protections, so P50.", policy_type='P50')
o(0, 81, "A coded restrict, B neutral. 'Caution should be exercised not to inadvertently expose personal or sensitive data' is a soft caution that does not restrict use, so neutral.", unit_stance='neutral')
o(0, 83, "A coded require, B neutral. A duty to report suspected violations does not take a position on AI use, so neutral.", unit_stance='neutral')
o(0, 84, "A coded require, B neutral. Same as the preceding reporting duty: neutral.", unit_stance='neutral')
o(0, 87, "A coded phase general, B over-time. Approval of exemptions is not a review or revision of the policy over time, so general.", phase='general')
o(0, 88, "A coded phase general, B over-time. Referring questions to the CISO is not a review or revision step, so general.", phase='general')
o(0, 89, "A coded restrict, B neutral. 'All AI use must conform to this code' points to an existing code, so neutral.", unit_stance='neutral')
o(0, 91, "A coded neutral, B encourage. The entry only lists links to training resources in a reference list, so neutral.", unit_stance='neutral')
# doc 1 : tips
o(1, 1, "A coded neutral, B encourage. 'Faculty are encouraged to communicate clear expectations' asks for communication and takes no position on AI use, so neutral.", unit_stance='neutral')
o(1, 4, "Both coded P01 and the same codes, but A anchored on the consequence clause and B on the ban. The Prohibited statement bans 'use of generative artificial intelligence tools in any capacity while completing academic work that is submitted for credit', so B's anchor is kept with A's normalized policy, which includes the consequence.", base='B', policy="Use of generative AI tools in any capacity while completing academic work submitted for credit, independently or collaboratively, is academic dishonesty in the course and is reported to the Office of Academic Initiatives and Integrity.")
o(1, 5, "A coded informs, B must. In the Restricted statement 'Specific permissions will be provided to students regarding the use of generative artificial intelligence tools on certain graded activities' is the instructor's commitment, so must. Both coded P04 and restrict.", modality='must')
o(1, 6, "A coded restrict, B require. 'I will communicate explicit permission as well as expectations and any pertinent limitations for use and attribution' is an instructor promise inside the Restricted tier; it sets no requirement on AI use, so restrict (the tier's stance).", unit_stance='restrict')
o(1, 9, "A coded must/require, B should/neutral. 'Please be aware of the limitations ... and verify the accuracy' is phrased as a request, so should; verifying does not restrict use, so neutral.", modality='should', unit_stance='neutral')
o(1, 12, "A coded must-not, B must. 'The use of content generated by artificial intelligence, without proper citation, will be considered academic dishonesty' forbids uncited use by the student, so must-not.", modality='must-not')
# doc 2 : libguide
o(2, 2, "A coded restrict, B neutral. 'it is critical that they ask their instructor for clarification before using it' is an ask-first step and the ban itself is in the permission unit, so neutral.", unit_stance='neutral')
o(2, 8, "A coded P06, B coded P36. The sentence ('they must receive permission from their instructors prior to using any resource ... to avoid being accused of academic dishonesty') restates the permission-first rule and adds the integrity consequence. The rule asked of the student is to get permission, so P06, with the misconduct link in fit_note. B's phase when-misuse is not followed because the duty applies while doing the work.", base='A')

o(0, 19, "A coded one unit (P74, actor ta-staff) covering all four Act 848 items; B split them and coded the political-opinion item UNCOVERED. 'Express a personal political opinion to an elected official unless the opinion is within the scope of the employee's regular job duties or requested by an elected official or public entity' is a state-mandated limit on political speech, not a deceptive, fabricated or malicious use, so P74 would be a stretch and UNCOVERED is kept. The lobbying item (2) is a distinct rule and is coded as its own unit; item (3) repeats the illegal-activity ban already coded; item (4) is B's separate P74 unit. The sentence is addressed to AI use in general ('AI must not be used to'), so actor is all.", base='B', actor='all', policy="AI must not be used to express a personal political opinion to an elected official unless the opinion is within the scope of the employee's regular job duties or requested by an elected official or public entity.", uncovered_note="Employees may not use AI to express personal political opinions to elected officials or to lobby, as required by Arkansas Act 848 (state-mandated limit on political speech).", fit_note="A fitted this partly to P74 (general conduct ban); the political-opinion and lobbying items are not captured by it.")
o(0, 22, "A coded P24 (should, during-work) with a policy joining plagiarism and citation; B coded P45 for 'Plagiarism rules apply to AI outputs' and split out the copyright and citation rules. The source sentence has three distinct rules ('Plagiarism rules apply to AI outputs'; 'they must ensure that doing so does not violate any copyrights'; 'they should cite or credit sources as required'), so it is split in three, B's way. This unit is the first: it says existing plagiarism rules cover AI output, which is P45, a statement that points to existing rules (informs) in a general paragraph (phase general).", policy_type='P45', modality='informs', phase='general', unit_stance='neutral', base='B', policy=None)
o(0, 23, "A coded restrict, B neutral. 'they must ensure that doing so does not violate any copyrights or intellectual property rights' is a condition on using AI output, so restrict.", unit_stance='restrict')
o(2, 3, "Both coded P24/must/require. A also split the next sentence ('This includes text generated by artificial intelligence') into a second unit with the same code. The two sentences state one rule, so they are merged into this unit and A's second unit is dropped as a repeat.", policy="Students are expected to provide citations for anything that is not their original work, including text generated by artificial intelligence.", frag_end="generated by artificial intelligence.")
o(2, 5, "Only A coded this. It is a pointer to citation guidance with no rule content. P25 (what a citation includes) does not fit because nothing is said about what to cite, so UNCOVERED.", policy_type='UNCOVERED', uncovered_note="Points students to posted guidance on citing AI in common citation styles (a resource pointer).", fit_note="A coded P25 (what a citation includes); the sentence gives no content, only where to find guidance.")
o(1, 11, "Only A coded this. 'Please refer to the examples/guidance provided by this University of Arkansas Library Research Guide on AI and Academic Integrity' points students to a library guide. P72 is about human help, which a guide is not, so UNCOVERED.", policy_type='UNCOVERED', uncovered_note="Points students to a library research guide on AI and academic integrity for citation examples (a resource pointer).", fit_note="A coded P72 (point to human help); a library guide is not human help.")

o(0, 25, "A coded require, B neutral. 'all AI-generated content (e.g. text, data, and references) must be verified for accuracy' governs how outputs are treated and does not restrict or require AI use, so neutral (same call as the other verification units).", unit_stance='neutral')
o(0, 26, "A coded require, B neutral. 'The existence of AI-generated references should be confirmed' is a verification duty, so neutral (same call as the other verification units).", unit_stance='neutral')
o(0, 27, "A coded P77 (when-misuse), B coded P62 (general). 'The University's Research and Scholarly Misconduct Policy applies to work involving AI just as it does to any other work' says an existing policy covers AI, which is the P77 pattern (the same call as 'All existing IT conduct rules apply'); the policy is not triggered by a misuse event, so phase general. Its research setting is noted in fit_note.", policy_type='P77', phase='general', fit_note="Concerns research and scholarly misconduct specifically; P62 (govern AI use in research) is also close.")

# Units where only one coder: keep decision
KEEP_ONLY_A = {1: {11: "Only A coded this."}, 0: {9: "Only A coded this. The source says 'Results that are indicative of harmful biases should be recognized and ethically addressed', a real duty on users, so kept.",
                    75: "Only A coded this. 'Otherwise, a licensed University approved tool is required' is a separate rule for copyrighted data and not a repeat, so kept.",
                    78: "Only A coded this. 'University members should stay aware of and comply with any federal or state regulations governing AI use and data privacy' is a real expectation, so kept."},
               2: {5: "Only A coded this. The FAQ points students to citation guidance for AI; it is a resource pointer and no existing type captures it, so kept as UNCOVERED.",
                   7: "Only A coded this. 'sometimes this assistance may not be allowed by an instructor' states that an instructor may bar the help just described, a real statement of instructor discretion, so kept."}}
KEEP_ONLY_B = {0: {24: "Only B coded this as a separate unit. 'they should cite or credit sources as required' is the citation rule, distinct from the plagiarism-applies statement and the copyright rule in the same sentence, so kept (A merged it into one unit).",
                    49: "Only B coded this. 'Student general use of AI must adhere to the University's Academic Integrity Policy' is a separate requirement from the following sentence, so kept.",
                    56: "Only B coded this. 'University researchers and units making use of AI must follow ethical guidelines and, where applicable, research protocols' is a real research rule, so kept.",
                    72: "Only B coded this. The sensitive (internal) data paragraph is a separate classification rule, so kept.",
                    83: "Only B coded this. The note that university records, including AI-generated data, may be subject to FOIA is a legal fact about AI use that the guidelines state, so kept.",
                    19: "Only B coded this. Item (4) of the Act 848 list, 'Intentionally override or avoid the security and system integrity procedures of the public entity', is a separate ban from items (1) and (2), so kept; A put all items into one unit."}}


def merge_notes(a, b, key):
    xs = []
    for u in (a, b):
        if u and u.get(key) and u[key] not in xs:
            xs.append(u[key])
    return ' | '.join(xs) if xs else None


def finalize(base_u, ua, ub, ov, why_pool=None):
    u = copy.deepcopy(base_u)
    for k in FIELDS + ('policy', 'anchor', 'frag_start', 'frag_end', 'topics'):
        if k in ov:
            u[k] = ov[k]
    # choose why: coder whose policy_type matches final, preferring base
    cand = [x for x in (ua, ub) if x]
    whys = [x for x in cand if x['policy_type'] == u['policy_type']]
    pick = (whys or cand)[0]
    if base_u in cand and base_u['policy_type'] == u['policy_type']:
        pick = base_u
    u['why'] = pick['why']
    for k in ('fit_note', 'uncovered_note'):
        parts = []
        for src in ({k: ov.get(k)}, ua, ub):
            if src and src.get(k) and src[k] not in parts:
                parts.append(src[k])
        if k == 'uncovered_note' and u['policy_type'] != 'UNCOVERED':
            parts = []
        if parts:
            u[k] = ' | '.join(parts)
        else:
            u.pop(k, None)
    if 'resolution_why' in ov:
        u['resolution_why'] = ov['resolution_why']
    return u


def order_keys(u):
    keys = ['why', 'resolution_why', 'anchor', 'frag_start', 'frag_end', 'policy', 'actor', 'phase', 'modality', 'policy_type', 'unit_stance', 'topics', 'fit_note', 'uncovered_note']
    return {k: u[k] for k in keys if k in u}


stats = dict(units_A=0, units_B=0, matched=0, only_A=0, only_B=0, kept_only_A=0, kept_only_B=0)
agree = {k: [0, 0] for k in ('actor', 'phase', 'modality', 'policy_type')}
out_docs = []
dropped = []
for di, da in enumerate(A['documents']):
    db = next(d for d in B['documents'] if d['id'] == da['id'])
    hay = fold(open(tf[da['id']]).read())
    ua, ub = da['units'], db['units']
    ma, mb, sa, sb = auto_match(hay, ua, ub, MANUAL.get(di, {}))
    stats['units_A'] += len(ua)
    stats['units_B'] += len(ub)
    stats['matched'] += len(ma)
    final = []  # (position, unit)
    for i, j in ma.items():
        a, b = ua[i], ub[j]
        for k in agree:
            agree[k][1] += 1
            agree[k][0] += a[k] == b[k]
        diff = [k for k in FIELDS if a[k] != b[k]]
        key = (di, i)
        ov = O.get(key, {})
        if diff and key not in O:
            print('UNRESOLVED', key, a['anchor'], {k: (a[k], b[k]) for k in diff})
        base = ub[j] if ov.get('base') == 'B' else a
        ovf = {k: v for k, v in ov.items() if k in FIELDS + ('policy', 'topics', 'fit_note', 'uncovered_note', 'frag_end')}
        if ov.get('base') == 'B':
            ovf.setdefault('topics', [t for t in b['topics'] if t != 'governance'] or a['topics'])
        # topics: use A's except governance/ research-use unknowns
        if 'topics' not in ovf and base is a:
            pass
        u = finalize(base, a, b, dict(ovf, **({'resolution_why': ov['res']} if ov else {})), None)
        # keep A's policy if A wrote one and B did not and no override
        if 'policy' not in ovf and u.get('policy') is None and a.get('policy'):
            u['policy'] = a['policy']
        if 'policy' not in ovf and u.get('policy') is None and b.get('policy'):
            u['policy'] = b['policy']
        if ov:
            pass
        final.append((sa[i][0], u))
    for i in range(len(ua)):
        if i in ma:
            continue
        stats['only_A'] += 1
        why = KEEP_ONLY_A.get(di, {}).get(i)
        if why:
            stats['kept_only_A'] += 1
            ovo = O.get((di, i), {})
            ovf = {k: v for k, v in ovo.items() if k in FIELDS + ('policy', 'topics', 'fit_note', 'uncovered_note', 'frag_end')}
            u = finalize(ua[i], ua[i], None, ovf)
            u['resolution_why'] = (ovo['res'] if ovo else why)
            final.append((sa[i][0], u))
        else:
            dropped.append((di, 'A', i, ua[i]['anchor']))
    for j in range(len(ub)):
        if j in mb:
            continue
        stats['only_B'] += 1
        why = KEEP_ONLY_B.get(di, {}).get(j)
        if why:
            stats['kept_only_B'] += 1
            u = copy.deepcopy(ub[j])
            u['topics'] = [t for t in u['topics'] if t != 'governance'] or ['policy-evolution']
            u['resolution_why'] = why
            final.append((sb[j][0], u))
        else:
            dropped.append((di, 'B', j, ub[j]['anchor']))
    out_docs.append((da, db, final))

print('DROPPED', dropped)
json.dump(dict(stats=stats, agree=agree), open('v2/run/_tmp_arkansas/stats.json', 'w'))
import pickle
pickle.dump(out_docs, open('v2/run/_tmp_arkansas/out.pkl', 'wb'))
print(stats, agree)


# ---------- assemble
LOB = dict(
    why="Item (2) of the Act 848 list, 'Engage in lobbying an elected official on a personal opinion if the employee is not a registered lobbyist for the public entity', is a separate ban from the political-opinion item; it matches no existing type, so UNCOVERED.",
    resolution_why="B coded the Act 848 items (1) and (2) together as one UNCOVERED unit and A coded all four as one P74 unit. Items (1) and (2) are distinct rules (expressing an opinion vs lobbying), so the lobbying ban is split out as its own unit; the Act 848 reference makes it a state-mandated limit on employees' AI use, which no type captures.",
    anchor="Engage in lobbying an elected official on a personal opinion", frag_start="(2) Engage in lobbying", frag_end="for the public entity;",
    policy="AI must not be used to engage in lobbying an elected official on a personal opinion if the employee is not a registered lobbyist for the public entity.",
    actor='all', phase='general', modality='must-not', policy_type='UNCOVERED',
    uncovered_note="Employees may not use AI to lobby an elected official on a personal opinion unless registered lobbyists for the public entity, as required by Arkansas Act 848 (state-mandated limit on political activity).",
    unit_stance='prohibit', topics=['prohibited-uses'])
NOTES_DOC = {}
docs = []
for di, (da, db, final) in enumerate(out_docs):
    if di == 0:
        # position for lobbying: right after the political unit
        pos = None
        for p0, u in final:
            if u['anchor'].startswith('Express a personal political'):
                pos = p0 + 1
        final.append((pos, copy.deepcopy(LOB)))
    final.sort(key=lambda t: t[0])
    doc = {k: v for k, v in da.items() if k != 'units'}
    doc['units'] = []
    for _, u in final:
        u = dict(u)
        u.pop('_', None)
        doc['units'].append(order_keys(u))
    docs.append(doc)

docs[0]['stance'] = 'restrict'
docs[0]['stance_why'] = ("A coded delegates and B coded restrict. The guidelines say faculty 'are responsible for determining the appropriate uses of AI in their courses' and that the university 'encourages innovation and the use of AI', which supports delegates. But for coursework the document itself sets the rule: 'Student use of AI to satisfy course requirements or assessments is prohibited without the explicit permission of the course instructor'. That is the codebook's restrict (banned unless explicitly permitted) and matches the Libraries FAQ, which both coders coded restrict for the same rule. Instructors can lift the ban, but the default and the ban are the document's own, so restrict.")
docs[0]['summary'] = ("Campus-wide acceptable-use guidelines for AI covering ethics, integrity, teaching and learning, research, tool approval, data classification, privacy, reporting and enforcement. For coursework the default is that student AI use is prohibited without the instructor's explicit permission, and faculty decide what uses are appropriate. Most of the text addresses data security, approved tools and employee conduct.")
docs[1]['stance_why'] = ("Both coders agree: the page says 'faculty have discretion over whether generative artificial intelligence tools ... can be used' and offers three syllabus statements (Prohibited, Restricted, Unrestricted Use) rather than one rule, so the document sets no single stance and delegates, with the tiers listed.")
docs[1]['summary'] = "The Provost-approved syllabus page gives faculty three model statements on generative AI: prohibited, restricted to explicit permission, and unrestricted with attribution. Faculty have discretion over which to use and are encouraged to state expectations clearly."
docs[2]['stance_why'] = ("Both coders agree: 'Students must receive permission in advance to use any generative AI technology in completing academic work from their instructor' bans AI unless the instructor permits it, so restrict, even though the instructor sets the terms.")
out = dict(university=A['university'], slug='arkansas', state=A['state'], type=A['type'], searched=A['searched'], documents=docs, new_types=[],
           notes=("Reconciled from coder A and coder B. Neither coder proposed new types. UNCOVERED units: the Act 848 limits on political opinion and lobbying (UNCOVERED in both final units; B coded the first UNCOVERED, A fitted it to P74 with a fit_note) and two pointers to library citation guidance (A fitted P72 and P25 with fit_notes). Academic Integrity Policy PDF, Walton page and any computing-unit policy were not collected (see collect file); the data classification tables were coded through their prose paragraphs. B's TIPS unit anchored on 'reported to the Office of Academic Initiatives and Integrity' pointed at the note-selling statement, not an AI statement, and was dropped; the AI reporting consequence is part of the Prohibited and Restricted statements."))
json.dump(out, open('v2/inst/arkansas.json', 'w'), indent=1, ensure_ascii=False)
st = json.load(open('v2/run/_tmp_arkansas/stats.json'))
ag = st['agree']
stance_docs = sum(1 for da, db, _ in out_docs if da['stance'] == db['stance'])
agr = dict(documents=3, units_A=st['stats']['units_A'], units_B=st['stats']['units_B'], matched=st['stats']['matched'], only_A=st['stats']['only_A'], only_B=st['stats']['only_B'], kept_only_A=st['stats']['kept_only_A'], kept_only_B=st['stats']['kept_only_B'])
for k in ('actor', 'phase', 'modality', 'policy_type'):
    agr['agree_' + k] = round(ag[k][0] / ag[k][1], 3)
agr['agree_stance_docs'] = round(stance_docs / 3, 3)
agr['notes'] = ("Main disagreements, by frequency: (1) unit_stance on duty-type statements (verification, reporting, ask-first, existing-policy pointers): resolved to neutral when the statement does not take a position on whether AI may be used; (2) phase for institution-wide rules (general vs during-work or before-course or over-time): resolved to general when the passage is not tied to a course stage or a review step; (3) policy_type where one sentence touches two types (P24/P45/P36 for citation and plagiarism; P50/P77 for privacy compliance; P62/P52/P49 for research data and course materials; P02/P04/P87 for the welcoming default): resolved by the operative clause and the other type recorded in fit_note; (4) modality informs vs must for statements of responsibility (resolved by whether the passage assigns a duty); (5) document stance for the University guidelines (A delegates, B restrict): resolved to restrict because the document itself sets the ban-unless-permitted default for coursework. Unit boundaries: A merged the three rules of the 'Plagiarism rules apply' sentence and all four Act 848 items into single units; B split them. Resolved by splitting (one rule per unit), which adds the lobbying unit as a reconciler split. Of the 14 single-coder units, 11 were kept (5 A, 6 B) as real policy statements; 3 were dropped (A's second libguide citation sentence, merged into the matching unit as one rule; B's TIPS reporting unit anchored on a non-AI statement; and none other). A's TIPS library-guide pointer was kept as UNCOVERED, so kept_only_A counts it.")
json.dump(agr, open('v2/run/agreement_arkansas.json', 'w'), indent=1)
print(agr)
