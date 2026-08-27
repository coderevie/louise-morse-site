"""Authoritative structure of The Wastena Retreat (238 scanned pages).

Derived by locating the printed DISCOURSE / INDEX headings in the page-marked
source transcription (transcripts/chatgpt-source/the-wastena-retreat_p1..p10.txt),
where each source file holds 24 pages (p10 holds 22), giving 238 pages in all.

The book runs:
    pages   1-6    Jottings title pages and the three volume indexes
    pages   7-41   "Jottings During The Sessions" - the session outlines
    pages  42-44   title page, publishing information, Forward
    page   45      Index, Volume One
    pages  46-122  Discourses 1-11
    page  123      Index, Volume Two
    pages 124-179  Discourses 12-22
    page  180      Index, Volume Three
    pages 181-238  Discourses 23-33
"""

# Front matter, in reading order. Each entry is a page of the site.
# (slug, title, subtitle, first_page, last_page)
FRONT = [
    ("wastena-front-01", "Title Pages & Volume Indexes",
     "The three volume title pages and their indexes", 1, 6),
    ("wastena-front-02", "Jottings During the Sessions — Volume One",
     "Session outlines, Discourses 1–11", 7, 17),
    ("wastena-front-03", "Jottings During the Sessions — Volume Two",
     "Session outlines, Discourses 12–22", 18, 28),
    ("wastena-front-04", "Jottings During the Sessions — Volume Three",
     "Session outlines, Discourses 23–33", 29, 41),
    ("wastena-front-05", "Title Page, Publishing Information & Forward",
     "How the retreat came about, in the Fellowship's own words", 42, 44),
    ("wastena-front-06", "Index — Volume One",
     "Discourses 1–11 · Morse Fellowship Lessons 331–341", 45, 45),
]

# Volume indexes that fall between discourses.
# (slug, title, subtitle, page, follows_discourse)
INTERLEAVED = [
    ("wastena-index-02", "Index — Volume Two",
     "Discourses 12–22 · Morse Fellowship Lessons 342–352", 123, 11),
    ("wastena-index-03", "Index — Volume Three",
     "Discourses 23–33 · Morse Fellowship Lessons 353–363", 180, 22),
]

# Discourse number -> (first_page, last_page). Boundaries are the printed
# "DISCOURSE / No. N" headings; a discourse ends where the next one begins.
DISCOURSE_PAGES = {
    1: (46, 53),    2: (54, 63),    3: (64, 69),    4: (70, 74),
    5: (75, 79),    6: (80, 87),    7: (88, 94),    8: (95, 98),
    9: (99, 105),  10: (106, 113), 11: (114, 122), 12: (124, 129),
    13: (130, 134), 14: (135, 139), 15: (140, 144), 16: (145, 149),
    17: (150, 155), 18: (156, 158), 19: (159, 163), 20: (164, 167),
    21: (168, 173), 22: (174, 179), 23: (181, 185), 24: (186, 190),
    25: (191, 195), 26: (196, 201), 27: (202, 207), 28: (208, 212),
    29: (213, 216), 30: (217, 221), 31: (222, 226), 32: (227, 231),
    33: (232, 238),
}

# Titles as printed in the volume indexes.
TITLES = {
    1: "Prepare Your Retreat",
    2: "Identify With the Early Christians",
    3: "Identify as His Disciples",
    4: "Listen to the Lord",
    5: "Call to Remembrance",
    6: "Many are with Us",
    7: "The Cells of the Body",
    8: "The Light Centers",
    9: "Soul Development",
    10: "The Lifting Veil",
    11: "Re-Orient in the Soul",
    12: "Light Centers Forming",
    13: "The Cup of the Water of Life",
    14: "Fulfill the Conditions",
    15: "The Wind of Spirit",
    16: "The Development of Families",
    17: "Soul Memories to be Restored",
    18: "Love in the Higher Nature",
    19: "Law of Love",
    20: "Spiritual Meat",
    21: "Awake, Begotten",
    22: "The True Bread",
    23: "Establish Communication with the Lord",
    24: "Rededicate Your Life to God",
    25: "Light Centers — The Loaves that Feed Many",
    26: "Spiritual Man",
    27: "The Be-attitudes",
    28: "Come Apart from the World",
    29: "The Heart Circuit",
    30: "Change Your Habits Now",
    31: "The Soul Restored",
    32: "Know Who You Follow",
    33: "The Mystical Body",
}

# (first, last, volume name, subtitle, lesson range)
VOLUMES = [
    (1, 11, "Volume One", "The Fourth Dimensional Discipleship", "331–341"),
    (12, 22, "Volume Two", "The Upper Room with the Master", "342–352"),
    (23, 33, "Volume Three", "Entering the Door into Paradise", "353–363"),
]

# The split PDFs in pdfs/wastena/, keyed by the page range they cover.
# Two files each hold two discourses, so several pages share a scan.
PDF_RANGES = [
    (1, 6), (7, 41), (42, 44), (45, 45), (46, 53), (54, 63), (64, 74),
    (75, 79), (80, 87), (88, 94), (95, 98), (99, 105), (106, 113),
    (114, 122), (123, 123), (124, 129), (130, 134), (135, 139),
    (140, 144), (145, 155), (156, 158), (159, 163), (164, 167),
    (168, 173), (174, 179), (180, 180), (181, 185), (186, 190),
    (191, 195), (196, 201), (202, 207), (208, 212), (213, 216),
    (217, 221), (222, 226), (227, 231), (232, 238),
]


def pdf_name(lo, hi):
    return f"page{lo}.pdf" if lo == hi else f"page{lo}-{hi}.pdf"


def pdf_for_pages(first, last):
    """Return the scan file that contains the given page range."""
    for lo, hi in PDF_RANGES:
        if lo <= first and last <= hi:
            return pdf_name(lo, hi)
    # Fall back to whichever scan holds the opening page.
    for lo, hi in PDF_RANGES:
        if lo <= first <= hi:
            return pdf_name(lo, hi)
    raise KeyError(f"no scan covers pages {first}-{last}")


def volume_of(n):
    for lo, hi, name, subtitle, lessons in VOLUMES:
        if lo <= n <= hi:
            return name, subtitle, lessons
    raise KeyError(n)


def reading_order():
    """Every page of the retreat, in the order the book reads.

    Yields (kind, slug, title, subtitle, first_page, last_page) where kind is
    'front', 'index' or 'discourse'.
    """
    for slug, title, subtitle, lo, hi in FRONT:
        yield ("front", slug, title, subtitle, lo, hi)

    after = {d: (slug, title, sub, page)
             for slug, title, sub, page, d in INTERLEAVED}

    for n in sorted(DISCOURSE_PAGES):
        lo, hi = DISCOURSE_PAGES[n]
        yield ("discourse", f"wastena-{n:02d}", f"Discourse {n} — {TITLES[n]}",
               "", lo, hi)
        if n in after:
            slug, title, sub, page = after[n]
            yield ("index", slug, title, sub, page, page)
