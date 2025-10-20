import os
import math
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# 🪐 Gezegen sembolleri
PLANET_SYMBOLS = {
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

# 🔵 Aspect açıları ve renkleri
ASPECTS = {
    "Conjunction": {"angle": 0, "color": (255, 255, 255)},   # beyaz
    "Opposition": {"angle": 180, "color": (255, 0, 0)},      # kırmızı
    "Trine": {"angle": 120, "color": (0, 128, 255)},         # mavi
    "Square": {"angle": 90, "color": (255, 165, 0)},         # turuncu
    "Sextile": {"angle": 60, "color": (255, 0, 255)}         # mor
}


def draw_chart(planets, name, dob, tob, city, country):
    """Doğum haritası görselini oluşturur ve kaydeder."""

    # 🖼️ Görsel ayarları
    width, height = 1000, 1000
    center = (width // 2, height // 2)
    radius = 400

    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    # 🟠 Ana çember
    draw.ellipse(
        (center[0] - radius, center[1] - radius,
         center[0] + radius, center[1] + radius),
        outline="black", width=3
    )

    # 🔵 İç çember (ev sınırı)
    draw.ellipse(
        (center[0] - radius // 3, center[1] - radius // 3,
         center[0] + radius // 3, center[1] + radius // 3),
        outline="gray", width=2
    )

    # ⚪ 12 burç çizgisi
    for i in range(12):
        angle = math.radians(i * 30)
        x = center[0] + radius * math.cos(angle)
        y = center[1] - radius * math.sin(angle)
        draw.line((center[0], center[1], x, y), fill="gray", width=1)

    # ✳️ Gezegenleri yerleştir
    planet_font = ImageFont.load_default()
    planet_radius = radius * 0.85  # %15 içeri
    planet_positions = {}

    for p in planets:
        if p.get("ecliptic_long") is None:
            continue

        angle = math.radians(360 - p["ecliptic_long"])
        x = center[0] + planet_radius * math.cos(angle)
        y = center[1] - planet_radius * math.sin(angle)
        planet_positions[p["name"]] = (x, y)

        symbol = PLANET_SYMBOLS.get(p["name"], "?")
        bbox = draw.textbbox((0, 0), symbol, font=planet_font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((x - w / 2, y - h / 2), symbol, fill=(138, 43, 226), font=planet_font)

    # 🔺 Aspect çizgileri
    planet_names = list(planet_positions.keys())
    for i in range(len(planet_names)):
        for j in range(i + 1, len(planet_names)):
            p1, p2 = planet_names[i], planet_names[j]
            a1 = next((pl["ecliptic_long"] for pl in planets if pl["name"] == p1), None)
            a2 = next((pl["ecliptic_long"] for pl in planets if pl["name"] == p2), None)
            if a1 is None or a2 is None:
                continue
            diff = abs(a1 - a2)
            diff = min(diff, 360 - diff)
            for asp, info in ASPECTS.items():
                if abs(diff - info["angle"]) < 4:
                    draw.line([planet_positions[p1], planet_positions[p2]], fill=info["color"], width=2)
                    break

    # 🧭 Başlık
    title_font = ImageFont.load_default()
    title_text = f"{name}'s Natal Birth Chart"
    bbox = draw.textbbox((0, 0), title_text, font=title_font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((center[0] - tw / 2, 50), title_text, fill="black", font=title_font)

    # 📅 Alt Bilgi
    info_font = ImageFont.load_default()
    info_y = height - 80
    draw.text((80, info_y), f"Date of Birth: {dob}  Time: {tob}", fill="black", font=info_font)
    draw.text((80, info_y + 20), f"Place of Birth: {city}, {country}", fill="black", font=info_font)

    # 🌈 Aspect Legend
    legend_y = height - 50
    x_pos = 80
    for asp, data in ASPECTS.items():
        draw.rectangle([x_pos, legend_y, x_pos + 15, legend_y + 15], fill=data["color"])
        draw.text((x_pos + 25, legend_y), asp, fill="black", font=info_font)
        x_pos += 110

    # 💾 Görseli kaydet
    os.makedirs("charts", exist_ok=True)
    filename = f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    output_path = os.path.join("charts", filename)
    img.save(output_path, "PNG")

    # 🌐 URL döndür
    return {"chart_url": f"https://madam-dudu-astro-core-1.onrender.com/charts/{filename}"}
