from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageChops

BASE_DIR = Path(__file__).parent
BADGE_TEMPLATE = BASE_DIR / "assets" / "myguard-quiz-winner-badge.png"
FONT_PATH = BASE_DIR / "assets" / "NotoSansDisplay-CondensedBlack.ttf"

NAVY = (8, 34, 72)
GOLD = (255, 190, 20)
WHITE = (250, 252, 253)
MAX_NAME_CHARS = 25


def _font(size: int):
    if FONT_PATH.exists():
        return ImageFont.truetype(str(FONT_PATH), size)
    fallback = "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"
    if Path(fallback).exists():
        return ImageFont.truetype(fallback, size)
    return ImageFont.load_default()


def _fit_font(draw, text, max_width, start_size=82, min_size=38):
    for size in range(start_size, min_size - 1, -1):
        font = _font(size)
        bbox = draw.textbbox((0, 0), text, font=font)
        if bbox[2] - bbox[0] <= max_width:
            return font
    return _font(min_size)


def _star_points(cx, cy, outer, inner):
    import math
    points = []
    for i in range(10):
        angle = -math.pi / 2 + i * math.pi / 5
        radius = outer if i % 2 == 0 else inner
        points.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    return points


def generate_winner_badge(name: str) -> bytes:
    """Generate a personalized winner badge for names up to 25 characters."""
    image = Image.open(BADGE_TEMPLATE).convert("RGB")
    width, height = image.size
    cx = width // 2
    cy = height // 2
    draw = ImageDraw.Draw(image)

    clean_name = " ".join(name.strip().split()).upper()
    if not clean_name:
        raise ValueError("Name is required")
    if len(clean_name) > MAX_NAME_CHARS:
        raise ValueError(f"Name must be {MAX_NAME_CHARS} characters or fewer.")

    # The approved badge artwork already has a clean white name area.
    # Cover only the existing sample name there; this stays fully inside the
    # white panel and therefore leaves the ribbon and circular border untouched.
    cover = Image.new("RGB", (width, height), WHITE)
    cover_mask = Image.new("L", (width, height), 0)
    cm = ImageDraw.Draw(cover_mask)
    cm.rounded_rectangle(
        (int(width * 0.18), int(height * 0.795),
         int(width * 0.82), int(height * 0.905)),
        radius=int(width * 0.035), fill=255
    )
    image.paste(cover, (0, 0), cover_mask)
    draw = ImageDraw.Draw(image)

    # Keep the name visually consistent with QUIZ WINNER while scaling down
    # smoothly for long names. 25 characters still get a readable display size.
    font = _fit_font(draw, clean_name, int(width * 0.57), start_size=82, min_size=38)
    bbox = draw.textbbox((0, 0), clean_name, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    name_x = cx - text_w / 2
    name_y = int(height * 0.802)

    # Gold offset + navy foreground = same visual language as the gold ribbon.
    draw.text((name_x, name_y), clean_name, font=font, fill=NAVY, stroke_width=2, stroke_fill=GOLD)

    # For long names, keep ornaments compact and inside the white field.
    ornament_y = int(height * 0.875)
    star_r = max(9, int(width * 0.009))
    star_x_gap = int(min(48, width * 0.038))
    draw.polygon(_star_points(cx, ornament_y, star_r, star_r * 0.42), fill=NAVY)

    line_len = int(min(105, width * 0.075))
    draw.line((cx - line_len - 28, ornament_y, cx - 12, ornament_y), fill=NAVY, width=4)
    draw.line((cx + 12, ornament_y, cx + line_len + 28, ornament_y), fill=NAVY, width=4)

    thank = "THANK YOU FOR VISITING OUR STALL!"
    thank_font = _font(18)
    tb = draw.textbbox((0, 0), thank, font=thank_font)
    draw.text(((width - (tb[2] - tb[0])) / 2, int(height * 0.895)),
              thank, font=thank_font, fill=NAVY)

    output = BytesIO()
    image.save(output, format="JPEG", quality=98, optimize=True, subsampling=0)
    return output.getvalue()
