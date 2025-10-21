import os
import math
import logging
from PIL import Image, ImageDraw, ImageFont

# === Klasör kontrolü (kritik düzeltme) ===
if not os.path.exists("charts"):
    os.makedirs("charts")

def draw_chart(name, dob, tob, city, country, planets):
    logging.info("=== 🌌 DRAW_CHART STARTED ===")
    logging.info(f"Name: {name}, DOB: {dob}, TOB: {tob}, Location: {city}, {country}")

    # === Template yükle ===
    try:
        template_path = "chart_template.png"
        template = Image.open(template_path).convert("RGBA")
        logging.info("✅ Template başarıyla yüklendi.")
    except Exception as e:
        logging.error(f"❌ Template yüklenemedi: {e}")
        raise

    draw = ImageDraw.Draw(template)
    width, height = template.size
    logging.info(f"🖼️ Template boyutu: {width}x{height}")

    # === Font yükleme ===
    try:
        astro_font = ImageFont.truetype("astrogadget.ttf", 42)
        text_font = ImageFont.truetype("arial.ttf", 28)
        logging.info("✅ Fontlar başarıyla yüklendi.")
    except Exception as e:
        logging.error(f"❌ Font yüklenemedi: {e}")
        raise

    # === Başlık (Mor renk, dışta) ===
    title_text = f"{name}'s Natal Chart"
    title_bbox = draw.textbbox((0, 0), title_text, font=text_font)
    title_w = title_bbox[2] - title_bbox[0]
    draw.text(((width - title_w) / 2, 50), title_text, fill=(128, 0, 128), font=text_font)
    logging.info("✅ Başlık çizildi.")

    # === Alt bilgi (Mor renk, tarih ve konum) ===
    import datetime
    try:
        dob_date = datetime.datetime.strptime(dob, "%Y-%m-%d")
        formatted_date = dob_date.strftime("%d %B %Y")
    except Exception:
        formatted_date = dob

    footer_text = f"{formatted_date} @ {tob} / {city}, {country}"
    footer_bbox = draw.textbbox((0, 0), footer_text, font=text_font)
    footer_w = footer_bbox[2] - footer_bbox[0]
    draw.text(((width - footer_w) / 2, height - 100), footer_text, fill=(128, 0, 128), font=text_font)
    logging.info("✅ Alt bilgi çizildi.")

    # === Gezegen sembolleri (Mor renkte, Wheel üzerinde) ===
    center_x, center_y = width // 2, height // 2
    radius = min(center_x, center_y) * 0.75

    for p in planets:
        angle_deg = p["ecliptic_long"]
        angle_rad = math.radians(angle_deg - 90)
        x = center_x + radius * math.cos(angle_rad)
        y = center_y + radius * math.sin(angle_rad)
        draw.text((x, y), "☉", fill=(128, 0, 128), font=astro_font, anchor="mm")
    logging.info(f"✅ {len(planets)} gezegen sembolü çizildi.")

    # === Aspect çizgileri (örnek renkler) ===
    aspect_colors = {
        "Conjunction": (128, 0, 128),
        "Opposition": (255, 0, 0),
        "Trine": (0, 0, 255),
        "Square": (255, 128, 0),
        "Sextile": (0, 255, 0)
    }

    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            diff = abs(planets[i]["ecliptic_long"] - planets[j]["ecliptic_long"]) % 360
            aspect_type = None
            if abs(diff - 0) < 5:
                aspect_type = "Conjunction"
            elif abs(diff - 180) < 5:
                aspect_type = "Opposition"
            elif abs(diff - 120) < 5:
                aspect_type = "Trine"
            elif abs(diff - 90) < 5:
                aspect_type = "Square"
            elif abs(diff - 60) < 5:
                aspect_type = "Sextile"

            if aspect_type:
                color = aspect_colors[aspect_type]
                x1 = center_x + radius * math.cos(math.radians(planets[i]["ecliptic_long"] - 90))
                y1 = center_y + radius * math.sin(math.radians(planets[i]["ecliptic_long"] - 90))
                x2 = center_x + radius * math.cos(math.radians(planets[j]["ecliptic_long"] - 90))
                y2 = center_y + radius * math.sin(math.radians(planets[j]["ecliptic_long"] - 90))
                draw.line((x1, y1, x2, y2), fill=color, width=2)

    logging.info("✅ Aspect çizgileri oluşturuldu.")

    # === Legend (Renk açıklamaları, en altta) ===
    y_legend = height - 50
    x_start = 100
    for label, color in aspect_colors.items():
        draw.rectangle([x_start, y_legend, x_start + 20, y_legend + 20], fill=color)
        draw.text((x_start + 30, y_legend), label, fill=(255, 255, 255), font=text_font)
        x_start += 200
    logging.info("✅ Legend çizildi.")

    # === Kayıt işlemi ===
    filename = f"chart_{name.lower()}_final.png"
    filepath = os.path.join("charts", filename)
    template.save(filepath)
    logging.info(f"✅ Chart başarıyla kaydedildi: {filepath}")
    logging.info("=== ✅ DRAW_CHART TAMAMLANDI ===")

    return filepath
