import os
from math import sin, cos, radians
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont


def draw_chart(name, dob, tob, city, country, planets, template_path="chart_template.png"):
    # Load template
    base = Image.open(template_path).convert("RGBA")
    width, height = base.size
    draw = ImageDraw.Draw(base)

    # Font setup
    font_dir = "/usr/share/fonts/truetype/dejavu/"
    astro_font_path = "AstroGadget.ttf"  # gezegen sembolleri için
    text_font_path = os.path.join(font_dir, "DejaVuSans.ttf")  # metinler için

    # Colors
    purple = (160, 100, 255, 255)
    black = (0, 0, 0, 255)

    # Title
    title_font = ImageFont.truetype(text_font_path, 70)
    title_y = int(height * 0.05)
    title_text = f"{name}'s Natal Chart"
    tw, th = draw.textsize(title_text, font=title_font)
    draw.text(((width - tw) / 2, title_y), title_text, font=title_font, fill=purple)

    # Date and location footer
    footer_font = ImageFont.truetype(text_font_path, 50)
    dob_dt = datetime.strptime(dob, "%Y-%m-%d")
    formatted_date = dob_dt.strftime("%d %B %Y")
    footer_text1 = f"{formatted_date} @{tob}"
    footer_text2 = f"{city}/{country}"
    fw1, fh1 = draw.textsize(footer_text1, font=footer_font)
    fw2, fh2 = draw.textsize(footer_text2, font=footer_font)
    draw.text(((width - fw1) / 2, height * 0.92), footer_text1, font=footer_font, fill=purple)
    draw.text(((width - fw2) / 2, height * 0.96), footer_text2, font=footer_font, fill=purple)

    # Center and radius
    cx, cy = width / 2, height / 2
    outer_radius = min(width, height) * 0.45
    planet_radius = outer_radius * 0.85

    # Load fonts
    planet_font = ImageFont.truetype(astro_font_path, 60)

    # Planet symbols
    planet_symbols = {
        "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Mars": "♂",
        "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅", "Neptune": "♆", "Pluto": "♇"
    }

    # Draw planets
    for planet in planets:
        symbol = planet_symbols.get(planet["name"], "?")
        angle = radians(planet["ecliptic_long"] - 90)
        x = cx + planet_radius * cos(angle)
        y = cy + planet_radius * sin(angle)
        draw.text((x - 20, y - 20), symbol, font=planet_font, fill=purple)

    # Draw aspects
    def draw_aspects(draw, planets):
        for i in range(len(planets)):
            for j in range(i + 1, len(planets)):
                diff = abs(planets[i]["ecliptic_long"] - planets[j]["ecliptic_long"])
                diff = diff if diff <= 180 else 360 - diff
                color = None
                if diff < 5:
                    color = (255, 215, 0, 255)  # Conjunction
                elif abs(diff - 60) < 3:
                    color = (0, 255, 0, 255)  # Sextile
                elif abs(diff - 90) < 3:
                    color = (255, 0, 0, 255)  # Square
                elif abs(diff - 120) < 3:
                    color = (0, 0, 255, 255)  # Trine
                elif abs(diff - 180) < 3:
                    color = (128, 0, 128, 255)  # Opposition
                if color:
                    x1 = cx + planet_radius * cos(radians(planets[i]["ecliptic_long"] - 90))
                    y1 = cy + planet_radius * sin(radians(planets[i]["ecliptic_long"] - 90))
                    x2 = cx + planet_radius * cos(radians(planets[j]["ecliptic_long"] - 90))
                    y2 = cy + planet_radius * sin(radians(planets[j]["ecliptic_long"] - 90))
                    draw.line((x1, y1, x2, y2), fill=color, width=4)

    draw_aspects(draw, planets)

    # Aspect legend
    legend_font = ImageFont.truetype(text_font_path, 35)
    legend_y = height * 0.85
    aspects = [
        ("Conjunction", (255, 215, 0, 255)),
        ("Sextile", (0, 255, 0, 255)),
        ("Square", (255, 0, 0, 255)),
        ("Trine", (0, 0, 255, 255)),
        ("Opposition", (128, 0, 128, 255)),
    ]
    legend_x = width * 0.05
    draw.text((legend_x, legend_y - 40), "Aspects:", font=legend_font, fill=purple)
    offset_y = 0
    for name, color in aspects:
        draw.rectangle([legend_x, legend_y + offset_y, legend_x + 30, legend_y + offset_y + 20], fill=color)
        draw.text((legend_x + 40, legend_y + offset_y - 10), name, font=legend_font, fill=purple)
        offset_y += 35

    # Save file
    output_path = f"chart_{name.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    base.save(output_path)
    return output_path
