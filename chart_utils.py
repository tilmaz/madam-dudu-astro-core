from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime
import math

PURPLE = "#800080"
ASPECTS = {
    0:   ("#FFD400", 8),
    60:  ("#1DB954", 8),
    90:  ("#E63946", 8),
    120: ("#1E88E5", 8),
    180: ("#7B1FA2", 8),
}

PLANET_SYMBOLS = {
    "Sun":"a","Moon":"b","Mercury":"c","Venus":"d","Mars":"e",
    "Jupiter":"f","Saturn":"g","Uranus":"h","Neptune":"i","Pluto":"j"
}

def _r(x, n=3): return round(float(x), n)

def _angle_to_xy(deg, radius, cx, cy):
    a = math.radians(90 - (deg % 360))
    x = cx + radius * math.cos(a)
    y = cy - radius * math.sin(a)
    return (_r(x), _r(y))

def _clamp(pt, cx, cy, radius):
    vx, vy = pt[0]-cx, pt[1]-cy
    d = math.hypot(vx, vy)
    if d == 0: return (cx, cy)
    k = radius/d
    return (_r(cx + vx*k), _r(cy + vy*k))

def draw_chart(planets, name=None, dob=None, tob=None, city=None, country=None):
    """
    planets: [{"name":"Sun","ecliptic_long":311.533}, ...]
    returns: bytes (PNG)
    """
    # --- YEREL ŞABLON ve FONTLAR ---
    template_path = "chart_template.png"   # repo kökünde
    font_planet   = "AstroGadget.ttf"      # repo kökünde
    font_text     = "DejaVuSans.ttf"       # yoksa default

    bg = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(bg)

    try:
        planet_font = ImageFont.truetype(font_planet, 64)
    except Exception:
        planet_font = ImageFont.load_default()

    try:
        label_font = ImageFont.truetype(font_text, 48)
        small_font = ImageFont.truetype(font_text, 36)
    except Exception:
        label_font = small_font = ImageFont.load_default()

    # --- GEOMETRİ ---
    cx, cy = bg.width//2, bg.height//2
    R_planet  = int((min(cx, cy) - 50) * 0.85)
    R_aspect  = int(R_planet * 0.80)

    # --- GEZEGENLER ---
    pos = {}
    for p in planets:
        deg = float(p["ecliptic_long"]) % 360
        x, y = _angle_to_xy(deg, R_planet, cx, cy)
        pos[p["name"]] = (x, y)
        sym = PLANET_SYMBOLS.get(p["name"], "?")
        bx, by, bx2, by2 = draw.textbbox((0,0), sym, font=planet_font)
        draw.text((_r(x-(bx2-bx)/2), _r(y-(by2-by)/2)), sym, fill=PURPLE, font=planet_font)

    # --- ASPECT ÇİZGİLERİ (±4° orb) ---
    ORB = 4.0
    n = len(planets)
    for i in range(n):
        for j in range(i+1, n):
            p1, p2 = planets[i], planets[j]
            d = abs(float(p1["ecliptic_long"]) - float(p2["ecliptic_long"])) % 360
            if d > 180: d = 360 - d
            for A, (col, th) in ASPECTS.items():
                if abs(d - A) < ORB:
                    a = _clamp(pos[p1["name"]], cx, cy, R_aspect)
                    b = _clamp(pos[p2["name"]], cx, cy, R_aspect)
                    draw.line([a, b], fill=col, width=th)
                    break

    # --- BAŞLIK ---
    title = f"{name}'s Natal Chart Wheel" if name else "Natal Chart Wheel"
    tb = draw.textbbox((0,0), title, font=label_font)
    draw.text(((bg.width-(tb[2]-tb[0]))//2, 30), title, fill=PURPLE, font=label_font)

    # --- ALT BİLGİ ---
    if dob:
        try:
            date_txt = datetime.strptime(dob, "%Y-%m-%d").strftime("%d %B %Y")
        except Exception:
            date_txt = dob
    else:
        date_txt = ""
    if tob:
        date_txt = (date_txt + f" @{tob}").strip()
    loc_txt = f"{city}/{country}" if (city and country) else (city or country or "")

    y0 = bg.height - 120
    db = draw.textbbox((0,0), date_txt, font=small_font)
    lb = draw.textbbox((0,0), loc_txt,  font=small_font)
    draw.text(((bg.width-(db[2]-db[0]))//2, y0),       date_txt, fill=PURPLE, font=small_font)
    draw.text(((bg.width-(lb[2]-lb[0]))//2, y0 + 50),  loc_txt,  fill=PURPLE, font=small_font)

    # --- LEJAND ---
    legend = [("Conjunction","#FFD400"),("Sextile","#1DB954"),("Square","#E63946"),
              ("Trine","#1E88E5"),("Opposition","#7B1FA2")]
    yL = bg.height - 240
    for label, col in legend:
        draw.rectangle([30, yL+12, 60, yL+24], fill=col)
        draw.text((70, yL), label, fill=col, font=small_font)
        yL += 38

    # --- PNG oluşturma ---
    out = BytesIO()
    bg.save(out, format="PNG", optimize=True)
    out.seek(0)

    # ✅ BytesIO yerine ham bytes döndür
    return out.getvalue()
