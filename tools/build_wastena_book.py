"""Build The Wastena Retreat as a continuous book: front matter, the three
volume indexes and the 33 discourses, each page linking to its own scan and
carrying previous/next controls at the top and the bottom.

Run from the repo root, after tools/extract_wastena.py:
    python tools/build_wastena_book.py            # the whole book
    python tools/build_wastena_book.py --preview  # one page, for trying ideas
"""
import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wastena_map import (TITLES, VOLUMES, pdf_for_pages,  # noqa: E402
                         reading_order, volume_of)

SRC = os.path.join("transcripts", "wastena", "book")
NOTE = ("Web text edition, read from scans of the original typewritten pages. "
        "The typescript's own spelling and punctuation are preserved, and some "
        "scanning errors remain; this text is still being proofread against "
        "the originals.")

FONTS = ("https://fonts.googleapis.com/css2?"
         "family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500"
         "&family=Courier+Prime:ital,wght@0,400;0,700;1,400"
         "&family=Inter:wght@400;500;600&display=swap")

HEAD = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; \
style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; \
font-src https://fonts.gstatic.com; script-src 'self' 'unsafe-inline'" />
  <title>{title} — Louise Morse</title>
  <meta name="description" content="{description}" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="{fonts}" rel="stylesheet" />
  <link rel="stylesheet" href="style.css" />
  <script>
    (function () {{
      var t = localStorage.getItem("lm_theme");
      if (["light", "dark"].includes(t)) document.documentElement.setAttribute("data-theme", t);
    }})();
  </script>
</head>

<body>
  <header class="site-header">
    <div class="wrap masthead">
      <div class="brand">
        <a href="index.html">
          <h1 class="site-title">Louise Morse</h1>
          <p class="site-subtitle">The Channeler · Digital Library</p>
        </a>
      </div>
      <nav class="top-nav" aria-label="Primary">
        <a href="index.html">Home</a>
        <a href="library.html">Library</a>
        <button id="themeToggle" class="theme-toggle" type="button" aria-pressed="false">Dark mode</button>
      </nav>
    </div>
  </header>
