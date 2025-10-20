import math
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

def draw_chart(name, dob, tob, city, country, planets, output_path="charts/chart_final.png"):
    print("=== 🌌 DRAW_CHART_V6 STARTED ===")
    print(f"Name: {name}, DOB: {dob}, TOB: {tob}, Location: {city}, {country}")

    # 📄 Template ve Fontlar
    template_path = "chart_template.png"
    astro_font_path = "AstroGadget.ttf"
    text_font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

    img = Image.open(template_path).convert("RGBA")
    W, H = img.size

    draw = ImageDraw.Draw(img)
    astro_font = ImageFont.truetype(astro_font_path, 26)
    text_font = ImageFont.truetype(text_font_path, 28)
    legend_font = ImageFont.truetype(text_font_path, 22)

    # 📅 Tarih formatı
    try:
        date_obj = datetime.strptime(dob, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%d %B %Y")
    except Exception:
        formatted_date = dob

    # 🎨 Renkler
    purple = (150, 100, 255)
    colors = {
        "Conjunction": (255, 215, 0),
        "Sextile": (0, 255, 128),
        "Square": (255, 0, 0),
        "Trine": (0, 128, 255),
        "Opposition": (200, 0, 255)
    }

    # 🪐 Gezegen sembolleri
    planet_symbols = {
        "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Mars": "♂",
        "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅", "Neptune": "♆", "Pluto": "♇"
    }

    cx, cy = W // 2, H // 2 + 40
    r_inner, r_outer = 240, 500

    # 🪐 Gezegen sembollerini çiz
    for p in planets:
        angle = math.radians(p["ecliptic_long"])
        x = cx + r_inner * math.cos(angle)
        y = cy - r_inner * math.sin(angle)
        symbol = planet_symbols.get(p["name"], "?")
        draw.text((x - 10, y - 10), symbol, font=astro_font, fill=purple)

    # 🔗 Aspect çizgileri (örnek ilişkiler)
    pairs = [(0, 5, "Trine"), (1, 6, "Square"), (2, 4, "Opposition"),
             (3, 7, "Sextile"), (8, 9, "Conjunction")]
    for i1, i2, aspect in pairs:
        if i1 < len(planets) and i2 < len(planets):
            p1, p2 = planets[i1], planets[i2]
            a1, a2 = math.radians(p1["ecliptic_long"]), math.radians(p2["ecliptic_long"])
            x1, y1 = cx + r_inner * math.cos(a1), cy - r_inner * math.sin(a1)
            x2, y2 = cx + r_inner * math.cos(a2), cy - r_inner * math.sin(a2)
            draw.line((x1, y1, x2, y2), fill=colors[aspect], width=2)

    # 🟣 Başlık
    title = f"{name}'s Natal Birth Chart"
    draw.text((W / 2, 60), title, fill=purple, font=text_font, anchor="mm")

    # 🟣 Legend (Aspect renk açıklamaları)
    legend_y = H - 180
    draw.text((W / 2, legend_y - 40), "Aspects:", fill=purple, font=legend_font, anchor="mm")
    lx = W / 2 - 200
    for aspect, color in colors.items():
        draw.rectangle([lx, legend_y, lx + 25, legend_y + 25], fill=color)
        draw.text((lx + 40, legend_y + 10), aspect, fill=purple, font=legend_font, anchor="lm")
        lx += 130

    # 📍 Alt bilgi (Tarih ve Lokasyon)
    bottom_text = f"{formatted_date} @ {tob}"
    location_text = f"{city}, {country}"

    draw.text((W / 2, H - 90), bottom_text, fill=purple, font=text_font, anchor="mm")
    draw.text((W / 2, H - 50), location_text, fill=purple, font=text_font, anchor="mm")

    # 💾 Kaydet
    os.makedirs("charts", exist_ok=True)
    img.save(output_path, "PNG")
    print(f"✅ Chart başarıyla kaydedildi: {output_path}")
    print("=== ✅ DRAW_CHART_V6 TAMAMLANDI ===")
    return output_path
