"""Build a Word document of the readings that need a second pair of eyes.

One entry per doubtful word: the word cut from the scan, what the site
currently reads it as, and room to mark that true or false. The word is
found on the page by measuring the image rather than by guessing at it, so
the cut is round the word and not round the paragraph it lives in - see
tools/locate_on_scan.py.

    python tools/make_review_doc.py [count] [start]

Writes review/wastena-review.docx and the cuts beside it.
"""
import os
import re
import sys

import pymupdf
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import locate_on_scan as LOC  # noqa: E402
import proofread_wastena as P  # noqa: E402

SCAN = os.path.join("pdfs", "wastena", "wastena-full.pdf")
SOURCE = os.path.join("transcripts", "chatgpt-source")
OUT = "review"
CUT_WIDTH = 900        # pixels across the cut
QUALITY = 84


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


def cut_word(doc, pages, word, out_path):
    """Cut the word itself out of the scan. Returns (page, tight?) or None."""
    found = LOC.find(pages, word)
    if not found:
        return None
    (page_no, line_no, line_count, word_no, word_count, where,
     letters, line_letters) = found
    rect, exact = LOC.locate(doc, page_no, line_no, line_count,
                             word_no, word_count, where,
                             letters, line_letters)
    page = doc[page_no - 1]
    scale = min(CUT_WIDTH / rect.width, 400)
    pix = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), clip=rect,
                          colorspace=pymupdf.csGRAY)
    with open(out_path, "wb") as f:
        f.write(pix.tobytes("jpeg", jpg_quality=QUALITY))
    return page_no, exact


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 1

    texts = P.load()
    words = P.vocabulary(texts)
    suspects = [r for r in P.remaining(texts, words) if r[3]]
    suspects.sort(key=lambda r: r[0])
    batch = suspects[start - 1:start - 1 + count]
    if not batch:
        sys.exit("no suspects in that range")

    os.makedirs(OUT, exist_ok=True)
    pages = raw_pages()
    scan = pymupdf.open(SCAN)

    doc = Document()
    for section in doc.sections:
        section.left_margin = section.right_margin = Inches(0.9)
        section.top_margin = section.bottom_margin = Inches(0.7)

    doc.add_heading("The Wastena Retreat — readings to check", 0)
    intro = doc.add_paragraph()
    intro.add_run("Each entry is one word, cut from the scan. Under it is "
                  "what the site reads it as. Mark ")
    intro.add_run("T").bold = True
    intro.add_run(" if that is what the page says, or ")
    intro.add_run("F").bold = True
    intro.add_run(" and the right word if it is not. Nothing needs typing "
                  "out.")
    note = doc.add_paragraph()
    note.add_run(
        f"Entries {start} to {start + len(batch) - 1} of {len(suspects)}. "
        "Most will be right as they stand: of the ones already checked, about "
        "nine in ten were. If a long run comes back true, say so and we can "
        "stop."
    ).italic = True

    made, loose = 0, 0
    for n, (word, freq, near, _) in enumerate(batch, start=start):
        img = os.path.join(OUT, f"cut-{word}.jpg")
        try:
            result = cut_word(scan, pages, word, img)
        except Exception as exc:                       # a page that will not cut
            print(f"  skipped {word}: {exc}")
            continue
        if not result:
            continue
        page_no, exact = result
        if not exact:
            loose += 1

        doc.add_paragraph()
        pic = doc.add_paragraph()
        pic.alignment = WD_ALIGN_PARAGRAPH.LEFT
        pic.add_run().add_picture(img, width=Inches(3.1))

        line = doc.add_paragraph()
        line.add_run(f"{n}.  ").bold = True
        shown = line.add_run(word)
        shown.bold = True
        shown.font.size = Pt(13)
        tail = line.add_run(f"      T  /  F → ______________________"
                            f"        (page {page_no})")
        tail.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
        made += 1

    path = os.path.join(OUT, "wastena-review.docx")
    doc.save(path)
    size = os.path.getsize(path) / 1048576
    print(f"wrote {path} — {made} words, {size:.1f} MB")
    if loose:
        print(f"  {loose} could not be pinned exactly; those cuts are wider")


if __name__ == "__main__":
    main()
