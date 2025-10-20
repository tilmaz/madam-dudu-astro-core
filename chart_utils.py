import os
import math
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Gezegen sembolleri (Unicode)
PLANET_SYMBOLS = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Mars": "♂",
    "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅", "Neptune": "♆", "Pluto": "♇"
}

ASPECTS = {
    "conjunction": ((0, 255, 0), "Conjunction (0°)"),
    "opposition": ((255, 0, 0), "Opposition (180°)"),
    "trine": ((0, 0, 255), "Trine (120°)"),
    "square": ((255, 165, 0), "Square (90°)"),
    "sextile": ((255, 0, 255), "Sextile (60°)")
}


def angle_diff(a, b):
    diff = abs(a - b) % 360
    return min(diff, 360 - diff)


def find_aspects(planets):
    results = []
    for i, p1 in enumerate(planets):
        for p2 in planets[i + 1:]:
            if p1.get("ecliptic_long") is None or p2.get("ecliptic_long") is None:
                continue
            diff = angle_diff(p1["ecliptic_long"], p2["ecliptic_long"])
            for name, (color, label) in ASPECTS.items():
                angle_val = float(label.split("(")[-1].replace("°)", ""))
                if abs(diff - angle_val) <= 4:
                    results.append((p1, p2, name))
    return results


def get_text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_chart(planets, name="User", dob="", tob="", city="", country=""):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(base_dir, "chart_template.png")
        astro_font_path = os.path.join(base_dir, "AstroGadget.ttf")
        charts_dir = os.path.join(base_dir, "charts")
        os.makedirs(charts_dir, exist_ok=True)

        base_image = Image.open(template_path).convert("RGBA")
        W, H = base_image.size
        draw = ImageDraw.Draw(base_image, "RGBA")
        cx, cy = W // 2, H // 2
        radius = min(cx, cy) - 60
        inner_radius = radius * 0.85

        # Fontlar
        try:
            text_font = ImageFont.truetype("DejaVuSans.ttf", 28)
        except Exception:
            text_font = ImageFont.load_default()

        try:
            astro_font = ImageFont.truetype(astro_font_path, 34)
        except Exception:
            astro_font = ImageFont.load_default()

        title_font = text_font
        info_font = ImageFont.truetype("DejaVuSans.ttf", 22) if text_font != ImageFont.load_default() else text_font

        # Gezegen konumları
        coords = {}
        for p in planets:
            val = p.get("ecliptic_long")
            if val is None:
                continue
            angle_deg = float(val) - 90
            angle_rad = math.radians(angle_deg)
            x = cx + inner_radius * math.cos(angle_rad)
            y = cy + inner_radius * math.sin(angle_rad)
            coords[p["name"]] = (x, y)

        # Aspect çizgileri
        aspects = find_aspects(planets)
        for p1, p2, aspect_type in aspects:
            color, _ = ASPECTS.get(aspect_type, ((180, 180, 180), ""))
            if p1["name"] not in coords or p2["name"] not in coords:
                continue
            x1, y1 = coords[p1["name"]]
            x2, y2 = coords[p2["name"]]
            draw.line((x1, y1, x2, y2), fill=color + (160,), width=2)

        # Gezegen sembolleri (mor)
        for p in planets:
            n = p["name"]
            if n not in coords:
                continue
            x, y = coords[n]
            symbol = PLANET_SYMBOLS.get(n, n[0])
            draw.text((x - 10, y - 10), symbol, fill=(180, 80, 255), font=astro_font)

        # Başlık
        title_text = f"{name}'s Natal Birth Chart"
        tw, th = get_text_size(draw, title_text, title_font)
        draw.text(((W - tw) / 2, 20), title_text, fill=(30, 30, 30), font=title_font)

        # Alt Bilgiler
        info_y = H - 120
        info1 = f"Date of Birth: {dob}   Time: {tob}"
        info2 = f"Place of Birth: {city}, {country}"
        w1, _ = get_text_size(draw, info1, info_font)
        w2, _ = get_text_size(draw, info2, info_font)
        draw.text(((W - w1) / 2, info_y), info1, fill=(30, 30, 30), font=info_font)
        draw.text(((W - w2) / 2, info_y + 30), info2, fill=(30, 30, 30), font=info_font)

        # Aspect açıklamaları
        legend_y = H - 50
        x_offset = 60
        for asp, (color, label) in ASPECTS.items():
            draw.rectangle((x_offset, legend_y, x_offset + 20, legend_y + 10), fill=color + (200,))
            draw.text((x_offset + 30, legend_y - 5), label, fill=(40, 40, 40), font=info_font)
            x_offset += 220

        # Kaydet
        filename = f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        path = os.path.join(charts_dir, filename)
        base_image.save(path, "PNG")

        chart_url = f"https://madam-dudu-astro-core-1.onrender.com/charts/{filename}"
        print(f"[draw_chart] ✅ Chart created: {chart_url}")
        return {"chart_url": chart_url}

    except Exception as e:
        print(f"[draw_chart] ❌ Error: {e}")
        return {"error": str(e)}
