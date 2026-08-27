"""Split the Wastena Retreat transcription into one Markdown file per Discourse.

Input:  the ChatGPT transcriptions of P3.txt-P10.txt (the full-text scans),
        which carry "===== PAGE n =====" markers, typescript hard line wraps,
        and page footers like "4-3".
Output: transcripts/wastena/final/discourse-NN.md

Run from the repo root:  python tools/split_wastena.py
"""
import os
import re
import sys

SRC_DIR = None  # resolved below
OUT_DIR = os.path.join("transcripts", "wastena", "final")

# Titles as printed in the volume indexes. The scan headings are OCR-noisy
# ("No, 50", "Noe 13"), so these are the authority for titles and numbering.
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

VOLUMES = [
    (1, 11, "Volume 1", "The Fourth Dimensional Discipleship, Continued", "331-341"),
    (12, 22, "Volume 2", "The Upper Room with the Master", "342-352"),
    (23, 33, "Volume 3", "Entering the Door into Paradise", "353-363"),
]

PAGE_MARKER = re.compile(r"^=====\s*PAGE\s+\d+\s*=====\s*$", re.I)
# Typescript footers: "4-3", "12-5", or a bare page number.
FOOTER = re.compile(r"^[\s'\"`.,<>&*|~^_-]*\d{1,3}\s*[-–—]\s*\d{1,3}[\s.,'\"]*$")
BARE_NUM = re.compile(r"^[\s'\"`.,<>&*|~^_-]*\d{1,3}[\s.,'\"]*$")
# "DISCOURSE" alone on a line, possibly with OCR speckle around it -- including
# a stray letter picked up from the margin, as in "y DISCOURSE".
DISCOURSE_LINE = re.compile(
    r"^(?:[A-Za-z0-9]\s+)?[^A-Za-z]{0,4}DISCOURSE[^A-Za-z]{0,4}$", re.I
)
# "No. 12" / "Noe 13" / "No, 50" / "Nos 352" / "No. ll"
NUMBER_LINE = re.compile(r"^[^A-Za-z0-9]{0,4}No[.,es]{0,3}\s*([0-9lIoO]{1,3})\b", re.I)
SENTENCE_END = re.compile(r"[.!?:;\"']\s*$")


def volume_of(n):
    for lo, hi, name, subtitle, lessons in VOLUMES:
        if lo <= n <= hi:
            return name, subtitle, lessons
    return None, None, None


def load_lines():
    """Concatenate P3..P10 (the full-text scans) into one cleaned line list."""
    lines = []
    for n in range(3, 11):
        path = os.path.join(SRC_DIR, f"P{n}.txt")
        if not os.path.exists(path):
            sys.exit(f"missing source: {path}")
        raw = open(path, encoding="utf-8", errors="replace").read().split("\n")
        for line in raw:
            s = line.rstrip()
            if PAGE_MARKER.match(s):
                # A page break is not a paragraph break; mark it so the
                # paragraph builder can decide whether to join across it.
                lines.append("\x00PAGEBREAK")
                continue
            if FOOTER.match(s) or (BARE_NUM.match(s) and s.strip()):
                continue
            lines.append(s)
    return lines


def find_discourse_starts(lines):
    """Return [(line_index, ocr_number)] for each discourse heading."""
    starts = []
    for i, line in enumerate(lines):
        if not DISCOURSE_LINE.match(line.strip()):
            continue
        ocr = None
        for j in range(i + 1, min(i + 5, len(lines))):
            m = NUMBER_LINE.match(lines[j].strip())
            if m:
                digits = m.group(1).lower().replace("l", "1").replace("i", "1")
                digits = digits.replace("o", "0")
                try:
                    ocr = int(digits)
                except ValueError:
                    ocr = None
                break
            if lines[j].strip():
                break
        starts.append((i, ocr))
    return starts


def strip_speckle(line):
    """Remove margin/binding marks the scanner picked up as stray characters."""
    s = line.strip()
    s = re.sub(r"^[|}{\\/~^*_]+\s*", "", s)
    s = re.sub(r"\s*[|}{\\~^]+\s*$", "", s)
    s = re.sub(r"\s+[|}{\\~^]+\s+", " ", s)
    return s.strip()


def normalize_divider(par):
    """The typescript's '* * * * *' rules OCR into things like 'x ok ok Ok O*'."""
    if len(par) <= 40 and re.fullmatch(r"[\s*oOxXkK.\-,']+", par) and len(par) > 2:
        return "* * * * *"
    return par


