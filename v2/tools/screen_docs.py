#!/usr/bin/env python3
"""Screen collected documents against the inclusion criteria (decisions D06–D10, D14).

Deterministic checks per document, plus the collector's quality label:
  text_ok      saved text exists and is at least 400 characters
  ai_terms     at least 3 mentions of AI terms (AI, artificial intelligence, generative, ChatGPT, LLM, Copilot, ...)
  policy_lang  at least 2 normative phrases near AI terms (must, may not, prohibited, permitted, allowed, cite, disclose, ...)
  not_excluded URL/title not news, event, workshop, blog, tool list
  unique       URL and text not duplicated elsewhere in the corpus
Result per document: include | exclude | review. Claude decides every "review" (manual decisions are kept in
v2/screening_decisions.json and override the automatic result). Writes v2/screening_log.json.
"""
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "v2"
AI = re.compile(r"\b(AI|A\.I\.|artificial intelligence|generative|GenAI|Gen AI|ChatGPT|LLMs?|large language model|Copilot|Claude|Gemini|chatbots?|IAG|intelligence artificielle|inteligencia artificial|IA generativa)\b", re.I)
NORM = re.compile(r"\b(must|may not|must not|shall|prohibit\w*|forbid\w*|not (?:be )?(?:allowed|permitted)|permitted|allowed|require\w*|cite|citation|disclos\w*|acknowledg\w*|should|violation|misconduct|unauthori[sz]ed|policy|policies)\b", re.I)
EXCL = re.compile(r"/(news|stories|story|events?|calendar|blog|press|magazine|podcast)/|webinar|workshop|newsletter", re.I)


def main():
    manual = json.loads((V2 / "screening_decisions.json").read_text()) if (V2 / "screening_decisions.json").exists() else {}
    rows, by_url, by_hash = [], defaultdict(list), defaultdict(list)
    for f in sorted((V2 / "collect").glob("*.json")):
        c = json.loads(f.read_text())
        for d in c.get("documents", []):
            tf = d.get("text_file") or ""
            p = Path(tf) if tf.startswith("/") else ROOT / tf
            text = p.read_text(errors="ignore") if tf and p.exists() else ""
            body = text.split("\n", 2)[-1]
            ai = len(AI.findall(body))
            # normative phrases within 300 characters of an AI mention
            norm = sum(1 for m in AI.finditer(body) if NORM.search(body[max(0, m.start() - 300): m.end() + 300]))
            h = hashlib.sha1(re.sub(r"\s+", " ", body).strip().lower().encode()).hexdigest()
            r = {"university": c.get("slug"), "doc_id": d.get("id"), "layer": d.get("layer"), "title": d.get("title"), "url": d.get("url"),
                 "collector_quality": d.get("quality"), "chars": len(body), "ai_mentions": ai, "normative_near_ai": norm,
                 "text_ok": len(body) >= 400, "ai_terms": ai >= 3, "policy_lang": norm >= 2,
                 "not_excluded": not EXCL.search((d.get("url") or "") + " " + (d.get("title") or ""))}
            rows.append(r)
            # duplicates count only within one university: a system policy shared by campuses belongs to each
            by_url[(c.get("slug"), (d.get("url") or "").split("#")[0].rstrip("/"))].append(r)
            if body:
                by_hash[(c.get("slug"), h)].append(r)
    for group in list(by_url.values()) + list(by_hash.values()):
        for r in group[1:]:
            r["duplicate_of"] = group[0]["doc_id"]
    for r in rows:
        checks = [r["text_ok"], r["ai_terms"], r["policy_lang"], r["not_excluded"], "duplicate_of" not in r]
        q = r["collector_quality"]
        if not r["text_ok"] or "duplicate_of" in r or q in ("generic", "superseded"):
            auto = "exclude"
        elif all(checks) and q in ("good", "partial"):
            auto = "include"
        elif all(checks) and q == "thin":
            auto = "include"  # D30: a short AI clause is still the institution's policy
        elif q == "thin" and r["text_ok"] and r["not_excluded"] and r["normative_near_ai"] >= 1:
            auto = "include"  # D30
        else:
            auto = "review"
        r["auto"] = auto
        m = manual.get(r["doc_id"])
        r["decision"] = m["decision"] if m else auto
        r["decision_by"] = "Claude (manual review)" if m else "rule"
        r["decision_reason"] = m["reason"] if m else ""
    (V2 / "screening_log.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False))
    # write each decision into its collect file so coders see it (coders code only screen == "include")
    dec = {(r["university"], r["doc_id"]): r["decision"] for r in rows}
    for f in sorted((V2 / "collect").glob("*.json")):
        c = json.loads(f.read_text())
        changed = False
        for d in c.get("documents", []):
            v = dec.get((c.get("slug"), d.get("id")))
            if v and d.get("screen") != v:
                d["screen"] = v
                changed = True
        if changed:
            f.write_text(json.dumps(c, indent=1, ensure_ascii=False))
    tally = defaultdict(int)
    for r in rows:
        tally[r["decision"]] += 1
    pending = [r for r in rows if r["decision"] == "review"]
    print(f"{len(rows)} documents: {dict(tally)}; {len(pending)} awaiting manual review")


if __name__ == "__main__":
    main()
