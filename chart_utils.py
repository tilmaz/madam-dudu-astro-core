import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import math

def draw_chart(planets):
    # --- Şablon görselini indir ---
    template_url = "https://tilmaz.github.io/madam-dudu-astro-core/chart_template.png"
    response = requests.get(template_url)
    bg = Image.open(BytesIO(response.content)).convert("RGBA")

    draw = ImageDraw.Draw(bg)

    # --- Gezegen sembolleri haritası ---
    planet_symbols = {
        "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Mars": "♂",
        "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅", "Neptune": "♆", "Pluto": "♇"
    }

    # --- Yazı tipi ve boyutu ---
    try:
        font = ImageFont.truetype("arial.ttf", 22)
    except:
        font = ImageFont.load_default()

    # --- Merkez ve yarıçap ---
    center_x, center_y = bg.width // 2, bg.height // 2
    radius = min(center_x, center_y) - 50

    # --- Gezegenleri çiz ---
    for p in planets:
        angle_deg = p["degree"]
        angle_rad = math.radians(90 - angle_deg)

        x = center_x + radius * math.cos(angle_rad)
        y = center_y - radius * math.sin(angle_rad)

        symbol = planet_symbols.get(p["name"], p["name"])
        draw.text((x - 10, y - 10), symbol, fill="black", font=font)

    # --- Görseli belleğe yaz ---
    output = BytesIO()
    bg.save(output, format="PNG")
    output.seek(0)
    return output
