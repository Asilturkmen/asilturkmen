"""Turn .preview/readme.html (GitHub's rendered README) into a browsable page.

    python scripts/preview.py          # renders README through GitHub's API
    python scripts/preview_page.py     # then open .preview/index.html
"""
from pathlib import Path

P = Path(__file__).resolve().parent.parent / ".preview"
frag = (P / "readme.html").read_text(encoding="utf-8").replace("https://readme.preview/", "../")
(P / "view.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>README preview</title>
<link rel="stylesheet" href="vendor/github-markdown-css-5.9.0/github-markdown-light.css" id="css">
<style>
html,body{{margin:0}} body{{padding:16px}}
body[data-color-mode=light]{{background:#fff;color-scheme:light}} body[data-color-mode=dark]{{background:#0d1117;color-scheme:dark}}
.box{{max-width:896px;margin:0 auto;border:1px solid #d0d7de;border-radius:6px;padding:24px;box-sizing:border-box}}
body[data-color-mode=dark] .box{{border-color:#3d444d}}
.cap{{font:12px ui-monospace,SFMono-Regular,Menlo,monospace;margin:0 0 16px;color:#59636e}}
.markdown-body{{font-size:14px;line-height:21px}}
body[data-color-mode=light] .markdown-body [href$="#gh-dark-mode-only"]{{display:none}}
body[data-color-mode=dark] .markdown-body [href$="#gh-light-mode-only"]{{display:none}}
</style></head>
<body data-color-mode="light">
<div class="box"><p class="cap"><b>asilturkmen</b> / README.md</p><article class="markdown-body entry-content">
{frag}
</article></div>
<script>
const t=new URLSearchParams(location.search).get('theme')||'light';
document.body.setAttribute('data-color-mode',t);
document.getElementById('css').href='vendor/github-markdown-css-5.9.0/github-markdown-'+t+'.css';
</script></body></html>''', encoding="utf-8")
print("wrote", P / "view.html")
