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

# Aspect renkleri ve anlamları
ASPECTS = {
    "conjunction": ((0, 255, 0), "Conjunction (0°)"),
    "opposition": ((255, 0, 0), "Opposition (180°)"),
    "trine": ((0, 0, 255), "Trine (120°)"),
    "square": ((255, 100, 0), "Square (90°)"),
    "sextile": ((255, 0, 255), "Sextile (60°)")
}


def angle_diff(a, b):
    diff = abs(a - b) % 360
    return min(diff, 360 - diff)


def find_aspects(planets):
    results = []
    for i, p1 in enumerate(planets):
        for j, p2 in enumerate(planets[i + 1:], i + 1):
            diff = angle_diff(p1["ecliptic_long"], p2["ecliptic_long"])
            for name, (color, label) in ASPECTS.items():
                if abs(diff - float(label.split("(")[-1].replace("°)", ""))) <= 4:
                    results.append((p1, p2, name))
    return results


def draw_chart(planets, name="User", dob="", tob="", city="", country=""):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(base_dir, "chart_template.png")
        font_path = os.path.join(base_dir, "AstroGadget.ttf")
        charts_dir = os.path.join(base_dir, "charts")
        os.makedirs(charts_dir, exist_ok=True)

        base_image = Image.open(template_path).convert("RGBA")
        W, H = base_image.size
        draw = ImageDraw.Draw(base_image, "RGBA")

        center_x, center_y = W // 2, H // 2
        radius = min(center_x, center_y) - 60
        inner_radius = radius * 0.85

        try:
            font = ImageFont.truetype(font_path, 32)
            info_font = ImageFont.truetype(font_path, 22)
        except Exception:
            font = ImageFont.load_default()
            info_font = ImageFont.load_default()

        # Pozisyonları hesapla
        coords = {}
        for planet in planets:
            angle_deg = float(planet["ecliptic_long"]) - 90
            angle_rad = math.radians(angle_deg)
            x = center_x + inner_radius * math.cos(angle_rad)
            y = center_y + inner_radius * math.sin(angle_rad)
            coords[planet["name"]] = (x, y)

        # Aspect çizgileri
        aspects = find_aspects(planets)
        for p1, p2, aspect_type in aspects:
            color, _ = ASPECTS.get(aspect_type, ((180, 180, 180), ""))
            x1, y1 = coords[p1["name"]]
            x2, y2 = coords[p2["name"]]
            draw.line((x1, y1, x2, y2), fill=color + (160,), width=2)

        # Gezegen sembolleri
        for planet in planets:
            name_p = planet["name"]
            if name_p not in coords:
                continue
            x, y = coords[name_p]
            symbol = PLANET_SYMBOLS.get(name_p, name_p[0])
            draw.text((x - 10, y - 10), symbol, fill=(180, 80, 255), font=font)

        # Başlık
        title_text = f"{name}'s Natal Birth Chart"
        title_font = ImageFont.truetype(font_path, 36)
        tw, th = draw.textsize(title_text, font=title_font)
        draw.text(((W - tw) / 2, 20), title_text, fill=(50, 50, 50), font=title_font)

        # Bilgi bölümü (alt)
        info_y = H - 100
        info_text1 = f"Date of Birth: {dob}    Time: {tob}"
        info_text2 = f"Place of Birth: {city}, {country}"
        draw.text(((W - draw.textlength(info_text1, font=info_font)) / 2, info_y), info_text1, fill=(30, 30, 30), font=info_font)
        draw.text(((W - draw.textlength(info_text2, font=info_font)) / 2, info_y + 30), info_text2, fill=(30, 30, 30), font=info_font)

        # Aspect efsanesi
        legend_y = H - 50
        x_offset = 60
        for aspect_name, (color, label) in ASPECTS.items():
            draw.rectangle((x_offset, legend_y, x_offset + 20, legend_y + 10), fill=color + (200,))
            draw.text((x_offset + 30, legend_y - 5), label, fill=(50, 50, 50), font=info_font)
            x_offset += 220

        # Çıktı kaydet
        filename = f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        file_path = os.path.join(charts_dir, filename)
        base_image.save(file_path, "PNG")

        chart_url = f"https://madam-dudu-astro-core-1.onrender.com/charts/{filename}"
        print(f"[draw_chart] ✅ Chart created at: {chart_url}")

        return {"chart_url": chart_url}

    except Exception as e:
        print(f"[draw_chart] ❌ Hata: {e}")
        return {"error": str(e)}
