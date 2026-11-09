"""Write counter/glyphs.json: the digit, comma and "views" outlines the profile-views
tile is composed from at request time (counter/render.js). Satoshi itself is never
shipped; only these outlines, like every other text on the page."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import FONT_DIR, FONT_FILES, Face, fonts_ready  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "counter" / "glyphs.json"
NUM_SIZE, LABEL_SIZE = 16, 12


def main() -> None:
    fonts_ready()
    faces = {w: Face(FONT_DIR / Path(p).name) for w, p in FONT_FILES.items()}
    bold, medium = faces[700], faces[500]
    digits = {}
    for ch in "0123456789,":
        run = bold.layout(ch, NUM_SIZE)
        digits[ch] = {"d": run.d(0, 0, 2), "adv": round(run.width, 2)}
    label = medium.layout("views", LABEL_SIZE)
    data = {
        "numSize": NUM_SIZE,
        "labelSize": LABEL_SIZE,
        "cap": round(bold.cap_height(NUM_SIZE), 2),
        "digits": digits,
        "label": {"d": label.d(0, 0, 2), "w": round(label.width, 2)},
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8", newline="\n")
    print(OUT, OUT.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
