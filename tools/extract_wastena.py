"""Slice the page-marked source transcription into one Markdown file per
section of The Wastena Retreat, following tools/wastena_map.py.

The source keeps the typescript's hard line wrapping, so paragraphs are
reflowed here: lines within a block are joined, and words broken across a
line ending in a hyphen are rejoined.

Run from the repo root:
    python tools/extract_wastena.py
Writes to transcripts/wastena/book/.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wastena_map import TITLES, reading_order  # noqa: E402

SRC = os.path.join("transcripts", "chatgpt-source")
OUT = os.path.join("transcripts", "wastena", "book")
PAGES_PER_FILE = 24


def load_pages():
    """Return {global_page_number: raw text} across the ten source files."""
    pages = {}
    n = 0
    for i in range(1, 11):
        path = os.path.join(SRC, f"the-wastena-retreat_p{i}.txt")
        text = open(path, encoding="utf-8", errors="replace").read()
        parts = re.split(r"===== PAGE (\d+) =====", text)
        for j in range(1, len(parts), 2):
            n += 1
            pages[n] = parts[j + 1]
    return pages


def letters(s):
    return re.sub(r"[^a-z]", "", s.lower())


def strip_heading(lines, title):
    """Drop the printed DISCOURSE / No. N / Title block from a page's start.

    The site's page header carries that information, so repeating it in the
    body would print it twice. The scan's own title line is matched loosely,
    since the OCR of these headings is often imperfect.
    """
    want = letters(title)
    out = list(lines)
    for _ in range(8):
        if not out:
            break
        first = out[0].strip()
        if not first:
            out.pop(0)
        elif re.fullmatch(r"[^A-Za-z0-9]{0,4}\s*DISCOURSE\.?\s*[^A-Za-z0-9]{0,4}",
                          first, re.I):
            out.pop(0)
        elif re.fullmatch(r"[^A-Za-z0-9]{0,4}\s*No[.,e]?\s*[0-9lIS]{1,3}\.?\s*",
                          first, re.I):
            out.pop(0)
        elif want and letters(first) and letters(first) in want:
            out.pop(0)          # the title, or the first half of a wrapped one
        else:
            break
    return out


def drop_noise(lines):
    """Remove stray OCR marks: lines with no real word on them."""
    kept = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            kept.append("")
            continue
        # A line needs at least one three-letter word to count as text.
        if not re.search(r"[A-Za-z]{3}", stripped):
            continue
        kept.append(line)
    return kept


def reflow(lines):
    """Join hard-wrapped lines into paragraphs, mending split words."""
    paragraphs = []
    current = []
    for line in lines:
        if not line.strip():
            if current:
                paragraphs.append(current)
                current = []
            continue
        current.append(line.strip())
    if current:
        paragraphs.append(current)

    out = []
    for para in paragraphs:
        text = ""
        for line in para:
            if text.endswith("-") and not text.endswith("--"):
                text = text[:-1] + line          # mend a word split by the wrap
            elif text:
                text += " " + line
            else:
                text = line
        text = re.sub(r"\s+", " ", text).strip()
        # Stray rule marks the scanner read as punctuation.
        text = re.sub(r"\s*[|]+\s*", " ", text)
        text = re.sub(r"\s+", " ", text).strip(" .,|_~-") if len(text) < 60 else text
        if text:
            out.append(text)
    return out


def section_markdown(kind, title, first, last, pages, scan_title=""):
    """Build the Markdown body for one section."""
    blocks = []
    for p in range(first, last + 1):
        lines = pages[p].splitlines()
        if p == first and kind == "discourse":
            lines = strip_heading(lines, scan_title)
        lines = drop_noise(lines)
        paras = reflow(lines)
        if not paras:
            continue
        # Mark where each scanned page begins, so the text can be checked
        # against the scan page by page.
        blocks.append(f"[page {p}]")
        blocks.extend(paras)
    return "\n\n".join(blocks) + "\n"


def main():
    pages = load_pages()
    if len(pages) != 238:
        print(f"warning: found {len(pages)} pages, expected 238")
    os.makedirs(OUT, exist_ok=True)

    written = 0
    for kind, slug, title, subtitle, first, last in reading_order():
        n = int(slug.split("-")[-1]) if kind == "discourse" else None
        body = section_markdown(kind, title, first, last, pages,
                                TITLES.get(n, ""))
        path = os.path.join(OUT, f"{slug}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n{body}")
        written += 1
    print(f"wrote {written} sections to {OUT}")


if __name__ == "__main__":
    main()
