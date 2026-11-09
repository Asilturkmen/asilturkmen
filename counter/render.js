// Draws the two images that carry the view count. Text is composed from the outlines
// in glyphs.json (scripts/counter_glyphs.py), so no font is needed at request time.
//
//   renderTile(text)          the standalone "N views" tile (/api/views): the same obsidian/gold
//                             box as the link tiles (assets/link-*.svg), an eye, the count
//                             in Satoshi Bold and "views" in Satoshi Medium
//   renderBadge(text, slot)   the same box at the size the hero asks for, above the name
//   renderHero(variant, text) the hero (scripts/build.py writes the templates to hero/)
//                             with the badge composed into its <!--VIEWS {...}--> slot
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const G = JSON.parse(readFileSync(join(HERE, "glyphs.json"), "utf8"));

const H = 42, PAD = 13, EYE = 20, EYE_GAP = 9, GAP = 7;
const INK = "#e4e5e9", MUTED = "#8b929c", GOLD = "#d4b483", EDGE = "#363b45";

export function formatCount(n) {
  return Number.isFinite(n) ? Math.max(0, Math.floor(n)).toLocaleString("en-US") : "—";
}

// An eye in a 20-unit box: the outline of a closed almond and the iris.
function eye(x, y, size, colour, stroke) {
  const k = size / 20;
  return `<g transform="translate(${x.toFixed(2)} ${y.toFixed(2)}) scale(${k.toFixed(3)})" fill="none" stroke="${colour}" ` +
    `stroke-width="${(stroke / k).toFixed(2)}" stroke-linecap="round" stroke-linejoin="round">` +
    `<path d="M1 10C4 4.4 7 2 10 2s6 2.4 9 8c-3 5.6-6 8-9 8s-6-2.4-9-8Z"/><circle cx="10" cy="10" r="3.1"/></g>`;
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
  const dash = text === "—"
    ? `<path d="M${(PAD + EYE + EYE_GAP).toFixed(2)} ${(H / 2).toFixed(2)}h10" stroke="${MUTED}" stroke-width="2" stroke-linecap="round"/>`
    : "";
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-label="${text} profile views">
<defs><clipPath id="frame"><rect width="${W}" height="${H}" rx="10"/></clipPath>
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#12151a"/><stop offset="1" stop-color="#161920"/></linearGradient>
<linearGradient id="sheen" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffffff" stop-opacity="0.03"/><stop offset="0.5" stop-color="${GOLD}" stop-opacity="0.22"/><stop offset="1" stop-color="#ffffff" stop-opacity="0.03"/></linearGradient></defs>
<g clip-path="url(#frame)"><rect width="${W}" height="${H}" fill="url(#bg)"/>${eye(PAD, 11, EYE, GOLD, 1.6)}${num}${dash}${label}
<rect x="0.5" y="0.5" width="${W - 1}" height="${H - 1}" rx="9.5" fill="none" stroke="${EDGE}"/><rect x="10" y="0.5" width="${W - 20}" height="1" fill="url(#sheen)"/></g></svg>
`;
}

// ------------------------------------------------------------------ hero
export const HERO_VARIANTS = ["desktop", "mobile", "desktop-still", "mobile-still"];
const SLOT_RE = /<!--VIEWS (\{.*?\})-->/;
const templates = new Map();

function template(variant) {
  if (!templates.has(variant)) {
    const file = "hero" + (variant.startsWith("mobile") ? "-mobile" : "") + (variant.endsWith("-still") ? "-still" : "") + ".svg";
    templates.set(variant, readFileSync(join(HERE, "hero", file), "utf8"));
  }
  return templates.get(variant);
}

/**
 * "(eye) 1,248 views" in a rounded box drawn like the tile, its top-left corner at
 * (slot.x, slot.y), slot.h high, the number at slot.num and "views" at slot.label.
 * Its gradients live in the group's own <defs> (vb-*), clear of the hero's ids.
 */
export function renderBadge(text, slot) {
  const B = G.badge, h = slot.h, kn = slot.num / B.units, kl = slot.label / B.units;
  const pad = 0.43 * h, eyeSize = 0.48 * h, gap = 0.2 * h, rx = h / 3;
  const dash = text === "—", dashW = h * 0.3;
  const chars = [...text];
  const numW = dash ? dashW : chars.reduce((w, ch) => w + (B.digits[ch]?.adv ?? 0) * kn, 0);
  const W = pad + eyeSize + gap + numW + gap + B.label.w * kl + pad;
  const x0 = slot.x, y0 = slot.y, yb = y0 + h / 2 + (B.cap * kn) / 2;   // number baseline
  const f = (v) => v.toFixed(2);
  let x = x0 + pad + eyeSize + gap;
  const num = dash
    ? `<path d="M${f(x)} ${f(y0 + h / 2)}h${f(dashW)}" stroke="${MUTED}" stroke-width="1.6" stroke-linecap="round"/>`
    : chars.map((ch) => {
        const g = B.digits[ch];
        if (!g) return "";
        const s = `<path transform="translate(${f(x)} ${f(yb)}) scale(${kn.toFixed(4)})" d="${g.d}" fill="${INK}"/>`;
        x += g.adv * kn;
        return s;
      }).join("");
  x += numW * (dash ? 1 : 0) + gap;
  const label = `<path transform="translate(${f(x)} ${f(yb)}) scale(${kl.toFixed(4)})" d="${B.label.d}" fill="${MUTED}"/>`;
  return `<g><defs>` +
    `<linearGradient id="vb-bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#12151a"/><stop offset="1" stop-color="#161920"/></linearGradient>` +
    `<linearGradient id="vb-sheen" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffffff" stop-opacity="0.03"/><stop offset="0.5" stop-color="${GOLD}" stop-opacity="0.22"/><stop offset="1" stop-color="#ffffff" stop-opacity="0.03"/></linearGradient>` +
    `</defs>` +
    `<rect x="${f(x0)}" y="${f(y0)}" width="${f(W)}" height="${f(h)}" rx="${f(rx)}" fill="url(#vb-bg)"/>` +
    `<rect x="${f(x0 + 0.5)}" y="${f(y0 + 0.5)}" width="${f(W - 1)}" height="${f(h - 1)}" rx="${f(rx - 0.5)}" fill="none" stroke="${EDGE}"/>` +
    `<rect x="${f(x0 + rx)}" y="${f(y0 + 0.5)}" width="${f(W - 2 * rx)}" height="1" fill="url(#vb-sheen)"/>` +
    eye(x0 + pad, y0 + (h - eyeSize) / 2, eyeSize, GOLD, Math.max(1, 0.04 * h)) +
    num + label + `</g>`;
}

/** The hero template with the badge in its slot; text null leaves the badge out. */
export function renderHero(variant, text) {
  return template(variant).replace(SLOT_RE, (_, json) => (text == null ? "" : renderBadge(text, JSON.parse(json))));
}
