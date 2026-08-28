"""Build the lessons, readings and booklets from their transcripts.

Each page was previously built by hand, so the wording of its heading was
whatever was typed at the time; keeping the arguments here means a page can
be rebuilt after the text is corrected without having to remember them.

    python tools/build_readings.py
"""
import os
import subprocess
import sys

NOTE = ("Web text edition, transcribed from the original typewritten pages. "
        "The original spelling and punctuation are preserved.")

PUBLIC_NOTE = "Web text edition, transcribed from the original publication."

# (transcript, page, title, note, subtitle, scan or None)
PAGES = [
    ("lesson83.md", "83.html", "Lesson 83", NOTE,
     "Morse Fellowship — Identifier: John 17", "lesson-83"),
    ("lesson215.md", "215.html", "Lesson 215", NOTE,
     "Morse Fellowship — Identifier: Acts 1", "lesson-215"),
    ("may12.md", "reading-1983-05-12.html", "May 12, 1983 — Morse Reading",
     NOTE + " Some passages were unreadable on the scan and are marked "
            "[illegible].",
     "Greetings Dear Ones", "reading-1983-05-12"),
    ("may24.md", "reading-1983-05-24.html", "May 24, 1983 — Morse Reading",
     NOTE, "Establish A Communication Within", "reading-1983-05-24"),
    ("booklet2.md", "booklet-channelling-and-group-vortex.html",
     "Booklet No. 2 — Channelling and Group Vortex", NOTE,
     "Morse Fellowship", "booklet-2"),
    ("publist.md", "publications-list.html",
     "Through the Portals — Publications List", PUBLIC_NOTE,
     "Morse Fellowship", "publications-list"),
]

SRC = os.path.join("transcripts", "published")


def main():
    for md, out, title, note, subtitle, scan in PAGES:
        args = [sys.executable, "tools/build_reading.py",
                os.path.join(SRC, md), out, title, note, subtitle]
        if scan:
            args.append(scan)
        subprocess.run(args, check=True, capture_output=True)
        print(f"  {out}")
    print(f"built {len(PAGES)} pages")


if __name__ == "__main__":
    main()
