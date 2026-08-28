"""Build a Word document of the readings that need a second pair of eyes.

For each word the checker cannot settle on its own, this cuts the strip of
the scan the word sits on, prints what the text currently says and what the
alternative would be, and leaves a line to write what the page actually
shows.

The scans carry no text layer, so a word's place on the page is worked out
from how far down the OCR's own lines it falls, measured against the band of
the page that actually holds ink. That lands within a line or two, and the
strip is cut generously enough to take that in.

    python tools/make_review_doc.py [first] [count]

Writes review/wastena-review-<first>-<last>.docx and the strips beside it.
"""
import os
import re
import sys

import pymupdf
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import proofread_wastena as P  # noqa: E402

SCAN = os.path.join("pdfs", "wastena", "wastena-full.pdf")
SOURCE = os.path.join("transcripts", "chatgpt-source")
OUT = "review"
WIDTH = 1500          # pixels across the cut strip
LINES_EITHER_SIDE = 5


def raw_pages():
    """The scanner's own output, page by page, with its line breaks kept."""
    pages, n = {}, 0
    for i in range(1, 11):
        path = os.path.join(SOURCE, f"the-wastena-retreat_p{i}.txt")
        text = open(path, encoding="utf-8", errors="replace").read()
        parts = re.split(r"===== PAGE (\d+) =====", text)
        for j in range(1, len(parts), 2):
            n += 1
            pages[n] = parts[j + 1]
    return pages


def ink_band(page):
    """The top and bottom of the part of the page that carries typing.

    Only the middle of the sheet is measured. These are photographs of loose
    pages, so the edges carry the shadow of the desk and the dark of the
    binder holes, and taking those in would make every page look inked from
    top to bottom.
    """
    pix = page.get_pixmap(colorspace=pymupdf.csGRAY, dpi=40)
    x0, x1 = int(pix.width * 0.18), int(pix.width * 0.82)
    y0, y1 = int(pix.height * 0.04), int(pix.height * 0.96)
    rows = []
    for y in range(y0, y1):
        row = [pix.pixel(x, y)[0] for x in range(x0, x1, 3)]
        rows.append((y, sum(row) / len(row)))
    if len(rows) < 10:
        return 0.10, 0.82

    values = sorted(v for _, v in rows)
    paper = values[int(len(values) * 0.9)]        # the bare sheet
    inked = [y for y, v in rows if v < paper - 12]
    if len(inked) < 8:
        return 0.10, 0.82
    return inked[0] / pix.height, (inked[-1] + 1) / pix.height


def strip_for(doc, page_no, line_no, line_count, out_path):
    """Cut the strip of the scan that holds a given line of the page."""
    page = doc[page_no - 1]
    top, bottom = ink_band(page)
    height = bottom - top
    # Where this line falls down the inked band, plus a little either side.
    centre = top + height * ((line_no + 0.5) / max(line_count, 1))
    span = height * (LINES_EITHER_SIDE * 2 + 1) / max(line_count, 1)
    span = min(max(span, 0.10), 0.34)
    y0 = max(0.0, centre - span / 2)
    y1 = min(1.0, centre + span / 2)

    rect = page.rect
    clip = pymupdf.Rect(rect.x0, rect.y0 + rect.height * y0,
                        rect.x1, rect.y0 + rect.height * y1)
    scale = WIDTH / rect.width
    pix = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), clip=clip)
    pix.save(out_path)
    return out_path


def find_word(pages, word):
    """Where a word sits: its page, its line, and how many lines that page has.

    Only lines carrying something are counted, since the blank ones the
    scanner leaves between paragraphs have no height on the page and would
    otherwise push the estimate down.
    """
    pattern = re.compile(r"\b" + re.escape(word) + r"\b", re.I)
    for page_no, text in pages.items():
        lines = [ln for ln in text.splitlines() if ln.strip()]
        for i, line in enumerate(lines):
            if pattern.search(line):
                return page_no, i, len(lines), line.strip()
    return None


def sentence_for(word, texts):
    """The word in its sentence, as the site currently prints it."""
    for text in texts.values():
        m = re.search(r"\b" + re.escape(word) + r"\b", text, re.I)
        if m:
            start = max(0, m.start() - 130)
            end = min(len(text), m.end() + 130)
            return re.sub(r"\s+", " ", text[start:end]).strip()
    return ""


def shade(run, rgb):
    run.font.color.rgb = RGBColor(*rgb)


def main():
    first = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 40

    texts = P.load()
    words = P.vocabulary(texts)
    suspects = [r for r in P.remaining(texts, words) if r[3]]
    suspects.sort(key=lambda r: (-r[1], r[0]))
    batch = suspects[first - 1:first - 1 + count]
    if not batch:
        sys.exit("no suspects in that range")

    os.makedirs(OUT, exist_ok=True)
    pages = raw_pages()
    scan = pymupdf.open(SCAN)

    doc = Document()
    for section in doc.sections:
        section.left_margin = section.right_margin = Inches(0.8)

    doc.add_heading("The Wastena Retreat — readings to check", 0)
    intro = doc.add_paragraph()
    intro.add_run(
        "Each entry below shows the strip of the scan a doubtful word sits on. "
        "Underneath is what the site currently prints, and what the alternative "
        "would be. Please write what you actually see on the line marked "
    )
    b = intro.add_run("On the page:")
    b.bold = True
    intro.add_run(
        " — a few words either side is plenty. Where the current reading is "
        "already right, just write \"ok\"."
    )
    doc.add_paragraph(
        f"Entries {first} to {first + len(batch) - 1} of {len(suspects)}."
    ).italic = True

    made = 0
    for n, (word, freq, near, _) in enumerate(batch, start=first):
        found = find_word(pages, word)
        if not found:
            continue
        page_no, line_no, line_count, raw_line = found
        img = os.path.join(OUT, f"p{page_no}-{word}.png")
        try:
            strip_for(scan, page_no, line_no, line_count, img)
        except Exception as exc:                      # a page that will not cut
            print(f"  skipped {word}: {exc}")
            continue

        doc.add_paragraph()
        head = doc.add_paragraph()
        head.add_run(f"{n}. ").bold = True
        r = head.add_run(f'"{word}"')
        r.bold = True
        r.font.size = Pt(14)
        head.add_run(f"   ·   scan page {page_no}")

        doc.add_picture(img, width=Inches(6.9))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

        cur = doc.add_paragraph()
        cur.add_run("Site now:  ").bold = True
        shade(cur.add_run(sentence_for(word, texts)), (0x44, 0x44, 0x44))

        alt = doc.add_paragraph()
        alt.add_run("Could be:  ").bold = True
        shade(alt.add_run(", ".join(near)), (0x44, 0x44, 0x44))

        ask = doc.add_paragraph()
        ask.add_run("On the page:  ").bold = True
        ask.add_run("_" * 74)
        made += 1

    last = first + len(batch) - 1
    path = os.path.join(OUT, f"wastena-review-{first}-{last}.docx")
    doc.save(path)
    print(f"wrote {path} — {made} entries")


if __name__ == "__main__":
    main()
