import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import math
from datetime import datetime

# --- Aspect tanımları (açı ve tolerans) ---
ASPECTS = {
    "Conjunction": (0, 8, "#FFD700"),     # 🟡
    "Opposition": (180, 8, "#800080"),     # 🟣
    "Square": (90, 6, "#FF0000"),           # 🔴
    "Trine": (120, 6, "#0000FF"),           # 🔵
    "Sextile": (60, 4, "#00CC66")           # 🟢
}


def calculate_angle_diff(a1, a2):
    diff = abs(a1 - a2) % 360
    return min(diff, 360 - diff)


def find_aspects(planets):
    aspects = []
    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            p1, p2 = planets[i], planets[j]
            diff = calculate_angle_diff(p1["ecliptic_long"], p2["ecliptic_long"])
            for aspect, (target_angle, orb, color) in ASPECTS.items():
                if abs(diff - target_angle) <= orb:
                    aspects.append((p1, p2, aspect, color))
    return aspects


def draw_chart(planets, name=None, dob=None, tob=None, city=None, country=None):
    template_url = "https://tilmaz.github.io/madam-dudu-astro-core/chart_template.png"
    response = requests.get(template_url)
    bg = Image.open(BytesIO(response.content)).convert("RGBA")
    draw = ImageDraw.Draw(bg)

    # Fontlar
    try:
        font_path = "AstroGadget.ttf"
        planet_font = ImageFont.truetype(font_path, 64)
        label_font = ImageFont.truetype("DejaVuSans.ttf", 48)
        small_font = ImageFont.truetype("DejaVuSans.ttf", 36)
    except:
        planet_font = label_font = small_font = ImageFont.load_default()

    # Gezegen sembolleri
    planet_symbols = {
        "Sun": "a", "Moon": "b", "Mercury": "c", "Venus": "d", "Mars": "e",
        "Jupiter": "f", "Saturn": "g", "Uranus": "h", "Neptune": "i", "Pluto": "j"
    }

    center_x, center_y = bg.width // 2, bg.height // 2
    radius = min(center_x, center_y) - 50
    aspect_radius = int(radius * 0.85)

    # Gezegen koordinatlarını topla
    coords = {}
    for p in planets:
        angle_deg = p["ecliptic_long"]
        angle_rad = math.radians(90 - angle_deg)
        x = center_x + radius * math.cos(angle_rad)
        y = center_y - radius * math.sin(angle_rad)
        coords[p["name"]] = (x, y)
        symbol = planet_symbols.get(p["name"], p["name"])
        draw.text((x - 20, y - 20), symbol, fill="#800080", font=planet_font)

    # Aspect çizgileri
    for p1, p2, aspect, color in find_aspects(planets):
        x1, y1 = coords[p1["name"]]
        x2, y2 = coords[p2["name"]]
        draw.line((x1, y1, x2, y2), fill=color, width=2)

    # Üst başlık
    title_text = f"{name}'s Natal Chart Wheel" if name else "Natal Chart Wheel"
    bbox = draw.textbbox((0, 0), title_text, font=label_font)
    title_w = bbox[2] - bbox[0]
    draw.text(((bg.width - title_w) // 2, 30), title_text, fill="#800080", font=label_font)

    # Alt bilgiler
    try:
        dob_obj = datetime.strptime(dob, "%Y-%m-%d")
        date_str = dob_obj.strftime("%d %B %Y")
    except:
        date_str = dob or ""
    if tob:
        date_str += f" @{tob}"
    location_str = f"{city}/{country}" if city and country else ""

    spacing = 40
    line_y = bg.height - 120

    date_bbox = draw.textbbox((0, 0), date_str, font=small_font)
    date_w = date_bbox[2] - date_bbox[0]
    loc_bbox = draw.textbbox((0, 0), location_str, font=small_font)
    loc_w = loc_bbox[2] - loc_bbox[0]

    draw.text(((bg.width - date_w) // 2, line_y), date_str, fill="#800080", font=small_font)
    draw.text(((bg.width - loc_w) // 2, line_y + spacing), location_str, fill="#800080", font=small_font)

    # Legend (aspect açıklamaları)
    legend_text = "  ".join([f"{emoji} {name}" for name, (_, _, emoji) in zip(ASPECTS.keys(), ASPECTS.values())])
    legend_font = ImageFont.truetype("DejaVuSans.ttf", 28)
    draw.text((50, bg.height - 50), legend_text, fill="black", font=legend_font)

    output = BytesIO()
    bg.save(output, format="PNG")
    output.seek(0)
    return output
