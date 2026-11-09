# Profile views (Vercel function)

The hero on the profile README carries a live view count, served by this function with
an Upstash Redis counter behind it:

- `GET /api/hero?v=desktop|mobile|desktop-still|mobile-still` — the hero with an
  "(eye) N views" counter at its top centre, drawn as plain text on the hero surface (no
  box): a gold eye, the count in Satoshi Bold (desktop 20 / mobile 15) and "views" in Satoshi
  Medium (15 / 12) on one baseline, the whole group centred on the hero's midline. In the
  moving variants the eye blinks: first at 2.6 s, right after the hero's entrance, then every
  4.5 s, each blink a 0.18 s SMIL scale about the eye's own centre down to a closed-lid line;
  the `-still` variants draw a static eye. The README's `<picture>` fetches one
  variant per page view, and that fetch **counts the view** (GitHub's image proxy honours
  the no-cache headers). Templates in `hero/` are written by `scripts/build.py`; the counter
  is composed into their `<!--VIEWS {"cx","y","num","label","eye"}-->` slot from
  `glyphs.json` (`render.js` → `renderCounter`): width first, then placed at `cx − width/2`.
- `GET /api/views` — the standalone "N views" tile (42px high). **No longer on the README**
  (the counter in the hero replaced it); the route and `renderTile` stay as a plain counter
  image for anyone who wants one. Load it with `?peek=1` to show the number without counting.

`?peek=1` works on both routes.

**Accessibility.** The templates' `<title>` ends with the sentence "The number at the top is
the profile view count." (build.py's `VIEWS_TITLE`); `renderHero` rewrites it to "N profile
views so far." when it has the number and drops it when it has not.

**Failure modes.** The README shows nothing else where the hero goes, so the function always
answers with an SVG. Every Upstash call has a 1.5 s timeout (`AbortSignal.timeout`); if Redis
is slow, unreachable or unconfigured the hero is drawn without the counter and the tile shows
a dash. If composing the counter itself fails (template missing or corrupt) `/api/hero` sends
the raw template with the slot comment and the title sentence stripped; if even that cannot be
read it answers with an empty transparent SVG — still status 200, because GitHub's image proxy
(camo) shows a broken-image icon for any other status whatever the body. Each fallback logs
`hero: count|render|template: …` with `console.error`, so Vercel's logs still show it.

## Deploy

The Vercel project `asilturkmen-views` is linked to this repo with **Root Directory
`counter`**; every push to `main` deploys. Storage → Upstash for Redis (free) provides
`KV_REST_API_URL` / `KV_REST_API_TOKEN`. Optional env `VIEWS_SEED=N` continues an
older counter's number.

## Local

- `python scripts/build.py` writes `hero/*.svg` (and `assets/hero*.svg` without the counter).
- `python scripts/counter_glyphs.py` regenerates `glyphs.json` (Satoshi outlines for the
  digits and "views", for the tile and, in its `badge` block, for the hero counter).
- `node sample.js 1248` prints the tile; `node sample.js hero desktop 1248` prints a hero
  (`-` as the count draws the hero without the counter). `scripts/preview.py` uses the hero
  samples in place of the live URLs.
