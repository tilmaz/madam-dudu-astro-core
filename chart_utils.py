from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime
import math, os, logging

# Renkler ve sabitler
PURPLE = "#800080"
ASPECTS = {
    0:   ("#FFD400", 8),   # Conjunction
    60:  ("#1DB954", 8),   # Sextile
    90:  ("#E63946", 8),   # Square
    120: ("#1E88E5", 8),   # Trine
    180: ("#7B1FA2", 8),   # Opposition
}

PLANET_SYMBOLS = {
    "Sun": "a", "Moon": "b", "Mercury": "c", "Venus": "d", "Mars": "e",
    "Jupiter": "f", "Saturn": "g", "Uranus": "h", "Neptune": "i", "Pluto": "j"
}

def _r(x, n=3): return round(float(x), n)

def _angle_to_xy(deg, radius, cx, cy):
    a = math.radians(90 - (deg % 360))
    x = cx + radius * math.cos(a)
    y = cy - radius * math.sin(a)
    return (_r(x), _r(y))

def _clamp(pt, cx, cy, radius):
    vx, vy = pt[0] - cx, pt[1] - cy
    d = math.hypot(vx, vy)
    if d == 0: return (cx, cy)
    k = radius / d
    return (_r(cx + vx * k), _r(cy + vy * k))


def draw_chart(planets, name=None, dob=None, tob=None, city=None, country=None):
    """
    planets: [{"name":"Sun","ecliptic_long":311.533}, ...]
    returns: BytesIO (PNG)
    """
    logging.info("🎨 Chart çizimi başlatıldı...")
    # --- DOSYA YOLLARI ---
    template_path = "chart_template.png"
    font_planet = "AstroGadget.ttf"
    font_text = "arial.ttf"

    # --- ARKA PLAN ---
    bg = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(bg)

    # --- FONTLAR ---
    try:
        planet_font = ImageFont.truetype(font_planet, 64, layout_engine=ImageFont.LAYOUT_BASIC)
        logging.info("✅ Astro font başarıyla yüklendi (LAYOUT_BASIC aktif).")
    except Exception as e:
        logging.warning(f"⚠️ Astro font yüklenemedi ({e}), varsayılan font kullanılıyor.")
        planet_font = ImageFont.load_default()

    try:
        label_font = ImageFont.truetype(font_text, 48)
        small_font = ImageFont.truetype(font_text, 36)
        logging.info("✅ Yazı fontları yüklendi.")
    except Exception as e:
        logging.warning(f"⚠️ Yazı fontu yüklenemedi ({e}), varsayılan font kullanılacak.")
        label_font = small_font = ImageFont.load_default()

    # --- GEOMETRİ ---
    cx, cy = bg.width // 2, bg.height // 2
    R_planet = int((min(cx, cy) - 50) * 0.85)
    R_aspect = int(R_planet * 0.80)

    # --- GEZEGENLER ---
    pos = {}
    for p in planets:
        deg = float(p["ecliptic_long"]) % 360
        x, y = _angle_to_xy(deg, R_planet, cx, cy)
        pos[p["name"]] = (x, y)
        sym = PLANET_SYMBOLS.get(p["name"], "?")
        bx, by, bx2, by2 = draw.textbbox((0, 0), sym, font=planet_font)
        draw.text((_r(x - (bx2 - bx) / 2), _r(y - (by2 - by) / 2)), sym, fill=PURPLE, font=planet_font)
    logging.info("✅ Gezegen sembolleri çizildi (%d adet).", len(planets))

    # --- ASPECT ÇİZGİLERİ ---
    ORB = 4.0
    for i, p1 in enumerate(planets):
        for j in range(i + 1, len(planets)):
            p2 = planets[j]
            d = abs(float(p1["ecliptic_long"]) - float(p2["ecliptic_long"])) % 360
            if d > 180: d = 360 - d
            for A, (col, th) in ASPECTS.items():
                if abs(d - A) < ORB:
                    a = _clamp(pos[p1["name"]], cx, cy, R_aspect)
                    b = _clamp(pos[p2["name"]], cx, cy, R_aspect)
                    draw.line([a, b], fill=col, width=th)
                    break
    logging.info("✅ Aspect çizgileri oluşturuldu.")

    # --- BAŞLIK ---
    title = f"{name}'s Natal Birth Chart" if name else "Natal Birth Chart"
    tb = draw.textbbox((0, 0), title, font=label_font)
    draw.text(((bg.width - (tb[2] - tb[0])) // 2, 35), title, fill=PURPLE, font=label_font)
    logging.info("✅ Başlık çizildi.")

    # --- ALT BİLGİ ---
    date_txt = ""
    if dob:
        try:
            date_txt = datetime.strptime(dob, "%Y-%m-%d").strftime("%d %B %Y")
        except Exception:
            date_txt = dob
    if tob:
        date_txt = (date_txt + f" @ {tob}").strip()
    loc_txt = f"{city}, {country}" if (city and country) else (city or country or "")

    y0 = bg.height - 100
    db = draw.textbbox((0, 0), date_txt, font=small_font)
    lb = draw.textbbox((0, 0), loc_txt, font=small_font)
    draw.text(((bg.width - (db[2] - db[0])) // 2, y0 - 20), date_txt, fill=PURPLE, font=small_font)
    draw.text(((bg.width - (lb[2] - lb[0])) // 2, y0 + 20), loc_txt, fill=PURPLE, font=small_font)
    logging.info("✅ Alt bilgi çizildi.")

    # --- LEGEND ---
    legend = [
        ("Conjunction", "#FFD400"),
        ("Sextile", "#1DB954"),
        ("Square", "#E63946"),
        ("Trine", "#1E88E5"),
        ("Opposition", "#7B1FA2"),
    ]
    yL = bg.height - 180
    xL = 60
    spacing = 200
    for i, (label, col) in enumerate(legend):
        lx = xL + i * spacing
        draw.rectangle([lx, yL, lx + 24, yL + 24], fill=col)
        draw.text((lx + 34, yL + 4), label, fill=col, font=small_font)
    logging.info("✅ Legend açıklamaları çizildi.")

    # --- DOSYA ÇIKTI ---
    os.makedirs("charts", exist_ok=True)
    out_path = f"charts/chart_{name.lower()}_final.png" if name else "charts/chart_final.png"
    bg.save(out_path, format="PNG", optimize=True)
    logging.info(f"✅ Chart kaydedildi: {out_path}")
    logging.info("=== ✅ DRAW_CHART TAMAMLANDI ===")

    out = BytesIO()
    bg.save(out, format="PNG", optimize=True)
    out.seek(0)
    return out
