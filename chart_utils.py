import os
import math
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Gezegen sembolleri (AstroGadget.ttf)
PLANET_SYMBOLS = {
    "Sun": "☉",
    "Moon": "☽",
    "Mercury": "☿",
    "Venus": "♀",
    "Mars": "♂",
    "Jupiter": "♃",
    "Saturn": "♄",
    "Uranus": "♅",
    "Neptune": "♆",
    "Pluto": "♇"
}

# Aspect renkleri
ASPECTS = {
    "conjunction": (0, 255, 0),   # 🟢 Yeşil
    "opposition": (255, 0, 0),    # 🔴 Kırmızı
    "trine": (0, 0, 255),         # 🔵 Mavi
    "square": (255, 100, 0),      # 🟠 Turuncu
    "sextile": (255, 0, 255)      # 🟣 Mor
}


def angle_diff(a, b):
    diff = abs(a - b) % 360
    return min(diff, 360 - diff)


def find_aspects(planets):
    results = []
    for i, p1 in enumerate(planets):
        for j, p2 in enumerate(planets[i + 1:], i + 1):
            diff = angle_diff(p1["ecliptic_long"], p2["ecliptic_long"])
            for name, target in [("conjunction", 0), ("opposition", 180),
                                 ("trine", 120), ("square", 90), ("sextile", 60)]:
                if abs(diff - target) <= 4:  # 4° orb
                    results.append((p1, p2, name))
    return results


def draw_chart(planets):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(base_dir, "chart_template.png")
        font_path = os.path.join(base_dir, "AstroGadget.ttf")
        charts_dir = os.path.join(base_dir, "charts")
        os.makedirs(charts_dir, exist_ok=True)

        # Görseli yükle
        base_image = Image.open(template_path).convert("RGBA")
        draw = ImageDraw.Draw(base_image, "RGBA")

        center_x, center_y = base_image.size[0] // 2, base_image.size[1] // 2
        radius = min(center_x, center_y) - 60
        inner_radius = radius * 0.85  # %15 içeri

        try:
            font = ImageFont.truetype(font_path, 32)
        except Exception:
            font = ImageFont.load_default()

        # Planet pozisyonlarını hesapla
        coords = {}
        for planet in planets:
            angle_deg = float(planet["ecliptic_long"]) - 90
            angle_rad = math.radians(angle_deg)
            x = center_x + inner_radius * math.cos(angle_rad)
            y = center_y + inner_radius * math.sin(angle_rad)
            coords[planet["name"]] = (x, y)

        # Aspect çizgilerini çiz
        aspects = find_aspects(planets)
        for p1, p2, aspect_type in aspects:
            color = ASPECTS.get(aspect_type, (150, 150, 150))
            x1, y1 = coords[p1["name"]]
            x2, y2 = coords[p2["name"]]
            draw.line((x1, y1, x2, y2), fill=color + (180,), width=2)

        # Gezegen sembollerini çiz
        for planet in planets:
            name = planet["name"]
            if name not in coords:
                continue
            x, y = coords[name]
            symbol = PLANET_SYMBOLS.get(name, name[0])
            draw.text((x - 10, y - 10), symbol, fill=(180, 80, 255), font=font)  # Mor renk

        # Çıktıyı kaydet
        filename = f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        file_path = os.path.join(charts_dir, filename)
        base_image.save(file_path, "PNG")

        chart_url = f"https://madam-dudu-astro-core-1.onrender.com/charts/{filename}"
        print(f"[draw_chart] ✅ Chart created at: {chart_url}")

        return {"chart_url": chart_url}

    except Exception as e:
        print(f"[draw_chart] ❌ Hata: {e}")
        return {"error": str(e)}