def build_paragraphs(chunk):
    """Join typescript hard wraps into paragraphs.

    Blank line = paragraph break, except where the blank only exists because a
    page marker sat there. Line-end hyphens are soft wraps and get closed up
    (fre- / quencies -> frequencies).
    """
    # Drop blank lines that merely padded a page marker, so a paragraph running
    # across a page turn is not split in two.
    lines = []
    for line in chunk:
        if line == "\x00PAGEBREAK":
            while lines and not lines[-1].strip():
                lines.pop()
            lines.append(line)
            continue
        if line == "" and lines and lines[-1] == "\x00PAGEBREAK":
            continue
        lines.append(line)

    paras, cur = [], []

    def flush():
        if cur:
            paras.append(" ".join(cur).strip())
            cur.clear()

    for line in lines:
        if line == "\x00PAGEBREAK":
            # Only a finished sentence ends the paragraph at a page turn.
            if cur and SENTENCE_END.search(cur[-1]):
                flush()
            continue
        s = strip_speckle(line)
        if not s:
            flush()
            continue
        if cur and cur[-1].endswith("-"):
            # soft hyphen: glue this line onto the previous word
            cur[-1] = cur[-1][:-1] + s
        else:
            cur.append(s)
    flush()
    paras = [normalize_divider(p) for p in paras if p]

    # A paragraph that stops mid-sentence and is followed by one starting in
    # lower case was never a paragraph break -- it is a stray blank line in the
    # transcription. Real paragraphs start with a capital.
    merged = []
    for p in paras:
        if (
            merged
            and p[:1].islower()
            and not SENTENCE_END.search(merged[-1])
            and merged[-1] != "* * * * *"
        ):
            merged[-1] = f"{merged[-1]} {p}"
        else:
            merged.append(p)
    return merged


def clean_heading_block(paras):
    """Drop the leading OCR'd 'No. 12 / Title' lines; keep Scripture Reading."""
    out = list(paras)
    while out:
        first = out[0]
        if len(first) > 90:
            break
        if NUMBER_LINE.match(first) or first.strip(" .,'\"").lower() in {
            t.lower() for t in TITLES.values()
        }:
            out.pop(0)
            continue
        # An OCR-mangled repeat of the title: short, title-cased, no sentence end.
        if len(first) < 60 and not SENTENCE_END.search(first) and first[:1].isupper():
            words = first.split()
            if len(words) <= 8 and not first.lower().startswith("scripture"):
                out.pop(0)
                continue
        break
    return out


def main():
    global SRC_DIR
    base = r"C:/Dev/Louise Morse Site"
    folder = [x for x in os.listdir(base) if x.startswith("Let") and "transfer" in x]
    if not folder:
        sys.exit("could not find the 'Let's transfer' folder")
    SRC_DIR = os.path.join(base, folder[0], "The Wastena Retreat")

    lines = load_lines()
    starts = find_discourse_starts(lines)
    os.makedirs(OUT_DIR, exist_ok=True)

    # Discourse 1's opening is not in the scans; whatever precedes the first
    # heading is its surviving tail.
    segments = []
    if starts and starts[0][0] > 0:
        segments.append((1, None, lines[: starts[0][0]]))
    for idx, (line_no, ocr) in enumerate(starts):
        end = starts[idx + 1][0] if idx + 1 < len(starts) else len(lines)
        segments.append((None, ocr, lines[line_no:end]))

    # Number sequentially from 2; the OCR number is only a sanity check.
    expected = 2
    report = []
    for i, (forced, ocr, chunk) in enumerate(segments):
        if forced is not None:
            num = forced
        else:
            num = expected
            expected += 1
        paras = build_paragraphs(chunk)
        if forced is None:
            paras = clean_heading_block(paras[1:] if paras else [])
        title = TITLES.get(num, f"Discourse {num}")
        vol, subtitle, _ = volume_of(num)
        body = "\n\n".join(paras)
        text = f"## DISCOURSE No. {num}\n\n## {title}\n\n{body}\n"
        out = os.path.join(OUT_DIR, f"discourse-{num:02d}.md")
        with open(out, "w", encoding="utf-8") as f:
            f.write(text)
        flag = ""
        if forced is None and ocr is not None and ocr != num:
            flag = f"  (scan heading read as No. {ocr})"
        report.append((num, len(body.split()), vol, title, flag))

    print(f"{'#':>3}  {'words':>7}  {'volume':<9}  title")
    for num, words, vol, title, flag in report:
        print(f"{num:>3}  {words:>7,}  {vol:<9}  {title}{flag}")
    print(f"\n{len(report)} discourses, {sum(r[1] for r in report):,} words -> {OUT_DIR}")
    missing = sorted(set(TITLES) - {r[0] for r in report})
    if missing:
        print("MISSING:", missing)


if __name__ == "__main__":
    main()
