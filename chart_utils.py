import os
import math
from PIL import Image, ImageDraw, ImageFont

def draw_chart(name, dob, tob, city, country, planets, houses):
    # --- Dosya yollarını dinamik belirle ---
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_dir, "chart_template.png")
    font_path_astro = os.path.join(base_dir, "AstroGadget.ttf")

    # --- Font yükleme ---
    try:
        astro_font = ImageFont.truetype(font_path_astro, 48)
    except OSError:
        from PIL import ImageFont
        astro_font = ImageFont.load_default()

    try:
        title_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 52)
        info_font = ImageFont.truetype("DejaVuSans.ttf", 36)
    except:
        title_font = ImageFont.load_default()
        info_font = ImageFont.load_default()

    # --- Template aç ---
    base = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(base)
    w, h = base.size

    # --- Başlık ---
    title = f"{name}'s Natal Chart"
    tw, th = draw.textsize(title, font=title_font)
    draw.text(((w - tw) / 2, 30), title, fill=(160, 110, 255), font=title_font)

    # --- Alt Bilgi ---
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    y, m, d = dob.split("-")
    m_name = months[int(m) - 1]
    date_str = f"{int(d)} {m_name} {y} @{tob}"
    loc_str = f"{city}, {country}"

    dw, dh = draw.textsize(date_str, font=info_font)
    lw, lh = draw.textsize(loc_str, font=info_font)

    draw.text(((w - dw) / 2, h - 160), date_str, fill=(160, 110, 255), font=info_font)
    draw.text(((w - lw) / 2, h - 100), loc_str, fill=(160, 110, 255), font=info_font)

    # --- Aspect çizgileri ve gezegen pozisyonları ---
    cx, cy = w / 2, h / 2
    radius = min(w, h) * 0.4

    for planet in planets:
        lon = math.radians(planet["ecliptic_long"])
        px = cx + radius * math.cos(math.pi / 2 - lon)
        py = cy - radius * math.sin(math.pi / 2 - lon)
        symbol = {
            "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀",
            "Mars": "♂", "Jupiter": "♃", "Saturn": "♄",
            "Uranus": "♅", "Neptune": "♆", "Pluto": "♇"
        }.get(planet["name"], planet["name"][0])
        draw.text((px - 15, py - 15), symbol, fill=(160, 110, 255), font=astro_font)

    # --- Aspect legend ---
    legend_y = h - 260
    legend_x = 50
    aspects = [("Conjunction", "yellow"), ("Sextile", "green"),
               ("Square", "red"), ("Trine", "blue"), ("Opposition", "purple")]
    for name, color in aspects:
        draw.line([(legend_x, legend_y + 10), (legend_x + 50, legend_y + 10)], fill=color, width=4)
        draw.text((legend_x + 70, legend_y - 10), name, fill=(160, 110, 255), font=info_font)
        legend_y += 50

    # --- Kaydet ---
    output_filename = f"chart_{name.lower()}_final.png"
    output_path = os.path.join(base_dir, output_filename)
    base.save(output_path)

    return output_path
