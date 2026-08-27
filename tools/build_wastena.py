"""Build the Wastena Retreat pages: one per Discourse, plus an index page.

Run from the repo root, after tools/split_wastena.py:
    python tools/build_wastena.py
"""
import html
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from split_wastena import TITLES, VOLUMES, volume_of  # noqa: E402

SRC = os.path.join("transcripts", "wastena", "final")
NOTE = (
    "Web text edition, read from scans of the original typewritten pages. "
    "The typescript's own spelling and punctuation are preserved, and some "
    "scanning errors remain; this text is still being proofread against the "
    "originals."
)


def page_name(n):
    return f"wastena-{n:02d}.html"


def pdf_for_discourse(n):
    """Return the PDF file name for a given Discourse number."""
    # Map Discourses to their source PDFs
    # P1-P2 have indexes/outlines; P3-P10 have full text
    if n <= 2:
        return "pdfs/wastena/P3.pdf"
    elif n <= 4:
        return "pdfs/wastena/P3.pdf"
    elif n <= 5:
        return "pdfs/wastena/P4.pdf"
    elif n <= 8:
        return "pdfs/wastena/P4.pdf"
    elif n <= 11:
        return "pdfs/wastena/P5.pdf"
    elif n <= 15:
        return "pdfs/wastena/P6.pdf"
    elif n <= 19:
        return "pdfs/wastena/P7.pdf"
    elif n <= 22:
        return "pdfs/wastena/P8.pdf"
    elif n <= 25:
        return "pdfs/wastena/P8.pdf"
    elif n <= 28:
        return "pdfs/wastena/P9.pdf"
    elif n <= 31:
        return "pdfs/wastena/P10.pdf"
    else:
        return "pdfs/wastena/P10.pdf"


def build_discourse(n):
    src = os.path.join(SRC, f"discourse-{n:02d}.md")
    if not os.path.exists(src):
        return False
    text = open(src, encoding="utf-8").read()

    # The page header already states the number and title, so drop the repeated
    # headings from the body.
    body = re.sub(r"\A(##[^\n]*\n\s*){1,2}", "", text)

    vol, subtitle, _ = volume_of(n)
    title = f"Discourse {n} — {TITLES[n]}"
    page_sub = f"The Wastena Retreat, {vol} — {subtitle}"

    with tempfile.NamedTemporaryFile(
        "w", suffix=".md", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(body)
        tmp_path = tmp.name
    try:
        subprocess.run(
            [sys.executable, "tools/build_reading.py", tmp_path, page_name(n),
             title, NOTE, page_sub, pdf_for_discourse(n)],
            check=True, capture_output=True,
        )
    finally:
        os.unlink(tmp_path)

    inject_pager(n)
    return True


def inject_pager(n):
    """Add previous/next links between discourses, matching the lesson pages."""
    path = page_name(n)
    doc = open(path, encoding="utf-8").read()

    prev_link = (
        f'<a class="button button--ghost" href="{page_name(n - 1)}">'
        f"← Discourse {n - 1}</a>"
        if n > 1 else "<span></span>"
    )
    next_link = (
        f'<a class="button button--ghost" href="{page_name(n + 1)}">'
        f"Discourse {n + 1} →</a>"
        if n < 33 else "<span></span>"
    )
    pager = (
        '      <nav class="pager" aria-label="Discourse navigation">\n'
        f"        {prev_link}\n"
        f'        <a class="button button--ghost" href="wastena.html">All discourses</a>\n'
        f"        {next_link}\n"
        "      </nav>\n"
    )
    doc = doc.replace("    </div>\n  </main>", pager + "    </div>\n  </main>", 1)
    open(path, "w", encoding="utf-8").write(doc)


def build_index(built):
    sections = []
    for lo, hi, name, subtitle, lessons in VOLUMES:
        cards = []
        for n in range(lo, hi + 1):
            if n not in built:
                continue
            cards.append(
                f'        <a class="item-card" href="{page_name(n)}">\n'
                f'          <span class="item-kicker">Discourse {n}</span>\n'
                f"          <h3>{html.escape(TITLES[n])}</h3>\n"
                f'          <span class="item-note">Web text edition</span>\n'
                f"        </a>"
            )
        if not cards:
            continue
        sections.append(
            f'    <section class="section wrap">\n'
            f'      <h2 class="section-title">{html.escape(name)}</h2>\n'
            f'      <p class="section-sub">{html.escape(subtitle)} · '
            f"Morse Fellowship Lessons {lessons}</p>\n"
            f'      <div class="card-grid">\n' + "\n".join(cards) + "\n      </div>\n"
            f"    </section>"
        )

    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; script-src 'self' 'unsafe-inline'" />
  <title>The Wastena Retreat — Louise Morse</title>
  <meta name="description" content="The Wastena Retreat, June–July 1967: three volumes of discourses given through Louise Morse, as web text editions." />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Inter:wght@400;500;600&display=swap" rel="stylesheet" />
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

  <main>
    <div class="page-header wrap">
      <p class="eyebrow"><a href="library.html">← Back to Library</a></p>
      <h1>The Wastena Retreat</h1>
      <p class="page-sub">
        Wastena (Sparkling Waters) · June–July 1967 · Morse Fellowship.
        Three volumes of discourses given during the retreat sessions,
        published here as web text editions.
      </p>
    </div>

{chr(10).join(sections)}
  </main>

  <footer class="site-footer">
    <div class="wrap">
      <p>© <span id="year"></span> louisemorsethechannel.com</p>
    </div>
  </footer>

  <script>
    document.getElementById("year").textContent = new Date().getFullYear();

    const THEME_KEY = "lm_theme";
    const btn = document.getElementById("themeToggle");
    function applyTheme(theme) {{
      document.documentElement.setAttribute("data-theme", theme);
      localStorage.setItem(THEME_KEY, theme);
      btn.setAttribute("aria-pressed", String(theme === "dark"));
      btn.textContent = theme === "dark" ? "Light mode" : "Dark mode";
    }}
    applyTheme(localStorage.getItem(THEME_KEY) === "dark" ? "dark" : "light");
    btn.addEventListener("click", function () {{
      applyTheme(document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark");
    }});
  </script>
</body>
</html>
"""
    open("wastena.html", "w", encoding="utf-8").write(page)


def main():
    built = set()
    for n in sorted(TITLES):
        if build_discourse(n):
            built.add(n)
    build_index(built)
    print(f"built {len(built)} discourse pages + wastena.html")
    missing = sorted(set(TITLES) - built)
    if missing:
        print("missing:", missing)


if __name__ == "__main__":
    main()
