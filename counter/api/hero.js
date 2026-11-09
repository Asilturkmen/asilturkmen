// GET /api/hero?v=desktop|mobile|desktop-still|mobile-still -> the hero image with the
// live view count at its top centre (+1 per request; the README's <picture> fetches one
// variant per page view). ?peek=1 draws it without counting.
// The templates in ../hero/ are written by scripts/build.py; the count is composed
// from counter/glyphs.json into their <!--VIEWS {...}--> slot (render.js).
//
// The README shows nothing else where this image goes, so every failure still answers with
// an SVG: Redis down or slow (count.js times out at 1.5 s) -> the hero without the counter;
// renderHero throws (template missing/corrupt) -> the raw template with the slot stripped;
// even that fails -> an empty transparent SVG, still with status 200: GitHub's image proxy
// (camo) only passes 200s, any other status shows the broken-image icon whatever the body.
import { readFileSync } from "node:fs";
import { count, isPeek, svgHeaders } from "../count.js";
import { formatCount, renderHero, heroTemplatePath, HERO_VARIANTS, SLOT_RE, VIEWS_TITLE } from "../render.js";

const EMPTY_SVG = '<svg xmlns="http://www.w3.org/2000/svg" width="846" height="1" viewBox="0 0 846 1"/>\n';

export default async function handler(req, res) {
  const q = new URL(req.url || "/", "http://x").searchParams;
  const variant = HERO_VARIANTS.includes(q.get("v")) ? q.get("v") : "desktop";
  let text = null;
  try {
    text = formatCount(await count(isPeek(req)));
    if (text === "—") text = null;             // NaN from redis: no number, no counter
  } catch (e) {
    console.error("hero: count:", e.message);   // no number: the hero is drawn without the counter
  }
  let body;
  try {
    body = renderHero(variant, text);
  } catch (e) {
    console.error("hero: render:", e.message);  // no counter at all: the template as written
    try {
      body = readFileSync(heroTemplatePath(variant), "utf8")
        .replace(SLOT_RE, "")
        .replace(VIEWS_TITLE, "");
    } catch (e2) {
      console.error("hero: template:", e2.message);
      body = EMPTY_SVG;                         // 200 on purpose, see the note at the top
    }
  }
  svgHeaders(res);
  res.end(body);
}
