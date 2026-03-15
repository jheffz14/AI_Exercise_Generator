# thumbnail_generator.py
"""
Creates a high-impact YouTube-style thumbnail (1280×720).

Design inspired by top fitness channels:
  • Bold gradient background
  • Large, punchy title with thick outline
  • Sub-label / tagline bar
  • Fire emoji accent
"""

import os
from PIL import Image, ImageDraw, ImageFont

THUMB_W, THUMB_H = 1280, 720
FONT_PATH        = "arialbd.ttf"   # place in project root, or update path


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in [FONT_PATH, "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "/System/Library/Fonts/Helvetica.ttc"]:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _gradient_bg(draw: ImageDraw.ImageDraw, w: int, h: int):
    """Draw a dark-red → near-black vertical gradient."""
    top_color    = (180, 0, 0)
    bottom_color = (10, 10, 10)
    for y in range(h):
        t = y / h
        r = int(top_color[0] * (1 - t) + bottom_color[0] * t)
        g = int(top_color[1] * (1 - t) + bottom_color[1] * t)
        b = int(top_color[2] * (1 - t) + bottom_color[2] * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))


def _draw_outlined_text(draw, pos, text, font, fill, outline, thickness=5):
    x, y = pos
    for dx in range(-thickness, thickness + 1):
        for dy in range(-thickness, thickness + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=outline)
    draw.text((x, y), text, font=font, fill=fill)


def _text_center_x(draw, text, font, w):
    bbox = draw.textbbox((0, 0), text, font=font)
    return (w - (bbox[2] - bbox[0])) // 2


def create_thumbnail(folder: str, title: str = "10 MIN FAT BURN") -> str:
    os.makedirs(folder, exist_ok=True)

    img  = Image.new("RGB", (THUMB_W, THUMB_H))
    draw = ImageDraw.Draw(img)

    # ── Gradient background ──────────────────────────────
    _gradient_bg(draw, THUMB_W, THUMB_H)

    # ── Diagonal accent stripe ───────────────────────────
    draw.polygon(
        [(THUMB_W * 0.55, 0), (THUMB_W, 0),
         (THUMB_W, THUMB_H * 0.45), (THUMB_W * 0.65, 0)],
        fill=(220, 30, 30),
    )

    # ── Main title ───────────────────────────────────────
    font_main = _load_font(130)
    cx = _text_center_x(draw, title, font_main, THUMB_W)
    _draw_outlined_text(draw, (cx, THUMB_H * 0.18), title,
                        font_main, fill="white", outline="black", thickness=6)

    # ── Fire emoji accent ────────────────────────────────
    font_fire = _load_font(90)
    fire_text = "🔥 BURN CALORIES  •  LOSE WEIGHT 🔥"
    try:
        cx2 = _text_center_x(draw, fire_text, font_fire, THUMB_W)
        _draw_outlined_text(draw, (cx2, THUMB_H * 0.52), fire_text,
                            font_fire, fill="#ffcc00", outline="black", thickness=4)
    except Exception:
        pass   # emoji may fail on some systems; skip gracefully

    # ── Bottom banner ────────────────────────────────────
    banner_y = THUMB_H - 130
    draw.rectangle([0, banner_y, THUMB_W, THUMB_H], fill=(0, 0, 0))
    font_sub = _load_font(62)
    sub_text = "💪  HOME WORKOUT  •  NO EQUIPMENT  •  ALL LEVELS"
    cxs = _text_center_x(draw, sub_text, font_sub, THUMB_W)
    draw.text((cxs, banner_y + 22), sub_text, font=font_sub, fill="#ffcc00")

    # ── Save ─────────────────────────────────────────────
    thumb_path = os.path.join(folder, "thumbnail.jpg")
    img.save(thumb_path, quality=95)
    print(f"✅ Thumbnail saved: {thumb_path}")
    return thumb_path


# ── CLI test ──────────────────────────────────────────────
if __name__ == "__main__":
    create_thumbnail("output/test_thumb", "10 MIN FAT BURN")