import math
from PIL import Image, ImageDraw, ImageFont
import datetime
import os

def draw_chart(planets, name, dob, tob, city, country):
    """
    Doğum haritasını çizer, başlık, semboller ve alt bilgileri yerleştirir (v3.5 Final Visual + Astro Fix).
    """

    # 📁 Dosya yolları
    template_path = "chart_template.png"
    astro_font_path = "AstroGadget.ttf"
    normal_font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

    # 🎨 Renkler
    MOR = (165, 102, 255, 255)
    SIYAH = (20, 20, 20, 255)
    GRAY = (80, 80, 80, 255)
    WHITE = (255, 255, 255, 255)

    # 🌌 Template yükle
    base_img = Image.open(template_path).convert("RGBA")
    w, h = base_img.size

    # Padding ekle
    top_pad, bottom_pad = 100, 180
    new_h = h + top_pad + bottom_pad
    canvas = Image.new("RGBA", (w, new_h), WHITE)
    canvas.paste(base_img, (0, top_pad), mask=base_img)
    draw = ImageDraw.Draw(canvas)

    # 🔤 Fontlar
    try:
        astro_font = ImageFont.truetype(astro_font_path, 38)
    except:
        astro_font = ImageFont.load_default()

    try:
        title_font = ImageFont.truetype(normal_font_path, 42)
        small_font = ImageFont.truetype(normal_font_path, 26)
        mid_font = ImageFont.truetype(normal_font_path, 30)
    except:
        title_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
        mid_font = ImageFont.load_default()

    # 🟣 Başlık
    title = f"{name}'s Natal Birth Chart"
    tw, th = draw.textbbox((0, 0), title, font=title_font)[2:]
    draw.text(((w - tw) / 2, 25), title, fill=MOR, font=title_font)

    # 🔢 12 Ev numaraları
    center_x, center_y = w / 2, (new_h / 2)
    inner_radius = min(w, h) * 0.19
    for i in range(12):
        angle_deg = i * 30 + 15
        angle_rad = math.radians(angle_deg - 90)
        tx = center_x + inner_radius * math.cos(angle_rad)
        ty = center_y + inner_radius * math.sin(angle_rad)
        num = str(i + 1)
        draw.text((tx - 7, ty - 10), num, fill=SIYAH, font=small_font)

    # 🪐 Gezegen sembolleri
    planet_symbols = {
        "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Mars": "♂",
        "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅", "Neptune": "♆", "Pluto": "♇"
    }

    radius = min(w, h) * 0.33
    for planet in planets:
        if planet["name"] not in planet_symbols:
            continue
        angle_deg = planet["ecliptic_long"]
        angle_rad = math.radians(angle_deg - 90)
        px = center_x + radius * math.cos(angle_rad)
        py = center_y + radius * math.sin(angle_rad)

        sym = planet_symbols[planet["name"]]
        # Bold efekti: iki kez çiz
        draw.text((px - 10, py - 10), sym, fill=(120, 60, 230, 255), font=astro_font)
        draw.text((px - 11, py - 11), sym, fill=MOR, font=astro_font)

    # 📘 Footer Bilgisi
    footer1 = f"Born on {dob} at {tob}"
    footer2 = f"{city}, {country}"
    footer3 = "Aspects:"
    footer4 = "🔴 Opposition   🔵 Trine   🟢 Sextile   ⚪ Conjunction   🟠 Square"

    y_footer = h + top_pad + 20
    fw1 = draw.textbbox((0, 0), footer1, font=mid_font)[2]
    fw2 = draw.textbbox((0, 0), footer2, font=mid_font)[2]
    fw3 = draw.textbbox((0, 0), footer3, font=small_font)[2]
    fw4 = draw.textbbox((0, 0), footer4, font=small_font)[2]

    draw.text(((w - fw1) / 2, y_footer), footer1, fill=SIYAH, font=mid_font)
    draw.text(((w - fw2) / 2, y_footer + 35), footer2, fill=SIYAH, font=mid_font)
    draw.text(((w - fw3) / 2, y_footer + 80), footer3, fill=GRAY, font=small_font)
    draw.text(((w - fw4) / 2, y_footer + 115), footer4, fill=GRAY, font=small_font)

    # 💾 Kaydetme
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"charts/chart_{name.lower()}_{timestamp}.png"
    if not os.path.exists("charts"):
        os.makedirs("charts")
    canvas.save(output_path, format="PNG")

    return {
        "status": "ok",
        "url": f"/{output_path}"
    }
