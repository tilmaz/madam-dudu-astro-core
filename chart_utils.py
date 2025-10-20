import os
import math
import datetime
from PIL import Image, ImageDraw, ImageFont

# ==============================
# 🌌 Madam Dudu Astro Core v4
# Template Overlay Chart Renderer
# ==============================

def draw_chart(planets, name, dob, tob, city, country, houses=None):
    """
    Draws a natal chart on top of chart_template.png and returns the PNG path.
    """

    # === SETTINGS ===
    template_path = "chart_template.png"
    output_dir = "charts"
    font_path = "AstroGadget.ttf"  # fallback: Unicode glyphs
    os.makedirs(output_dir, exist_ok=True)

    # === LOAD BASE IMAGE (TEMPLATE) ===
    base_img = Image.open(template_path).convert("RGBA")

    # Resize for A4 aspect ratio (approx 2480x3508px @300dpi)
    base_img = base_img.resize((2480, 2480), Image.LANCZOS)
    draw = ImageDraw.Draw(base_img)

    # === FONT SETUP ===
    try:
        title_font = ImageFont.truetype("arial.ttf", 120)
        text_font = ImageFont.truetype("arial.ttf", 60)
        astro_font = ImageFont.truetype(font_path, 80)
    except:
        # fallback fonts (if system fonts unavailable)
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        astro_font = ImageFont.load_default()

    # === TITLE ===
    title_text = f"{name}'s Natal Chart Wheel"
    title_color = (179, 102, 255)  # mor
    title_w, title_h = draw.textsize(title_text, font=title_font)
    draw.text(
        ((base_img.width - title_w) / 2, 100),
        title_text,
        fill=title_color,
        font=title_font,
    )

    # === ASPECT LINES ===
    aspect_colors = {
        "Conjunction": (255, 215, 0, 255),
        "Sextile": (0, 255, 153, 255),
        "Square": (255, 51, 51, 255),
        "Trine": (51, 102, 255, 255),
        "Opposition": (162, 89, 255, 255),
    }

    # Chart center & geometry
    cx, cy = base_img.width // 2, base_img.height // 2
    radius = 950  # dış çember için
    inner_radius = 500  # gezegen konumu için

    # === DRAW PLANETS ===
    for planet in planets:
        angle_deg = planet["ecliptic_long"]
        angle_rad = math.radians(angle_deg)
        px = cx + inner_radius * math.cos(math.radians(270 - angle_deg))
        py = cy + inner_radius * math.sin(math.radians(270 - angle_deg))

        # planet symbol (with fallback)
        symbol_map = {
            "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀",
            "Mars": "♂", "Jupiter": "♃", "Saturn": "♄",
            "Uranus": "♅", "Neptune": "♆", "Pluto": "♇"
        }
        symbol = symbol_map.get(planet["name"], "?")

        draw.text(
            (px - 20, py - 20),
            symbol,
            font=astro_font,
            fill=(179, 102, 255),
        )

    # === FOOTER INFO ===
    footer_y = base_img.height - 250
    footer_text_1 = f"{dob} @ {tob}"
    footer_text_2 = f"{city}, {country}"

    for i, text in enumerate([footer_text_1, footer_text_2]):
        tw, th = draw.textsize(text, font=text_font)
        draw.text(
            ((base_img.width - tw) / 2, footer_y + i * 70),
            text,
            fill=(179, 102, 255),
            font=text_font,
        )

    # === SAVE IMAGE ===
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chart_{name.lower()}_{timestamp}.png"
    file_path = os.path.join(output_dir, filename)
    base_img.save(file_path, format="PNG")

    # === RETURN DATA ===
    return {
        "chart_url": f"/charts/{filename}",
        "text": (
            f"{name}'s Natal Chart\n"
            f"Date: {dob}\n"
            f"Time: {tob}\n"
            f"Location: {city}, {country}\n\n"
            f"Doğum haritasını görüntüle:\n"
            f"/charts/{filename}"
        ),
    }
