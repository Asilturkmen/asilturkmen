// The view count, kept in an Upstash Redis database connected to the Vercel project
// (Storage -> Upstash for Redis). Its REST URL/token arrive as KV_REST_API_URL /
// KV_REST_API_TOKEN (or UPSTASH_REDIS_REST_URL / UPSTASH_REDIS_REST_TOKEN); no SDK needed.
// Optional env: VIEWS_SEED (start the count from an older counter's number),
// VIEWS_KEY (redis key, default "profile:views").

const KEY = process.env.VIEWS_KEY || "profile:views";

async function redis(...cmd) {
  const url = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL;
  const token = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN;
  if (!url || !token) throw new Error("redis env missing");
  const r = await fetch(url, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: JSON.stringify(cmd),
  });
  if (!r.ok) throw new Error(`redis ${r.status}`);
  const j = await r.json();
  if (j.error) throw new Error(j.error);
  return j.result;
}

/** The count after this view (peek: the count as it is, nothing added). */
export async function count(peek) {
  const seed = Number(process.env.VIEWS_SEED || 0);
  if (peek) {
    const v = Number(await redis("GET", KEY));
    return Math.max(v || 0, seed);
  }
  let n = Number(await redis("INCR", KEY));
  if (seed && n < seed) {
    await redis("SET", KEY, String(seed));
    n = seed;
  }
  return n;
}

export function isPeek(req) {
  return /(^|[?&])peek=1(&|$)/.test((req.url || "").split("#")[0]);
}

export function svgHeaders(res) {
  res.statusCode = 200;
  res.setHeader("Content-Type", "image/svg+xml; charset=utf-8");
  res.setHeader("Cache-Control", "no-cache, no-store, must-revalidate, max-age=0, s-maxage=0");
  res.setHeader("CDN-Cache-Control", "no-store");
  res.setHeader("Pragma", "no-cache");
  res.setHeader("Expires", "0");
}
