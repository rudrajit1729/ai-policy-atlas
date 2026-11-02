import json
p = "v2/course_code/assign_packets/A_08.json"
d = json.load(open(p))
sids = [s["sid"] for s in d["statements"]]
codes = """CT01 CT06 CT40 CT01 CT36 CT12 CT02 CT30 CT25 CT23 CT45 CT36
CT03 CT40 CT35 CT43 CT34
CT17
CT36 CT04 CT25 CT36 CT04 CT25
CT01 CT17 CT01 CT06
CT40 CT40
OTHER CT18 CT26 CT17 CT38
OTHER CT18 CT26 CT17 CT38
CT17 CT17 CT36 CT40 CT38 CT36 CT04 CT05 CT30 CT37
CT01 CT01 CT15 CT35 CT06 CT37 CT40
CT13 CT42 CT17 CT34
CT02 CT31 CT30 CT02 CT37 CT06
CT36 CT29
CT14 CT32 CT26
CT33 CT26 CT27 CT27
CT33 CT25 CT27 CT27
CT35
CT49 CT36 CT37
CT01 CT03 CT17 CT45 CT41 CT08 CT09 CT15 CT17 CT22 CT22 CT25 CT26 CT37
CT17 CT09
CT32 CT01 CT32
CT32 CT01 CT32
CT01 CT33 CT32 CT25 CT22
CT20 CT01 CT17 CT13
CT17 CT22
CT07 CT48 CT25
CT32 CT32 CT04
CT32 CT32 CT04
CT01 CT37
CT32 CT32 CT04
CT34 CT02 CT03 CT15 CT19 CT25 CT29 CT30
CT02 OTHER CT25 CT27 CT27 CT40 CT28 CT35""".split()
assert len(codes) == len(sids), (len(codes), len(sids))
notes = {
    "OTHER": "",
}
out = []
for sid, c in zip(sids, codes):
    e = {"sid": sid, "type": c, "note": ""}
    if c == "OTHER":
        if "COS 217" in sid:
            e["type"] = "OTHER: rationale for policy change"
            e["note"] = "Explains the ban was dropped because it disadvantaged honest students."
        else:
            e["type"] = "OTHER: non-AI course resources allowed"
            e["note"] = "Says textbook and instructor resources are always allowed; not about AI."
    out.append(e)
json.dump({"packet": "A_08", "coder": "A", "statements": out},
          open("v2/course_code/assign_results/A_08.json", "w"), indent=1)
