import os
from PIL import Image, ImageDraw, ImageFont
from math import sin, cos, radians
from datetime import datetime

def draw_chart(planets, name, dob, tob, city, country):
    try:
        # Dosya yollarını güvenli şekilde oluştur
        base_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(base_dir, "chart_template.png")
        font_path = os.path.join(base_dir, "AstroGadget.ttf")

        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template bulunamadı: {template_path}")
        if not os.path.exists(font_path):
            raise FileNotFoundError(f"Font bulunamadı: {font_path}")

        # Template'i yükle
        base_img = Image.open(template_path).convert("RGBA")
        draw = ImageDraw.Draw(base_img)

        # Renkler
        purple = (170, 130, 255, 255)
        white = (255, 255, 255, 255)

        # Yazı tipleri
        title_font = ImageFont.truetype(font_path, 120)
        text_font = ImageFont.truetype(font_path, 70)

        # Başlık
        title_text = f"{name}'s Natal Chart"
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_w = title_bbox[2] - title_bbox[0]
        title_h = title_bbox[3] - title_bbox[1]
        title_x = (base_img.width - title_w) / 2
        title_y = 150  # üstte boşluk
        draw.text((title_x, title_y), title_text, font=title_font, fill=purple)

        # Alt bilgi (mor renkte)
        footer_text1 = f"{dob} @ {tob}"
        footer_text2 = f"{city}, {country}"

        footer1_bbox = draw.textbbox((0, 0), footer_text1, font=text_font)
        footer1_w = footer1_bbox[2] - footer1_bbox[0]
        footer1_h = footer1_bbox[3] - footer1_bbox[1]

        footer2_bbox = draw.textbbox((0, 0), footer_text2, font=text_font)
        footer2_w = footer2_bbox[2] - footer2_bbox[0]
        footer2_h = footer2_bbox[3] - footer2_bbox[1]

        footer_y = base_img.height - 200  # alta boşluk

        draw.text(
            ((base_img.width - footer1_w) / 2, footer_y - footer1_h),
            footer_text1, font=text_font, fill=purple
        )
        draw.text(
            ((base_img.width - footer2_w) / 2, footer_y + 20),
            footer_text2, font=text_font, fill=purple
        )

        # Gezegen yerleşimleri
        center_x, center_y = base_img.width / 2, base_img.height / 2 + 50
        radius = 800

        astro_font = ImageFont.truetype(font_path, 80)

        for planet in planets:
            angle = radians(planet["ecliptic_long"] - 90)
            x = center_x + radius * cos(angle)
            y = center_y + radius * sin(angle)
            symbol = get_planet_symbol(planet["name"])
            draw.text((x - 25, y - 25), symbol, font=astro_font, fill=white)

        # Kayıt işlemi
        os.makedirs("charts", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        chart_filename = f"chart_{name.lower()}_{timestamp}.png"
        chart_path = os.path.join("charts", chart_filename)
        base_img.save(chart_path, "PNG")

        return {
            "text": f"{name}'s Natal Chart generated successfully.",
            "chart_url": f"/charts/{chart_filename}"
        }

    except Exception as e:
        return {"error": str(e)}


def get_planet_symbol(name):
    symbols = {
        "Sun": "☉",
        "Moon": "☽",
        "Mercury": "☿",
        "Venus": "♀",
        "Mars": "♂",
        "Jupiter": "♃",
        "Saturn": "♄",
        "Uranus": "♅",
        "Neptune": "♆",
        "Pluto": "♇"
    }
    return symbols.get(name, "?")
