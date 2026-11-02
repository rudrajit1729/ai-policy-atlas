import json
U = []


def u(why, anchor, fs, fe, policy, actor, phase, mod, pt, us, topics, **kw):
    d = dict(why=why, anchor=anchor, frag_start=fs, frag_end=fe, policy=policy, actor=actor, phase=phase,
             modality=mod, policy_type=pt, unit_stance=us, topics=topics)
    d.update(kw)
    U.append(d)


u("The pledge says students will 'Complete all assignments and examinations according to the guidelines provided to me by my instructors', which makes the instructor's guidelines (and so any AI rules) the governing rule for all work; it is a duty on students to follow each course's rules (P78).",
  "Complete all assignments and examinations according to the guidelines provided to me by my instructors",
  "Complete all assignments and examinations", "provided to me by my instructors", None,
  "student", "general", "must", "P78", "neutral", ["default-stance", "instructor-discretion"],
  fit_note="The pledge does not mention AI; it reaches AI only by implication through instructor guidelines.")
u("The code requires instructors to 'make known, including within the course syllabus, the expectations for completing assignments and examinations at the beginning of each semester', a syllabus-statement duty (P09). It is not AI-specific, but it is the channel through which AI rules reach students.",
  "Instructors shall make known, including within the course syllabus, the expectations for completing assignments",
  "Instructors shall make known, including within", "at the beginning of each semester", None,
  "instructor", "course-start", "must", "P09", "neutral", ["syllabus-communication"],
  fit_note="Not AI-specific; covers expectations for completing assignments generally.")
u("'Instructors shall discuss these expectations with students in a manner appropriate for each course' asks instructors to talk through expectations with students beyond listing them, which is P66 rather than P09 (the syllabus duty is a separate unit).",
  "Instructors shall discuss these expectations with students in a manner appropriate for each course.",
  "Instructors shall discuss these expectations with", "appropriate for each course.", None,
  "instructor", "course-start", "must", "P66", "neutral", ["syllabus-communication"],
  fit_note="Not AI-specific; applies to assignment and exam expectations in general.")
u("The cheating definition says 'the use of artificial intelligence (AI) products in a way that violates an instructor's guidelines' is cheating, which classifies unauthorized AI use as academic misconduct (P36). P36 fits better than P06 because the sentence is about classification.",
  "the use of artificial intelligence (AI) products in a way that violates an instructor’s guidelines",
  "Cheating also consists of the", "instructor’s guidelines", None,
  "student", "when-misuse", "must-not", "P36", "prohibit", ["integrity-sanctions", "prohibited-uses"])
u("'or using it to complete coursework in a way not expressly permitted by the instructor' makes AI use cheating unless the instructor expressly permits it, which states the fallback rule when the instructor is silent (P06); P36 is already used for the preceding clause.",
  "using it to complete coursework in a way not expressly permitted by the instructor",
  "or using it to complete coursework", "permitted by the instructor", None,
  "student", "during-work", "must-not", "P06", "restrict", ["default-stance", "prohibited-uses"])
u("'It is the responsibility of the student to consult with the instructor concerning what constitutes permissible collaboration and what materials/products are allowed' puts the duty on students to ask the instructor what is allowed, which is P10 (ask first); it sits in the cheating definition that includes AI.",
  "responsibility of the student to consult with the instructor concerning what constitutes permissible collaboration",
  "It is the responsibility of the", "consulted and/or utilized.", None,
  "student", "during-work", "must", "P10", "neutral", ["syllabus-communication", "instructor-discretion"],
  fit_note="Not AI-specific; refers to materials/products and collaboration generally.")
u("Section III.H opens by declaring that use of technology 'including AI' that 'violates instructor and/or University guidelines... is prohibited'; this is a stated prohibition of unauthorized AI use as an honor-code violation, so P36 (misconduct) rather than P19 (which is about having AI produce submitted work).",
  "Use of technology (including AI) in a way that violates instructor and/or University",
  "Use of technology (including AI) in", "expressly permitted by the instructor, is prohibited.", None,
  "student", "when-misuse", "must-not", "P36", "prohibit", ["integrity-sanctions", "prohibited-uses"])
u("'How and whether instructors permit the use of AI products will vary widely from course to course, and is always subject to each instructor's authority and guidelines' hands the AI decision to instructors, so it is P04; the point is who decides.",
  "How and whether instructors permit the use of AI products will vary widely",
  "How and whether instructors permit the", "each instructor’s authority and guidelines.", None,
  "all", "general", "informs", "P04", "neutral", ["instructor-discretion", "default-stance"])
u("'Students should always check with the instructor before using these products to complete their coursework' tells students to ask before using AI, the core of P10.",
  "Students should always check with the instructor before using these products to complete their coursework.",
  "Students should always check with the", "complete their coursework.", None,
  "student", "during-work", "should", "P10", "neutral", ["instructor-discretion", "syllabus-communication"])
