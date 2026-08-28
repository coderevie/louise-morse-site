"""Find where a word actually sits on a scanned page.

The scans carry no text layer, so the position has to be measured off the
image. The typing is dark on pale paper and set in even lines, so the rows
that carry ink group into bands, one band to a typed line; within a band the
columns that carry ink group into runs, one run to a word. Counting bands
and runs against the scanner's own lines and words puts a box round the word
itself rather than round the paragraph it lives in.

Two things make that harder than it sounds. The reverse of each sheet shows
through, so the paper between lines is never quite blank and the threshold
has to be taken from each page's own range rather than fixed. And where a
line is faint its band still merges with its neighbour, so any band much
taller than the page's usual line is cut into equal parts afterwards.

Where the counts still do not agree - the scanner ran two words together, or
split one - the position is interpolated and the box widened, so the word
stays in frame even when it cannot be pinned exactly.
"""
import re

import pymupdf

LINE_DPI = 80          # enough to tell one typed line from the next
WORD_DPI = 200         # enough to tell one word from the next
MIN_GAP = 4            # columns of paper that mean a word has ended


def _gray(page, dpi, clip=None):
    zoom = dpi / 72
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=clip,
                          colorspace=pymupdf.csGRAY)
    return pix, zoom


def _dark_table(cut):
    """Maps every byte to 1 if it is darker than `cut`, else 0."""
    return bytes(1 if i < cut else 0 for i in range(256))


def _row_ink(pix, x0, x1, y0, y1, cut):
    """How much of each row carries ink, as a 0-1 fraction."""
    table = _dark_table(cut)
    w, data, out = pix.width, pix.samples, []
    span = max(x1 - x0, 1)
    for y in range(y0, y1):
        row = data[y * w + x0:y * w + x1]
        out.append(row.translate(table).count(1) / span)
    return out


def _col_ink(pix, x0, x1, y0, y1, cut):
    """How much of each column carries ink, as a 0-1 fraction."""
    table = _dark_table(cut)
    w, data = pix.width, pix.samples
    rows = [data[y * w + x0:y * w + x1].translate(table)
            for y in range(y0, y1)]
    span = max(y1 - y0, 1)
    return [sum(r[i] for r in rows) / span for i in range(x1 - x0)]


