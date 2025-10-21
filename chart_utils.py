import os
import math
import logging
from PIL import Image, ImageDraw, ImageFont

# Log formatı
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def draw_chart(name, dob, tob, city, country, planets):
    logging.info(f"🎨 Rendering chart for {name} ({dob} @ {tob}, {city}, {country})")
    logging.info("=== 🌌 DRAW_CHART STARTED ===")

    # --- TEMPLATE YÜKLE ---
    template_path = os.path.join(os.path.dirname(__file__), "chart_template.png")
    template = Image.open(template_path).convert("RGBA")
    width, height = template.size
    draw = ImageDraw.Draw(template)
    logging.info("✅ Template başarıyla yüklendi. 🖼️ Boyut: %dx%d", width, height)

    # --- FONTLAR ---
    astro_font_path = os.path.join(os.path.dirname(__file__), "AstroGadget.ttf")
    text_font_path = os.path.join(os.path.dirname(__file__), "arial.ttf")

    try:
        # AstroGadget özel sembol fontu — Render’da kutu çıkmasını engeller
        astro_font = ImageFont.truetype(astro_font_path, 42, layout_engine=ImageFont.LAYOUT_BASIC)
        text_font = ImageFont.truetype(text_font_path, 26)
        logging.info("✅ Fontlar başarıyla yüklendi (LAYOUT_BASIC ile).")
    except Exception as e:
        logging.error(f"❌ Font yüklenemedi ({e}) — varsayılan fontlar devreye alındı.")
        astro_font = ImageFont.load_default()
        text_font = ImageFont.load_default()

    # --- BAŞLIK ---
    title_text = f"{name}'s Natal Birth Chart"
    draw.text((width / 2, 60), title_text, font=text_font, fill=(180, 140, 255), anchor="mm")
    logging.info("✅ Başlık çizildi.")

    # --- ALT TARİH BİLGİSİ ---
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    year, month, day = dob.split("-")
    month_name = months[int(month) - 1]
    footer_text = f"{int(day)} {month_name} {year} @ {tob} / {city}, {country}"

    draw.text(
        (width / 2, height - 65),
        footer_text,
        font=text_font,
        fill=(180, 140, 255),
        anchor="mm",
    )
    logging.info("✅ Alt bilgi çizildi.")

    # --- GEZEGEN SEMBOLLERİ ---
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
        symbol = planet_symbols.get(p["name"], "?")
        draw.text((x, y), symbol, font=astro_font, fill=(180, 140, 255), anchor="mm")
    logging.info("✅ %d gezegen sembolü çizildi.", len(planets))

    # --- ASPECT ÇİZGİLERİ ---
    aspect_colors = {
        "conjunction": ((180, 180, 180, 255), "Conjunction"),
        "sextile": ((60, 255, 120, 255), "Sextile"),
        "square": ((255, 60, 60, 255), "Square"),
        "trine": ((0, 150, 255, 255), "Trine"),
        "opposition": ((180, 100, 255, 255), "Opposition"),
    }

    def get_aspect_color(angle_diff):
        angle = min(abs(angle_diff), 360 - abs(angle_diff))
        if abs(angle - 0) < 8: return aspect_colors["conjunction"][0]
        if abs(angle - 60) < 8: return aspect_colors["sextile"][0]
        if abs(angle - 90) < 8: return aspect_colors["square"][0]
        if abs(angle - 120) < 8: return aspect_colors["trine"][0]
        if abs(angle - 180) < 8: return aspect_colors["opposition"][0]
        return None

    for i, p1 in enumerate(planets):
        for j, p2 in enumerate(planets):
            if i >= j:
                continue
            diff = (p1["ecliptic_long"] - p2["ecliptic_long"]) % 360
            color = get_aspect_color(diff)
            if color:
                lon1 = math.radians(p1["ecliptic_long"])
                lon2 = math.radians(p2["ecliptic_long"])
                x1 = cx + radius * 0.8 * math.cos(lon1)
                y1 = cy + radius * 0.8 * math.sin(lon1)
                x2 = cx + radius * 0.8 * math.cos(lon2)
                y2 = cy + radius * 0.8 * math.sin(lon2)
                draw.line((x1, y1, x2, y2), fill=color, width=2)
    logging.info("✅ Aspect çizgileri oluşturuldu.")

    # --- LEGEND (RENGİN ALTINDA AÇIKLAMALAR) ---
    legend_y = height - 35
    start_x = 100
    spacing = 220

    for idx, (aspect_name, (color, label)) in enumerate(aspect_colors.items()):
        x = start_x + idx * spacing
        draw.rectangle((x, legend_y - 12, x + 25, legend_y + 12), fill=color)
        draw.text((x + 40, legend_y), label, font=text_font, fill=(255, 255, 255), anchor="lm")

    logging.info("✅ Aspect açıklamaları alt hizalı olarak çizildi.")

    # --- KAYDETME ---
    os.makedirs("charts", exist_ok=True)
    filename = f"charts/chart_{name.lower()}_final.png"
    template.save(filename)
    logging.info(f"✅ Chart başarıyla kaydedildi: {filename}")
    logging.info("=== ✅ DRAW_CHART TAMAMLANDI ===")

    return filename
