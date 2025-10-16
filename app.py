from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from dateutil import parser
import pytz
import swisseph as swe
import os, requests
from chart_utils import draw_chart
from fastapi.responses import StreamingResponse

app = FastAPI(title="Madam Dudu Astro Core", version="2.4.0")

# --- env vars ---
GOOGLE_KEY  = os.getenv("GOOGLE_MAPS_API_KEY", "")
EPHE_PATH   = os.getenv("EPHE_PATH", "./ephe")
SERVICE_KEY = os.getenv("API_KEY", "")

if not GOOGLE_KEY:
    print("WARN: GOOGLE_MAPS_API_KEY not set; /compute will fail for city lookups.")
if not SERVICE_KEY:
    print("WARN: API_KEY not set; /compute requires Authorization header.")

swe.set_ephe_path(EPHE_PATH)

ZODIAC = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
]

class Input(BaseModel):
    name: str | None = None
    dob: str
    tob: str | None = None
    city: str
    country: str
    zodiac: str = Field("Tropical", pattern="^(Tropical|Sidereal\\(Lahiri\\))$")
    house_system: str = Field("Placidus", pattern="^(Placidus|WholeSign)$")
    mode: str = Field("manual", pattern="^(manual|auto)$")
    time_uncertainty_minutes: int | None = 15

@app.get("/health")
def health():
    return {"ok": True, "service": "Madam Dudu Astro Core", "version": "2.4.0"}

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

def sign_index_from_lon(lon: float) -> int:
    return int((lon % 360.0) // 30)

def build_whole_sign_cusps(anchor_sign_idx: int):
    base = (anchor_sign_idx * 30.0) % 360.0
    return [round((base + k*30.0) % 360.0, 2) for k in range(12)]

def asc_sign_for_jd(jd_ut: float, lat: float, lon: float) -> int:
    houses_tmp, ascmc_tmp = swe.houses(jd_ut, lat, lon, b'P')
    return sign_index_from_lon(ascmc_tmp[0])

def planet_payload(xx0: float, speed_lon: float):
    s, d, lon = sign_deg(xx0)
    return {
        "sign": s,
        "degree": d,
        "ecliptic_long": lon,
        "retrograde": bool(speed_lon < 0)
    }

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
    data = r.json()
    if data.get("status") != "OK":
        raise HTTPException(400, detail="Time Zone bulunamadı.")
    return data["timeZoneId"]

@app.post("/chart")
def chart(i: Input, Authorization: str | None = Header(default=None)):
    if not SERVICE_KEY:
        raise HTTPException(500, detail="Sunucu API_KEY tanımlı değil.")
    if Authorization is None or not Authorization.startswith("Bearer "):
        raise HTTPException(401, detail="Authorization: Bearer <API_KEY> başlığı gerekli.")
    if Authorization.split(" ", 1)[1] != SERVICE_KEY:
        raise HTTPException(403, detail="Geçersiz API_KEY.")

    lat, lon = geocode_to_latlon(i.city.strip(), i.country.strip())
    tzid = latlon_to_tzid(lat, lon, int(datetime.utcnow().timestamp()))
    tz = pytz.timezone(tzid)

    if i.house_system == "Placidus" and not i.tob:
        raise HTTPException(400, detail="Placidus için saat zorunlu.")
    
    tob_str = i.tob if i.tob else "12:00"
    try:
        local_dt = tz.localize(parser.parse(f"{i.dob} {tob_str}"), is_dst=None)
    except:
        raise HTTPException(400, detail="Tarih/saat geçersiz.")
    
    utc_dt = local_dt.astimezone(pytz.UTC)
    jd_ut = jd_from_dt(utc_dt)

    flag = swe.FLG_SWIEPH
    if i.zodiac.startswith("Sidereal"):
        swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
        flag |= swe.FLG_SIDEREAL

    PLANET_IDS = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY, "Venus": swe.VENUS,
        "Mars": swe.MARS, "Jupiter": swe.JUPITER, "Saturn": swe.SATURN,
        "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE, "Pluto": swe.PLUTO
    }

    chart_planets = []
    for name, pid in PLANET_IDS.items():
        xx, _rf = swe.calc_ut(jd_ut, pid, flag)
        payload = planet_payload(xx[0], xx[3] if len(xx) > 3 else 0.0)
        payload["name"] = name
        chart_planets.append(payload)

    # 🔮 Şimdi çizimi yap!
    image_stream = draw_chart(
        chart_planets,
        name=i.name,
        dob=i.dob,
        tob=i.tob,
        city=i.city,
        country=i.country
    )
    
    return StreamingResponse(image_stream, media_type="image/png")
