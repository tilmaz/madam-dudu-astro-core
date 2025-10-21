# chart_utils.py
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import os
import math
import logging

# --- LOG ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# --- KANVAS SABİTLERİ ---
CANVAS_W = 1800
CANVAS_H = 1800
MARGIN   = 80

def _load_font(preferred_path: str | None, size: int):
    """Güvenli font yükleyici (fallback: DejaVuSans -> Pillow default)."""
    try:
        if preferred_path and os.path.exists(preferred_path):
            return ImageFont.truetype(preferred_path, size)
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()

def draw_chart(
    planets: list[dict],
    name: str,
    dob: str,
    tob: str,
    city: str,
    country: str,
) -> BytesIO:
    """
    Basit placeholder harita. Çıkış: PNG içeren BytesIO.
    """
    # --- ARKA PLAN ---
    bg = Image.new("RGB", (CANVAS_W, CANVAS_H), (14, 16, 20))
    draw = ImageDraw.Draw(bg)

    # --- FONTLAR ---
    font_path  = os.getenv("FONT_PATH")
    title_font = _load_font(font_path, 72)
    meta_font  = _load_font(font_path, 40)
    small_font = _load_font(font_path, 32)

    # --- BAŞLIK & METADATA ---
    draw.text((MARGIN, MARGIN), f"ASTRO CHART — {name}", fill=(230,235,240), font=title_font)
    meta = f"Date/Time (local): {dob} @ {tob} | Location: {city}, {country}"
    draw.text((MARGIN, MARGIN + 110), meta, fill=(200,205,210), font=meta_font)

    # --- DIŞ ÇERÇEVE + ANA ÇEMBER ---
    draw.rectangle([MARGIN, MARGIN, CANVAS_W - MARGIN, CANVAS_H - MARGIN], outline=(70,75,85), width=3)
    cx, cy = CANVAS_W // 2, CANVAS_H // 2
    R = min(CANVAS_W, CANVAS_H) // 2 - 2 * MARGIN
    draw.ellipse([cx - R, cy - R, cx + R, cy + R], outline=(120,125,135), width=4)

    # --- GEZEGEN ETİKETLERİ (placeholder: ecliptic_long varsa onu kullan) ---
    ring_r = int(R * 0.85)
    planets = planets or []
    for i, p in enumerate(planets):
        angle_deg = p.get("ecliptic_long", (i / max(1, len(planets))) * 360.0)
        rad = math.radians(angle_deg)
        x = cx + ring_r * 0.95 * math.cos(rad)
        y = cy + ring_r * 0.95 * math.sin(rad)
        draw.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(220,220,220))
        draw.text((x + 10, y - 10), p.get("name", f"P{i+1}"), fill=(220,220,220), font=small_font)

    # --- LEGEND (en altta, %50 küçük) ---
    legend = [
        ("Conjunction", "#FFD400"),
        ("Sextile",     "#1DB954"),
        ("Square",      "#E63946"),
        ("Trine",       "#1E88E5"),
        ("Opposition",  "#7B1FA2"),
    ]
    # %50 küçült
    legend_font_size = max(12, int(getattr(small_font, "size", 32) * 0.5))
    legend_font = _load_font(font_path, legend_font_size)

    yL = CANVAS_H - 50
    xL = MARGIN
    spacing = 180
    for i, (label, col) in enumerate(legend):
        lx = xL + i * spacing
        # renk kutusu
        draw.rectangle([lx, yL + 8, lx + 18, yL + 18], fill=col)
        # etiket
        draw.text((lx + 26, yL + 2), label, fill=col, font=legend_font)

    logging.info("✅ Legend en altta ve %50 küçük olarak çizildi.")

    # --- PNG/BytesIO ÇIKIŞ ---
    buf = BytesIO()
    bg.save(buf, format="PNG")
    buf.seek(0)
    return buf