u("'Guidelines about these practices may change over time, so students should be sure to ask for the most up-to-date guidelines' says AI guidance is provisional; the 'ask for the most up-to-date guidelines' part is a student duty to keep informed. P54 fits the first clause and P102 the second; I chose P54 as the main point.",
  "Guidelines about these practices may change over time",
  "Guidelines about these practices may change", "most up-to-date guidelines.", None,
  "student", "over-time", "informs", "P54", "neutral", ["policy-evolution"],
  fit_note="Also tells students to ask for the latest guidelines (P102 stay informed); P54 captures only that the guidance will change.")
u("'For broader University level guidance please refer to' a UDit page points students to the university's separate AI policies and guidelines, a pointer to an institution-level framework (P56) rather than a rule.",
  "For broader University level guidance please refer to",
  "For broader University level guidance please", "policies-and-guidelines", None,
  "student", "general", "informs", "P56", "neutral", ["policy-evolution"],
  fit_note="Only refers to an external page (login required, not coded) and does not state the framework itself.")
u("The consequence clause says 'Appropriate consequences for individual academic honor code violations are determined by the course instructor... maximum consequence... is an F in the course', so penalties for honor-code violations (which include unauthorized AI use per III.A and III.H) are instructor-set up to course failure; P37 states penalties, though not AI-specific.",
  "Typically, the maximum consequence identified by the instructor is an F in the course",
  "Appropriate consequences for individual academic honor", "consequences may include dismissal from the University",
  "Instructors determine the consequences for individual academic honor code violations; typically the maximum consequence identified by the instructor is an F in the course, and the dean may add consequences up to dismissal.",
  "instructor", "when-misuse", "informs", "P37", "neutral", ["integrity-sanctions"],
  fit_note="General honor-code penalties, not AI-specific; they apply to AI misuse because III.A and III.H classify it as an honor-code violation.")
u("'Instructors are required to investigate all suspected violations of academic dishonesty and report all those confirmed' sets a mandatory reporting procedure for honor-code violations including AI misuse, which is the formal reporting procedure (P81).",
  "Instructors are required to investigate all suspected violations of academic dishonesty and report all",
  "Instructors are required to investigate all", "confirmed to have occurred", None,
  "instructor", "when-misuse", "must", "P81", "neutral", ["integrity-sanctions"],
  fit_note="Not AI-specific; applies to all academic dishonesty.")
u("The procedure requires the instructor to notify the student and 'make a reasonable effort to meet with the student... within five business days of the initial notification to discuss the situation', so the student is spoken with before the report goes to the dean; this is talking with the student first (P57).",
  "The instructor will make a reasonable effort to meet with the student",
  "The instructor will make a reasonable", "discuss the situation.", None,
  "instructor", "when-misuse", "must", "P57", "neutral", ["integrity-sanctions"],
  fit_note="Not AI-specific; the meeting is part of the general honor-code procedure.")
u("The code lets students contest findings: 'A student may appeal the filing of an Honor Code Violation Incident Report and/or any consequences', a right to respond in integrity cases (P64), which includes AI-misuse cases.",
  "A student may appeal the filing of an Honor Code Violation Incident",
  "A student may appeal the filing", "consequences identified by the instructor.", None,
  "student", "when-misuse", "may", "P64", "neutral", ["integrity-sanctions"],
  fit_note="Not AI-specific; general honor-code appeal right.")
u("'Dean's offices are required to review and maintain records of all received Incident Report Forms' names the dean's office as the body that reviews and keeps records of honor-code incidents, including AI cases, which is P80 (who owns and enforces), though the dean's role is general.",
  "Dean’s offices are required to review and maintain records of all received Incident Report Forms",
  "Dean’s offices are required to review", "academic honor code violations.", None,
  "admin", "when-misuse", "must", "P80", "neutral", ["integrity-sanctions"],
  fit_note="Not AI-specific; general honor-code records duty.")

d = json.load(open('v2/collect/dayton.json'))
c = d['documents'][0]
doc = {k: c[k] for k in ("id", "layer", "unit", "course", "title", "url", "date_or_term")}
doc.update(
    stance_why="The Honor Code does not set its own AI stance. It makes AI use that 'violates an instructor's guidelines' or is 'not expressly permitted by the instructor' a form of cheating, and says 'How and whether instructors permit the use of AI products will vary widely from course to course'. This delegates the decision to instructors, with unauthorized use treated as misconduct, so the stance is delegates (not restrict, because it gives no university-wide default rule or defined uses and leaves permission to each instructor).",
    stance="delegates", tiers=[],
    summary="The university-wide Academic Honor Code for undergraduates classes unauthorized AI use as cheating and leaves the decision on whether AI is allowed to each instructor. Students must check with the instructor first and ask for current guidance; broader UDit guidance sits behind a login and was not read. The remainder is general honor-code procedure that applies to AI cases.",
    units=U)
out = dict(university=d['university'], slug='dayton', state=d['state'], type=d['type'], searched=d['searched'],
           documents=[doc], new_types=[],
           notes="UDit AI policies and guidelines page (porches.udayton.edu) requires login and was not available; only the Honor Code was coded. Units from sections IV-V are general honor-code rules that cover AI misuse only through the classification in III.A and III.H, flagged with fit_note. Later appeal tiers (VI.B-F) were treated as repeats of the appeal right and not coded separately.")
json.dump(out, open('v2/run/coderA/dayton.json', 'w'), indent=1, ensure_ascii=False)
