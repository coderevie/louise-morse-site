"""Slice the page-marked source transcription into one Markdown file per
section of The Wastena Retreat, following tools/wastena_map.py.

The source keeps the typescript's hard line wrapping, so paragraphs are
reflowed here: lines within a block are joined, and words broken across a
line ending in a hyphen are rejoined.

Run from the repo root:
    python tools/extract_wastena.py
Writes to transcripts/wastena/book/.
"""
import difflib
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


def similar(a, b):
    """Whether a scanned heading is the title, allowing for misread letters.

    The headings scan badly - "Love in the Higher Mature" for "...Nature",
    "Know Whom You. Follow" for "Know Who You Follow" - so they are matched
    loosely rather than exactly.
    """
    if a in b or b in a:
        return True
    return difflib.SequenceMatcher(None, a, b).ratio() >= 0.75


def strip_heading(lines, title):
    """Drop the printed DISCOURSE / No. N / Title block from a page's start.

    The site's page header carries that information, so repeating it in the
    body would print it twice. The scan's own title line is matched loosely,
    since the OCR of these headings is often imperfect.
    """
    want = letters(title)
    out = list(lines)
    for _ in range(14):
        if not out:
            break
        first = out[0].strip()
        if not first:
            out.pop(0)
        elif re.search(r"DISCOURSE", first, re.I) and len(first) < 40:
            out.pop(0)
        elif re.fullmatch(r"[^A-Za-z0-9]{0,4}\s*No[.,es]{0,2}\s*"
                          r"[0-9lIS]{1,3}\.?\s*", first, re.I):
            out.pop(0)
        elif want and letters(first) and similar(letters(first), want):
            out.pop(0)          # the title, or the first half of a wrapped one
        elif is_noise(first):
            out.pop(0)          # speckle the scanner read before the heading
        else:
            break
    return out


# Words so ordinary that a line of real prose is unlikely to lack them all.
EVERYDAY = {
    "the", "and", "you", "your", "are", "for", "that", "this", "with", "have",
    "will", "not", "his", "her", "from", "they", "all", "was", "one", "but",
    "who", "god", "lord", "shall", "unto", "our", "there", "then", "when",
    "which", "what", "know", "into", "upon", "them", "their", "would", "come",
    "soul", "spirit", "light", "love", "life", "man", "may", "can", "has",
    "been", "each", "more", "must", "now", "out", "own", "say", "see", "shall",
    "him", "she", "yet", "did", "let", "was", "were", "you", "are", "is", "in",
    "to", "of", "be", "as", "at", "so", "do", "he", "it", "we", "an", "or",
    "on", "if", "no", "up", "by", "us", "my", "me",
}


def is_noise(block):
    """True for a block the scanner invented out of speckle and paper grain.

    Real prose carries a few everyday words; these carry none at all:
    "ee nee ae", "Pa, eee eee, eee", "HU Lo SRE", "poe Take Ri gO".
    """
    words = re.findall(r"[A-Za-z]+", block)
    if not words:
        return True
    if any(w.lower() in EVERYDAY for w in words):
        return False
    # No everyday word: real only if it reads as several proper words.
    real = [w for w in words if len(w) > 3 and len(set(w.lower())) > 2]
    return len(real) < 3


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


ENDS_SENTENCE = ('.', '!', '?', '"', ':', ';', '--', ',')


def join_continuations(paras):
    """Rejoin a paragraph the scanner broke in the middle of a sentence.

    Where the typist underlined a phrase, the scanner often returned it as a
    block of its own: "...learned to obey Him. Be still" / "and know." The
    tell is that the preceding block stops without any closing punctuation,
    so the sentence plainly runs on.
    """
    out = []
    for para in paras:
        if (out and not out[-1].endswith(ENDS_SENTENCE)
                and para[:1].islower()):
            out[-1] = out[-1] + " " + para
        else:
            out.append(para)
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
        if kind == "discourse":
            paras = [p for p in paras if not is_noise(p)]
            paras = join_continuations(paras)
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
