import json
U = []


def u(why, anchor, fs, fe, actor, phase, mod, pt, us, topics, policy=None):
    U.append(dict(why=why, anchor=anchor, frag_start=fs, frag_end=fe, policy=policy, actor=actor, phase=phase,
                  modality=mod, policy_type=pt, unit_stance=us, topics=topics))


u("The sentence sets the baseline expectation that submitted work is the student's own ('prepare and present their own work'), the ownership rule P29; it frames the AI clause that follows.",
  "Eagles are expected to prepare and present their own work", "Eagles are expected to prepare", "satisfy academic requirements.",
  "student", "general", "should", "P29", "restrict", ["accountability-understanding"])
u("This defines AI misuse as an integrity violation: 'in violation of University, program, course or instructor requirements, including unauthorized use'. Classified as misconduct, so P36.",
  "Using artificial intelligence or automated technologies in violation of University, program, course or instructor requirements",
  "Using artificial intelligence or automated", "to facilitate other prohibited conduct.",
  "student", "when-misuse", "must-not", "P36", "restrict", ["integrity-sanctions", "prohibited-uses"])
u("Lists 'misrepresentation of AI-generated work' as a violation; passing AI output off as one's own is the nondisclosure-as-violation idea in P28, rather than the general misconduct class P36 used for the neighbouring items.",
  "misrepresentation of AI-generated work", "Using artificial intelligence or automated", "to facilitate other prohibited conduct.",
  "student", "when-misuse", "must-not", "P28", "prohibit", ["disclosure-citation", "integrity-sanctions"])
u("Names 'fabrication or falsification of information' through AI as a violation; a form of misconduct, hence P36.",
  "fabrication or falsification of information", "Using artificial intelligence or automated", "to facilitate other prohibited conduct.",
  "student", "when-misuse", "must-not", "P36", "prohibit", ["integrity-sanctions"])
u("Names 'use of AI to facilitate other prohibited conduct' as a violation; misconduct class, P36.",
  "use of AI to facilitate other prohibited conduct", "Using artificial intelligence or automated", "to facilitate other prohibited conduct.",
  "student", "when-misuse", "must-not", "P36", "prohibit", ["integrity-sanctions"])
u("Sets the guiding principle for all educational AI use ('must be guided by ethical principles and academic integrity'), an institution-level framework statement, P56.",
  "must be guided by ethical principles and academic integrity", "The use of artificial intelligence (AI)", "see below for more information.",
  "all", "general", "must", "P56", "neutral", ["ethics-bias-environment", "default-stance"])
u("Expresses the university's welcome of AI skill-building: 'encourages students to develop fluency in artificial intelligence'. Framed as professional development, so P44 rather than a default-permit rule (P02), which the next permission unit covers.",
  "encourages students to develop fluency in artificial intelligence", "Embry-Riddle Aeronautical University encourages students", "academic and professional development.",
  "student", "general", "informs", "P44", "encourage", ["ai-literacy-career"])
u("States the default permission with conditions: 'Students may use AI to support learning and productivity when its use is consistent with course objectives'. Allowed by default but bounded by course rules, so P02.",
  "Students may use AI to support learning and productivity", "Students may use AI to", "or supervisor directions.",
  "student", "during-work", "may", "P02", "permit", ["default-stance", "permitted-uses"])
u("Requires that AI 'strengthen, and not replace, the student's own understanding, judgment, intellectual effort'; students remain the primary thinker, P32.",
  "AI use should strengthen, and not replace, the student’s own understanding", "However, AI use should strengthen", "development of required skills.",
  "student", "during-work", "should", "P32", "restrict", ["accountability-understanding", "learning-rationale"])
u("First listed appropriate use: 'Clarifying difficult concepts or receiving explanations', AI as a tutor, P12.",
  "Clarifying difficult concepts or receiving explanations.", "Clarifying difficult concepts or", "receiving explanations.",
  "student", "during-work", "may", "P12", "permit", ["permitted-uses"])
u("'Practicing language, coding or problem-solving skills' is a practice use of AI; P14 fits better than P13 since debugging is not mentioned.",
  "Practicing language, coding or problem-solving skills.", "Practicing language, coding or", "problem-solving skills.",
  "student", "during-work", "may", "P14", "permit", ["permitted-uses", "code-generation"])
