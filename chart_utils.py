import math
import os
from PIL import Image, ImageDraw, ImageFont

# ===========================
# CHART CONFIGURATION
# ===========================
TEMPLATE_PATH = "chart_template.png"
CHARTS_DIR = "charts"
FONT_PATH = "AstroGadget.ttf"
DEFAULT_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

ASPECT_COLORS = {
    "conjunction": (255, 255, 255),  # white
    "opposition": (255, 0, 0),       # red
    "trine": (0, 102, 255),          # blue
    "square": (255, 165, 0),         # orange
    "sextile": (0, 255, 0)           # green
}

PLANET_SYMBOLS = {
    "Sun": "☉",
    "Moon": "☽",
    "Mercury": "☿",
    "Venus": "♀",
    "Mars": "♂",
    "Jupiter": "♃",
    "Saturn": "♄",
    "Uranus": "♅",
    "Neptune": "♆",
    "Pluto": "♇"
}


def get_font(size):
    """Try Astro font, fall back to DejaVuSans."""
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except:
        return ImageFont.truetype(DEFAULT_FONT, size)


def draw_text_center(draw, text, xy, font, fill=(255, 255, 255)):
    """Draw centered text with textbbox() support."""
    bbox = draw.textbbox(xy, text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x, y = xy
    draw.text((x - text_w / 2, y - text_h / 2), text, font=font, fill=fill)


def draw_chart(planets, name, dob, tob, city, country):
    """Draws natal chart with title, aspect lines, and planet symbols."""
    if not os.path.exists(CHARTS_DIR):
        os.makedirs(CHARTS_DIR)

    template = Image.open(TEMPLATE_PATH).convert("RGBA")
    draw = ImageDraw.Draw(template)
    W, H = template.size
    cx, cy = W // 2, H // 2

    # Chart circle radius
    radius = min(W, H) * 0.42
    planet_radius = radius * 0.85

    # --------------------------
    # Planet Positions
    # --------------------------
    coords = {}
    for planet in planets:
        angle_deg = planet["ecliptic_long"]
        angle_rad = math.radians(angle_deg - 90)
        x = cx + planet_radius * math.cos(angle_rad)
        y = cy + planet_radius * math.sin(angle_rad)
        coords[planet["name"]] = (x, y)

        # Draw planet symbol
        symbol = PLANET_SYMBOLS.get(planet["name"], "?")
        planet_font = get_font(40)
        draw_text_center(draw, symbol, (x, y), planet_font, fill="#AA66FF")

    # --------------------------
    # Aspect Lines
    # --------------------------
    def angle_diff(a, b):
        d = abs(a - b) % 360
        return min(d, 360 - d)

    for p1 in planets:
        for p2 in planets:
            if p1["name"] == p2["name"]:
                continue
            diff = angle_diff(p1["ecliptic_long"], p2["ecliptic_long"])
            color = None
            if abs(diff - 0) < 8:
                color = ASPECT_COLORS["conjunction"]
            elif abs(diff - 60) < 6:
                color = ASPECT_COLORS["sextile"]
            elif abs(diff - 90) < 6:
                color = ASPECT_COLORS["square"]
            elif abs(diff - 120) < 6:
                color = ASPECT_COLORS["trine"]
            elif abs(diff - 180) < 8:
                color = ASPECT_COLORS["opposition"]
            if color:
                draw.line([coords[p1["name"]], coords[p2["name"]]], fill=color, width=2)

    # --------------------------
    # Title & Footer
    # --------------------------
    title_font = get_font(48)
    info_font = get_font(28)
    legend_font = get_font(22)

    # Title
    title_text = f"{name}'s Natal Birth Chart"
    draw_text_center(draw, title_text, (cx, 50), title_font, fill="white")

    # Footer info
    footer_text1 = f"Born on {dob} at {tob}"
    footer_text2 = f"{city}, {country}"
    draw_text_center(draw, footer_text1, (cx, H - 90), info_font, fill="white")
    draw_text_center(draw, footer_text2, (cx, H - 55), info_font, fill="white")

    # Legend
    legend_y = H - 25
    legend_x = 40
    legends = [
        ("Conjunction", "⚪", ASPECT_COLORS["conjunction"]),
        ("Opposition", "🔴", ASPECT_COLORS["opposition"]),
        ("Trine", "🔵", ASPECT_COLORS["trine"]),
        ("Square", "🟠", ASPECT_COLORS["square"]),
        ("Sextile", "🟢", ASPECT_COLORS["sextile"]),
    ]
    x_offset = legend_x
    for label, symbol, color in legends:
        text = f"{symbol} {label}"
        draw.text((x_offset, legend_y), text, font=legend_font, fill=color)
        x_offset += draw.textlength(text, font=legend_font) + 40

    # Save
    filename = f"chart_{name.lower()}_{dob.replace('-', '')}.png"
    path = os.path.join(CHARTS_DIR, filename)
    template.save(path, "PNG")

    return {"url": f"/charts/{filename}", "status": "ok"}
