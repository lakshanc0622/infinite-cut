#!/usr/bin/env python3
"""The Infinite Cut mark, and every raster size the build needs.

The mark is a lemniscate drawn as a single ribbon and sliced on a steep
diagonal, the two halves pushed apart along the cut's normal: infinity,
cut. It survives 16px because it is one closed stroke and one gap -- at
that size the gap closes up and it still reads as an infinity glyph.

Nothing here derives from upstream's artwork, which is not under the
AGPL and is not ours to reuse.

Usage: make_logo.py <tree>
"""

import io
import math
import os
import sys

import cairosvg
from PIL import Image, ImageDraw, ImageFont

# The ribbon: a figure eight, centred, as cubics.
LEMNISCATE = (
    "M 256 256 "
    "C 236 212 210 188 176 188 "
    "C 138 188 108 218 108 256 "
    "C 108 294 138 324 176 324 "
    "C 210 324 236 300 256 256 "
    "C 276 212 302 188 336 188 "
    "C 374 188 404 218 404 256 "
    "C 404 294 374 324 336 324 "
    "C 302 324 276 300 256 256 "
    "Z"
)

CUT_ANGLE = -62          # degrees; steep, so it reads as a blade stroke
GAP = 7                  # each half moves this far along the cut's normal
STROKE = 38

NORMAL = (
    math.sin(math.radians(-CUT_ANGLE)),
    math.cos(math.radians(-CUT_ANGLE)),
)

LIGHT_TILE = ("#8B2BFF", "#00D1C1")   # violet -> teal, deliberately not upstream blue
DARK_TILE = "#111318"


def svg(*, rounded: bool, dark: bool) -> str:
    rx = 112 if rounded else 0
    dx, dy = NORMAL[0] * GAP, NORMAL[1] * GAP
    if dark:
        tile = f'<rect width="512" height="512" rx="{rx}" fill="{DARK_TILE}"/>'
        stroke = "url(#ink)"
    else:
        tile = f'<rect width="512" height="512" rx="{rx}" fill="url(#tile)"/>'
        stroke = "#FFFFFF"

    def half(clip: str, sign: int) -> str:
        return (
            f'<g transform="translate({sign * dx:.2f} {sign * dy:.2f})">'
            f'<g clip-path="url(#{clip})">'
            f'<path d="{LEMNISCATE}" fill="none" stroke="{stroke}" '
            f'stroke-width="{STROKE}" stroke-linecap="round" '
            f'stroke-linejoin="round"/>'
            f"</g></g>"
        )

    return f"""<svg width="512" height="512" viewBox="0 0 512 512" fill="none" xmlns="http://www.w3.org/2000/svg">
  <title>Infinite Cut</title>
  <defs>
    <linearGradient id="tile" x1="0" y1="0" x2="512" y2="512" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{LIGHT_TILE[0]}"/>
      <stop offset="1" stop-color="{LIGHT_TILE[1]}"/>
    </linearGradient>
    <linearGradient id="ink" x1="108" y1="188" x2="404" y2="324" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{LIGHT_TILE[0]}"/>
      <stop offset="1" stop-color="{LIGHT_TILE[1]}"/>
    </linearGradient>
    <clipPath id="above">
      <rect x="-344" y="-344" width="1200" height="600"
            transform="rotate({CUT_ANGLE} 256 256)"/>
    </clipPath>
    <clipPath id="below">
      <rect x="-344" y="256" width="1200" height="600"
            transform="rotate({CUT_ANGLE} 256 256)"/>
    </clipPath>
  </defs>
  {tile}
  {half("above", -1)}
  {half("below", 1)}
</svg>
"""


def glyph_only(dark: bool) -> str:
    """The ribbon with no tile, for the wordmark."""
    dx, dy = NORMAL[0] * GAP, NORMAL[1] * GAP
    stroke = "#FFFFFF" if dark else "url(#ink)"

    def half(clip: str, sign: int) -> str:
        return (
            f'<g transform="translate({sign * dx:.2f} {sign * dy:.2f})">'
            f'<g clip-path="url(#{clip})">'
            f'<path d="{LEMNISCATE}" fill="none" stroke="{stroke}" '
            f'stroke-width="{STROKE}" stroke-linecap="round" '
            f'stroke-linejoin="round"/></g></g>'
        )

    return f"""<svg width="512" height="512" viewBox="0 0 512 512" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="ink" x1="108" y1="188" x2="404" y2="324" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{LIGHT_TILE[0]}"/>
      <stop offset="1" stop-color="{LIGHT_TILE[1]}"/>
    </linearGradient>
    <clipPath id="above"><rect x="-344" y="-344" width="1200" height="600" transform="rotate({CUT_ANGLE} 256 256)"/></clipPath>
    <clipPath id="below"><rect x="-344" y="256" width="1200" height="600" transform="rotate({CUT_ANGLE} 256 256)"/></clipPath>
  </defs>
  {half("above", -1)}
  {half("below", 1)}
</svg>
"""


