import json
U = []


def u(why, anchor, fs, fe, policy, actor, phase, mod, pt, us, topics):
    U.append(dict(why=why, anchor=anchor, frag_start=fs, frag_end=fe, policy=policy, actor=actor,
                  phase=phase, modality=mod, policy_type=pt, unit_stance=us, topics=topics))


u("Defines AI misuse as a violation: 'Using artificial intelligence or automated technologies in violation of University, program, course or instructor requirements'. It classes unauthorized or misrepresented AI use as an academic integrity violation, so P36; it binds students and applies when misuse occurs.",
  "Using artificial intelligence or automated technologies in violation of University, program, course or instructor requirements",
  "Using artificial intelligence or automated", "other prohibited conduct", None, "student", "when-misuse", "must-not", "P36", "restrict",
  ["integrity-sanctions", "prohibited-uses"])
u("Lists specific forms of misuse: 'misrepresentation of AI-generated work, fabrication or falsification of information, or use of AI to facilitate other prohibited conduct'. Chosen P36 (misconduct classification) because it names violations, not disclosure rules.",
  "misrepresentation of AI-generated work, fabrication or falsification of information",
  "Using artificial intelligence or automated", "other prohibited conduct", None, "student", "when-misuse", "must-not", "P36", "prohibit",
  ["integrity-sanctions", "disclosure-citation"])
u("Principle for AI in education: 'must be guided by ethical principles and academic integrity'. It is an institution-level framing statement, so P56.",
  "must be guided by ethical principles and academic integrity",
  "The use of artificial intelligence", "see below for more information.", None, "all", "general", "must", "P56", "neutral",
  ["default-stance", "policy-evolution"])
u("States 'encourages students to develop fluency in artificial intelligence', a career/development rationale for AI use, so P44; the university welcomes AI.",
  "encourages students to develop fluency in artificial intelligence",
  "Embry-Riddle Aeronautical University encourages students", "academic and professional development.", None, "student", "general", "informs", "P44", "encourage",
  ["ai-literacy-career", "learning-rationale"])
u("'students are expected to engage thoughtfully and responsibly with these technologies' is a general expectation of responsible use, a framework principle (P56) rather than a specific permitted or prohibited use.",
  "students are expected to engage thoughtfully and responsibly with these technologies",
  "However, students are expected", "academic and professional development.", None, "student", "general", "should", "P56", "neutral",
  ["accountability-understanding"])
u("'Students may use AI to support learning and productivity when its use is consistent with course objectives' sets a conditional default permission, so P02. P04 (instructor decides) also fits but the sentence first grants permission, with instructor direction as a condition.",
  "Students may use AI to support learning and productivity when its use is consistent",
  "Students may use AI to", "instructor or supervisor directions.", None, "student", "during-work", "may", "P02", "permit",
  ["default-stance", "permitted-uses"])
u("'AI use should strengthen, and not replace, the student's own understanding, judgment, intellectual effort' says AI must not replace the student's thinking, so P32.",
  "AI use should strengthen, and not replace, the student’s own understanding, judgment",
  "However, AI use should strengthen", "development of required skills.", None, "student", "during-work", "should", "P32", "restrict",
  ["accountability-understanding", "learning-rationale"])
u("Example of appropriate use: 'Clarifying difficult concepts or receiving explanations', i.e. AI as a tutor, so P12.",
  "Clarifying difficult concepts or receiving explanations.",
  "Clarifying difficult concepts or", "receiving explanations.", None, "student", "during-work", "may", "P12", "permit",
  ["permitted-uses"])
u("'Practicing language, coding or problem-solving skills' is a listed appropriate use for practice and self-study, so P14 (not P13, as debugging is not mentioned).",
  "Practicing language, coding or problem-solving skills.",
  "Practicing language, coding or", "problem-solving skills.", None, "student", "during-work", "may", "P14", "permit",
  ["permitted-uses", "code-generation"])
u("'Creating non-graded examples, scenarios or visuals to support learning' is a study-aid use limited to non-graded material, so P14.",
  "Creating non-graded examples, scenarios or visuals to support learning.",
  "Creating non-graded examples, scenarios", "support learning.", None, "student", "during-work", "may", "P14", "permit",
  ["permitted-uses"])
