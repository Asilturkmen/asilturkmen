// Draws the profile-views tile: the same obsidian/gold box as the link tiles under
// the plate (assets/link-*.svg), an eye, the count in Satoshi Bold and "views" in
// Satoshi Medium. Text is composed from the outlines in glyphs.json, so no font is
// needed at request time.
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const G = JSON.parse(readFileSync(join(dirname(fileURLToPath(import.meta.url)), "glyphs.json"), "utf8"));

const H = 42, PAD = 13, EYE = 20, EYE_GAP = 9, GAP = 7;
const INK = "#e4e5e9", MUTED = "#8b929c", GOLD = "#d4b483", EDGE = "#363b45";

export function formatCount(n) {
  return Number.isFinite(n) ? Math.max(0, Math.floor(n)).toLocaleString("en-US") : "—";
}

export function renderTile(text) {
  const chars = [...text];
  const numW = text === "—" ? 10 : chars.reduce((w, ch) => w + (G.digits[ch]?.adv ?? 0), 0);
  const W = Math.round(PAD + EYE + EYE_GAP + numW + GAP + G.label.w + PAD);
  const y = H / 2 + G.cap / 2;
  let x = PAD + EYE + EYE_GAP;
  const num = chars.map((ch) => {
    const g = G.digits[ch];
    if (!g) return "";
    const s = `<path transform="translate(${x.toFixed(2)} ${y.toFixed(2)})" d="${g.d}" fill="${INK}"/>`;
    x += g.adv;
    return s;
  }).join("");
  x += (text === "—" ? 10 : 0) + GAP;
  const label = `<path transform="translate(${x.toFixed(2)} ${y.toFixed(2)})" d="${G.label.d}" fill="${MUTED}"/>`;
  const eye = `<g transform="translate(${PAD} 11)" fill="none" stroke="${GOLD}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">` +
    `<path d="M1 10C4 4.4 7 2 10 2s6 2.4 9 8c-3 5.6-6 8-9 8s-6-2.4-9-8Z"/><circle cx="10" cy="10" r="3.1"/></g>`;
  const dash = text === "—"
    ? `<path d="M${(PAD + EYE + EYE_GAP).toFixed(2)} ${(H / 2).toFixed(2)}h10" stroke="${MUTED}" stroke-width="2" stroke-linecap="round"/>`
    : "";
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-label="${text} profile views">
<defs><clipPath id="frame"><rect width="${W}" height="${H}" rx="10"/></clipPath>
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#12151a"/><stop offset="1" stop-color="#161920"/></linearGradient>
<linearGradient id="sheen" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffffff" stop-opacity="0.03"/><stop offset="0.5" stop-color="${GOLD}" stop-opacity="0.22"/><stop offset="1" stop-color="#ffffff" stop-opacity="0.03"/></linearGradient></defs>
<g clip-path="url(#frame)"><rect width="${W}" height="${H}" fill="url(#bg)"/>${eye}${num}${dash}${label}
<rect x="0.5" y="0.5" width="${W - 1}" height="${H - 1}" rx="9.5" fill="none" stroke="${EDGE}"/><rect x="10" y="0.5" width="${W - 20}" height="1" fill="url(#sheen)"/></g></svg>
`;
}