def render(source: str, size: int) -> Image.Image:
    png = cairosvg.svg2png(
        bytestring=source.encode(), output_width=size, output_height=size
    )
    return Image.open(io.BytesIO(png)).convert("RGBA")


def font(size: int) -> ImageFont.FreeTypeFont:
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def wordmark(dark: bool) -> Image.Image:
    """Glyph plus the name, for a README header."""
    height = 128
    glyph = render(glyph_only(dark), height)
    text_colour = "#F4F6FA" if dark else "#141720"
    face = font(74)
    scratch = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    width = int(scratch.textlength("Infinite Cut", font=face))
    out = Image.new("RGBA", (height + 24 + width + 8, height), (0, 0, 0, 0))
    out.alpha_composite(glyph, (0, 0))
    ImageDraw.Draw(out).text(
        (height + 24, height // 2), "Infinite Cut",
        font=face, fill=text_colour, anchor="lm",
    )
    return out


def main() -> int:
    root = sys.argv[1]
    assets = os.path.join(root, "assets")
    icons = os.path.join(assets, "icons")
    os.makedirs(icons, exist_ok=True)
    written = []

    def save(image: Image.Image, path: str) -> None:
        image.save(path)
        written.append(os.path.relpath(path, root))

    # --- the four SVG masters ------------------------------------------
    variants = {
        "new_infinitecut_logo_512_rounded_light_theme.svg": (True, False),
        "new_infinitecut_logo_512_square_light_theme.svg": (False, False),
        "new_infinitecut_logo_512_dark_theme_rounded.svg": (True, True),
        "new_infinitecut_logo_512_square_dark_theme.svg": (False, True),
    }
    for name, (rounded, dark) in variants.items():
        path = os.path.join(assets, name)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(svg(rounded=rounded, dark=dark))
        written.append(os.path.relpath(path, root))

    master = svg(rounded=True, dark=False)

    # --- the app icon, every size the build asks for ---------------------
    save(render(master, 512), os.path.join(assets, "infinitecut_logo_512.png"))
    for size in (512, 256, 128, 64, 32, 16):
        save(render(master, size),
             os.path.join(icons, f"infinitecut_logo_{size}.png"))

    # --- Windows .ico ----------------------------------------------------
    ico = os.path.join(icons, "infinitecut.ico")
    render(master, 256).save(
        ico, format="ICO",
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    written.append(os.path.relpath(ico, root))

    # --- Android launcher densities --------------------------------------
    res = os.path.join(root, "src/crates/infinitecut-android/res")
    for folder, size in (
        ("mipmap-mdpi", 48), ("mipmap-hdpi", 72), ("mipmap-xhdpi", 96),
        ("mipmap-xxhdpi", 144), ("mipmap-xxxhdpi", 192),
    ):
        os.makedirs(os.path.join(res, folder), exist_ok=True)
        save(render(master, size), os.path.join(res, folder, "ic_launcher.png"))

    # --- README wordmarks -------------------------------------------------
    save(wordmark(dark=False), os.path.join(assets, "infinitecut-mark.png"))
    save(wordmark(dark=True), os.path.join(assets, "infinitecut-mark-dark.png"))

    # --- upstream artwork that is not ours to ship ------------------------
    for stale in (
        "infinitecut_logo.af", "infinitecut_logo_draft.af",
        "proxyon_sponsor_logo.png", "download_button.svg",
        "editor.png", "editor-light.png", "editor-dark.png",
    ):
        path = os.path.join(assets, stale)
        if os.path.exists(path):
            os.remove(path)
            print(f"  removed assets/{stale}")

    for name in sorted(written):
        print(f"  wrote {name}")
    print(f"\n{len(written)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
