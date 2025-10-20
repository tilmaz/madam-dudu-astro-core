import math
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Aspect açı aralıkları (derece)
ASPECTS = {
    "Conjunction": (0, 8, (255, 255, 255)),      # beyaz
    "Sextile": (60, 6, (0, 255, 128)),           # yeşil
    "Square": (90, 6, (255, 60, 60)),            # kırmızı
    "Trine": (120, 6, (60, 120, 255)),           # mavi
    "Opposition": (180, 8, (200, 200, 200)),     # gri
}


def angle_diff(a, b):
    """İki gezegen arasındaki en kısa açı farkını hesapla."""
    diff = abs(a - b) % 360
    return diff if diff <= 180 else 360 - diff


def draw_chart(planets, name, dob, tob, city, country):
    size = 1400
    pad_top, pad_bottom = 200, 260
    total_h = size + pad_top + pad_bottom

    img = Image.new("RGB", (size, total_h), (8, 8, 16))
    draw = ImageDraw.Draw(img)

    cx, cy = size // 2, pad_top + size // 2
    radius = size // 2 - 100

    # Fontlar
    font_main = ImageFont.truetype("DejaVuSans-Bold.ttf", 46)
    font_text = ImageFont.truetype("DejaVuSans.ttf", 26)
    font_small = ImageFont.truetype("DejaVuSans.ttf", 20)
    try:
        planet_font = ImageFont.truetype("AstroGadget.ttf", 42)
    except:
        planet_font = font_text

    # 🟣 Başlık
    title = f"{name}'s Natal Birth Chart"
    tw, th = draw.textbbox((0, 0), title, font=font_main)[2:]
    draw.text(((size - tw) / 2, 60), title, fill=(165, 102, 255), font=font_main)

    # Dış daire
    draw.ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        outline=(180, 160, 255), width=3
    )

    # 12 ev dilimi + numaraları
    for i in range(12):
        angle = math.radians((360 / 12) * i)
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        draw.line([cx, cy, x, y], fill=(100, 100, 180), width=2)

        # Ev numarası
        num_angle = math.radians((360 / 12) * i + 15)
        nx = cx + (radius - 50) * math.cos(num_angle)
        ny = cy + (radius - 50) * math.sin(num_angle)
        draw.text((nx - 10, ny - 10), str(i + 1), fill=(220, 220, 250), font=font_small)

    # Gezegen pozisyonları
    planet_positions = {}
    inner_radius = radius * 0.85
    for p in planets:
        angle = math.radians(p["ecliptic_long"])
        x = cx + inner_radius * math.cos(angle)
        y = cy + inner_radius * math.sin(angle)
        draw.text((x - 12, y - 12), "☉", fill=(165, 102, 255), font=planet_font)
        planet_positions[p["name"]] = (x, y, p["ecliptic_long"])

    # Aspect çizgileri
    planet_names = list(planet_positions.keys())
    for i in range(len(planet_names)):
        for j in range(i + 1, len(planet_names)):
            p1, p2 = planet_names[i], planet_names[j]
            angle = angle_diff(planet_positions[p1][2], planet_positions[p2][2])

            for asp, (deg, orb, color) in ASPECTS.items():
                if abs(angle - deg) <= orb:
                    draw.line(
                        [planet_positions[p1][:2], planet_positions[p2][:2]],
                        fill=color, width=2
                    )

    # Alt bilgi (tarih, saat, yer)
    info1 = f"Date: {dob} — Time: {tob}"
    info2 = f"Location: {city}, {country}"
    iw1 = draw.textbbox((0, 0), info1, font=font_text)[2]
    iw2 = draw.textbbox((0, 0), info2, font=font_text)[2]
    y_base = pad_top + size + 30
    draw.text(((size - iw1) / 2, y_base), info1, fill=(210, 210, 230), font=font_text)
    draw.text(((size - iw2) / 2, y_base + 40), info2, fill=(210, 210, 230), font=font_text)

    # Aspect legend
    legend_y = y_base + 100
    lx = 300
    draw.text((lx, legend_y - 40), "Aspects:", fill=(180, 160, 255), font=font_text)
    for i, (asp, (_, _, color)) in enumerate(ASPECTS.items()):
        box_y = legend_y + i * 30
        draw.rectangle([lx, box_y, lx + 25, box_y + 25], fill=color)
        draw.text((lx + 40, box_y - 2), asp, fill=(220, 220, 240), font=font_small)

    # Kaydet
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("charts", exist_ok=True)
    file_path = f"charts/chart_{name.lower()}_{timestamp}.png"
    img.save(file_path)

    return {"url": f"/{file_path}"}
