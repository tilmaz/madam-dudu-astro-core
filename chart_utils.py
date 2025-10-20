import math
from PIL import Image, ImageDraw, ImageFont
import datetime
import os

def draw_chart(planets, name, dob, tob, city, country):
    """
    Doğum haritasını çizer, başlık ve alt bilgi alanlarını düzenler.
    """

    # 🟣 Template ve font yolları
    template_path = "chart_template.png"
    astro_font_path = "AstroGadget.ttf"
    normal_font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

    # 🟣 Template yükle
    base_img = Image.open(template_path).convert("RGBA")
    w, h = base_img.size

    # 🟣 Yeni canvas oluştur (üst ve alt boşluk eklenmiş)
    top_pad = 100
    bottom_pad = 160
    new_h = h + top_pad + bottom_pad
    canvas = Image.new("RGBA", (w, new_h), (255, 255, 255, 255))

    # 🟣 Template’i ortala (padding dahil)
    canvas.paste(base_img, (0, top_pad), mask=base_img)

    draw = ImageDraw.Draw(canvas)

    # 🟣 Fontları yükle
    try:
        astro_font = ImageFont.truetype(astro_font_path, 28)
    except:
        astro_font = ImageFont.load_default()

    try:
        normal_font = ImageFont.truetype(normal_font_path, 36)
        small_font = ImageFont.truetype(normal_font_path, 28)
    except:
        normal_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # 🟣 Başlık
    title_text = f"{name}'s Natal Birth Chart"
    tw, th = draw.textbbox((0, 0), title_text, font=normal_font)[2:]
    draw.text(((w - tw) / 2, 20), title_text, fill=(30, 30, 30, 255), font=normal_font)

    # 🟣 Footer bilgisi
    footer1 = f"Born on {dob} at {tob}"
    footer2 = f"{city}, {country}"
    footer3 = "Aspects: 🔴 Opposition  🔵 Trine  🟢 Sextile  ⚪ Conjunction  🟠 Square"

    # Footer yazılarını ortala
    y_footer_start = h + top_pad + 20
    fw1 = draw.textbbox((0, 0), footer1, font=small_font)[2]
    fw2 = draw.textbbox((0, 0), footer2, font=small_font)[2]
    fw3 = draw.textbbox((0, 0), footer3, font=small_font)[2]

    draw.text(((w - fw1) / 2, y_footer_start), footer1, fill=(40, 40, 40, 255), font=small_font)
    draw.text(((w - fw2) / 2, y_footer_start + 35), footer2, fill=(40, 40, 40, 255), font=small_font)
    draw.text(((w - fw3) / 2, y_footer_start + 80), footer3, fill=(70, 70, 70, 255), font=small_font)

    # 🟣 Planet sembolleri
    center_x, center_y = w / 2, (new_h / 2)
    radius = min(w, h) * 0.38  # biraz daha içeri alındı

    for planet in planets:
        angle_deg = planet["ecliptic_long"]
        angle_rad = math.radians(angle_deg - 90)
        px = center_x + radius * math.cos(angle_rad)
        py = center_y + radius * math.sin(angle_rad)

        symbol = planet["name"][0]  # şimdilik sadece ilk harf (örnek)
        draw.text((px - 10, py - 10), symbol, fill=(160, 80, 255, 255), font=astro_font)

    # 🟣 Kaydetme
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"charts/chart_{name.lower()}_{timestamp}.png"

    if not os.path.exists("charts"):
        os.makedirs("charts")

    canvas.save(output_path, format="PNG")
    return {
        "status": "ok",
        "url": f"/{output_path}"
    }
