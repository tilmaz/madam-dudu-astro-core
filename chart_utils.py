import os
import math
import datetime
from PIL import Image, ImageDraw, ImageFont
import logging

# 🔹 Log ayarları
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def draw_chart(planets, name, dob, tob, city, country):
    """
    Debug log’lu natal chart çizimi.
    Her adım Render loglarına yazılır.
    """

    logging.info("=== 🌌 DRAW_CHART STARTED ===")
    logging.info(f"Name: {name}, DOB: {dob}, TOB: {tob}, Location: {city}, {country}")

    # 🟣 Template dosyasını yükle
    template_path = "chart_template.png"
    if not os.path.exists(template_path):
        logging.error(f"❌ Template bulunamadı: {template_path}")
        return {"error": f"Template not found: {template_path}"}

    try:
        base = Image.open(template_path).convert("RGBA")
        logging.info("✅ Template başarıyla yüklendi.")
    except Exception as e:
        logging.exception("❌ Template yükleme hatası:")
        return {"error": f"Template load error: {str(e)}"}

    draw = ImageDraw.Draw(base)

    # 🟣 Font yükleme (AstroGadget + Yazı fontu)
    astro_font_path = "AstroGadget.ttf"
    text_font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

    try:
        astro_font = ImageFont.truetype(astro_font_path, 28)
        logging.info("✅ Astro font yüklendi.")
    except Exception as e:
        logging.warning(f"⚠️ Astro font yüklenemedi ({astro_font_path}): {str(e)}")
        astro_font = ImageFont.load_default()

    try:
        text_font = ImageFont.truetype(text_font_path, 28)
        logging.info("✅ Text font yüklendi.")
    except Exception as e:
        logging.warning(f"⚠️ Text font yüklenemedi ({text_font_path}): {str(e)}")
        text_font = ImageFont.load_default()

    # 🟣 Görsel boyut bilgisi
    w, h = base.size
    center = (w / 2, h / 2)
    logging.info(f"🖼️ Template boyutu: {w}x{h}")

    # 🟣 Başlık (Mor renkte)
    title = f"{name}'s Natal Birth Chart"
    title_color = (140, 80, 255)
    title_y = 60
    draw.text((center[0] - len(title) * 7, title_y), title, fill=title_color, font=text_font)
    logging.info("✅ Başlık çizildi.")

    # 🟣 Alt bilgi: tarih, saat, şehir
    bottom_text_1 = f"{dob} @ {tob}"
    bottom_text_2 = f"{city}, {country}"
    bottom_color = (140, 80, 255)

    draw.text((center[0] - len(bottom_text_1) * 7, h - 140), bottom_text_1, fill=bottom_color, font=text_font)
    draw.text((center[0] - len(bottom_text_2) * 7, h - 100), bottom_text_2, fill=bottom_color, font=text_font)
    logging.info("✅ Alt bilgi çizildi.")

    # 🟣 Gezegen yerleşimleri (örnek noktalar)
    radius = min(w, h) * 0.35
    planet_positions = []
    for planet in planets:
        angle_deg = planet["ecliptic_long"]
        angle_rad = math.radians(angle_deg)
        x = center[0] + radius * math.cos(math.radians(90 - angle_deg))
        y = center[1] - radius * math.sin(math.radians(90 - angle_deg))
        planet_positions.append((x, y))
        draw.ellipse((x - 8, y - 8, x + 8, y + 8), fill=(180, 0, 255, 255))
        draw.text((x + 10, y - 10), planet["name"][0], fill="white", font=astro_font)

    logging.info(f"✅ {len(planet_positions)} gezegen çizildi.")

    # 🟣 Aspect çizgileri (örnek)
    for i in range(len(planet_positions)):
        for j in range(i + 1, len(planet_positions)):
            dx = planets[i]["ecliptic_long"] - planets[j]["ecliptic_long"]
            if abs(dx) in [60, 90, 120, 180]:
                color = (255, 0, 0, 150) if abs(dx) == 180 else (0, 255, 255, 120)
                draw.line([planet_positions[i], planet_positions[j]], fill=color, width=2)
    logging.info("✅ Aspect çizgileri oluşturuldu.")

    # 🟣 Çizgi renk açıklaması (legend)
    legend_y = h - 60
    legend_text = "Aspects: 🔴 Opposition | 🔵 Trine | 🟢 Sextile | ⚪ Conjunction | 🟣 Square"
    draw.text((center[0] - len(legend_text) * 7, legend_y), legend_text, fill=(255, 255, 255), font=text_font)
    logging.info("✅ Legend çizildi.")

    # 🟣 Görseli kaydet
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"chart_{name.lower()}_{timestamp}.png"
    output_dir = "charts"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)

    try:
        base.save(output_path)
        logging.info(f"✅ Chart başarıyla kaydedildi: {output_path}")
    except Exception as e:
        logging.exception("❌ Görsel kaydetme hatası:")
        return {"error": f"Save error: {str(e)}"}

    logging.info("=== ✅ DRAW_CHART TAMAMLANDI ===")

    return {
        "chart_url": f"/charts/{output_filename}",
        "message": "Chart successfully generated with debug logs."
    }
