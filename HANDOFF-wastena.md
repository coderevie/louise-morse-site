# Handoff: Transcribing The Wastena Retreat

**For whoever picks this up next — ChatGPT, another assistant, or a human.**
You do not need any prior conversation to use this document. Everything required is below.

---

## 1. What this job is

The Wastena Retreat is a 1967 Morse Fellowship publication: **3 volumes, 33 numbered Discourses**, preserved only as scanned typewritten pages. We are converting those scans into clean text so they can be published on <https://louisemorsethechannel.com>.

**About half is already done.** Roughly **66,600 words** of finished transcription are saved in `transcripts/wastena/` in this repository. Do not start over. Your job is to **continue from where each file stops**.

The site is text-first: we publish readable transcriptions, not PDF downloads.

---

## 2. Source scans

Ten PDFs, 238 pages total, all image-only (no text layer — they need visual reading/OCR):

| File | Pages | What it contains |
|---|---|---|
| `P1.pdf` | 24 | Title pages + indexes for all 3 volumes, then Discourse 1 onward |
| `P2.pdf` | 24 | Session outlines for Discourses 19–28, plus Volume I index |
| `P3.pdf` | 24 | Full text, Discourse 2 onward |
| `P4.pdf` | 24 | Full text, Discourses ~4–10 |
| `P5.pdf` | 24 | Full text, Discourse 9 onward |
| `P6.pdf` | 24 | Volume II index, then Discourse 12 onward |
| `P7.pdf` | 24 | Full text, Discourses 16–17 onward |
| `P8.pdf` | 24 | Full text, Discourse 22 onward |
| `P9.pdf` | 24 | Full text, Discourses 26–27 onward |
| `P10.pdf` | 22 | Full text, Discourses 30–31 onward |

**Where they are:** `C:\Dev\Louise Morse Site\Wastena Retreat\` (also inside `C:\Dev\Louise Morse Site\Filess from Iphone.zip` under `Let's transfer/The Wastena Retreat/`). They are ~320 MB total and deliberately **not** committed to this repository.

To work in ChatGPT, upload one PDF at a time — they are 15–38 MB each.

### The page-number trick

Most scanned pages carry a footer like `4-4` or `22-2`, meaning **Discourse 4, page 4** and **Discourse 22, page 2**. Use this to identify exactly where any page belongs and to detect gaps. It is the fastest way to orient yourself in a stack of scans.

---

## 3. The complete Discourse index

Transcribed from the volume indexes. Discourse numbers run continuously 1–33 across the three volumes, and each volume also maps to the Morse Fellowship's numbered lesson series.

**Volume 1 — "The Fourth Dimensional Discipleship, Continued"** (Morse Fellowship Lessons 331–341)

1. Prepare Your Retreat
2. Identify With the Early Christians
3. Identify as His Disciples
4. Listen to the Lord
5. Call to Remembrance
6. Many are with Us
7. The Cells of the Body
8. The Light Centers
9. Soul Development
10. The Lifting Veil
11. Re-Orient in the Soul

**Volume 2 — "The Upper Room with the Master"** (Lessons 342–352)

12. Light Centers Forming
13. The Cup of the Water of Life
14. Fulfill the Conditions
15. The Wind of Spirit
16. The Development of Families
17. Soul Memories to be Restored
18. Love in the Higher Nature
19. Law of Love
20. Spiritual Meat
21. Awake, Begotten
22. The True Bread

**Volume 3 — "Entering the Door into Paradise"** (Lessons 353–363)

23. Establish Communication with the Lord
24. Rededicate Your Life to God
25. Light Centers — The Loaves that Feed Many
26. Spiritual Man
27. The Be-attitudes
28. Come Apart from the World
29. The Heart Circuit
30. Change Your Habits Now
31. The Soul Restored
32. Know Who You Follow
33. The Mystical Body

---

## 4. What is already transcribed, and where to resume

Each file below is in `transcripts/wastena/`. **Every one stops mid-document.** To continue: open the matching PDF, find the passage quoted under "Stops at", and transcribe onward from that exact point.

