const THEME_KEY = "lm_theme";

function setTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem(THEME_KEY, theme);

  const btn = document.getElementById("themeToggle");
  if (btn) {
    const isDark = theme === "dark";
    btn.setAttribute("aria-pressed", String(isDark));
    btn.textContent = isDark ? "Light mode" : "Dark mode";
  }
}

function initTheme() {
  const saved = localStorage.getItem(THEME_KEY);
  if (saved === "dark" || saved === "light") {
    setTheme(saved);
    return;
  }
  // Default: light
  setTheme("light");
}

async function loadLibrary() {
  const res = await fetch("s("library.json", { cache: "no-store" });
  if (!res.ok) throw new Error("Missing library.json");
  return await res.json();
}

function norm(s) {
  return (s || "").toLowerCase().trim();
}

function matches(item, query) {
  const q = norm(query);
  if (!q) return true;

  // Search only by lesson number OR scripture reference
  const numberText = String(item.lessonNumber || "");
  const scripture = norm(item.searchKey);

  // Allow: "83", "lesson 83", "john 17", "acts 1"
  return (
    numberText.includes(q.replace(/[^\d]/g, "")) && /\d/.test(q) ||
    scripture.includes(q)
  );
}

function renderRow(item) {
  return `
    <div class="row">
      <a class="row-link" href="${item.href}">
        <span class="row-title">
          ${item.lessonNumber} — ${item.title}
        </span>
      </a>
      <div class="row-meta">
        ${item.searchKey}
      </div>
    </div>
  `;
}


async function main() {
  initTheme();

  const q = document.getElementById("q");
  const results = document.getElementById("results");
  const toggle = document.getElementById("themeToggle");

  if (toggle) {
    toggle.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme") || "light";
      setTheme(current === "dark" ? "light" : "dark");
    });
  }

  const items = await loadLibrary();

  // Sort lesson number ascending
  items.sort((a, b) => (a.lessonNumber || 0) - (b.lessonNumber || 0));

  function update() {
    const filtered = items.filter(it => matches(it, q.value));
    results.innerHTML = filtered.length
      ? filtered.map(renderRow).join("")
      : `<p class="muted small" style="padding:12px 0;">No matches found.</p>`;
  }

  q.addEventListener("input", update);
  update();
}

main().catch(err => {
  console.error(err);
  const results = document.getElementById("results");
  if (results) results.innerHTML =
    `<p class="muted small">Library failed to load. Check that <strong>library.json</strong> exists in the same folder as index.html.</p>`;
});
