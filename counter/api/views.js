// GET /api/views  -> SVG tile with the profile view count (+1 per request).
// GET /api/views?peek=1 -> same tile, nothing counted (the README uses this: the hero counts).
import { count, isPeek, svgHeaders } from "../count.js";
import { formatCount, renderTile } from "../render.js";

export default async function handler(req, res) {
  let text;
  try {
    text = formatCount(await count(isPeek(req)));
  } catch (e) {
    console.error("views:", e.message);
    text = "—";
  }
  svgHeaders(res);
  res.end(renderTile(text));
}