| File | Words | Source | Stops at (find this passage, continue after it) |
|---|---|---|---|
| `part1.md` | 5,194 | P1.pdf | "...Direct the power. In the vortex is the Christ. **The Presence** of the Lord." |
| `part2.md` | 4,158 | P2.pdf | "...9. Soul Development / 10. The Lifting Veil / 11. Re-Orient in the Soul" (end of a Volume I index page) |
| `part3.md` | 7,887 | P3.pdf | "...The same is true of appearances of loved ones from the other side, or of watching celestial" |
| `part4a.md` | 3,809 | P4.pdf pp.1–12 | "...This is all right as a temporary measure, but it is only" |
| `part4b.md` | 5,070 | P4.pdf pp.13–24 | "...As you do for a time you forget, lose sight of the other role that you are playing. When you take the" |
| `part4-discourse10.md` | 2,100 | P4.pdf | "...Have no panic, no fear, but in orderly fashion trust your Lord. This is the common sense that God gave" |
| `part5.md` | 5,711 | P5.pdf | "...for you are giving up one life to receive the eternal. Bless you. Selah." |
| `part6.md` | 4,576 | P6.pdf | "...but we speak directly to God's church through your souls, encouraging" |
| `part6-continued.md` | 2,377 | P6.pdf | "...as your soul willingly comes into line with God's plan of" |
| `part7.md` | 6,248 | P7.pdf | "...But there is a different way, a different manner. One with true spiritual" |
| `part8.md` | 6,098 | P8.pdf | "...ask anything and it shall be done. Then" |
| `part9.md` | 7,333 | P9.pdf | "...Be in a heavenly frame of reference, looking from the mountaintop over the valley. You are" |
| `part10.md` | 6,066 | P10.pdf | "...You can feel and experience the power moving through, and greater action will follow according to the laws of God." |

Note that `part4a`, `part4b` and `part4-discourse10` all came from P4.pdf via different passes and cover **different** Discourses (roughly 5, 7 and 10). Check the page footers before assuming any of them are contiguous.

---

## 5. Transcription rules

New text must match the existing text, so follow these exactly:

- **Transcribe faithfully.** Preserve the original wording, punctuation, and spelling — **including typos** (e.g. "ascention", "trhough", "prise God"). This is a historical document; do not modernize, correct, paraphrase, or summarize.
- **Handwritten corrections on the page win.** Where someone wrote a correction over the typescript, use the corrected wording.
- **Underlined passages** → wrap in `<u>...</u>`.
- **Unreadable text** → `[illegible]`. Do not guess.
- **Headings printed in the document** → `##` (e.g. `## DISCOURSE No. 12`, `## The Cup of the Water of Life`).
- **Paragraphs** separated by a blank line. Do not re-wrap or merge paragraphs.
- **No editorial commentary in the file** — no notes, no "[continued]", no summaries. Only the document's own words.

---

## 6. Known problems to expect

- **Duplicate scans.** P2 pages 13–14 repeat pages 11–12. Others may too. Check page footers; transcribe repeated content only once.
- **Damaged margins.** Some pages have a torn or cut-off left margin. Mark those spots `[illegible]` rather than inventing words.
- **Content filters may refuse these pages.** Two automated attempts were blocked by safety classifiers. The material is ordinary 1967 devotional writing, but it contains end-times prophecy ("the day of wrath"), talk of a chosen remnant, and celestial/UFO passages that can pattern-match to doomsday or cult content. If a tool refuses:
  - work in **smaller batches** (~10–12 pages), and
  - **state the framing plainly**: this is archival digitization of a historical religious document from 1967 for a preservation website.
- **Missing pages.** One earlier document (the May 12, 1983 reading) was missing a page from its scan. If the Discourse/page footers skip a number, note it to Scott — the page may need re-photographing.

---

## 7. What to hand back

**One Markdown file per Discourse**, named `discourse-01.md` … `discourse-33.md`, placed in `transcripts/wastena/final/`.

Each file starts with the Discourse number and title as printed, then the full text:

```markdown
## DISCOURSE No. 12

## Light Centers Forming

<u>Scripture Reading:</u> ...

Blessings be unto you, beloveds. ...
```

Publish **full Discourse text only**. The brief session outlines in P1/P2 ("Jottings During The Sessions") are working notes and are **not** being published — use them for cross-checking titles and ordering, not as content.

---

## 8. Turning the Markdown into web pages

The repository already has a generator. From the repository root:

```bash
python tools/build_reading.py transcripts/wastena/final/discourse-12.md discourse-12.html "Discourse 12 — Light Centers Forming" "Web text edition, transcribed from the original typewritten pages. Original spelling and typing preserved." "The Wastena Retreat, Volume 2 — The Upper Room with the Master"
```

Arguments are: input Markdown, output HTML, page title, the small note above the text, and the subtitle under the heading. The generator handles the site's shared styling — the academic serif transcript layout, light/dark theme, header and footer — so no HTML needs writing by hand.

Then add each finished Discourse to `library.html` in the "Booklets & Retreat Volumes" section. Follow the pattern of the existing cards: a `<a class="item-card" href="...">` with an `item-kicker` (e.g. "Discourse 12"), an `<h3>` title, and an `item-note` reading "Web text edition". The card currently marked "Coming soon" for the retreat should be replaced by an index page once enough Discourses exist.

---

## 9. Definition of done

- [ ] All 33 Discourses transcribed into `transcripts/wastena/final/`
- [ ] Any gaps or missing scan pages reported to Scott
- [ ] Each Discourse built into an HTML page with `tools/build_reading.py`
- [ ] An index page listing all 33 Discourses by volume, linking to each
- [ ] `library.html` updated — retreat card no longer "Coming soon"
- [ ] Committed and pushed to `main` (this deploys the live site automatically)