u("'Creating non-graded examples, scenarios or visuals to support learning' is a study-aid use, P14; the 'non-graded' qualifier leaves graded work uncovered.",
  "Creating non-graded examples, scenarios or visuals to support learning.", "Creating non-graded examples, scenarios", "to support learning.",
  "student", "during-work", "may", "P14", "permit", ["permitted-uses"])
u("'Supporting course learning activities where permitted by the instructor' makes AI use depend on the instructor, so P04.",
  "Supporting course learning activities where permitted by the instructor.", "Supporting course learning activities where", "permitted by the instructor.",
  "student", "during-work", "may", "P04", "permit", ["instructor-discretion"])
u("Students 'are responsible for evaluating and verifying any material produced' by AI, including fabricated citations; a verification duty, P31.",
  "Students are responsible for evaluating and verifying any material produced, summarized, transformed or suggested",
  "Students are responsible for evaluating", "incomplete or misleading outputs.",
  "student", "during-work", "must", "P31", "require", ["accountability-understanding"])
u("AI use 'must comply with' IT and data security policies and points to AI Resources; data protection and vetted-tool guidance, P50.",
  "IT and data security policies.", "IT and data security policies. For", "Embry-Riddle AI Resources.",
  "student", "during-work", "must", "P50", "restrict", ["privacy-data"])
u("AI use must comply with course guidelines 'including expectations for disclosure and labeling of AI-generated content'; disclosure with submissions, P24.",
  "including expectations for disclosure and labeling of AI-generated content", "Course- or program-specific guidelines (e.g.,", "labeling of AI-generated content.",
  "student", "during-work", "must", "P24", "require", ["disclosure-citation", "syllabus-communication"])
u("Students are 'responsible for understanding and following any instructor-specific restrictions on AI use', so rules vary by instructor, P04.",
  "Students are responsible for understanding and following any instructor-specific restrictions on AI use.",
  "Students are responsible for understanding", "restrictions on AI use.",
  "student", "course-start", "must", "P04", "restrict", ["instructor-discretion"])
u("Defines cheating as 'unauthorized assistance, including technology' on assignments, quizzes and exams, which reaches AI tools; misconduct class, P36 (not P22, since it is not an AI-specific exam ban).",
  "Eagles may not use unauthorized assistance, including technology, websites, and/or electronics", "Eagles may not use", "quiz or examination.",
  "student", "when-misuse", "must-not", "P36", "restrict", ["integrity-sanctions", "exams-in-person"])
u("Defines fraud to include 'the unauthorized use of AI technology' to gain unfair advantage; misconduct class, P36.",
  "including the unauthorized use of AI technology", "Eagles may not gain unfair", "unauthorized use of AI technology.",
  "student", "when-misuse", "must-not", "P36", "prohibit", ["integrity-sanctions", "prohibited-uses"])

doc = dict(
    id="erau-student-code", layer="university", unit="Student Code of Conduct (Worldwide student handbook page)", course=None,
    title="Student Code of Conduct: Academic Integrity, Artificial Intelligence (AI)",
    url="https://worldwide.erau.edu/administration/student-handbook", date_or_term="undated",
    stance_why="The section says 'Students may use AI to support learning and productivity when its use is consistent with course objectives, assignment requirements, and instructor or supervisor directions' and bans use 'in violation of University, program, course or instructor requirements'. It sets no uniform rule itself and defers to course and instructor, so delegates.",
    stance="delegates", tiers=[],
    summary="The handbook's academic-integrity section lists AI misuse as a violation and encourages AI fluency, while permitting AI for learning when consistent with course and instructor rules. It gives examples of appropriate uses and a duty to verify output, and defers disclosure and restrictions to syllabus statements.",
    units=U)
d = dict(university="Embry-Riddle Aeronautical University-Daytona Beach", slug="embry-riddle-aeronautical-daytona-beach", state="FL", type="R2",
         searched={"university": "found", "school": "none-found", "computing": "none-found", "course": "deferred"},
         documents=[doc], new_types=[],
         notes="Only one included document. The text file is the whole handbook; only the AI part of the Academic Integrity section and the Cheating/Fraud definitions were coded. Over-sharing and Plagiarism definitions do not mention AI and were skipped.")
json.dump(d, open("v2/run/coderB/embry-riddle-aeronautical-daytona-beach.json", "w"), indent=1, ensure_ascii=False)
