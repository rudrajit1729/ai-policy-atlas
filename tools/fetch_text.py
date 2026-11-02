#!/usr/bin/env python3
"""Fetch a policy page (HTML or PDF) and save its plain text verbatim.

Usage: python3 tools/fetch_text.py <url> <slug>
Writes $POLICY_TEXT_DIR/<slug>.txt (local cache, not part of the corpus) and prints the path + character count.
The saved text is the source of truth for verbatim excerpts.
"""
import io
import re
import subprocess
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"


def fetch(url: str) -> bytes:
    m = re.match(r"https://docs\.google\.com/document/d/(?!e/)([\w-]+)", url)
    if m:  # Google Docs: plain-text export of the same document
        url = f"https://docs.google.com/document/d/{m.group(1)}/export?format=txt"
    m = re.match(r"https://([\w.-]+\.simplesyllabus\.com)/[\w-]+/doc/(\w+)", url)
    if m:  # Simple Syllabus view pages render client-side; read the public JSON behind them
        url = f"https://{m.group(1)}/api2/doc-full-page-get?code={m.group(2)}"
    m = re.match(r"(https://[\w.-]+\.instructure\.com)/courses/(\d+)/pages/([\w-]+)", url)
    if m:  # public Canvas pages: the pages API returns the same body as JSON
        url = f"{m.group(1)}/api/v1/courses/{m.group(2)}/pages/{m.group(3)}"
    m = re.match(r"https://drive\.google\.com/file/d/([\w-]+)", url)
    if m:  # Google Drive file viewer -> direct download of the same file
        url = f"https://drive.google.com/uc?export=download&id={m.group(1)}"
    out = subprocess.run(
        ["curl", "-sSL", "--max-time", "40", "-A", UA, url],
        capture_output=True, check=True,
    )
    return out.stdout


def docx_to_text(raw: bytes) -> str:
    import docx
    d = docx.Document(io.BytesIO(raw))
    parts = [p.text for p in d.paragraphs]
    for t in d.tables:
        for row in t.rows:
            parts.extend(c.text for c in row.cells)
    return "\n".join(parts)


def json_to_text(raw: bytes) -> str:
    import json as _json
    parts = []

    def walk(x):
        if isinstance(x, str):
            parts.append(html_to_text(x.encode()) if "<" in x else x)
        elif isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(_json.loads(raw))
    return "\n".join(parts)


def to_text(raw: bytes) -> str:
    if raw.lstrip()[:1] in (b"{", b"["):
        try:
            return json_to_text(raw)
        except ValueError:
            pass
    if raw[:5] == b"%PDF-":
        return pdf_to_text(raw)
    if raw[:2] == b"PK":
        return docx_to_text(raw)
    if raw[:200].lstrip()[:1] not in (b"<",) and b"<html" not in raw[:2000].lower():
        return raw.decode("utf-8", "replace")  # plain text (e.g. Google Docs export)
    return html_to_text(raw)


def html_to_text(raw: bytes) -> str:
    soup = BeautifulSoup(raw, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    text = soup.get_text("\n")
    return text


def pdf_to_text(raw: bytes) -> str:
    import pypdf
    reader = pypdf.PdfReader(io.BytesIO(raw))
    return "\n".join((p.extract_text() or "") for p in reader.pages)


def normalize(text: str) -> str:
    text = text.replace(" ", " ")
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.splitlines()]
    out, blank = [], 0
    for ln in lines:
        if not ln:
            blank += 1
            if blank > 1:
                continue
        else:
            blank = 0
        out.append(ln)
    return "\n".join(out).strip()


def main():
    url, slug = sys.argv[1], sys.argv[2]
    raw = fetch(url)
    text = to_text(raw)
    text = normalize(text)
    import os
    path = Path(os.environ.get("POLICY_TEXT_DIR", str(ROOT / ".cache" / "text"))) / f"{slug}.txt"
    path.write_text(f"SOURCE: {url}\n\n{text}\n")
    print(f"{path} {len(text)} chars")


if __name__ == "__main__":
    main()
