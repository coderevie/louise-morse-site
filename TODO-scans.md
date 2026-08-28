# Scans still worth redoing

Things the site would be better for, none of them urgent, and none of them
breaking anything as it stands.

## The May 12, 1983 reading — pages 4 to 16 are cut off at the left

The reading was photographed in two batches. The first three pages are
square and clean. The remaining thirteen, which came off the phone as
`P2.pdf`, were shot at an angle with the sheet running off the left edge of
the frame, so the first few words of nearly every line are missing from the
photograph:

```
…ll be painful and more and more diffiu   to tune in as they are antennas.
…eration is increasing so very much now, rapidly, and the vibrations
…opposite of the dark forces trying to interfere trying to defeat the
```

The words are on the paper; they are simply not in the picture. That is why
this reading carries **42 `[illegible]` marks** while the May 24 reading
carries none.

**To fix:** re-photograph those thirteen pages square-on with the whole
sheet in frame, and the missing text can be read back in and most of those
marks cleared. The joined scan lives at
`pdfs/readings/reading-1983-05-12.pdf`; `tools/join_scans.py` rebuilds it
from its parts.

## Discourse 1 may be missing its opening

Worth checking whether the Wastena scan begins where the discourse begins,
or whether a page or two of the opening was never photographed.

## Five Wastena pages were typed out by hand

Pages 55, 149, 203, 205 and 211 were returned by the scanner with their
lines out of order, so they were read off the scans and typed out into
`transcripts/wastena/pages/`. Any other page can be corrected the same way:
put the page's text in `transcripts/wastena/pages/<n>.txt` and re-run
`tools/extract_wastena.py`.
