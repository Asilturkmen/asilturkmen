// node sample.js [count] -> prints the tile SVG (used by scripts/preview.py before deploy).
import { formatCount, renderTile } from "./render.js";

const arg = process.argv[2];
process.stdout.write(renderTile(arg === undefined ? formatCount(1248) : arg === "-" ? "—" : formatCount(Number(arg))));
