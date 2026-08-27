"""Correct typing errors in the lessons, readings and booklets.

These were transcribed page by page rather than run through the bulk
scanner, so they carry almost none of the faults the Wastena text does -
about a dozen slips in forty-two thousand words. Each is listed here with
enough of its sentence to show it is a slip and not the typist's own
spelling, which stays as it was.

    python tools/proofread_readings.py           # apply, then report
    python tools/proofread_readings.py --dry-run # report only
"""
import collections
import glob
import os
import sys

SRC = os.path.join("transcripts", "published")

# Wrong -> right, with the sentence each was found in.
FIXES = {
    # lesson 83
    "personal attentioh and": "personal attention and",
    "and small changes can ta ke place": "and small changes can take place",
    'in the grea t "Supreme Intelligence"': 'in the great "Supreme Intelligence"',
    "an ideal, an inage": "an ideal, an image",
    "trying to evalute the spiritual": "trying to evaluate the spiritual",
    "without words. Ther you know": "without words. There you know",
    # May 12, 1983
    "actually getting ride of the false kingdom":
        "actually getting rid of the false kingdom",
    'yoked." Woever you are marrying': 'yoked." Whoever you are marrying',
    "[illegible] imself from places": "[illegible] himself from places",
    # May 24, 1983
    "and throguh those that are willing": "and through those that are willing",
    "to be humble ehough, obedient": "to be humble enough, obedient",
    "But the expectency is needed": "But the expectancy is needed",
    "you could certainly prise God": "you could certainly praise God",
}


def main():
    dry = "--dry-run" in sys.argv
    tally = collections.Counter()
    touched = 0

    for path in sorted(glob.glob(os.path.join(SRC, "*.md"))):
        text = open(path, encoding="utf-8").read()
        fixed = text
        for wrong, right in FIXES.items():
            if wrong in fixed:
                tally[(wrong, right)] += fixed.count(wrong)
                fixed = fixed.replace(wrong, right)
        if fixed != text:
            touched += 1
            if not dry:
                open(path, "w", encoding="utf-8").write(fixed)

    total = sum(tally.values())
    print(f"{'would correct' if dry else 'corrected'} {total} readings "
          f"across {touched} files")
    for (a, b), n in tally.most_common():
        short = a if len(a) < 46 else a[:43] + "..."
        print(f"    {short}")

    missing = [w for w in FIXES if not tally.get((w, FIXES[w]))]
    if missing:
        print(f"\n{len(missing)} entries matched nothing (already corrected):")
        for w in missing:
            print(f"    {w[:60]}")


if __name__ == "__main__":
    main()
