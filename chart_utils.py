import os
import math
import logging
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def draw_chart(name, dob, tob, city, country, planets):
    logging.info("🎨 Rendering chart for %s (%s @ %s, %s, %s)", name, dob, tob, city, country)
    logging.info("=== 🌌 DRAW_CHART STARTED ===")

    # Template yükleme
    template_path = os.path.join(os.path.dirname(__file__), "chart_template.png")
    template = Image.open(template_path).convert("RGBA")
    width, height = template.size
    draw = ImageDraw.Draw(template)

    # Font yolları (absolute path)
    astro_font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "AstroGadget.ttf"))
    text_font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "arial.ttf"))

    # Font yükleme (try + fallback)
    try:
        with open(astro_font_path, "rb"):
            astro_font = ImageFont.truetype(astro_font_path, 38)
        text_font = ImageFont.truetype(text_font_path, 28)
        logging.info("✅ Fontlar başarıyla yüklendi.")
    except Exception as e:
        logging.error("❌ Font yüklenemedi (%s). Varsayılan font kullanılıyor.", e)
        astro_font = ImageFont.load_default()
        text_font = ImageFont.load_default()

    # Başlık
    title_text = f"{name}'s Natal Birth Chart"
    draw.text((width / 2, 60), title_text, font=text_font, fill=(180, 140, 255), anchor="mm")
    logging.info("✅ Başlık çizildi.")

    # Tarih formatlama
    months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
    year, month, day = dob.split("-")
    month_name = months[int(month) - 1]
    footer_text = f"{int(day)} {month_name} {year} @ {tob} / {city}, {country}"
    draw.text((width / 2, height - 60), footer_text, font=text_font, fill=(180, 140, 255), anchor="mm")
    logging.info("✅ Alt bilgi çizildi.")

    # Gezegen sembolleri
    planet_symbols = {
        "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Mars": "♂",
        "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅", "Neptune": "♆", "Pluto": "♇"
    }
    cx, cy = width // 2, height // 2 - 40
    radius = 420

    for p in planets:
        lon = math.radians(p["ecliptic_long"])
        x = cx + radius * math.cos(lon)
        y = cy + radius * math.sin(lon)
        draw.text((x, y), planet_symbols.get(p["name"], "?"), font=astro_font, fill=(180, 140, 255), anchor="mm")
    logging.info("✅ %d gezegen sembolü çizildi.", len(planets))

    # Aspect renkleri
    aspect_colors = {
        "conjunction": ((180, 180, 180, 255), "Conjunction"),
        "trine": ((0, 150, 255, 255), "Trine"),
        "square": ((255, 60, 60, 255), "Square"),
        "sextile": ((60, 255, 120, 255), "Sextile"),
        "opposition": ((180, 100, 255, 255), "Opposition"),
    }

    def aspect_color(angle_diff):
        angle = min(abs(angle_diff), 360 - abs(angle_diff))
        if abs(angle - 0) < 8: return aspect_colors["conjunction"][0]
        if abs(angle - 60) < 8: return aspect_colors["sextile"][0]
        if abs(angle - 90) < 8: return aspect_colors["square"][0]
        if abs(angle - 120) < 8: return aspect_colors["trine"][0]
        if abs(angle - 180) < 8: return aspect_colors["opposition"][0]
        return None

    # Aspect çizgileri
    for i, p1 in enumerate(planets):
        for j, p2 in enumerate(planets):
            if i >= j: continue
            diff = (p1["ecliptic_long"] - p2["ecliptic_long"]) % 360
            color = aspect_color(diff)
            if color:
                lon1 = math.radians(p1["ecliptic_long"])
                lon2 = math.radians(p2["ecliptic_long"])
                x1 = cx + radius * 0.8 * math.cos(lon1)
                y1 = cy + radius * 0.8 * math.sin(lon1)
                x2 = cx + radius * 0.8 * math.cos(lon2)
                y2 = cy + radius * 0.8 * math.sin(lon2)
                draw.line((x1, y1, x2, y2), fill=color, width=2)
    logging.info("✅ Aspect çizgileri oluşturuldu.")

    # Legend (alt açıklamalı)
    legend_y = height - 90
    start_x = 120
    spacing = 230
    for idx, (aspect_name, (color, label)) in enumerate(aspect_colors.items()):
        x = start_x + idx * spacing
        draw.rectangle((x, legend_y - 10, x + 25, legend_y + 10), fill=color)
        draw.text((x + 40, legend_y), label, font=text_font, fill=(255, 255, 255), anchor="lm")
    logging.info("✅ Legend açıklamaları çizildi.")

    # Kaydetme
    os.makedirs("charts", exist_ok=True)
    filename = f"charts/chart_{name.lower()}_final.png"
    template.save(filename)
    logging.info("✅ Chart kaydedildi: %s", filename)
    logging.info("=== ✅ DRAW_CHART TAMAMLANDI ===")

    return filename
