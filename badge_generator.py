from io import BytesIO
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).parent
BADGE_TEMPLATE = BASE_DIR / "assets" / "myguard-quiz-winner-badge.png"
FONT_PATH = BASE_DIR / "assets" / "NotoSansDisplay-CondensedBlack.ttf"

NAVY = (8, 34, 72)
GOLD = (255, 190, 20)
WHITE = (250, 252, 253)
BLUE = (31, 126, 218)
BLUE_DARK = (15, 82, 156)
MAX_NAME_CHARS = 25


def _font(size: int):
    if FONT_PATH.exists():
        return ImageFont.truetype(str(FONT_PATH), size)
    fallback = "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"
    if Path(fallback).exists():
        return ImageFont.truetype(fallback, size)
    return ImageFont.load_default()


def _fit_font(draw, text, max_width, start_size=82, min_size=28):
    for size in range(start_size, min_size - 1, -1):
        font = _font(size)
        bbox = draw.textbbox((0, 0), text, font=font, stroke_width=1)
        if bbox[2] - bbox[0] <= max_width:
            return font
    return _font(min_size)


def _star_points(cx, cy, outer, inner):
    points = []
    for i in range(10):
        angle = -math.pi / 2 + i * math.pi / 5
        radius = outer if i % 2 == 0 else inner
        points.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    return points


def _prepare_base():
    image = Image.open(BADGE_TEMPLATE).convert("RGB")
    width, height = image.size
    # Remove the sample name and the sample lower text while retaining the artwork.
    cover = Image.new("RGB", (width, height), WHITE)
    mask = Image.new("L", (width, height), 0)
    md = ImageDraw.Draw(mask)
    md.rectangle((int(width * .18), int(height * .795), int(width * .82), int(height * .91)), fill=255)
    image.paste(cover, (0, 0), mask)
    return image


def _add_name(image, name: str):
    width, height = image.size
    draw = ImageDraw.Draw(image)
    clean_name = " ".join(name.strip().split()).upper()
    if not clean_name:
        raise ValueError("Name is required")
    if len(clean_name) > MAX_NAME_CHARS:
        raise ValueError(f"Name must be {MAX_NAME_CHARS} characters or fewer.")

    font = _fit_font(draw, clean_name, int(width * .62), start_size=84, min_size=32)
    bbox = draw.textbbox((0, 0), clean_name, font=font, stroke_width=2)
    tw = bbox[2] - bbox[0]
    x = (width - tw) / 2
    y = int(height * .812)
    # Gold edge + navy face, matching the winner ribbon typography.
    draw.text((x, y), clean_name, font=font, fill=NAVY, stroke_width=3, stroke_fill=GOLD)

    ornament_y = int(height * .887)
    star_r = max(9, int(width * .012))
    draw.polygon(_star_points(width // 2, ornament_y, star_r, star_r * .42), fill=NAVY)
    line_len = int(min(105, width * .075))
    draw.line((width // 2 - line_len - 32, ornament_y, width // 2 - 14, ornament_y), fill=NAVY, width=4)
    draw.line((width // 2 + 14, ornament_y, width // 2 + line_len + 32, ornament_y), fill=NAVY, width=4)

    thank = "THANK YOU FOR VISITING OUR STALL!"
    thank_font = _font(18)
    tb = draw.textbbox((0, 0), thank, font=thank_font)
    draw.text(((width - (tb[2] - tb[0])) / 2, int(height * .902)), thank, font=thank_font, fill=NAVY)
    return image


def generate_winner_badge(name: str) -> bytes:
    """Generate the gold QUIZ WINNER badge for a 5/5 score."""
    image = _prepare_base()
    return _encode(_add_name(image, name))


def _blueify_ribbon(image):
    """Turn the existing gold ribbon artwork into a blue participant ribbon while retaining shading."""
    px = image.load()
    w, h = image.size
    y0, y1 = int(h * .64), int(h * .81)
    for y in range(y0, y1):
        t = (y - y0) / max(1, y1 - y0)
        target = tuple(int(BLUE_DARK[i] * (1 - t) + BLUE[i] * t) for i in range(3))
        for x in range(w):
            r, g, b = px[x, y]
            # Gold/yellow pixels: convert hue to the participant blue palette.
            if r > 145 and g > 85 and b < 145 and r > b * 1.35 and g > b * 1.15:
                brightness = max(r, g, b) / 255.0
                px[x, y] = tuple(min(255, int(c * (0.72 + 0.38 * brightness))) for c in target)
    return image


def _add_participant_ribbon(image):
    width, height = image.size
    draw = ImageDraw.Draw(image)

    # Recolor the original gold ribbon first so its tails, bevels and shadows
    # remain visually consistent with the supplied winner artwork.
    px = image.load()
    for y in range(int(height * .64), int(height * .82)):
        t = (y - height * .64) / (height * .18)
        base = tuple(int(BLUE_DARK[i] * (1 - t) + BLUE[i] * t) for i in range(3))
        for x in range(width):
            r, g, b = px[x, y]
            if r > 145 and g > 85 and b < 150 and r > b * 1.30 and g > b * 1.10:
                brightness = max(r, g, b) / 255.0
                px[x, y] = tuple(min(255, int(c * (0.78 + 0.30 * brightness))) for c in base)

    draw = ImageDraw.Draw(image)
    # Cover only the original QUIZ WINNER lettering with a compact blue center
    # panel, leaving the original ribbon silhouette and tails visible.
    draw.polygon([
        (int(width*.145), int(height*.665)),
        (int(width*.855), int(height*.665)),
        (int(width*.875), int(height*.795)),
        (int(width*.125), int(height*.795)),
    ], fill=BLUE)
    draw.line((int(width*.17), int(height*.67), int(width*.83), int(height*.67)), fill=(72,170,245), width=8)
    draw.line((int(width*.16), int(height*.785), int(width*.84), int(height*.785)), fill=BLUE_DARK, width=5)

    text = "CHALLENGE PARTICIPANT"
    font = _fit_font(draw, text, int(width*.66), start_size=66, min_size=30)
    bbox = draw.textbbox((0,0), text, font=font, stroke_width=2)
    tw = bbox[2]-bbox[0]
    th = bbox[3]-bbox[1]
    x = (width-tw)/2
    y = int(height*.685)
    draw.text((x+2,y+3), text, font=font, fill=BLUE_DARK, stroke_width=3, stroke_fill=WHITE)
    draw.text((x,y), text, font=font, fill=NAVY, stroke_width=1, stroke_fill=WHITE)

    star_r = 22
    draw.polygon(_star_points(int(width*.17), int(height*.72), star_r, star_r*.42), fill=NAVY)
    draw.polygon(_star_points(int(width*.83), int(height*.72), star_r, star_r*.42), fill=NAVY)
    return image

def generate_participant_badge(name: str) -> bytes:
    """Generate a personalized blue CHALLENGE PARTICIPANT badge for scores 0/5–4/5."""
    image = _prepare_base()
    image = _add_participant_ribbon(image)
    image = _add_name(image, name)
    return _encode(image)


def _encode(image):
    output = BytesIO()
    image.save(output, format="JPEG", quality=98, optimize=True, subsampling=0)
    return output.getvalue()
