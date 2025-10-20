import math
import logging
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def draw_chart(name, dob, tob, city, country, planets):
    logging.info("=== 🌌 DRAW_CHART STARTED ===")
    logging.info(f"Name: {name}, DOB: {dob}, TOB: {tob}, Location: {city}, {country}")

    # Template ve fontlar
    try:
        template = Image.open("chart_template.png").convert("RGBA")
        logging.info("✅ Template başarıyla yüklendi.")
    except Exception as e:
        logging.error(f"❌ Template yüklenemedi: {e}")
        raise

    try:
        astro_font = ImageFont.truetype("AstroGadget.ttf", 36)
        text_font = ImageFont.truetype("arial.ttf", 30)
        logging.info("✅ Fontlar başarıyla yüklendi.")
    except Exception as e:
        logging.error(f"❌ Font yüklenemedi: {e}")
        raise

    draw = ImageDraw.Draw(template)
    w, h = template.size
    cx, cy = w // 2, h // 2
    radius = min(cx, cy) * 0.85

    # Renk paleti
    purple = (164, 124, 255)
    aspect_colors = {
        "Conjunction": (255, 215, 0),   # sarı
        "Sextile": (0, 255, 128),       # yeşil
        "Square": (255, 64, 64),        # kırmızı
        "Trine": (64, 128, 255),        # mavi
        "Opposition": (200, 64, 255)    # mor
    }

    # Başlık
    title = f"{name}'s Natal Birth Chart"
    draw.text((cx, 60), title, font=text_font, fill=purple, anchor="mm")
    logging.info("✅ Başlık çizildi.")

    # Alt Bilgi
    date_text = f"{dob.replace('-', ' ')} @{tob}"
    location_text = f"{city}, {country}"
    draw.text((cx, h - 100), date_text, font=text_font, fill=purple, anchor="mm")
    draw.text((cx, h - 60), location_text, font=text_font, fill=purple, anchor="mm")
    logging.info("✅ Alt bilgi çizildi.")

    # Gezegen konumlarını çiz
    planet_positions = []
    for p in planets:
        angle = math.radians(p["ecliptic_long"])
        x = cx + radius * math.cos(angle - math.pi / 2)
        y = cy + radius * math.sin(angle - math.pi / 2)
        planet_positions.append((x, y))
        draw.text((x, y), "•", font=astro_font, fill=purple, anchor="mm")

    logging.info(f"✅ {len(planets)} gezegen sembolü çizildi.")

    # Aspect çizgileri (yaklaşık tolerans ile)
    tolerance = 6
    aspect_angles = {
        "Conjunction": 0,
        "Sextile": 60,
        "Square": 90,
        "Trine": 120,
        "Opposition": 180
    }

    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            lon1 = planets[i]["ecliptic_long"]
            lon2 = planets[j]["ecliptic_long"]
            diff = abs(lon1 - lon2)
            diff = diff if diff <= 180 else 360 - diff

            for aspect, base_angle in aspect_angles.items():
                if abs(diff - base_angle) <= tolerance:
                    draw.line([planet_positions[i], planet_positions[j]],
                              fill=aspect_colors[aspect], width=3)
                    break

    logging.info("✅ Aspect çizgileri oluşturuldu.")

    # Legend açıklaması
    legend_y = h - 30
    x_start = cx - 220
    for idx, (aspect, color) in enumerate(aspect_colors.items()):
        x = x_start + idx * 130
        draw.line((x, legend_y - 10, x + 30, legend_y - 10), fill=color, width=4)
        draw.text((x + 60, legend_y - 12), aspect, font=text_font, fill=purple, anchor="lm")

    logging.info("✅ Legend çizildi.")

    # Kaydet
    filename = f"charts/chart_{name.lower()}_final.png"
    template.save(filename)
    logging.info(f"✅ Chart başarıyla kaydedildi: {filename}")
    logging.info("=== ✅ DRAW_CHART TAMAMLANDI ===")

    return filename