def _ink_cut(pix):
    """Where to draw the line between paper and typing on this page.

    Taken from the page's own tones, since the sheets vary a good deal in
    how they were lit.
    """
    data = pix.samples
    step = max(len(data) // 20000, 1)
    sample = sorted(data[::step])
    paper = sample[int(len(sample) * 0.75)]      # the bare sheet
    return max(60, paper - 55)


def _runs(profile, threshold, min_len, offset=0):
    """Contiguous stretches of the profile that carry ink."""
    runs, start = [], None
    for i, v in enumerate(profile):
        if v > threshold and start is None:
            start = i
        elif v <= threshold and start is not None:
            if i - start >= min_len:
                runs.append((start + offset, i + offset))
            start = None
    if start is not None and len(profile) - start >= min_len:
        runs.append((start + offset, len(profile) + offset))
    return runs


def _split_merged(bands):
    """Cut apart bands that plainly hold more than one line of typing."""
    if len(bands) < 4:
        return bands
    heights = sorted(b - a for a, b in bands)
    typical = heights[len(heights) // 2]
    if typical <= 0:
        return bands
    out = []
    for a, b in bands:
        n = round((b - a) / typical)
        if n <= 1:
            out.append((a, b))
            continue
        step = (b - a) / n
        out.extend((int(a + i * step), int(a + (i + 1) * step))
                   for i in range(n))
    return out


def line_bands(page):
    """The typed lines on a page, as (top, bottom) fractions of its height."""
    pix, _ = _gray(page, LINE_DPI)
    cut = _ink_cut(pix)
    x0, x1 = int(pix.width * 0.10), int(pix.width * 0.93)
    y0, y1 = int(pix.height * 0.03), int(pix.height * 0.97)
    rows = _row_ink(pix, x0, x1, y0, y1, cut)
    # Where to call a row inked has to come from the page. Some sheets were
    # photographed dark enough that every row carries something, and a fixed
    # level would read the whole page as one band.
    ranked = sorted(rows)
    low = ranked[int(len(ranked) * 0.20)]
    high = ranked[int(len(ranked) * 0.88)]
    level = low + (high - low) * 0.45 if high > low else 0.030
    bands = _runs(rows, level, 2, offset=y0)
    bands = _split_merged(bands)
    bands = _drop_page_number(bands, pix.height)
    return [(a / pix.height, b / pix.height) for a, b in bands]


def _drop_page_number(bands, height):
    """Drop the typed page number standing alone at the foot of the sheet.

    It is a line like any other to the ink, but not to the text, and counting
    it throws every line out by one. Only a band low on the sheet and well
    clear of the last line of typing is taken to be one.
    """
    if len(bands) < 6:
        return bands
    gaps = sorted(bands[i + 1][0] - bands[i][1] for i in range(len(bands) - 1))
    usual = gaps[len(gaps) // 2]
    for _ in range(2):
        if len(bands) < 6:
            break
        top, _bottom = bands[-1]
        clear = bands[-1][0] - bands[-2][1] > max(usual * 3, 10)
        if top / height > 0.86 and clear:
            bands = bands[:-1]
        else:
            break
    return bands


def band_widths(page, bands):
    """How far across the sheet each band's typing runs, as a fraction.

    A line of eighty characters reaches twice as far as one of forty, so
    these widths are a rough picture of the page's shape, which is what
    lets the scanner's lines be matched to it.
    """
    pix, _ = _gray(page, LINE_DPI)
    cut = _ink_cut(pix)
    table = _dark_table(cut)
    w, data = pix.width, pix.samples
    x0, x1 = int(w * 0.04), int(w * 0.97)
    out = []
    for top, bottom in bands:
        y0 = max(0, int(top * pix.height))
        y1 = min(pix.height, max(y0 + 1, int(bottom * pix.height)))
        left, right = None, None
        for y in range(y0, y1):
            row = data[y * w + x0:y * w + x1].translate(table)
            first = row.find(1)
            if first == -1:
                continue
            last = len(row) - 1 - row[::-1].find(1)
            left = first if left is None else min(left, first)
            right = last if right is None else max(right, last)
        out.append(0.0 if left is None else (right - left) / (x1 - x0))
    return out


def align(scanned, measured):
    """Match the scanner's lines to the bands measured off the page.

    Both are sequences of line lengths, one counted in characters and one
    measured in ink, so they are put on the same scale and then aligned the
    way two versions of a text are: a line may be missing from either side,
    and the pairing that costs least overall is taken. That copes with the
    scanner dropping a line or inventing one, which plain counting does not.

    Returns a list as long as `scanned`, giving the band each line matched
    to, or None where it matched nothing.
    """
    if not scanned or not measured:
        return [None] * len(scanned)

    def norm(xs):
        top = max(xs) or 1
        return [x / top for x in xs]

    a, b = norm(scanned), norm(measured)
    gap = 0.30
    n, m = len(a), len(b)
    cost = [[0.0] * (m + 1) for _ in range(n + 1)]
    back = [[None] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        cost[i][0] = i * gap
        back[i][0] = "up"
    for j in range(1, m + 1):
        cost[0][j] = j * gap
        back[0][j] = "left"
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            pair = cost[i - 1][j - 1] + abs(a[i - 1] - b[j - 1])
            skip_a = cost[i - 1][j] + gap
            skip_b = cost[i][j - 1] + gap
            best = min(pair, skip_a, skip_b)
            cost[i][j] = best
            back[i][j] = ("pair" if best == pair
                          else "up" if best == skip_a else "left")

    out = [None] * n
    i, j = n, m
    while i > 0 and j > 0:
        step = back[i][j]
        if step == "pair":
            out[i - 1] = j - 1
            i, j = i - 1, j - 1
        elif step == "up":
            i -= 1
        else:
            j -= 1
    return out


def word_boxes(page, top, bottom, expect=None):
    """The words on one line, as (left, right) fractions of the page width.

    What separates two words from two letters is only the width of the gap,
    and how wide that is depends on the size of the type. The line's own
    height stands in for that, so the same rule works on a page shot close
    up and one shot from further back.
    """
    rect = page.rect
    clip = pymupdf.Rect(rect.x0, rect.y0 + rect.height * top,
                        rect.x1, rect.y0 + rect.height * bottom)
    pix, _ = _gray(page, WORD_DPI, clip=clip)
    cut = _ink_cut(pix)
    x0, x1 = int(pix.width * 0.05), int(pix.width * 0.97)
    cols = _col_ink(pix, x0, x1, 0, pix.height, cut)

    def split(min_gap):
        boxes, start, gap = [], None, 0
        for i, v in enumerate(cols):
            if v > 0.04:
                if start is None:
                    start = i
                gap = 0
            elif start is not None:
                gap += 1
                if gap >= min_gap:
                    boxes.append((start + x0, i - gap + x0))
                    start = None
        if start is not None:
            boxes.append((start + x0, len(cols) + x0))
        return [b for b in boxes if b[1] - b[0] > pix.height * 0.22]

    # Where the line's own word count is known, take the gap width that
    # yields it. Ink varies enough from page to page that no single width
    # separates words from letters everywhere.
    widths = range(max(MIN_GAP, int(pix.height * 0.22)),
                   max(MIN_GAP + 1, int(pix.height * 0.95)))
    if expect:
        best = min(widths, key=lambda g: (abs(len(split(g)) - expect), g))
    else:
        best = max(MIN_GAP, int(pix.height * 0.45))
    return [(a / pix.width, b / pix.width) for a, b in split(best)]


def _span(boxes, where):
    """Where along the typed line a fraction falls, in page coordinates."""
    first, last = boxes[0][0], boxes[-1][1]
    return first + (last - first) * where


def locate(doc, page_no, line_no, line_count, word_no, word_count,
           where=None, letters=0, line_letters=0, line_lengths=None):
    """A box round one word, and whether it was pinned or merely narrowed.

    The scanner drops a line here and invents one there, so its numbering
    does not line up with the page exactly. Rather than trust it, the bands
    near where the line ought to be are each tried, and the one whose count
    of words matches the line's own is taken: a line of thirteen words is
    unlikely to sit above one of six by accident.

    `where` is how far along the line the word starts, as a fraction. The
    typing is evenly spaced, so that points at the word directly, and is
    steadier than counting words in when the scanner has run two together.
    """
    page = doc[page_no - 1]
    bands = line_bands(page)
    if not bands:
        raise ValueError(f"no typed lines found on page {page_no}")

    if line_lengths:
        matched = align(line_lengths, band_widths(page, bands))
        middle = matched[line_no] if line_no < len(matched) else None
        if middle is None:
            middle = min(int(line_no / max(line_count, 1) * len(bands)),
                         len(bands) - 1)
    else:
        middle = min(int(line_no / max(line_count, 1) * len(bands)),
                     len(bands) - 1)

    # The alignment weighs the whole page at once, so it is trusted over any
    # local hunt: a neighbouring line often holds a similar count of words,
    # and choosing between them on that alone lands on the wrong one.
    top, bottom = bands[min(middle, len(bands) - 1)]
    boxes = word_boxes(page, top, bottom, expect=word_count)
    exact = bool(boxes) and abs(len(boxes) - word_count) <= 1

    if boxes and where is not None:
        # Take the box nearest where the typing says the word begins.
        left, right = min(boxes, key=lambda b: abs(b[0] - _span(boxes, where)))
    elif boxes and word_no < len(boxes):
        left, right = boxes[word_no]
    elif boxes:
        i = min(int(word_no / max(word_count, 1) * len(boxes)), len(boxes) - 1)
        left, right = boxes[i]
    else:
        exact, left, right = False, 0.08, 0.92

    # The typewriter gave every letter the same width, so a box round the
    # right word is about as wide as the word is long. One that is not is a
    # box round some other word, however well the counts agreed.
    if exact and boxes and letters:
        span = boxes[-1][1] - boxes[0][0]
        per_letter = span / max(line_letters, 1)
        expected = letters * per_letter
        if expected > 0 and not 0.6 <= (right - left) / expected <= 1.7:
            exact = False

    # A word either side and nothing above or below. Measuring the position
    # is good but not certain, and a neighbour in frame costs a moment to
    # read past, where a miss with nothing round it costs the whole entry.
    per_letter = (boxes[-1][1] - boxes[0][0]) / max(line_letters, 1) if boxes \
        else 0.012
    # The word and nothing else. Anything more and the reader has to work out
    # which of several words is the one in question.
    pad_x = per_letter * (0.6 if exact else 3.0)
    pad_y = (bottom - top) * (0.30 if exact else 0.9)
    x0, x1 = max(0.0, left - pad_x), min(1.0, right + pad_x)
    y0, y1 = max(0.0, top - pad_y), min(1.0, bottom + pad_y)

    # Never cut so small that the reader is looking at a magnified fragment.
    # Where the measurement collapses - a line the ink was too faint to
    # divide - this leaves a strip that can still be read.
    x0, x1 = _at_least(x0, x1, 0.055)
    y0, y1 = _at_least(y0, y1, 0.013)

    rect = page.rect
    return pymupdf.Rect(
        rect.x0 + rect.width * x0, rect.y0 + rect.height * y0,
        rect.x0 + rect.width * x1, rect.y0 + rect.height * y1,
    ), exact


def _at_least(a, b, want):
    """Widen a span about its middle until it is at least `want` across."""
    if b - a >= want:
        return a, b
    mid = (a + b) / 2
    a, b = mid - want / 2, mid + want / 2
    if a < 0:
        a, b = 0.0, want
    if b > 1:
        a, b = 1.0 - want, 1.0
    return max(0.0, a), min(1.0, b)


def find(pages, word):
    """Where a word sits in the scanner's own text: page, line, word index."""
    pattern = re.compile(r"\b" + re.escape(word) + r"\b", re.I)
    for page_no, text in pages.items():
        lines = [ln for ln in text.splitlines() if ln.strip()]
        lengths = [len(ln.strip()) for ln in lines]
        for i, line in enumerate(lines):
            if pattern.search(line):
                words = re.findall(r"\S+", line)
                idx = next((j for j, w in enumerate(words)
                            if pattern.search(w)), 0)
                m = pattern.search(line)
                body = line.rstrip()
                start = len(line) - len(line.lstrip())
                width = max(len(body) - start, 1)
                where = min(max((m.start() - start) / width, 0.0), 1.0)
                return (page_no, i, len(lines), idx, len(words), where,
                        len(word), width, lengths)
    return None
