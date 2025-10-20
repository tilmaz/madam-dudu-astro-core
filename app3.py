# app3.py — Madam Dudu Astro Core (Unified API)
# Version 3.2.0
# Author: Seray + GPT-5
# Description: Combined compute + render astro engine with full image generation.

from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from dateutil import parser
from io import BytesIO
import pytz, math, os, requests, swisseph as swe
from PIL import Image, ImageDraw, ImageFont

# --- CONFIG ---
GOOGLE_KEY  = os.getenv("GOOGLE_MAPS_API_KEY", "")
EPHE_PATH   = os.getenv("EPHE_PATH", "./ephe")
SERVICE_KEY = os.getenv("API_KEY", "")
TMP_DIR     = "./charts"

os.makedirs(TMP_DIR, exist_ok=True)
swe.set_ephe_path(EPHE_PATH)

# --- FASTAPI APP ---
app = FastAPI(
    title="Madam Dudu Astro Core Unified",
    description="Unified API (deep debug) for Madam Dudu Astrology engine.",
    version="3.2.0-debug"
)

# --- CONSTS ---
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
ZODIAC = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
]

# --- HELPERS ---
def _r(x, n=3): return round(float(x), n)
def _angle_to_xy(deg, radius, cx, cy):
    a = math.radians(90 - (deg % 360))
    return (_r(cx + radius * math.cos(a)), _r(cy - radius * math.sin(a)))
def _clamp(pt, cx, cy, radius):
    vx, vy = pt[0]-cx, pt[1]-cy
    d = math.hypot(vx, vy)
    if d == 0: return (cx, cy)
    k = radius/d
    return (_r(cx + vx*k), _r(cy + vy*k))

