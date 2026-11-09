// node sample.js [count]                 -> prints the tile SVG
// node sample.js hero <variant> [count]  -> prints the hero SVG (desktop | mobile | desktop-still | mobile-still)
// "-" as the count draws the no-number state. Used by scripts/preview.py before deploy.
import { formatCount, renderHero, renderTile, HERO_VARIANTS } from "./render.js";

const [a, b, c] = process.argv.slice(2);
const number = (v) => (v === undefined ? formatCount(1248) : v === "-" ? null : formatCount(Number(v)));

if (a === "hero") {
  if (!HERO_VARIANTS.includes(b)) {
    console.error(`usage: node sample.js hero <${HERO_VARIANTS.join("|")}> [count]`);
    process.exit(2);
  }
  process.stdout.write(renderHero(b, number(c)));
} else {
  process.stdout.write(renderTile(number(a) ?? "—"));
}