u("'Supporting course learning activities where permitted by the instructor' makes the use depend on the instructor's permission, so P04.",
  "Supporting course learning activities where permitted by the instructor.",
  "Supporting course learning activities", "by the instructor.", None, "student", "during-work", "may", "P04", "permit",
  ["instructor-discretion", "permitted-uses"])
u("'Students are responsible for evaluating and verifying any material produced, summarized, transformed or suggested by AI tools' requires checking AI output for errors, so P31.",
  "Students are responsible for evaluating and verifying any material produced, summarized, transformed or suggested",
  "Students are responsible for evaluating", "incomplete or misleading outputs.", None, "student", "during-work", "must", "P31", "neutral",
  ["accountability-understanding"])
u("'Use of AI must comply with: Embry-Riddle's Academic Integrity Policy' ties AI use to the existing integrity policy; it is a scope/framework rule, P56.",
  "Use of AI must comply with:",
  "Use of AI must comply", "Academic Integrity Policy", None, "student", "general", "must", "P56", "neutral",
  ["default-stance", "integrity-sanctions"])
u("'IT and data security policies. For more information, see Embry-Riddle AI Resources' requires AI use to comply with data security rules and points to university resources, so P50.",
  "IT and data security policies. For more information, see Embry-Riddle AI Resources.",
  "IT and data security policies.", "Embry-Riddle AI Resources.", None, "student", "during-work", "must", "P50", "neutral",
  ["privacy-data"])
u("AI use must follow 'Course- or program-specific guidelines (e.g., syllabus statements or assignment instructions), including expectations for disclosure and labeling of AI-generated content.' Disclosure and labeling is the load-bearing rule, so P24; the delegation to syllabi is secondary.",
  "including expectations for disclosure and labeling of AI-generated content.",
  "Course- or program-specific guidelines (e.g.,", "labeling of AI-generated content.", None, "student", "during-work", "must", "P24", "require",
  ["disclosure-citation", "syllabus-communication"])
u("'Students are responsible for understanding and following any instructor-specific restrictions on AI use' delegates restrictions to instructors and makes students responsible for knowing them, so P04.",
  "Students are responsible for understanding and following any instructor-specific restrictions on AI use.",
  "Students are responsible for understanding", "restrictions on AI use.", None, "student", "course-start", "must", "P04", "restrict",
  ["instructor-discretion", "accountability-understanding"])
u("Under Fraud: 'including the unauthorized use of AI technology' counts unauthorized AI use as deceit, so misconduct classification, P36.",
  "including the unauthorized use of AI technology.",
  "Eagles may not gain unfair", "unauthorized use of AI technology.", None, "student", "when-misuse", "must-not", "P36", "prohibit",
  ["integrity-sanctions", "prohibited-uses"])

d = dict(
    university="Embry-Riddle Aeronautical University-Daytona Beach",
    slug="embry-riddle-aeronautical-daytona-beach", state="FL", type="R2",
    searched=dict(university="found", school="none-found", computing="none-found", course="deferred"),
    documents=[dict(
        id="erau-student-code", layer="university",
        unit="Student Code of Conduct (Worldwide student handbook page)", course=None,
        title="Student Code of Conduct: Academic Integrity, Artificial Intelligence (AI)",
        url="https://worldwide.erau.edu/administration/student-handbook", date_or_term="undated",
        stance_why="The section says students 'may use AI to support learning and productivity when its use is consistent with course objectives, assignment requirements, and instructor or supervisor directions' and that students must follow 'instructor-specific restrictions'. It sets no uniform rule and defers to courses and instructors, with encouragement of AI fluency, so delegates.",
        stance="delegates", tiers=[],
        summary="The AI section of the student conduct code defines AI misuse as an academic integrity violation, encourages AI fluency, and lists appropriate learning uses. It makes students responsible for verifying output, following data security rules, and complying with course-level disclosure and instructor restrictions.",
        units=U)],
    new_types=[],
    notes="Only the AI section (about lines 1181-1214) of the handbook was coded, plus the Fraud line that mentions AI. No computing-specific document exists.")
json.dump(d, open("v2/run/coderA/embry-riddle-aeronautical-daytona-beach.json", "w"), indent=1, ensure_ascii=False)
