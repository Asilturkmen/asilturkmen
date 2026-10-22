"""Local look at README.md the way the GitHub profile page lays it out.

Writes .preview/ (git-ignored) and prints the page to open:
desktop and phone side by side, dark and light theme.

    .venv/bin/python scripts/preview.py && open .preview/index.html

It mirrors GitHub's widths, the 14px profile README text and GitHub's own
markdown styles. It does not run GitHub's sanitizer or path rewriting, so a
real check on github.com is still needed before merging.
"""
import os

import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, ".preview")
CSS = "https://cdn.jsdelivr.net/npm/github-markdown-css@5.8.1/github-markdown-{}.css"
USER = "Asilturkmen"

THEMES = {
    "dark": dict(bg="#0d1117", fg="#e6edf3", muted="#8d96a0", line="#30363d"),
    "light": dict(bg="#ffffff", fg="#1f2328", muted="#59636e", line="#d1d9e0"),
}

PROFILE = """<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="{css}">
<style>
  body {{ margin: 0; background: {bg}; color: {fg};
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif; }}
  .wrap {{ max-width: 1280px; margin: 0 auto; padding: 24px 32px;
    display: grid; grid-template-columns: 296px minmax(0, 1fr); gap: 24px; }}
  .side img {{ width: 100%; border-radius: 50%; border: 1px solid {line}; display: block; }}
  .side h1 {{ margin: 16px 0 0; font-size: 24px; font-weight: 600; }}
  .side p {{ margin: 0; color: {muted}; font-size: 20px; font-weight: 300; }}
  .box {{ border: 1px solid {line}; border-radius: 6px; margin-top: 16px; }}
  .box-head {{ padding: 16px 24px 0; font-size: 12px; color: {muted};
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
  .markdown-body {{ padding: 16px 24px 24px; font-size: 14px; background: transparent; }}
  .pinned {{ margin-top: 24px; font-size: 16px; color: {fg}; }}
  .pinned div {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 8px; }}
  .pinned span {{ border: 1px solid {line}; border-radius: 6px; height: 96px; display: block; }}
  @media (max-width: 1011px) {{ .wrap {{ grid-template-columns: 256px minmax(0, 1fr); padding: 24px; }} }}
  @media (max-width: 767px) {{
    .wrap {{ grid-template-columns: minmax(0, 1fr); padding: 16px; }}
    .side {{ display: flex; gap: 16px; align-items: center; }}
    .side img {{ width: 64px; }}
    .side h1 {{ margin: 0; font-size: 20px; }}
    .side p {{ font-size: 16px; }}
    .pinned div {{ grid-template-columns: 1fr; }}
  }}
</style>
<div class="wrap">
  <div class="side"><img src="https://github.com/{user}.png" alt=""><div><h1>Asil Türkmen</h1><p>{user}</p></div></div>
  <div>
    <div class="box">
      <div class="box-head">{user} / README.md</div>
      <article class="markdown-body">{body}</article>
    </div>
    <div class="pinned">Pinned<div><span></span><span></span><span></span><span></span></div></div>
  </div>
</div>
"""

INDEX = """<!doctype html>
<meta charset="utf-8">
<title>README preview</title>
<style>
  body { margin: 0; background: #16181d; color: #c9d1d9; font: 13px -apple-system, Helvetica, Arial, sans-serif; }
  header { display: flex; gap: 12px; align-items: center; padding: 12px 20px; border-bottom: 1px solid #2b2f36; }
  button { font: inherit; color: inherit; background: #22262d; border: 1px solid #3a3f47; border-radius: 6px; padding: 5px 12px; cursor: pointer; }
  button[aria-pressed="true"] { border-color: #e3c78c; color: #e3c78c; }
  main { display: flex; flex-wrap: wrap; gap: 24px; padding: 20px; align-items: flex-start; }
  figure { margin: 0; display: grid; gap: 8px; }
  figcaption { color: #8b949e; }
  .desk { width: 1280px; height: 900px; border: 1px solid #2b2f36; border-radius: 8px; overflow: hidden; }
  .phone { width: 390px; height: 844px; border: 1px solid #2b2f36; border-radius: 28px; overflow: hidden; }
  iframe { border: 0; width: 100%; height: 100%; display: block; }
</style>
<header>
  <strong>README önizleme</strong>
  <button type="button" data-theme="dark" aria-pressed="true">Koyu tema</button>
  <button type="button" data-theme="light" aria-pressed="false">Açık tema</button>
  <button type="button" id="replay">Baştan oynat</button>
</header>
<main>
  <figure><figcaption>Masaüstü · 1280 px</figcaption><div class="desk"><iframe id="d" src="profile-dark.html"></iframe></div></figure>
  <figure><figcaption>Telefon · 390 px</figcaption><div class="phone"><iframe id="p" src="profile-dark.html"></iframe></div></figure>
</main>
<script>
  var theme = 'dark';
  function load() {
    ['d', 'p'].forEach(function (id) { document.getElementById(id).src = 'profile-' + theme + '.html?r=' + Date.now(); });
  }
  document.querySelectorAll('[data-theme]').forEach(function (b) {
    b.addEventListener('click', function () {
      theme = b.dataset.theme;
      document.querySelectorAll('[data-theme]').forEach(function (o) { o.setAttribute('aria-pressed', String(o === b)); });
      load();
    });
  });
  document.getElementById('replay').addEventListener('click', load);
</script>
"""


def main():
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(ROOT, "README.md")) as fh:
        body = markdown.markdown(fh.read())
    body = body.replace('srcset="assets/', 'srcset="../assets/').replace('src="assets/', 'src="../assets/')
    for name, colors in THEMES.items():
        with open(os.path.join(OUT, f"profile-{name}.html"), "w") as fh:
            fh.write(PROFILE.format(css=CSS.format(name), body=body, user=USER, **colors))
    with open(os.path.join(OUT, "index.html"), "w") as fh:
        fh.write(INDEX)
    print(os.path.join(OUT, "index.html"))


if __name__ == "__main__":
    main()
