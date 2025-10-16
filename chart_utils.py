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

    # --- AstroGadget fontunu yükle ---
    try:
        font = ImageFont.truetype("AstroGadget.ttf", 32)  # Daha büyük yazı
    except:
        font = ImageFont.load_default()

    # --- AstroGadget'e uygun gezegen sembolleri ---
    planet_symbols = {
        "Sun": "a",
        "Moon": "b",
        "Mercury": "c",
        "Venus": "d",
        "Mars": "e",
        "Jupiter": "f",
        "Saturn": "g",
        "Uranus": "h",
        "Neptune": "i",
        "Pluto": "j"
    }

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
        draw.text((x - 12, y - 12), symbol, fill="#800080", font=font)

    # --- Görseli belleğe yaz ---
    output = BytesIO()
    bg.save(output, format="PNG")
    output.seek(0)
    return output
