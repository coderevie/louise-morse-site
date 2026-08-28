"""Join scans that were photographed in more than one batch.

The May 12, 1983 reading came off the phone as two files, P1 holding the
first three pages and P2 the remaining thirteen. They are one reading, so
they are joined into one scan here rather than asking a reader to know that
the second file continues the first.

    python tools/join_scans.py
"""
import os
import sys

import pymupdf

# (parts, joined file, what it is)
JOBS = [
    (["pdfs/readings/P1.pdf", "pdfs/readings/P2.pdf"],
     "pdfs/readings/reading-1983-05-12.pdf",
     "Morse Reading, May 12, 1983"),
]


def main():
    for parts, out, what in JOBS:
        missing = [p for p in parts if not os.path.exists(p)]
        if missing:
            print(f"skipping {out}: missing {', '.join(missing)}")
            continue

        joined = pymupdf.open()
        counts = []
        for part in parts:
            doc = pymupdf.open(part)
            counts.append(doc.page_count)
            joined.insert_pdf(doc)
            doc.close()

        joined.set_metadata({"title": what, "author": "Morse Fellowship"})
        joined.save(out, deflate=True, garbage=4)
        pages = joined.page_count
        joined.close()

        size = os.path.getsize(out) / 1048576
        print(f"wrote {out} - {pages} pages "
              f"({' + '.join(str(c) for c in counts)}), {size:.0f} MB")


if __name__ == "__main__":
    main()
