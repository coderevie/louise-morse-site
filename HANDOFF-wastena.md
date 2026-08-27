# The Wastena Retreat — transcription notes

**Status: published.** All 33 Discourses are live as web text editions at
`wastena.html` and `wastena-01.html` … `wastena-33.html`.

This document records where the text came from, how the pages are generated, and
what still needs attention.

---

## What the document is

The Wastena Retreat is a 1967 Morse Fellowship publication — **3 volumes, 33
numbered Discourses**, given at Wastena ("Sparkling Waters") in June–July 1967 and
preserved only as scanned typewritten pages.

| Volume | Discourses | Subtitle | Morse Fellowship Lessons |
|---|---|---|---|
| 1 | 1–11 | The Fourth Dimensional Discipleship, Continued | 331–341 |
| 2 | 12–22 | The Upper Room with the Master | 342–352 |
| 3 | 23–33 | Entering the Door into Paradise | 353–363 |

## Where the text came from

Two independent transcription passes exist, and both are kept:

- **`transcripts/chatgpt-source/the-wastena-retreat_p*.txt`** — a complete pass by
  ChatGPT over all ten scans, with `===== PAGE n =====` markers. **This is the
  source the published pages are built from** (~128,000 words).
- **`transcripts/wastena/part*.md`** — an earlier, partial pass (~67,000 words,
  roughly half of each scan). Superseded for publishing, but valuable as a
  **second independent reading** to check the published text against.

The original scans are ~320 MB and live outside git, at
`C:\Dev\Louise Morse Site\Wastena Retreat\` (`P1.pdf`–`P10.pdf`). `P1` and `P2`
hold front matter, volume indexes and brief session outlines; `P3`–`P10` hold the
full Discourse texts.

## How the pages are built

Two scripts, run from the repo root in this order:

```bash
python tools/split_wastena.py    # P3-P10 source text -> transcripts/wastena/final/discourse-NN.md
python tools/build_wastena.py    # those -> wastena-NN.html + wastena.html index
```

`split_wastena.py` strips page markers and typescript footers, closes up
end-of-line hyphenation, rejoins hard-wrapped lines into paragraphs, removes
margin speckle the scanner picked up (`|`, `}`, `\`), and splits on the
`DISCOURSE / No. N` headings. Because those headings OCR badly ("No, 50",
"Nos 352", "Noe 13"), Discourses are numbered **sequentially** and the scanned
number is only used as a sanity check — the script prints a warning when the two
disagree. Titles come from the volume indexes, which are authoritative.

`build_wastena.py` feeds each Discourse through `tools/build_reading.py` (the
shared page generator used by every other page on the site), then adds
previous/next navigation and writes the index page.

## What still needs attention

- **Proofreading.** The scans are faint in places and the machine reading carries
  through visible errors — most commonly a typed period read as the letter "e"
  ("youe" for "you.", "backe" for "back."), plus misreadings like "seoking",
  "thoir", "inorease". The page note tells readers the text is still being
  proofread. A pass against the scans, or a diff against the second transcription
  in `transcripts/wastena/part*.md`, would clean this up.
- **Discourse 1 is incomplete.** Its opening is not in the scans — `P3.pdf` begins
  partway through it. Only the surviving tail is published. The missing pages may
  need re-photographing.
- **A few trailing fragments.** Some Discourses end with a short dangling line
  (e.g. "The message is") that appears at the foot of a scanned page. These are
  reproduced as found rather than guessed at.
- **The May 12, 1983 reading, separately.** The published page
  (`reading-1983-05-12.html`) carries 42 `[illegible]` marks from a torn left
  margin, and is missing page 5 of its original. ChatGPT's pass of the same
  document (`transcripts/chatgpt-source/readings_p1.txt` and `_p2.txt`) has **no**
  gaps. That is either a better reading or reconstruction of unreadable text —
  it should be checked against the scan before replacing the published page.

## Transcription conventions

If you add or correct text, match what is already there:

- Transcribe faithfully — preserve the typescript's own wording, punctuation and
  typos. Do not modernize or paraphrase.
- Where a handwritten correction amends the typing, use the corrected wording.
- Underlined passages → `<u>...</u>`. Unreadable text → `[illegible]`, never a guess.
- `##` for headings printed in the document; blank line between paragraphs.
- No editorial commentary inside a transcript file — notes belong here instead.
