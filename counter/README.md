# Profile-views tile

A Vercel serverless function that returns the "N views" tile on the profile README.
Every load of the image on github.com counts one view (GitHub's image proxy honours
the no-cache headers, so each page view fetches it once).

## Deploy

1. Vercel → Add New → Project → import this repo. **Root Directory: `counter`.** Framework: Other.
2. Project → Storage → Create → **Upstash for Redis** (free) → connect to the project.
   It adds `KV_REST_API_URL` / `KV_REST_API_TOKEN` to the environment.
3. Optional env `VIEWS_SEED=192` continues the old counter's number.
4. Deploy. The image URL is `https://<project>.vercel.app/api/views`; `?peek=1` shows it without counting.

`scripts/counter_glyphs.py` regenerates `glyphs.json` (the Satoshi outlines for 0–9, "," and "views").
`node sample.js 1248` prints a sample tile.
