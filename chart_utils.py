import io
import math
import requests
from PIL import Image, ImageDraw

# Sabit template URL
TEMPLATE_URL = "https://tilmaz.github.io/madam-dudu-astro-core/chart_template.png"

# Gezegen sembolleri (görsel olarak yerleştirilmiyor ama ileride eklenebilir)
PLANET_SYMBOLS = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Mars": "♂",
    "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅", "Neptune": "♆", "Pluto": "♇"
}

def draw_chart(planets):
    # Şablonu indir
    response = requests.get(TEMPLATE_URL)
    base = Image.open(io.BytesIO(response.content)).convert("RGBA")
    draw = ImageDraw.Draw(base)

    # Harita merkezini ve yarıçapı tanımla
    center_x, center_y = base.size[0] // 2, base.size[1] // 2
    radius = base.size[0] // 2 - 50

    # Her gezegeni yerleştir
    for planet in planets:
        angle_deg = planet["degree"]
        angle_rad = math.radians(angle_deg - 90)  # 0° = Koç, saat yönü ters

        x = center_x + radius * math.cos(angle_rad)
        y = center_y + radius * math.sin(angle_rad)

        r = 8
        draw.ellipse((x - r, y - r, x + r, y + r), fill="black")

    # Görseli belleğe kaydet
    output = io.BytesIO()
    base.save(output, format="PNG")
    output.seek(0)
    return output
