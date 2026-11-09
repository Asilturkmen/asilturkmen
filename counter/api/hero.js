// GET /api/hero?v=desktop|mobile|desktop-still|mobile-still -> the hero image with the
// live view count above the name (+1 per request; the README's <picture> fetches one
// variant per page view). ?peek=1 draws it without counting.
// The templates in ../hero/ are written by scripts/build.py; the count is composed
// from counter/glyphs.json into their <!--VIEWS {...}--> slot (render.js).
import { count, isPeek, svgHeaders } from "../count.js";
import { formatCount, renderHero, HERO_VARIANTS } from "../render.js";

export default async function handler(req, res) {
  const q = new URL(req.url || "/", "http://x").searchParams;
  const variant = HERO_VARIANTS.includes(q.get("v")) ? q.get("v") : "desktop";
  let text = null;
  try {
    text = formatCount(await count(isPeek(req)));
  } catch (e) {
    console.error("hero:", e.message);          // no number: the hero is drawn without the badge
  }
  svgHeaders(res);
  res.end(renderHero(variant, text));
}
