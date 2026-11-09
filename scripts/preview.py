"""Render README.md the way the github.com profile page does and screenshot it.

* Markdown -> HTML through GitHub's own renderer (POST /markdown, gfm, repo context), so the
  real sanitizer decides what survives (<picture>, align=, #gh-*-mode-only anchors, ...).
  Responses are cached in .preview/cache/ keyed by the request body.
* The HTML is placed in a replica of the profile README box: 1px border, 6px radius,
  24px padding (GitHub's `Box-body p-4`), "repo / README.md" caption, and an
  `article.markdown-body.f5` (14px/21px) that is 846px wide at a 1280px viewport and
  308px wide at 390px (viewport - 82 on phones), styled with github-markdown-css 5.9.0
  (downloaded once into .preview/vendor/).
* Relative src/srcset (assets/..., media/...) are rewritten to a virtual origin that
  Playwright serves straight from the repo directory; nothing listens on a port.
* `#gh-dark-mode-only` / `#gh-light-mode-only` use GitHub's rule, and the browser's
  colour scheme is emulated to match the page theme so <picture> sources agree with it.

Usage:
  python scripts/preview.py [--reduced-motion] [--views desktop-light,mobile-dark]
                            [--readme PATH] [--root DIR] [--out DIR] [--wait MS]
Writes <out>/<view>[-rm].png at device_scale_factor 2 and prints the measured heights.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / ".preview"                  # vendor CSS + API cache live here whatever --out is
REPO_SLUG = "Asilturkmen/asilturkmen"
ORIGIN = "https://readme.preview"          # virtual origin, fulfilled from --root by Playwright
CSS_VERSION = "5.9.0"
CSS_URLS = (
    "https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/{v}/github-markdown-{t}.min.css",
    "https://cdn.jsdelivr.net/npm/github-markdown-css@{v}/github-markdown-{t}.css",
)
# name: (viewport width, markdown-body width, theme)
VIEWS = {
    "desktop-light": (1280, 846, "light"),
    "desktop-dark": (1280, 846, "dark"),
    "mobile-light": (390, 308, "light"),
    "mobile-dark": (390, 308, "dark"),
}
THEME = {  # page background, box border, default text, muted text (Primer light / dark)
    "light": ("#ffffff", "#d1d9e0", "#1f2328", "#59636e"),
    "dark": ("#0d1117", "#3d444d", "#f0f6fc", "#9198a1"),
}
PAD, BORDER = 24, 1
# github.com --fontStack-sansSerif (Nov 2026). "Mona Sans VF" is not served as a web font, so
# visitors without it installed get the system face (Segoe UI on Windows, SF on Apple).
SANS = ('"Mona Sans VF",-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans",Helvetica,Arial,'
        'sans-serif,"Apple Color Emoji","Segoe UI Emoji"')


def http(url: str, data: bytes | None = None, headers: dict | None = None) -> bytes:
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "readme-preview", **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def gh_token() -> str | None:
    for k in ("GH_TOKEN", "GITHUB_TOKEN"):
        if os.environ.get(k):
            return os.environ[k]
    try:
        out = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    tok = out.stdout.strip()
    return tok if out.returncode == 0 and tok else None


def render_markdown(md: str, cache_dir: Path) -> str:
    body = json.dumps({"text": md, "mode": "gfm", "context": REPO_SLUG}, ensure_ascii=False).encode("utf-8")
    cache = cache_dir / f"md-{hashlib.sha256(body).hexdigest()[:16]}.html"
    if cache.exists():
        return cache.read_text(encoding="utf-8")
    headers = {"Accept": "application/vnd.github+json", "Content-Type": "application/json",
               "X-GitHub-Api-Version": "2022-11-28"}
    tok = gh_token()
    if tok:
        headers["Authorization"] = f"Bearer {tok}"
    try:
        html = http("https://api.github.com/markdown", body, headers).decode("utf-8")
    except urllib.error.HTTPError as e:
        sys.exit(f"GitHub markdown API failed: {e.code} {e.reason} {e.read()[:300]!r}")
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache.write_text(html, encoding="utf-8")
    return html


def markdown_css(theme: str, vendor: Path) -> str:
    path = vendor / f"github-markdown-css-{CSS_VERSION}" / f"github-markdown-{theme}.css"
    if not path.exists():
        last = None
        for tpl in CSS_URLS:
            try:
                css = http(tpl.format(v=CSS_VERSION, t=theme))
                break
            except (urllib.error.URLError, OSError) as e:
                last = e
        else:
            sys.exit(f"could not download github-markdown-css: {last}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(css)
    return path.read_text(encoding="utf-8")


_ABS = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//|/|#)", re.I)


def _absolutise(url: str) -> str:
    url = url.strip()
    if not url or _ABS.match(url):
        return url
    while url.startswith("./"):
        url = url[2:]
    return f"{ORIGIN}/{url}"


def rewrite_urls(html: str) -> str:
    """Relative src/srcset -> virtual origin (GitHub itself rewrites them to /raw/main/...)."""
    def src(m: re.Match) -> str:
        return f'src="{_absolutise(m.group(1))}"'

    def srcset(m: re.Match) -> str:
        parts = []
        for cand in m.group(1).split(","):
            bits = cand.strip().split(None, 1)
            if bits:
                parts.append(" ".join([_absolutise(bits[0])] + bits[1:]))
        return f'srcset="{", ".join(parts)}"'

    html = re.sub(r'\bsrc="([^"]*)"', src, html)
    return re.sub(r'\bsrcset="([^"]*)"', srcset, html)


def page_html(body: str, theme: str, col: int, css: str) -> str:
    bg, border, fg, muted = THEME[theme]
    other = "light" if theme == "dark" else "dark"
    repo = REPO_SLUG.split("/")[1]
    return f"""<!doctype html>
