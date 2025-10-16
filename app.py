from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
from datetime import datetime
from dateutil import parser
import pytz
import swisseph as swe
import os, requests
from chart_utils import draw_chart
from fastapi.responses import StreamingResponse

app = FastAPI(title="Madam Dudu Astro Core", version="2.6.0")

GOOGLE_KEY  = os.getenv("GOOGLE_MAPS_API_KEY", "")
EPHE_PATH   = os.getenv("EPHE_PATH", "./ephe")
SERVICE_KEY = os.getenv("API_KEY", "")

if not GOOGLE_KEY:
    print("WARN: GOOGLE_MAPS_API_KEY not set; /compute will fail for city lookups.")
if not SERVICE_KEY:
    print("WARN: API_KEY not set; /chart requires Authorization header.")

swe.set_ephe_path(EPHE_PATH)

ZODIAC = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
]

PLANET_IDS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY, "Venus": swe.VENUS,
    "Mars": swe.MARS, "Jupiter": swe.JUPITER, "Saturn": swe.SATURN,
    "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE, "Pluto": swe.PLUTO,
    "TrueNode": swe.TRUE_NODE, "Chiron": swe.CHIRON
}

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
    return {"ok": True, "service": "Madam Dudu Astro Core", "version": "2.6.0"}

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
    data = r.json()
    if data.get("status") != "OK" or not data.get("results"):
        raise HTTPException(400, detail=f"Şehir/ülke bulunamadı: {city}, {country}")
    loc = data["results"][0]["geometry"]["location"]
    return float(loc["lat"]), float(loc["lng"])

def latlon_to_tzid(lat: float, lon: float, utc_ts: int):
    url = "https://maps.googleapis.com/maps/api/timezone/json"
    r = requests.get(url, params={"location": f"{lat},{lon}", "timestamp": utc_ts, "key": GOOGLE_KEY}, timeout=15)
    data = r.json()
    if data.get("status") != "OK":
        raise HTTPException(400, detail="Time Zone bulunamadı.")
    return data["timeZoneId"]

@app.post("/compute")
def compute(i: Input, Authorization: str | None = Header(default=None)):
    if not SERVICE_KEY:
        raise HTTPException(500, detail="Sunucu API_KEY tanımlı değil.")
    if Authorization is None or not Authorization.startswith("Bearer "):
        raise HTTPException(401, detail="Authorization header eksik.")
    if Authorization.split(" ", 1)[1] != SERVICE_KEY:
        raise HTTPException(403, detail="Geçersiz API_KEY.")

    lat, lon = geocode_to_latlon(i.city.strip(), i.country.strip())
    tzid = latlon_to_tzid(lat, lon, int(datetime.utcnow().timestamp()))
    tz = pytz.timezone(tzid)

    tob_str = i.tob if i.tob else "12:00"
    local_dt = tz.localize(parser.parse(f"{i.dob} {tob_str}"))
    utc_dt = local_dt.astimezone(pytz.UTC)
    jd_ut = jd_from_dt(utc_dt)

    flag = swe.FLG_SWIEPH
    if i.zodiac.startswith("Sidereal"):
        swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
        flag |= swe.FLG_SIDEREAL

    # Planets
    chart_planets = []
    for name, pid in PLANET_IDS.items():
        xx, _rf = swe.calc_ut(jd_ut, pid, flag)
        sign, deg, lon_ = sign_deg(xx[0])
        chart_planets.append({
            "name": name,
            "sign": sign,
            "degree": deg,
            "ecliptic_long": lon_,
            "retrograde": bool(xx[3] < 0)
        })

    # Houses
    hsys = "P" if i.house_system == "Placidus" else "W"
    ascmc, cusp = swe.houses_ex(jd_ut, lat, lon, hsys)
    house_cusps = []
    for h in range(1, 13):
        s, d, l = sign_deg(cusp[h-1])
        house_cusps.append({"house": h, "sign": s, "degree": d})

    asc_sign, asc_deg, _ = sign_deg(ascmc[0])
    mc_sign, mc_deg, _ = sign_deg(ascmc[1])

    return {
        "normalized": {
            "datetime_local": str(local_dt),
            "datetime_utc": str(utc_dt),
            "tzid": tzid,
            "lat": lat,
            "lon": lon,
            "zodiac": i.zodiac,
            "house_system": i.house_system
        },
        "ascendant": {"sign": asc_sign, "degree": asc_deg},
        "midheaven": {"sign": mc_sign, "degree": mc_deg},
        "houses": house_cusps,
        "planets": chart_planets
    }

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

    tob_str = i.tob if i.tob else "12:00"
    local_dt = tz.localize(parser.parse(f"{i.dob} {tob_str}"))
    utc_dt = local_dt.astimezone(pytz.UTC)
    jd_ut = jd_from_dt(utc_dt)

    flag = swe.FLG_SWIEPH
    if i.zodiac.startswith("Sidereal"):
        swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
        flag |= swe.FLG_SIDEREAL

    chart_planets = []
    for name, pid in PLANET_IDS.items():
        xx, _rf = swe.calc_ut(jd_ut, pid, flag)
        sign, deg, lon_ = sign_deg(xx[0])
        chart_planets.append({
            "name": name,
            "sign": sign,
            "degree": deg,
            "ecliptic_long": lon_,
            "retrograde": bool(xx[3] < 0)
        })

    image_stream = draw_chart(
        chart_planets,
        name=i.name,
        dob=i.dob,
        tob=i.tob,
        city=i.city,
        country=i.country
    )
    return StreamingResponse(image_stream, media_type="image/png")
