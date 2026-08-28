"""Build a reading/lesson page from a Markdown transcript.

Usage: python tools/build_reading.py <transcript.md> <output.html> <page-title> <eyebrow> <subtitle> [pdf-path]
The transcript's H1/H2 lines become headings; blank-line-separated blocks become paragraphs.
If pdf-path is provided, a link to it appears in the footer.
"""
import sys, html, re, os

args = sys.argv[1:7]
md_path, out_path, title, eyebrow, subtitle = args[:5]
pdf_file = args[5] if len(args) > 5 else None  # e.g., 'lesson-83' or None

with open(md_path, encoding="utf-8") as f:
    blocks = [b.strip() for b in f.read().split("\n\n") if b.strip()]

body = []
for b in blocks:
    if b.startswith("## "):
        body.append(f'<h2>{html.escape(b[3:].strip())}</h2>')
    elif b.startswith("# "):
        continue  # page header supplies the title
    elif all(l.lstrip().startswith("- ") for l in b.splitlines()):
        items = "".join(f"<li>{html.escape(l.lstrip()[2:].strip())}</li>" for l in b.splitlines())
        body.append(f"<ul>{items}</ul>")
    else:
        # Replace escaped asterisks first
        text = b.replace("\\* ", "* ").replace("\\*", "*")
        # Extract underlined sections using placeholders to avoid double-escaping
        underlines = []
        def replace_underline(m):
            idx = len(underlines)
            underlines.append(html.escape(m.group(1)))
            return f"\x00UNDERLINE{idx}\x00"
        text = re.sub(r"<u>(.*?)</u>", replace_underline, text, flags=re.DOTALL)
        # Now escape everything else
        text = html.escape(text).replace("\n", " ")
        # Restore underlined sections
        for idx, content in enumerate(underlines):
            text = text.replace(f"\x00UNDERLINE{idx}\x00", f"<u>{content}</u>")
        body.append(f"<p>{text}</p>")

content = "\n        ".join(body)

# The link to the scan belongs at the head of the page, where a reader looks
# for it before starting, rather than buried under the text.
scan_bar = ""
if pdf_file:
    scan_bar = (
        '    <div class="wrap scan-bar">\n'
        f'      <a class="scan-link" href="pdf-viewer.html?file={html.escape(pdf_file)}">'
        "📄 Read the original scan</a>\n"
        "    </div>\n"
    )

page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; script-src 'self' 'unsafe-inline'" />
  <title>{html.escape(title)} — Louise Morse</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Inter:wght@400;500;600&family=STIX+Two+Text:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet" />
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
      <h1>{html.escape(title)}</h1>
      <p class="page-sub">{html.escape(subtitle)}</p>
    </div>

{scan_bar}
    <div class="wrap">
      <section class="card transcript">
        <p class="muted small">{html.escape(eyebrow)}</p>
        <hr style="border:none;border-top:1px solid var(--line);margin:14px 0;" />
        {content}
      </section>
    </div>
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

with open(out_path, "w", encoding="utf-8") as f:
    f.write(page)
print("wrote", out_path)
