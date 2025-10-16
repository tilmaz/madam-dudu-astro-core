import requests
from PIL import Image, ImageDraw
from io import BytesIO
import math

def draw_chart(planets):
    # --- 1. Arka plan şablonunu indir ---
    template_url = "https://tilmaz.github.io/madam-dudu-astro-core/chart_template.png"
    response = requests.get(template_url)
    bg = Image.open(BytesIO(response.content)).convert("RGBA")

    # --- 2. Çizim objesi oluştur ---
    draw = ImageDraw.Draw(bg)

    # --- 3. Gezegenleri çember üzerine yerleştir ---
    # Merkez koordinat ve yarıçap
    center_x, center_y = bg.width // 2, bg.height // 2
    radius = min(center_x, center_y) - 50  # kenarlardan biraz içeri

    for p in planets:
        angle_deg = p["degree"]
        angle_rad = math.radians(90 - angle_deg)  # 0° = yukarı

        # Konum
        x = center_x + radius * math.cos(angle_rad)
        y = center_y - radius * math.sin(angle_rad)

        # Nokta çiz
        draw.ellipse((x - 6, y - 6, x + 6, y + 6), fill="red")

        # Gezegen ismi (küçük harfle)
        label = p["name"][:2].capitalize()
        draw.text((x + 8, y - 8), label, fill="black")

    # --- 4. Görseli bellekte sakla ve döndür ---
    output = BytesIO()
    bg.save(output, format="PNG")
    output.seek(0)
    return output
