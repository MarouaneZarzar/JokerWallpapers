"""Builds the files the app downloads, from the original images in source/.

    full/<n>.jpg     original image, copied unchanged
    thumbs/<n>.webp  small preview for the grid
    wallpapers.json  the list the app reads (in number order)

To add wallpapers: drop new numbered images (101.jpg, 102.jpg, ...) into
source/, run `python build_data.py`, then commit and push.
Requires Pillow: `pip install pillow`.
"""
import json
import re
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).parent
SOURCE = ROOT / "source"
FULL = ROOT / "full"
THUMBS = ROOT / "thumbs"
THUMB_WIDTH = 400
THUMB_QUALITY = 75
# versionCode of the newest app release on Google Play. Raise it AFTER a new
# version is live on Play; older app versions then show "Update Available".
LATEST_VERSION = 23


def main():
    FULL.mkdir(exist_ok=True)
    THUMBS.mkdir(exist_ok=True)

    images = sorted(
        (p for p in SOURCE.iterdir() if re.fullmatch(r"\d+\.jpe?g", p.name, re.I)),
        key=lambda p: int(p.stem),
    )

    wallpapers = []
    for src in images:
        full = FULL / f"{src.stem}.jpg"
        thumb = THUMBS / f"{src.stem}.webp"
        if not full.exists():
            shutil.copyfile(src, full)
        if not thumb.exists():
            with Image.open(src) as img:
                img = img.convert("RGB")
                height = round(img.height * THUMB_WIDTH / img.width)
                img.resize((THUMB_WIDTH, height), Image.LANCZOS).save(
                    thumb, "WEBP", quality=THUMB_QUALITY, method=6)
        wallpapers.append({
            "id": src.stem,
            "full": f"full/{full.name}",
            "thumb": f"thumbs/{thumb.name}",
        })

    with open(ROOT / "wallpapers.json", "w", encoding="utf-8") as f:
        json.dump({"version": 1, "latestVersion": LATEST_VERSION, "wallpapers": wallpapers}, f, indent=2)

    print(f"{len(wallpapers)} wallpapers written to wallpapers.json")


if __name__ == "__main__":
    main()
