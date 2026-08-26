"""Build a reading/lesson page from a Markdown transcript.

Usage: python tools/build_reading.py <transcript.md> <output.html> <page-title> <eyebrow> <subtitle>
The transcript's H1/H2 lines become headings; blank-line-separated blocks become paragraphs.
"""
import sys, html

md_path, out_path, title, eyebrow, subtitle = sys.argv[1:6]

with open(md_path, encoding="utf-8") as f:
    blocks = [b.strip() for b in f.read().split("\n\n") if b.strip()]

body = []
for b in blocks:
    if b.startswith("## "):
        body.append(f'<h2>{html.escape(b[3:].strip())}</h2>')
    elif b.startswith("# "):
        continue  # page header supplies the title
    else:
        text = html.escape(b).replace("\n", " ")
        body.append(f"<p>{text}</p>")

content = "\n        ".join(body)

page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(title)} — Louise Morse</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Inter:wght@400;500;600&family=STIX+Two+Text:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="style.css" />
  <script>
    (function () {{
      var t = localStorage.getItem("lm_theme");
      if (t === "dark") document.documentElement.setAttribute("data-theme", "dark");
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
