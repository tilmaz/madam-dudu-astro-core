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

# --- Environment Variables ---
GOOGLE_KEY  = os.getenv("GOOGLE_MAPS_API_KEY", "")
EPHE_PATH   = os.getenv("EPHE_PATH", "./ephe")
SERVICE_KEY = os.getenv("API_KEY", "")

if not GOOGLE_KEY:
    print("⚠️ WARN: GOOGLE_MAPS_API_KEY not set; city lookups may fail.")
if not SERVICE_KEY:
    print("⚠️ WARN: API_KEY not set; protected endpoints will reject requests.")

swe.set_ephe_path(EPHE_PATH)

ZODIAC = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
]

# --- Input Model ---
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


# --- Health Check ---
@app.get("/health")
def health():
    return {"ok": True, "service": "Madam Dudu Astro Core", "version": "2.6.0"}


# --- Utilities ---
def sign_deg(ecl_lon: float):
    lon = ecl_lon % 360.0
    sidx = int(lon // 30)
    deg = lon - 30 * sidx
    return ZODIAC[sidx], round(deg, 2), round(lon, 2)


def jd_from_dt(dt_utc: datetime) -> float:
    return swe.julday(
        dt_utc.year, dt_utc.month, dt_utc.day,
        dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
    )


def geocode_to_latlon(city: str, country: str):
    q = f"{city}, {country}"
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    try:
        r = requests.get(url, params={"address": q, "key": GOOGLE_KEY}, timeout=15)
        data = r.json()
        if data.get("status") != "OK" or not data.get("results"):
            raise ValueError("No results")
        loc = data["results"][0]["geometry"]["location"]
        return float(loc["lat"]), float(loc["lng"])
    except Exception as e:
        print("❌ Geocode Error:", e)
        raise HTTPException(400, detail=f"Şehir/ülke bulunamadı: {city}, {country}")


def latlon_to_tzid(lat: float, lon: float, utc_ts: int):
    url = "https://maps.googleapis.com/maps/api/timezone/json"
    try:
        r = requests.get(url, params={"location": f"{lat},{lon}", "timestamp": utc_ts, "key": GOOGLE_KEY}, timeout=15)
        data = r.json()
        if data.get("status") != "OK":
            raise ValueError("Bad TZ result")
        return data["timeZoneId"]
    except Exception as e:
        print("❌ Timezone Error:", e)
        raise HTTPException(400, detail="Time Zone bulunamadı.")


# --- /compute endpoint ---
@app.post("/compute")
def compute(i: Input, Authorization: str | None = Header(default=None)):
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
    try:
        local_dt = tz.localize(parser.parse(f"{i.dob} {tob_str}"), is_dst=None)
    except Exception as e:
        raise HTTPException(400, detail=f"Tarih/saat geçersiz: {e}")

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

    chart_data = {}
    for name, pid in PLANET_IDS.items():
        xx, _rf = swe.calc_ut(jd_ut, pid, flag)
        s, d, lon_ = sign_deg(xx[0])
        chart_data[name] = {
            "sign": s,
            "degree": d,
            "ecliptic_long": lon_,
            "retrograde": bool(xx[3] < 0)
        }

    result = {
        "engine_version": "2.6.0",
        "normalized": {
            "datetime_local": local_dt.strftime("%Y-%m-%d %H:%M"),
            "datetime_utc": utc_dt.strftime("%Y-%m-%d %H:%M"),
            "tzid": tzid,
            "lat": lat,
            "lon": lon,
            "zodiac": i.zodiac,
            "house_system": i.house_system
        },
        "planets": chart_data
    }

    print("✅ Compute result:", result["normalized"])
    return result


# --- /chart endpoint ---
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
    local_dt = tz.localize(parser.parse(f"{i.dob} {tob_str}"), is_dst=None)
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
        s, d, lon_ = sign_deg(xx[0])
        chart_planets.append({
            "name": name,
            "sign": s,
            "degree": d,
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
