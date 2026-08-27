"""Make the web copy of the complete Wastena Retreat scan.

The camera original is around 320 MB, which is past what GitHub will accept
in a single file and far more than anyone wants to pull down in a browser.
Each page is one photograph of a typewritten sheet, so the text survives a
good deal of shrinking: the pages are re-rendered grey at 1600 px wide,
which is ample for the typescript and brings the file to roughly 70 MB.

The per-section scans in pdfs/wastena/ keep the full resolution, so nothing
is lost - this file is only for reading the volumes end to end.

    python tools/make_full_scan.py [source.pdf]
"""
import os
import sys

import pymupdf

DEFAULT_SRC = os.path.join("..", "..", "..", "Wastena Full.pdf")
OUT = os.path.join("pdfs", "wastena", "wastena-full.pdf")
WIDTH = 1600          # pixels across the page
QUALITY = 72          # JPEG quality


def main():
    src_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SRC
    if not os.path.exists(src_path):
        sys.exit(f"cannot find the source scan: {src_path}")

    src = pymupdf.open(src_path)
    out = pymupdf.open()

    for i, page in enumerate(src, start=1):
        scale = WIDTH / page.rect.width
        pix = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale),
                              colorspace=pymupdf.csGRAY)
        jpeg = pix.tobytes("jpeg", jpg_quality=QUALITY)
        new = out.new_page(width=pix.width, height=pix.height)
        new.insert_image(new.rect, stream=jpeg)
        if i % 40 == 0:
            print(f"  {i}/{src.page_count} pages")

    out.set_metadata({
        "title": "The Wastena Retreat",
        "author": "Morse Fellowship",
        "subject": "Wastena (Sparkling Waters), June-July 1967 - "
                   "complete scan of the three volumes",
    })
    pages = src.page_count
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    out.save(OUT, deflate=True, garbage=4)
    out.close()
    src.close()

    size = os.path.getsize(OUT) / 1048576
    print(f"wrote {OUT} - {pages} pages, {size:.0f} MB")
    if size > 95:
        print("warning: over 95 MB; GitHub rejects files above 100 MB")


if __name__ == "__main__":
    main()
