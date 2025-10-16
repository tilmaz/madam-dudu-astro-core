import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import math
from datetime import datetime


def draw_chart(planets, name=None, dob=None, tob=None, city=None, country=None, aspects=None):
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
    radius = int(min(center_x, center_y) * 0.85)  # %15 içeride

    # --- Gezegen koordinatlarını hesapla ---
    planet_coords = {}
    for p in planets:
        angle_deg = p["ecliptic_long"]
        angle_rad = math.radians(90 - angle_deg)
        x = center_x + radius * math.cos(angle_rad)
        y = center_y - radius * math.sin(angle_rad)
        planet_coords[p["name"]] = (x, y)

        symbol = planet_symbols.get(p["name"], p["name"])
        offset = planet_font.size // 2
        draw.text((x - offset, y - offset), symbol, fill="#800080", font=planet_font)

    # --- Aspect çizgileri ---
    if aspects:
        aspect_colors = {
            "conjunction": "#FFD700",  # Sarı
            "square": "#FF0000",       # Kırmızı
            "trine": "#0000FF",        # Mavi
            "sextile": "#00FF00",      # Yeşil
            "opposition": "#800080"    # Mor
        }
        for aspect in aspects:
            p1 = planet_coords.get(aspect["planet1"])
            p2 = planet_coords.get(aspect["planet2"])
            if p1 and p2:
                color = aspect_colors.get(aspect["type"], "black")
                draw.line([p1, p2], fill=color, width=3)  # Bold çizgi (width=3)

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

    spacing = 40
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

    # --- Aspect legend ---
    legend_text = (
        "\u2B24 Conjunction    \u2B24 Opposition    \u2B24 Square    \u2B24 Trine    \u2B24 Sextile"
    )
    legend_colors = ["#FFD700", "#800080", "#FF0000", "#0000FF", "#00FF00"]
    spacing_x = 280
    start_x = (bg.width - (spacing_x * 5)) // 2
    legend_y = bg.height - 40

    for idx, (color, label) in enumerate(zip(legend_colors, ["Conjunction", "Opposition", "Square", "Trine", "Sextile"])):
        cx = start_x + idx * spacing_x
        draw.text((cx, legend_y), label, fill=color, font=small_font)

    # --- Görseli belleğe yaz ---
    output = BytesIO()
    bg.save(output, format="PNG")
    output.seek(0)
    return output