"""

TAIL = """
  <footer class="site-footer">
    <div class="wrap">
      <p>© <span id="year"></span> louisemorsethechannel.com</p>
    </div>
  </footer>

  <script>
    document.getElementById("year").textContent = new Date().getFullYear();

    const THEME_KEY = "lm_theme";
    const btn = document.getElementById("themeToggle");
    function applyTheme(theme) {
      document.documentElement.setAttribute("data-theme", theme);
      localStorage.setItem(THEME_KEY, theme);
      btn.setAttribute("aria-pressed", String(theme === "dark"));
      btn.textContent = theme === "dark" ? "Light mode" : "Dark mode";
    }
    applyTheme(localStorage.getItem(THEME_KEY) === "dark" ? "dark" : "light");
    btn.addEventListener("click", function () {
      applyTheme(document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark");
    });
  </script>
</body>
</html>
"""


# A speaker or a heading the typist set off with a colon and an underline.
LABEL = re.compile(r"^(Scripture Reading|Teachers?|The Master|Aleph|Sarramya"
                   r"|The Presence of the Lord|Daily Word reading"
                   r"|Prayer|Meditation|Closing|Question):")


# The three volume indexes, which are set out rather than run as prose.
INDEX_PAGES = {"wastena-front-06", "wastena-index-02", "wastena-index-03"}

# Directions the typist set on a line of their own.
DIRECTIONS = {"Prayer", "Selah", "Meditation", "Silence", "Closing Prayer",
              "Opening of the Retreat", "Closing of the Retreat"}


def esc(s):
    return html.escape(s, quote=True)


def read_body(slug):
    path = os.path.join(SRC, f"{slug}.md")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    return [b.strip() for b in text.split("\n\n") if b.strip()]


def render_body(slug, kind):
    """Turn the extracted Markdown into the book's HTML.

    On the title pages and indexes the typist centred short lines rather than
    running them as prose, so those are set centred here too.
    """
    centre_short = kind in ("front", "index")
    out = []
    for block in read_body(slug):
        if block.startswith("# "):
            continue                        # the page header supplies the title
        mark = re.fullmatch(r"\[page (\d+)\]", block)
        if mark:
            out.append(f'<span class="page-mark">Page {mark.group(1)}</span>')
            continue
        if block.startswith("## "):
            out.append(f"<h3>{esc(block[3:].strip())}</h3>")
            continue
        if centre_short and len(block) < 60:
            out.append(f'<p class="book-line">{esc(block)}</p>')
            continue
        # The typist underlined the speaker and the scripture reference:
        # "Scripture Reading:  Luke 16-17.", "Teachers:  Welcome to this place".
        label = LABEL.match(block)
        if label:
            rest = esc(block[label.end():].strip())
            out.append(f'<p class="book-said"><u>{esc(label.group(1))}:</u> '
                       f"{rest}</p>")
            continue
        # A direction the typist set on a line of its own.
        if block.strip().rstrip(".") in DIRECTIONS:
            out.append(f'<p class="book-direction">{esc(block)}</p>')
            continue
        out.append(f"<p>{esc(block)}</p>")
    return "\n        ".join(out)


def render_index(slug):
    """Set a volume index as the typist set it.

    The scanner lost the discourse numbers down the left of these pages and
    ran the titles into one another, so the list is set out from the titles
    recorded in wastena_map instead: the volume name underlined, then each
    discourse against its number, as on the page.
    """
    volume = {"wastena-front-06": VOLUMES[0],
              "wastena-index-02": VOLUMES[1],
              "wastena-index-03": VOLUMES[2]}[slug]
    lo, hi, name, subtitle, lessons = volume
    roman = {"Volume One": "I", "Volume Two": "II", "Volume Three": "III"}[name]

    rows = "\n          ".join(
        f'<li><span class="index-no">{n}</span>'
        f"<span class=\"index-title\">{esc(TITLES[n])}</span></li>"
        for n in range(lo, hi + 1)
    )
    return (
        '<p class="book-line">THE WASTENA RETREAT</p>\n'
        f'        <p class="book-line">Index &mdash; Volume {roman}, {lo}-{hi}</p>\n'
        f'        <p class="book-line">Morse Fellowship Lessons {lessons}</p>\n'
        f'        <p class="book-line index-volume"><u>{esc(subtitle)}</u></p>\n'
        f'        <ol class="index-list">\n          {rows}\n        </ol>'
    )


def scan_bar(first, last):
    scan = pdf_for_pages(first, last)
    file_id = scan[:-4]                     # page46-53.pdf -> page46-53
    pages = (f"page {first}" if first == last
             else f"pages {first}–{last}")
    return (
        '    <div class="wrap scan-bar">\n'
        f'      <a class="scan-link" href="pdf-viewer.html?file={esc(file_id)}">'
        f'📄 Read the original scan <span class="scan-pages">· {pages}</span></a>\n'
        "    </div>\n"
    )


def pager(prev, nxt, position):
    """Previous/next controls. `prev` and `nxt` are (href, label) or None."""
    left = (f'<a class="button button--ghost" href="{prev[0]}">← {esc(prev[1])}</a>'
            if prev else "<span></span>")
    right = (f'<a class="button button--ghost" href="{nxt[0]}">{esc(nxt[1])} →</a>'
             if nxt else "<span></span>")
    cls = "pager pager--top" if position == "top" else "pager"
    return (
        f'      <nav class="{cls}" aria-label="Retreat navigation">\n'
        f"        {left}\n"
        '        <a class="button button--ghost" href="wastena.html">Contents</a>\n'
        f"        {right}\n"
        "      </nav>\n"
    )


def heading_block(kind, n, title):
    """The centred heading, set as the typist set it."""
    if kind == "discourse":
        return (
            '        <div class="book-heading">\n'
            '          <p class="book-kicker">Discourse</p>\n'
            f'          <p class="book-number">No. {n}</p>\n'
            f"          <h2>{esc(TITLES[n])}</h2>\n"
            "        </div>\n"
        )
    return ""


def short_label(entry):
    """A compact label for the previous/next buttons."""
    kind, slug, title = entry[0], entry[1], entry[2]
    if kind == "discourse":
        return f"Discourse {int(slug.split('-')[-1])}"
    if kind == "index":
        return title.replace("Index — ", "Index: ")
    return title.split(" — ")[0]


def build_page(entry, prev, nxt):
    kind, slug, title, subtitle, first, last = entry
    n = int(slug.split("-")[-1]) if kind == "discourse" else None

    if kind == "discourse":
        vol, vol_sub, lessons = volume_of(n)
        page_sub = f"The Wastena Retreat, {vol} — {vol_sub}"
    else:
        page_sub = subtitle

    prev_ctl = (prev[0], short_label(prev[1])) if prev else None
    next_ctl = (nxt[0], short_label(nxt[1])) if nxt else None

    doc = HEAD.format(title=esc(title), description=esc(page_sub or title),
                      fonts=FONTS)
    doc += (
        "\n  <main>\n"
        '    <div class="page-header wrap">\n'
        '      <p class="eyebrow"><a href="wastena.html">← The Wastena Retreat</a></p>\n'
        f"      <h1>{esc(title)}</h1>\n"
        + (f'      <p class="page-sub">{esc(page_sub)}</p>\n' if page_sub else "")
        + "    </div>\n\n"
        + scan_bar(first, last)
        + '\n    <div class="wrap">\n'
        + pager(prev_ctl, next_ctl, "top")
        + '\n      <section class="card book">\n'
        + heading_block(kind, n, title)
        + f'        <p class="muted small">{esc(NOTE)}</p>\n'
        '        <hr style="border:none;border-top:1px solid var(--line);margin:14px 0 26px;" />\n'
        f"        {render_index(slug) if slug in INDEX_PAGES else render_body(slug, kind)}\n"
        "      </section>\n\n"
        + pager(prev_ctl, next_ctl, "bottom")
        + "    </div>\n  </main>\n"
    )
    doc += TAIL
    return doc


def build_index(entries):
    """The contents page: front matter, then each volume's discourses."""
    front = [e for e in entries if e[0] == "front"]
    cards = "\n".join(
        f'        <a class="item-card" href="{e[1]}.html">\n'
        f'          <span class="item-kicker">Pages {e[4]}–{e[5]}</span>\n'
        f"          <h3>{esc(e[2])}</h3>\n"
        f'          <span class="item-note">{esc(e[3])}</span>\n'
        "        </a>"
        for e in front
    )
    sections = [
        '    <section class="section wrap">\n'
        '      <h2 class="section-title">Retreat Introduction</h2>\n'
        '      <p class="section-sub">Title pages, the session jottings, '
        "the Fellowship's foreword and the volume indexes.</p>\n"
        f'      <div class="card-grid">\n{cards}\n      </div>\n'
        "    </section>"
    ]

    by_slug = {e[1]: e for e in entries}
    for lo, hi, name, subtitle, lessons in VOLUMES:
        cards = []
        for n in range(lo, hi + 1):
            e = by_slug.get(f"wastena-{n:02d}")
            if not e:
                continue
            cards.append(
                f'        <a class="item-card" href="wastena-{n:02d}.html">\n'
                f'          <span class="item-kicker">Discourse {n}</span>\n'
                f"          <h3>{esc(TITLES[n])}</h3>\n"
                f'          <span class="item-note">Pages {e[4]}–{e[5]}</span>\n'
                "        </a>"
            )
        idx = next((e for e in entries
                    if e[0] == "index" and e[2].endswith(name)), None)
        index_line = (
            f'      <p class="section-sub"><a href="{idx[1]}.html">'
            f"Read the printed index for {name} →</a></p>\n" if idx else ""
        )
        sections.append(
            '    <section class="section wrap">\n'
            f'      <h2 class="section-title">{esc(name)} — {esc(subtitle)}</h2>\n'
            f'      <p class="section-sub">Discourses {lo}–{hi} · '
            f"Morse Fellowship Lessons {lessons}</p>\n"
            + index_line
            + f'      <div class="card-grid">\n' + "\n".join(cards) + "\n      </div>\n"
            "    </section>"
        )

    doc = HEAD.format(title="The Wastena Retreat",
                      description="The Wastena Retreat, June–July 1967: three "
                                  "volumes of discourses given through Louise "
                                  "Morse, as web text editions.",
                      fonts=FONTS)
    complete = (
        '    <section class="section wrap">\n'
        '      <h2 class="section-title">The Complete Scan</h2>\n'
        '      <p class="section-sub">All 238 pages of the three volumes in one\n'
        "        place, from the title pages through to the last discourse.</p>\n"
        '      <div class="scan-bar" style="justify-content:flex-start;">\n'
        '        <a class="scan-link" href="pdf-viewer.html?file=wastena-full">'
        "📄 Read the complete retreat "
        '<span class="scan-pages">· pages 1–238</span></a>\n'
        "      </div>\n"
        "    </section>"
    )

    doc += (
        "\n  <main>\n"
        '    <div class="page-header wrap">\n'
        '      <p class="eyebrow"><a href="library.html">← Back to Library</a></p>\n'
        "      <h1>The Wastena Retreat</h1>\n"
        '      <p class="page-sub">\n'
        "        Wastena (Sparkling Waters) · June–July 1967 · Morse Fellowship.\n"
        "        Three volumes of discourses given during the retreat sessions,\n"
        "        published here in the order the bound volumes read.\n"
        "      </p>\n"
        "    </div>\n\n"
        + "\n\n".join(sections + [complete])
        + "\n  </main>\n"
    )
    doc += TAIL
    return doc


def main():
    entries = list(reading_order())
    preview = "--preview" in sys.argv

    if preview:
        # One discourse, written aside so ideas can be tried without
        # disturbing the published pages.
        i = next(i for i, e in enumerate(entries) if e[1] == "wastena-01")
        doc = build_page(entries[i],
                         (f"{entries[i-1][1]}.html", entries[i - 1]),
                         (f"{entries[i+1][1]}.html", entries[i + 1]))
        with open("wastena-experiment.html", "w", encoding="utf-8") as f:
            f.write(doc)
        print("wrote wastena-experiment.html")
        return

    for i, entry in enumerate(entries):
        prev = (f"{entries[i-1][1]}.html", entries[i - 1]) if i else None
        nxt = ((f"{entries[i+1][1]}.html", entries[i + 1])
               if i + 1 < len(entries) else None)
        with open(f"{entry[1]}.html", "w", encoding="utf-8") as f:
            f.write(build_page(entry, prev, nxt))

    with open("wastena.html", "w", encoding="utf-8") as f:
        f.write(build_index(entries))
    print(f"built {len(entries)} pages + wastena.html")


if __name__ == "__main__":
    main()