def sign_deg(ecl_lon: float):
    lon = ecl_lon % 360.0
    sidx = int(lon // 30)
    deg  = lon - 30*sidx
    return ZODIAC[sidx], round(deg, 2), round(lon, 2)

def jd_from_dt(dt_utc: datetime) -> float:
    return swe.julday(
        dt_utc.year, dt_utc.month, dt_utc.day,
        dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
    )

def geocode_to_latlon(city: str, country: str):
    q = f"{city}, {country}"
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    r = requests.get(url, params={"address": q, "key": GOOGLE_KEY}, timeout=15)
    if r.status_code != 200:
        raise HTTPException(502, detail="Geocoding servisi cevap vermedi.")
    data = r.json()
    if data.get("status") != "OK" or not data.get("results"):
        raise HTTPException(400, detail="Şehir/ülke bulunamadı.")
    loc = data["results"][0]["geometry"]["location"]
    return float(loc["lat"]), float(loc["lng"])

def latlon_to_tzid(lat: float, lon: float, utc_ts: int):
    url = "https://maps.googleapis.com/maps/api/timezone/json"
    r = requests.get(url, params={"location": f"{lat},{lon}", "timestamp": utc_ts, "key": GOOGLE_KEY}, timeout=15)
    if r.status_code != 200:
        raise HTTPException(502, detail="Time Zone servisi cevap vermedi.")
    data = r.json()
    if data.get("status") != "OK":
        raise HTTPException(400, detail="Time Zone bulunamadı.")
    return data["timeZoneId"]

# --- MODELS ---
class Input(BaseModel):
    name: str | None = None
    dob: str
    tob: str | None = None
    city: str
    country: str
    zodiac: str = "Tropical"
    house_system: str = "Placidus"
    mode: str = "manual"
    time_uncertainty_minutes: int | None = 15

class RenderInput(BaseModel):
    name: str | None = None
    dob: str | None = None
    tob: str | None = None
    city: str | None = None
    country: str | None = None
    planets: list

# --- HEALTH CHECK ---
@app.get("/health")
def health():
    return {"ok": True, "service": "Madam Dudu Astro Core Unified", "version": "3.2.0"}

# --- COMPUTE ENDPOINT ---
@app.post("/compute")
def compute(i: Input, Authorization: str | None = Header(default=None)):
    if not SERVICE_KEY:
        raise HTTPException(500, detail="API_KEY tanımlı değil.")
    if Authorization is None or not Authorization.startswith("Bearer "):
        raise HTTPException(401, detail="Authorization başlığı gerekli.")
    if Authorization.split(" ", 1)[1] != SERVICE_KEY:
        raise HTTPException(403, detail="Geçersiz API_KEY.")

    lat, lon = geocode_to_latlon(i.city, i.country)
    tzid = latlon_to_tzid(lat, lon, int(datetime.utcnow().timestamp()))
    tz = pytz.timezone(tzid)
    local_dt = tz.localize(parser.parse(f"{i.dob} {i.tob or '12:00'}"), is_dst=None)
    utc_dt = local_dt.astimezone(pytz.UTC)
    jd_ut = jd_from_dt(utc_dt)

    flag = swe.FLG_SWIEPH
    if i.zodiac.startswith("Sidereal"):
        swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
        flag |= swe.FLG_SIDEREAL

    sun_xx, _ = swe.calc_ut(jd_ut, swe.SUN, flag)
    moon_xx, _ = swe.calc_ut(jd_ut, swe.MOON, flag)
    sun_sign, sun_deg, sun_lon = sign_deg(sun_xx[0])
    moon_sign, moon_deg, moon_lon = sign_deg(moon_xx[0])

    PLANETS = {
        "Mercury": swe.MERCURY,
        "Venus": swe.VENUS,
        "Mars": swe.MARS,
        "Jupiter": swe.JUPITER,
        "Saturn": swe.SATURN,
        "Uranus": swe.URANUS,
        "Neptune": swe.NEPTUNE,
        "Pluto": swe.PLUTO
    }
    planets = []
    for name, pid in PLANETS.items():
        xx, _rf = swe.calc_ut(jd_ut, pid, flag)
        sign, deg, lon = sign_deg(xx[0])
        planets.append({"name": name, "sign": sign, "degree": deg, "ecliptic_long": lon})

    return {
        "input": i.dict(),
        "lat": lat,
        "lon": lon,
        "tzid": tzid,
        "datetime_local": local_dt.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "datetime_utc": utc_dt.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "sun": {"sign": sun_sign, "degree": sun_deg, "ecliptic_long": sun_lon},
        "moon": {"sign": moon_sign, "degree": moon_deg, "ecliptic_long": moon_lon},
        "planets": planets,
        "engine_version": "3.2.0"
    }

# --- RENDER ENDPOINT ---
@app.post("/render")
def render_chart(data: RenderInput, Authorization: str | None = Header(default=None)):
    if not SERVICE_KEY:
        raise HTTPException(500, detail="API_KEY tanımlı değil.")
    if Authorization is None or not Authorization.startswith("Bearer "):
        raise HTTPException(401, detail="Authorization başlığı gerekli.")
    if Authorization.split(" ", 1)[1] != SERVICE_KEY:
        raise HTTPException(403, detail="Geçersiz API_KEY.")

    planets = data.planets
    if not planets or len(planets) < 5:
        raise HTTPException(400, detail="Geçersiz veya eksik gezegen listesi.")

    size = 1200
    bg = Image.new("RGBA", (size, size), "white")
    draw = ImageDraw.Draw(bg)
    cx, cy = size // 2, size // 2
    R_planet, R_aspect = int(size * 0.4), int(size * 0.35)

    try:
        planet_font = ImageFont.truetype("AstroGadget.ttf", 64)
    except:
        planet_font = ImageFont.load_default()
    try:
        label_font = ImageFont.truetype("DejaVuSans.ttf", 36)
    except:
        label_font = ImageFont.load_default()

    pos = {}
    for p in planets:
        deg = float(p["ecliptic_long"]) % 360
        x, y = _angle_to_xy(deg, R_planet, cx, cy)
        pos[p["name"]] = (x, y)
        sym = PLANET_SYMBOLS.get(p["name"], "?")
        draw.text((x - 20, y - 20), sym, fill=PURPLE, font=planet_font)

    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            p1, p2 = planets[i], planets[j]
            d = abs(p1["ecliptic_long"] - p2["ecliptic_long"]) % 360
            if d > 180: d = 360 - d
            for A, (col, th) in ASPECTS.items():
                if abs(d - A) < 4:
                    a = _clamp(pos[p1["name"]], cx, cy, R_aspect)
                    b = _clamp(pos[p2["name"]], cx, cy, R_aspect)
                    draw.line([a, b], fill=col, width=th)

    title = f"{data.name or 'Natal Chart'}"
    draw.text((cx - 200, 40), title, fill=PURPLE, font=label_font)

    filename = f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    path = os.path.join(TMP_DIR, filename)
    bg.save(path, "PNG")

    return {"url": f"https://madam-dudu-astro-core-1.onrender.com/charts/{filename}"}

# --- STATIC FILE ACCESS ---
@app.get("/charts/{filename}")
def get_chart(filename: str):
    path = os.path.join(TMP_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(404, detail="Chart not found or expired.")
    return FileResponse(path, media_type="image/png")
    from fastapi.responses import JSONResponse

@app.get("/debug/check-template")
async def check_template():
    import os
    path = os.path.join(os.path.dirname(__file__), "chart_template.png")
    exists = os.path.exists(path)
    size = os.path.getsize(path) if exists else 0
    return JSONResponse(content={"exists": exists, "size_bytes": size, "path": path})

