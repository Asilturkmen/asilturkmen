// Draws the two images that carry the view count. Text is composed from the outlines
// in glyphs.json (scripts/counter_glyphs.py), so no font is needed at request time.
//
//   renderTile(text)          the standalone "N views" tile (/api/views): a rounded obsidian box
//                             with a thin edge and a gold sheen, an eye, the count in Satoshi Bold
//                             and "views" in Satoshi Medium (a plain counter image; the README
//                             uses the hero counter instead)
//   renderCounter(text, slot, still)
//                             the hero's counter: "(eye) N views" as plain text, no box, the
//                             whole group centred on slot.cx; the eye blinks (first at 2.6 s,
//                             then every 4.5 s) unless still
//   renderHero(variant, text) the hero (scripts/build.py writes the templates to hero/)
//                             with the counter composed into its <!--VIEWS {...}--> slot
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
export const SLOT_RE = /<!--VIEWS (\{.*?\})-->/;
const templates = new Map();

// The sentence scripts/build.py appends to the templates' <title>; renderHero rewrites it with
// the number, or drops it when there is none. Must match VIEWS_TITLE in scripts/build.py exactly
// (template() checks every template that carries the slot and throws if it has drifted).
export const VIEWS_TITLE = " The number at the top is the profile view count.";

/** The template file for a variant (hero/hero[-mobile][-still].svg). */
export function heroTemplatePath(variant) {
  const file = "hero" + (variant.startsWith("mobile") ? "-mobile" : "") + (variant.endsWith("-still") ? "-still" : "") + ".svg";
  return join(HERE, "hero", file);
}

function template(variant) {
  if (!templates.has(variant)) {
    const svg = readFileSync(heroTemplatePath(variant), "utf8");
    if (SLOT_RE.test(svg) && !svg.includes(VIEWS_TITLE)) {
      throw new Error(`hero template ${variant}: title sentence drifted from VIEWS_TITLE (see scripts/build.py)`);
    }
    templates.set(variant, svg);
  }
  return templates.get(variant);
}

// The blink: the first at BLINK_FIRST s (right after the hero's entrance), then every
// BLINK_PERIOD s; each closes and reopens in 0.18 s at the start of its cycle. A vertical
// scale about the eye's own centre (the group is translated there and the eye drawn
// around the origin); the iris sits inside the same group, so it shuts with the lids.
// The trough stays at 0.14, not 0, so the squashed stroke still reads as a closed lid line.
const BLINK_PERIOD = 4.5, BLINK_FIRST = 2.6;
const blink = () =>
  `<animateTransform attributeName="transform" type="scale" values="1 1;1 0.14;1 1;1 1" ` +
  `keyTimes="0;0.02;0.04;1" calcMode="spline" keySplines="0.4 0 1 1;0 0 0.6 1;0 0 1 1" ` +
  `dur="${BLINK_PERIOD}s" begin="${BLINK_FIRST}s" repeatCount="indefinite"/>`;

/**
 * "(eye) 1,248 views" as plain text on the hero: a gold eye slot.eye high, the number in
 * Bold at slot.num (INK) and "views" in Medium at slot.label (MUTED) on the same baseline
 * slot.y, with gaps of 0.45 and 0.4 of the number size. The width is composed first and
 * the whole group is centred on slot.cx. The eye blinks (SMIL) unless still.
 */
export function renderCounter(text, slot, still = false) {
  const B = G.badge, kn = slot.num / B.units, kl = slot.label / B.units;
  const eyeSize = slot.eye, gapEye = 0.45 * slot.num, gapLabel = 0.4 * slot.num;
  const dash = text === "—", dashW = slot.num * 0.6;
  const chars = [...text];
  const numW = dash ? dashW : chars.reduce((w, ch) => w + (B.digits[ch]?.adv ?? 0) * kn, 0);
  const W = eyeSize + gapEye + numW + gapLabel + B.label.w * kl;
  const yb = slot.y, cap = B.cap * kn;                 // baseline, number cap height
  const x0 = slot.cx - W / 2;
  const f = (v) => v.toFixed(2);
  const ex = x0 + eyeSize / 2, ey = yb - cap / 2;      // the eye's centre, level with the number
  const eyeSvg = eye(-eyeSize / 2, -eyeSize / 2, eyeSize, GOLD, Math.max(1.2, 0.08 * eyeSize));
  const eyeGroup = `<g transform="translate(${f(ex)} ${f(ey)})"><g>${still ? "" : blink()}${eyeSvg}</g></g>`;
  let x = x0 + eyeSize + gapEye;
  const num = dash
    ? `<path d="M${f(x)} ${f(yb - cap / 2)}h${f(dashW)}" stroke="${MUTED}" stroke-width="${f(Math.max(1.5, slot.num * 0.09))}" stroke-linecap="round"/>`
    : chars.map((ch) => {
        const g = B.digits[ch];
        if (!g) return "";
        const s = `<path transform="translate(${f(x)} ${f(yb)}) scale(${kn.toFixed(4)})" d="${g.d}" fill="${INK}"/>`;
        x += g.adv * kn;
        return s;
      }).join("");
  x += (dash ? dashW : 0) + gapLabel;
  const label = `<path transform="translate(${f(x)} ${f(yb)}) scale(${kl.toFixed(4)})" d="${B.label.d}" fill="${MUTED}"/>`;
  return `<g>${eyeGroup}${num}${label}</g>`;
}

/**
 * The hero template with the counter in its slot and the <title>'s counter sentence turned
 * into "N profile views so far."; text null leaves the counter out and drops the sentence.
 */
export function renderHero(variant, text) {
  const still = variant.endsWith("-still");
  return template(variant)
    .replace(VIEWS_TITLE, () => (text == null ? "" : ` ${text} profile views so far.`))
    .replace(SLOT_RE, (_, json) => (text == null ? "" : renderCounter(text, JSON.parse(json), still)));
}
