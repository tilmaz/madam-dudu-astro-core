import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import math
from datetime import datetime

ASPECTS = {
    "Conjunction": {"angle": 0, "color": "#FFD700"},     # Sarı
    "Opposition": {"angle": 180, "color": "#800080"},     # Mor
    "Square": {"angle": 90, "color": "#FF0000"},          # Kırmızı
    "Trine": {"angle": 120, "color": "#0000FF"},          # Mavi
    "Sextile": {"angle": 60, "color": "#00FF00"}          # Yeşil
}

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
        legend_font = ImageFont.truetype("DejaVuSans.ttf", 28)
    except Exception as e:
        print("FONT LOAD ERROR:", e)
        planet_font = ImageFont.load_default()
        label_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
        legend_font = ImageFont.load_default()

    # --- Gezegen sembolleri haritası ---
    planet_symbols = {
        "Sun": "a", "Moon": "b", "Mercury": "c", "Venus": "d", "Mars": "e",
        "Jupiter": "f", "Saturn": "g", "Uranus": "h", "Neptune": "i", "Pluto": "j"
    }

    # --- Merkez ve yarıçap ---
    center_x, center_y = bg.width // 2, bg.height // 2
    outer_radius = min(center_x, center_y) - 50
    planet_radius = int(outer_radius * 0.85)  # %15 içeride

    # --- Gezegen konumları (x,y) hesapla ---
    planet_positions = {}
    for p in planets:
        angle_deg = p["ecliptic_long"]
        angle_rad = math.radians(90 - angle_deg)
        x = center_x + planet_radius * math.cos(angle_rad)
        y = center_y - planet_radius * math.sin(angle_rad)
        symbol = planet_symbols.get(p["name"], p["name"])
        draw.text((x - 20, y - 20), symbol, fill="#800080", font=planet_font)
        planet_positions[p["name"]] = (x, y, angle_deg)

    # --- Aspect çizgilerini çiz ---
    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            p1 = planets[i]
            p2 = planets[j]
            angle_diff = abs(p1["ecliptic_long"] - p2["ecliptic_long"]) % 360
            if angle_diff > 180:
                angle_diff = 360 - angle_diff

            for aspect, props in ASPECTS.items():
                if abs(angle_diff - props["angle"]) < 4:  # Tolerance 4°
                    x1, y1, _ = planet_positions[p1["name"]]
                    x2, y2, _ = planet_positions[p2["name"]]
                    draw.line([(x1, y1), (x2, y2)], fill=props["color"], width=3)
                    break

    # --- ÜST BAŞLIK ---
    title_text = f"{name}'s Natal Chart Wheel" if name else "Natal Chart Wheel"
    bbox = draw.textbbox((0, 0), title_text, font=label_font)
    title_w = bbox[2] - bbox[0]
    draw.text(
        ((bg.width - title_w) // 2, 30),
        title_text,
        fill="#800080",
        font=label_font
    )

    # --- ALT BİLGİLER (Tarih, saat, yer) ---
    try:
        dob_obj = datetime.strptime(dob, "%Y-%m-%d")
        date_str = dob_obj.strftime("%d %B %Y")
    except:
        date_str = dob or ""

    if tob:
        date_str += f" @{tob}"

    location_str = f"{city}/{country}" if city and country else ""

    spacing = 20
    line_y = bg.height - 110

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

    # --- Aspect açıklamaları (renkli yazılar) ---
    legend_y = bg.height - 30
    legend_x = 40
    for label, props in ASPECTS.items():
        draw.text(
            (legend_x, legend_y),
            label,
            fill=props["color"],
            font=legend_font
        )
        legend_x += draw.textlength(label + "   ", font=legend_font)

    # --- Görseli belleğe yaz ---
    output = BytesIO()
    bg.save(output, format="PNG")
    output.seek(0)
    return output