<html lang="en" data-color-mode="{theme}" data-light-theme="light" data-dark-theme="dark">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>README preview</title>
<style>{css}</style>
<style>
html{{color-scheme:{theme}}}
body{{margin:0;padding:16px 0;background:{bg};color:{fg};
  font:14px/1.5 {SANS}}}
.Box{{box-sizing:border-box;width:{col + 2 * (PAD + BORDER)}px;margin:0 auto;border:{BORDER}px solid {border};border-radius:6px;background:{bg}}}
.Box-body{{padding:{PAD}px}}
.caption{{font:12px/1.5 ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace;margin-bottom:16px}}
.caption i{{font-style:normal;color:{muted}}}
.markdown-body.f5{{font-family:{SANS};font-size:14px;line-height:1.5;background:transparent}}
/* GitHub: :root[data-color-mode=light] .readme [href$="#gh-dark-mode-only"]{{display:none}} and the mirror */
:root[data-color-mode={theme}] .markdown-body [href$="#gh-{other}-mode-only"]{{display:none}}
</style></head>
<body><div class="Box profile-readme"><div class="Box-body">
<div class="caption">{repo}<i style="padding:0 2px">/</i>README<i>.md</i></div>
<article class="markdown-body entry-content container-lg f5" itemprop="text">{body}</article>
</div></div></body></html>"""


# GitHub's renderer routes the tile through camo and keeps the real URL in data-canonical-src.
COUNTER_RE = re.compile(r'<img[^>]*vercel\.app/api/views[^>]*>')
SRC_RE = re.compile(r'(?<![\w-])src="[^"]*"')
# The hero's four variants come from the same function; GitHub leaves <source srcset>
# URLs alone and camo-wraps the <img> (its real URL stays in data-canonical-src).
HERO_URL_RE = re.compile(r'https://[^"]*vercel\.app/api/hero\?v=([a-z-]+)')


def _sample(out: Path, name: str, *args: str) -> Path | None:
    """Draw one of the counter's images with node (counter/sample.js) into out/."""
    path = out / name
    try:
        svg = subprocess.run(["node", str(ROOT / "counter" / "sample.js"), *args], check=True,
                             capture_output=True, text=True, encoding="utf-8").stdout
        path.write_text(svg, encoding="utf-8")
    except (OSError, subprocess.CalledProcessError) as e:
        print(f"counter sample skipped ({name}): {e}", file=sys.stderr)
        return None
    return path


