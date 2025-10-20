import os
from PIL import Image, ImageDraw, ImageFont
import math
import datetime

def draw_chart(planets, houses, ascendant, name, dob, tob, city, country, output_path=None):
    # Dosya yolu dinamik hale getirildi (Render için kritik)
    base_dir = os.path.dirname(__file__)
    template_path = os.path.join(base_dir, "chart_template.png")
    font_path = os.path.join(base_dir, "AstroGadget.ttf")

    # Template ve font yükle
    bg = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(bg)
    font = ImageFont.truetype(font_path, 20)

    width, height = bg.size
    center = (width // 2, height // 2)
    radius = min(center) - 50

    # Planet sembollerini çiz
    for planet, data in planets.items():
        angle = math.radians(data["ecliptic_long"])
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)

        draw.text((x - 10, y - 10), planet[0], fill="white", font=font)

    # Ascendant çizgisi
    asc_angle = math.radians(ascendant["ecliptic_long"])
    asc_x = center[0] + radius * math.cos(asc_angle)
    asc_y = center[1] + radius * math.sin(asc_angle)
    draw.line([center, (asc_x, asc_y)], fill="yellow", width=2)

    # Chart bilgilerini yaz
    info_text = f"{name}\n{dob} {tob}\n{city}, {country}"
    draw.text((20, height - 100), info_text, fill="white", font=font)

    # Kaydetme işlemi
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chart_{timestamp}.png"
    save_dir = os.path.join("/tmp", "charts")
    os.makedirs(save_dir, exist_ok=True)

    output_file = os.path.join(save_dir, filename)
    bg.save(output_file)

    print(f"[DEBUG] Chart saved at: {output_file}")

    return output_file
