import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import math
from datetime import datetime


def draw_chart(planets, name=None, dob=None, tob=None, city=None, country=None):
    # --- Şablon görselini indir ---
    template_url = "https://tilmaz.github.io/madam-dudu-astro-core/chart_template.png"
    response = requests.get(template_url)
    bg = Image.open(BytesIO(response.content)).convert("RGBA")
    draw = ImageDraw.Draw(bg)

    # --- Yazı tipleri ---
    try:
        font_path = "AstroGadget.ttf"
        planet_font = ImageFont.truetype(font_path, 64)
        label_font = ImageFont.truetype("DejaVuSans.ttf", 48)
        small_font = ImageFont.truetype("DejaVuSans.ttf", 36)
    except Exception as e:
        print("FONT LOAD ERROR:", e)
        planet_font = ImageFont.load_default()
        label_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # --- Gezegen sembolleri haritası ---
    planet_symbols = {
        "Sun": "a", "Moon": "b", "Mercury": "c", "Venus": "d", "Mars": "e",
        "Jupiter": "f", "Saturn": "g", "Uranus": "h", "Neptune": "i", "Pluto": "j"
    }

    # --- Merkez ve yarıçap ---
    center_x, center_y = bg.width // 2, bg.height // 2
    radius = int((min(center_x, center_y) - 50) * 0.85)  # %15 içeride

    # --- Gezegen pozisyonlarını hesapla (çizim için) ---
    positions = {}
    for p in planets:
        angle_deg = p["ecliptic_long"]
        angle_rad = math.radians(90 - angle_deg)
        x = center_x + radius * math.cos(angle_rad)
        y = center_y - radius * math.sin(angle_rad)
        positions[p["name"]] = (x, y)
        symbol = planet_symbols.get(p["name"], p["name"])
        draw.text((x - 20, y - 20), symbol, fill="#800080", font=planet_font)

    # --- Aspect çizgileri ---
    aspects = {
        0:   (8, "yellow"),   # Conjunction
        60:  (8, "green"),    # Sextile
        90:  (8, "red"),      # Square
        120: (8, "blue"),     # Trine
        180: (8, "purple"),   # Opposition
    }

    try:
        for i, p1 in enumerate(planets):
            for j, p2 in enumerate(planets):
                if i >= j:
                    continue
                diff = abs(p1["ecliptic_long"] - p2["ecliptic_long"])
                diff = diff if diff <= 180 else 360 - diff
                for aspect_angle, (thickness, color) in aspects.items():
                    if abs(diff - aspect_angle) < 4:  # orb toleransı
                        draw.line([positions[p1["name"]], positions[p2["name"]]], fill=color, width=thickness)
                        break
    except Exception as e:
        print("Aspect draw error:", e)

    # --- ÜST BAŞLIK (Chart Title) ---
    title_text = f"{name}'s Natal Chart Wheel" if name else "Natal Chart Wheel"
    bbox = draw.textbbox((0, 0), title_text, font=label_font)
    title_w = bbox[2] - bbox[0]
    draw.text(
        ((bg.width - title_w) // 2, 30),
        title_text,
        fill="#800080",
        font=label_font
    )

    # --- ALT BİLGİLER (DOB / TOB / LOCATION) ---
    try:
        dob_obj = datetime.strptime(dob, "%Y-%m-%d")
        date_str = dob_obj.strftime("%d %B %Y")
    except:
        date_str = dob or ""

    if tob:
        date_str += f" @{tob}"

    location_str = f"{city}/{country}" if city and country else ""

    spacing = 50
    line_y = bg.height - 120

    date_bbox = draw.textbbox((0, 0), date_str, font=small_font)
    date_w = date_bbox[2] - date_bbox[0]

    loc_bbox = draw.textbbox((0, 0), location_str, font=small_font)
    loc_w = loc_bbox[2] - loc_bbox[0]

    draw.text(
        ((bg.width - date_w) // 2, line_y),
        date_str,
        fill="#800080",
        font=small_font
    )
    draw.text(
        ((bg.width - loc_w) // 2, line_y + spacing),
        location_str,
        fill="#800080",
        font=small_font
    )

    # --- Aspect Legend ---
    legend = [
        ("🟡 Conjunction", "yellow"),
        ("🟢 Sextile",     "green"),
        ("🔴 Square",      "red"),
        ("🔵 Trine",       "blue"),
        ("🟣 Opposition",  "purple"),
    ]

    legend_y = bg.height - 220
    for label, color in legend:
        draw.text((40, legend_y), label, fill=color, font=small_font)
        legend_y += 38

    # --- Görseli belleğe yaz ---
    output = BytesIO()
    bg.save(output, format="PNG", optimize=True, quality=75)
    output.seek(0)
    return output
