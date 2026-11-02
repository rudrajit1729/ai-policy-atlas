#!/usr/bin/env python3
"""Build corpus/pass2_targets.json and corpus/known_urls.txt from the pass-1 corpus."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
c = json.loads((ROOT / "corpus" / "corpus.json").read_text())
included = {d["university"] for d in c["documents"]}

again = []
for s in c["searched_universities"]:
    weak = s["result"] != "included" or "browse-only" in (s.get("notes") or "").lower()
    if weak and s["university"] not in again:
        again.append(s["university"])

NEW = [
    # US R1/R2 not yet checked
    "Penn State", "University of Pittsburgh", "Temple University", "Drexel University", "Lehigh University", "Villanova University",
    "University of Delaware", "UConn", "University of New Hampshire", "University of Vermont", "University of Maine",
    "Syracuse University", "Binghamton University", "University at Albany", "Rochester Institute of Technology", "Stevens Institute of Technology",
    "New Jersey Institute of Technology", "Georgetown University", "George Washington University", "American University",
    "William & Mary", "James Madison University", "Old Dominion University", "Virginia Commonwealth University", "George Mason University",
    "University of Georgia", "University of Tennessee Knoxville", "University of Kentucky", "University of Louisville", "LSU",
    "Tulane University", "University of Alabama", "UAB", "Auburn University", "University of Mississippi", "Mississippi State University",
    "University of Arkansas", "University of Missouri", "University of Oklahoma", "Oklahoma State University", "Kansas State University",
    "Texas Tech University", "University of Houston", "University of North Texas", "UT San Antonio", "Baylor University", "SMU",
    "Florida State University", "University of South Florida", "Florida International University", "University of Miami",
    "University of Central Florida", "Wake Forest University", "University of South Carolina", "Colorado State University",
    "Colorado School of Mines", "University of Denver", "Utah State University", "Boise State University", "University of Nevada Reno",
    "UNLV", "University of New Mexico", "New Mexico State University", "Montana State University", "University of Idaho",
    "University of Cincinnati", "Wayne State University", "Michigan Technological University", "Western Michigan University",
    "University of Wisconsin–Milwaukee", "Marquette University", "Loyola University Chicago", "DePaul University", "Illinois Institute of Technology",
    "Saint Louis University", "University of Notre Dame", "Brandeis University", "Boston College", "WPI", "Northeastern Illinois University",
    "Cal State Long Beach", "Cal State Fullerton", "San Diego State University", "San Francisco State University", "Cal Poly Pomona",
    "Santa Clara University", "Seattle University", "Western Washington University", "Gonzaga University", "University of Portland",
    # Canada
    "University of Victoria", "University of Saskatchewan", "University of Manitoba", "University of Guelph", "Wilfrid Laurier University",
    "University of Windsor", "Toronto Metropolitan University", "Ontario Tech University", "Memorial University of Newfoundland",
    "University of New Brunswick", "Université Laval", "Université de Sherbrooke", "Polytechnique Montréal", "École de technologie supérieure",
    "UQAM", "University of Regina", "Brock University", "Trent University", "Thompson Rivers University", "UBC Okanagan",
    # HBCUs / MSIs
    "Howard University", "Spelman College", "Morehouse College", "North Carolina A&T", "Florida A&M University", "Morgan State University",
    "Hampton University", "Prairie View A&M University", "Tuskegee University", "Jackson State University", "Bowie State University",
    "UT El Paso", "UT Rio Grande Valley", "Cal State LA", "University of Puerto Rico Mayagüez",
    # Community colleges with transfer CS programs
    "De Anza College", "Foothill College", "Santa Monica College", "Austin Community College", "Miami Dade College",
    "Northern Virginia Community College", "Portland Community College", "Bellevue College", "Valencia College", "City College of San Francisco",
]
new = [n for n in NEW if n not in included and n not in again]
(ROOT / "corpus" / "pass2_targets.json").write_text(json.dumps({"research_again": again, "new_institutions": new}, indent=1, ensure_ascii=False))
urls = sorted({d["url"] for d in c["documents"]})
(ROOT / "corpus" / "known_urls.txt").write_text("\n".join(urls) + "\n")
print(f"research_again={len(again)} new={len(new)} known_urls={len(urls)}")
