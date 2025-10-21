# chart_utils.py
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import logging
import os
from datetime import datetime

# --- LOG AYARLARI (isteğe bağlı) ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# --- KANVAS AYARLARI ---
CANVAS_W = 1800
CANVAS_H = 1800
MARGIN = 80

# --- FONT YÜKLEME (fallback güvenli) ---
# Linux tabanlı Render ortamında genelde DejaVuSans bulunur. Bulunamazsa Pillow'un default'una düşer.
def _load_font(preferred_path: str | None, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        if preferred_path and os.path.exists(preferred_path):
            return ImageFont.truetype(preferred_path, size)
        # Yaygın yedek
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()

# Proje genelinde çağrılacak ana fonksiyon
def draw_chart(
    planets: list[dict],
    name: str,
    dob: str,
    tob: str,
    city: str,
    country: str,
) -> BytesIO:
    """
    Basit bir placeholder chart çizimi. Harita algoritmanız hazır olana kadar
    en azından servis sorunsuz çalışsın diye temel görsel üretir.

    Dönen değer: PNG verisi içeren BytesIO
    """
    # --- ARKA PLAN ---
    bg = Image.new("RGB", (CANVAS_W, CANVAS_H), (14, 16, 20))  # koyu gri/mavi
    draw = ImageDraw.Draw(bg)

    # --- FONTLAR ---
    # İsterseniz özel font yolunu env ile verin: FONT_PATH=/opt/render/project/src/assets/MyFont.ttf
    font_path = os.getenv("FONT_PATH")
    title_font = _load_font(font_path, 72)
    meta_font = _load_font(font_path, 40)
    small_font = _load_font(font_path, 32)

    # --- BAŞLIK & METADATA ---
    title = f"ASTRO CHART — {name}"
    draw.text((MARGIN, MARGIN), title, fill=(230, 235, 240), font=title_font)

    # Tarih/saat/konum satırı
    meta_y = MARGIN + 110
    meta = f"Date/Time (local): {dob} @ {tob} | Location: {city}, {country}"
    draw.text((MARGIN, meta_y), meta, fill=(200, 205, 210), font=meta_font)

    # Basit sınır çerçevesi
    draw.rectangle(
        [MARGIN, MARGIN, CANVAS_W - MARGIN, CANVAS_H - MARGIN],
        outline=(70, 75, 85),
        width=3,
    )

    # --- GÖSTERİMLİ YER TUTUCU DAİRE (çember) ---
    # Asıl harita çiziminiz burada dönecek; şu an placeholder.
    cx, cy = CANVAS_W // 2, CANVAS_H // 2
    R = min(CANVAS_W, CANVAS_H) // 2 - 2 * MARGIN
    draw.ellipse([cx - R, cy - R, cx + R, cy + R], outline=(120, 125, 135), width=4)

    # Gezegen isimlerini kabaca yerleştir (placeholder)
    # planets: [{'name': 'Sun', 'ecliptic_long': 123.45}, ...]
    ring_r = int(R * 0.85)
    if planets:
        for i, p in enumerate(planets):
            # Basit bir dağılım (gerçek ecliptik uzunluklarına göre yerleştirmeyi sonra uygularsınız)
            angle_deg = (i / max(1, len(planets))) * 360.0
            # Eğer gerçek açı varsa onu kullan
            angle_deg = p.get("ecliptic_long", angle_deg)
            angle_rad = angle_deg * 3.1415926535 / 180.0
            x = cx + ring_r * 0.95 * (float(__import__("math").cos(angle_rad)))
            y = cy + ring_r * 0.95 * (float(__import__("math").sin(angle_rad)))
            label = p.get("name", f"P{i+1}")
            draw.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(220, 220, 220))
            draw.text((x + 10, y - 10), label, fill=(220, 220, 220), font=small_font)

    # --- LEGEND (ASPECT AÇIKLAMALARI — EN ALTA ve %50 KÜÇÜK) ---
    legend = [
        ("Conjunction", "#FFD400"),
        ("Sextile", "#1DB954"),
        ("Square", "#E63946"),
        ("Trine", "#1E88E5"),
        ("Opposition", "#7B1FA2"),
    ]

    # Yazı boyutunu %50 küçült
    try:
        legend_font_size = max(12, int((small_font.size if hasattr(small_font, "size") else 32) * 0.5))
        legend_font = _load_font(font_path, legend_font_size)
    except Exception:
        legend_font = ImageFont.load_default()

    # Sayfanın en alt şeridine hizala
    yL = CANVAS_H - 50
    xL = MARGIN
    spacing = 180

    for i, (label, col) in enumerate(legend):
        lx = xL + i * spacing
        # Küçük renk kutu
