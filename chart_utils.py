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
    radius = min(center_x, center_y) - 50

    # --- Gezegenleri çiz ---
    for p in planets:
        angle_deg = p["ecliptic_long"]
        angle_rad = math.radians(90 - angle_deg)
        planet_radius = radius * 0.90
        x = center_x + radius * math.cos(angle_rad)
        y = center_y - radius * math.sin(angle_rad)
        symbol = planet_symbols.get(p["name"], p["name"])
        draw.text((x - 20, y - 20), symbol, fill="#800080", font=planet_font)

    # --- ÜST BAŞLIK (Chart Title) ---
    title_text = f"{name}'s Natal Chart Wheel" if name else "Natal Chart Wheel"
    bbox = draw.textbbox((0, 0), title_text, font=label_font)
    title_w = bbox[2] - bbox[0]
    draw.text(
        ((bg.width - title_w) // 2, 50),  # 30 → 50: biraz aşağı aldık
        title_text,
        fill="#800080",  # MOR
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

    spacing = 50  # ARTTIRILDI
    line_y = bg.height - 140  # biraz yukarı aldık

    date_bbox = draw.textbbox((0, 0), date_str, font=small_font)
    date_w = date_bbox[2] - date_bbox[0]

    loc_bbox = draw.textbbox((0, 0), location_str, font=small_font)
    loc_w = loc_bbox[2] - loc_bbox[0]

    draw.text(
        ((bg.width - date_w) // 2, line_y),
        date_str,
        fill="#800080",  # MOR
        font=small_font
    )
    draw.text(
        ((bg.width - loc_w) // 2, line_y + spacing),
        location_str,
        fill="#800080",  # MOR
        font=small_font
    )

    # --- Görseli belleğe yaz ---
    output = BytesIO()
    bg.save(output, format="PNG")
    output.seek(0)
    return output
