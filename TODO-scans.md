# Scans still worth redoing

Things the site would be better for, none of them urgent, and none of them
breaking anything as it stands.

## Done — the May 12, 1983 reading (29 August 2026)

Scott re-photographed the whole reading square-on, and dropped the blurred
duplicate of page 4 that was in the first set. The scan now runs to fifteen
clean pages and all **42 `[illegible]` marks are cleared** — the text they
stood for was on the paper the whole time, just outside the old frame.

Typed page 5 is genuinely lost and never was in these papers: the page
numbers run 1, 2, 3, 4, 6, 7 … 16, and the reading's note now says so.

One word is worth a second look if the sheet is ever handled again: the
last line of page 10 is clipped by the photograph's bottom edge, and
"don't **get** up and run away" was read from the surviving letter-tops
rather than the whole word.

## Done — page 2 of the publications list (29 August 2026)

That page turned out to be an extra rather than part of the booklet, so it
is deleted rather than re-photographed; the scan is now sixteen pages. The
twelve sideways pages in the same document were fixed earlier — see
`tools/rotate_scan_pages.py`.

## Closed — Discourse 1 is not missing its opening

This worry came from the original, mistaken page mapping, which had the
discourses starting further forward than they do. Discourse 1 in fact
begins at the top of scan page 46, with its own DISCOURSE / No. 1 /
Prepare Your Retreat heading and the words "Our blessings are upon you",
directly after the Volume One index on page 45. Nothing was left
unphotographed.

## Five Wastena pages were typed out by hand

Pages 55, 149, 203, 205 and 211 were returned by the scanner with their
lines out of order, so they were read off the scans and typed out into
`transcripts/wastena/pages/`. Any other page can be corrected the same way:
put the page's text in `transcripts/wastena/pages/<n>.txt` and re-run
`tools/extract_wastena.py`.
