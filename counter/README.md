# Profile views (Vercel function)

The hero on the profile README carries a live view count, served by this function with
an Upstash Redis counter behind it:

- `GET /api/hero?v=desktop|mobile|desktop-still|mobile-still` — the hero with an
  "(eye) N views" badge above the name: a small rounded box in the obsidian/gold style of
  the link tiles under the plate (dark gradient, 1px border, gold eye, the count in Satoshi
  Bold, "views" in Satoshi Medium), left-aligned with the name. The README's `<picture>`
  fetches one variant per page view, and that fetch **counts the view** (GitHub's image
  proxy honours the no-cache headers). Templates in `hero/` are written by
  `scripts/build.py`; the badge is composed into their `<!--VIEWS {...}-->` slot from
  `glyphs.json` (`render.js` → `renderBadge`).
- `GET /api/views` — the standalone "N views" tile (42px high). **No longer on the README**
  (the badge in the hero replaced it); the route and `renderTile` stay as a plain counter
  image for anyone who wants one. Load it with `?peek=1` to show the number without counting.

`?peek=1` works on both routes. If Redis is unreachable the hero is drawn without the
badge and the tile shows a dash.

## Deploy

The Vercel project `asilturkmen-views` is linked to this repo with **Root Directory
`counter`**; every push to `main` deploys. Storage → Upstash for Redis (free) provides
`KV_REST_API_URL` / `KV_REST_API_TOKEN`. Optional env `VIEWS_SEED=N` continues an
older counter's number.

## Local

- `python scripts/build.py` writes `hero/*.svg` (and `assets/hero*.svg` without the badge).
- `python scripts/counter_glyphs.py` regenerates `glyphs.json` (Satoshi outlines for the
  digits and "views", for the tile and for the badge).
- `node sample.js 1248` prints the tile; `node sample.js hero desktop 1248` prints a hero
  (`-` as the count draws the hero without the badge). `scripts/preview.py` uses the hero
  samples in place of the live URLs.
