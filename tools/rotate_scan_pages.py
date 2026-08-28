"""Set the rotation flag on specific pages of a scanned PDF.

Some pages were photographed with the phone turned sideways. The image
itself does not need to be redrawn - the PDF's own per-page rotation flag
is enough, and every reader (including the site's own viewer) honours it.

    python tools/rotate_scan_pages.py <pdf> <degrees> <page> [page ...]

Degrees is clockwise (90, 180 or 270) and pages are 1-based.
"""
import sys

import pymupdf


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    path = sys.argv[1]
    degrees = int(sys.argv[2])
    pages = [int(p) for p in sys.argv[3:]]

    doc = pymupdf.open(path)
    for n in pages:
        doc[n - 1].set_rotation(degrees)
    doc.saveIncr()
    print(f"rotated {len(pages)} page(s) of {path} by {degrees} degrees: "
          f"{pages}")


if __name__ == "__main__":
    main()
