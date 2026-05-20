import io
import random
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile


def _pick_background():
    palettes = [
        (222, 235, 247),
        (232, 240, 230),
        (245, 236, 228),
        (238, 232, 244),
        (230, 242, 240),
        (244, 238, 232),
    ]
    return random.choice(palettes)


def _pick_text_color(background):
    luminance = 0.299 * background[0] + 0.587 * background[1] + 0.114 * background[2]
    return (45, 55, 72) if luminance > 140 else (245, 247, 250)


def generate_avatar_file(letter):
    size = 256
    background = _pick_background()
    text_color = _pick_text_color(background)
    image = Image.new("RGB", (size, size), background)
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", 120)
    except OSError:
        font = ImageFont.load_default()
    char = (letter or "?")[0].upper()
    bbox = draw.textbbox((0, 0), char, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((size - text_width) / 2, (size - text_height) / 2 - 10)
    draw.text(position, char, fill=text_color, font=font)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return ContentFile(buffer.read(), name=f"avatar_{char.lower()}.png")