def local_counter(html: str, out: Path) -> str:
    """The profile-views tile and the hero are served by a Vercel function (counter/).
    Offline, or before it is deployed, draw samples with the same renderer instead."""
    if COUNTER_RE.search(html):
        sample = _sample(out, "views-sample.svg", "1248")
        if sample:
            rel = sample.relative_to(ROOT).as_posix()      # served from the virtual origin like assets/
            html = COUNTER_RE.sub(lambda m: SRC_RE.sub(f'src="{ORIGIN}/{rel}"', m.group(0)), html)
    heroes = {}
    for variant in set(HERO_URL_RE.findall(html)):
        sample = _sample(out, f"hero-{variant}-sample.svg", "hero", variant, "1248")
        if sample:
            heroes[variant] = f"{ORIGIN}/{sample.relative_to(ROOT).as_posix()}"
    if heroes:
        # plain URLs first; then the camo-wrapped <img src> / <source srcset>, whose real URL
        # GitHub keeps in data-canonical-src (on <source> too)
        html = HERO_URL_RE.sub(lambda m: heroes.get(m.group(1), m.group(0)), html)
        wrapped = re.compile(r'<(?:img|source)\b[^>]*data-canonical-src="[^"]*hero-(?P<v>[a-z-]+)-sample\.svg"[^>]*>')
        attr = re.compile(r'(?<![\w-])(src|srcset)="[^"]*"')
        html = wrapped.sub(lambda m: attr.sub(lambda a: f'{a.group(1)}="{heroes[m.group("v")]}"', m.group(0))
                           if m.group("v") in heroes else m.group(0), html)
    return html


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=ROOT, help="directory relative paths resolve against")
    ap.add_argument("--readme", type=Path, help="markdown file (default: <root>/README.md)")
    ap.add_argument("--out", type=Path, help="output directory (default: <repo>/.preview)")
    ap.add_argument("--views", default=",".join(VIEWS), help="comma-separated subset of " + ", ".join(VIEWS))
    ap.add_argument("--reduced-motion", action="store_true", help="emulate prefers-reduced-motion: reduce (*-rm.png)")
    ap.add_argument("--wait", type=int, default=2500, help="ms to wait after images load (the hero entrance takes ~2.1 s)")
    args = ap.parse_args(argv)

    views = [v.strip() for v in args.views.split(",") if v.strip()]
    unknown = [v for v in views if v not in VIEWS]
    if unknown:
        ap.error(f"unknown view(s): {', '.join(unknown)}")

    from playwright.sync_api import sync_playwright

    root = args.root.resolve()
    readme = (args.readme or root / "README.md").resolve()
    out = (args.out or ROOT / ".preview").resolve()
    out.mkdir(parents=True, exist_ok=True)
    body = rewrite_urls(render_markdown(readme.read_text(encoding="utf-8"), STATE / "cache"))
    body = local_counter(body, out)
    (out / "readme.html").write_text(body, encoding="utf-8")
    suffix = "-rm" if args.reduced_motion else ""

    mimetypes.add_type("image/svg+xml", ".svg")
    mimetypes.add_type("image/webp", ".webp")
    pages: dict[str, str] = {}

    def serve(route) -> None:
        path = route.request.url[len(ORIGIN):].split("?", 1)[0].split("#", 1)[0]
        if path in pages:
            route.fulfill(status=200, content_type="text/html; charset=utf-8", body=pages[path])
            return
        f = (root / urllib.request.url2pathname(path.lstrip("/"))).resolve()
        if root not in f.parents or not f.is_file():
            print(f"  404 {path}", file=sys.stderr)
            route.fulfill(status=404, body="not found")
            return
        ctype = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
        route.fulfill(status=200, content_type=ctype, body=f.read_bytes())

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name in views:
            vw, col, theme = VIEWS[name]
            path = f"/__preview__/{name}.html"
            pages[path] = page_html(body, theme, col, markdown_css(theme, STATE / "vendor"))
            ctx = browser.new_context(viewport={"width": vw, "height": 900}, device_scale_factor=2,
                                      color_scheme=theme,
                                      reduced_motion="reduce" if args.reduced_motion else "no-preference")
            ctx.route(f"{ORIGIN}/**", serve)
            page = ctx.new_page()
            page.goto(ORIGIN + path, wait_until="load")
            page.wait_for_function("[...document.images].every(i => i.complete)")
            page.wait_for_timeout(args.wait)
            dims = page.evaluate("""() => {
                const r = e => e.getBoundingClientRect();
                const a = document.querySelector('article'), b = document.querySelector('.Box');
                const broken = [...document.images]
                    .filter(i => i.offsetParent && !i.naturalWidth).map(i => i.currentSrc || i.src);
                return {box: r(b).height, article: r(a).height, width: r(a).width, broken};
            }""")
            shot = out / f"{name}{suffix}.png"
            page.locator(".Box").screenshot(path=str(shot))
            print(f"{name + suffix:17} markdown-body {dims['width']:.0f} x {dims['article']:.1f} px   "
                  f"README box {dims['box']:.1f} px   {shot}")
            for b in dims["broken"]:
                print(f"  broken image: {b}", file=sys.stderr)
            ctx.close()
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
