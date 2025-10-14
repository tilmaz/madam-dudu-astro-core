from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from dateutil import parser
import pytz
import swisseph as swe
import os, requests

app = FastAPI(title="Madam Dudu Astro Core", version="2.2.0")

# --- env vars ---
GOOGLE_KEY  = os.getenv("GOOGLE_MAPS_API_KEY", "")
EPHE_PATH   = os.getenv("EPHE_PATH", "./ephe")
SERVICE_KEY = os.getenv("API_KEY", "")

if not GOOGLE_KEY:
    print("WARN: GOOGLE_MAPS_API_KEY not set; /compute will fail for city lookups.")
if not SERVICE_KEY:
    print("WARN: API_KEY not set; /compute requires Authorization header.")

# Swiss Ephemeris data path
swe.set_ephe_path(EPHE_PATH)

ZODIAC = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
]

# ------------------------------ Models ------------------------------

class Input(BaseModel):
    name: str | None = None
    dob: str = Field(..., description="YYYY-MM-DD")
    # Birth time:
    # - Placidus için ZORUNLU
    # - WholeSign için OPSİYONEL
    # - mode=auto için MERKEZ SAAT olarak kullanılır
    tob: str | None = Field(
        None,
        description="HH:MM (local). Required for Placidus, optional for WholeSign. For mode=auto, used as center time."
    )
    city: str
    country: str
    zodiac: str = Field("Tropical", pattern="^(Tropical|Sidereal\\(Lahiri\\))$")
    house_system: str = Field("Placidus", pattern="^(Placidus|WholeSign)$")
    # Auto modu için yeni alanlar:
    mode: str = Field("manual", pattern="^(manual|auto)$")
    time_uncertainty_minutes: int | None = Field(
        60, ge=1, le=180,
        description="Only for mode=auto; default 60"
    )

# ------------------------------ Helpers ------------------------------

def sign_deg(ecl_lon: float):
    lon = ecl_lon % 360.0
    sidx = int(lon // 30)
    deg  = lon - 30*sidx
    return ZODIAC[sidx], round(deg, 2), round(lon, 2)

def sign_index_from_lon(lon: float) -> int:
    return int((lon % 360.0) // 30)

def build_whole_sign_cusps(anchor_sign_idx: int):
    # 1. ev = anchor_sign 0°
    base = (anchor_sign_idx * 30.0) % 360.0
    return [round((base + k*30.0) % 360.0, 2) for k in range(12)]

def jd_from_dt(dt_utc: datetime) -> float:
    return swe.julday(
        dt_utc.year, dt_utc.month, dt_utc.day,
        dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
    )

def asc_sign_for_jd(jd_ut: float, lat: float, lon: float) -> int:
    houses_tmp, ascmc_tmp = swe.houses(jd_ut, lat, lon, b'P')
    asc_lon_tmp = ascmc_tmp[0]
    return sign_index_from_lon(asc_lon_tmp)

@app.get("/health")
def health():
    return {"ok": True, "service": "Madam Dudu Astro Core", "version": app.version if hasattr(app, "version") else "2.2.0"}

def geocode_to_latlon(city: str, country: str):
    q = f"{city}, {country}"
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    r = requests.get(url, params={"address": q, "key": GOOGLE_KEY}, timeout=15)
    if r.status_code != 200:
        raise HTTPException(502, detail="Geocoding servisi cevap vermedi.")
    data = r.json()
    if data.get("status") != "OK" or not data.get("results"):
        raise HTTPException(400, detail="Şehir/ülke bulunamadı; yazımı kontrol edin.")
    loc = data["results"][0]["geometry"]["location"]
    return float(loc["lat"]), float(loc["lng"])

def latlon_to_tzid(lat: float, lon: float, utc_ts: int):
    # Google Time Zone API → IANA TZID (örn. Europe/Berlin)
    url = "https://maps.googleapis.com/maps/api/timezone/json"
    r = requests.get(url, params={"location": f"{lat},{lon}", "timestamp": utc_ts, "key": GOOGLE_KEY}, timeout=15)
    if r.status_code != 200:
        raise HTTPException(502, detail="Time Zone servisi cevap vermedi.")
    data = r.json()
    if data.get("status") != "OK":
        raise HTTPException(400, detail="Time Zone bulunamadı.")
    return data["timeZoneId"]

# ------------------------------ Main ------------------------------

@app.post("/compute")
def compute(i: Input, Authorization: str | None = Header(default=None)):
    # basit auth
    if not SERVICE_KEY:
        raise HTTPException(500, detail="Sunucu API_KEY tanımlı değil.")
    if Authorization is None or not Authorization.startswith("Bearer "):
        raise HTTPException(401, detail="Authorization: Bearer <API_KEY> başlığı gerekli.")
    if Authorization.split(" ", 1)[1] != SERVICE_KEY:
        raise HTTPException(403, detail="Geçersiz API_KEY.")

    # 1) Geocode: şehir→lat/lon
    lat, lon = geocode_to_latlon(i.city.strip(), i.country.strip())

    # 2) IANA TZID
    approx_utc = int(datetime.utcnow().timestamp())  # tzid için güncel zaman yeterli
    tzid = latlon_to_tzid(lat, lon, approx_utc)
    tz = pytz.timezone(tzid)

    # 3) Yerel zamanı TZID ile oluştur (DST doğru)
    approx_time = False
    if i.house_system == "Placidus":
        if not i.tob:
            raise HTTPException(400, detail="Birth time (tob) is required for Placidus.")
        try:
            local_dt = tz.localize(parser.parse(f"{i.dob} {i.tob}"), is_dst=None)
        except pytz.AmbiguousTimeError:
            raise HTTPException(400, detail="Yerel saat DST nedeniyle belirsiz (ambiguous). Erken/Geç blok belirtin.")
        except pytz.NonExistentTimeError:
            raise HTTPException(400, detail="Yerel saat DST nedeniyle geçersiz (non-existent). Geçerli bir dakika seçin.")
        except Exception:
            raise HTTPException(400, detail="Tarih/saat biçimi hatalı. Örn: 1985-04-30 ve 10:30")
    else:
        # WholeSign: saat verilmişse kullan; verilmemişse 12:00 varsay (Solar Whole Sign)
        tob_use = i.tob if i.tob else "12:00"
        try:
            local_dt = tz.localize(parser.parse(f"{i.dob} {tob_use}"), is_dst=None)
        except pytz.AmbiguousTimeError:
            raise HTTPException(400, detail="Yerel saat DST nedeniyle belirsiz (ambiguous). Placidus için net saat verin veya WholeSign (no exact time) kullanın.")
        except pytz.NonExistentTimeError:
            raise HTTPException(400, detail="Yerel saat DST nedeniyle geçersiz (non-existent). Placidus için geçerli bir saat verin veya WholeSign kullanın.")
        except Exception:
            raise HTTPException(400, detail="Tarih/saat biçimi hatalı. Örn: 1985-04-30 ve 10:30")
        approx_time = (i.tob is None)

    utc_dt = local_dt.astimezone(pytz.UTC)

    # 4) Julian Day (UT)
    jd_ut = jd_from_dt(utc_dt)

    # 5) Zodyak bayrakları
    flag = swe.FLG_SWIEPH
    if i.zodiac.startswith("Sidereal"):
        swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
        flag |= swe.FLG_SIDEREAL

    # 6) Güneş / Ay
    sun = swe.calc_ut(jd_ut, swe.SUN, flag)[0]
    moon = swe.calc_ut(jd_ut, swe.MOON, flag)[0]
    sun_sign,  sun_deg,  sun_lon  = sign_deg(sun[0])
    moon_sign, moon_deg, moon_lon = sign_deg(moon[0])

    # --- AUTO MODE (± window) ---
    mode_final = None
    auto_reason = None
    asc_probe = None
    if i.mode == "auto":
        if not i.tob:
            raise HTTPException(400, detail="mode=auto için merkez saat (tob) gerekir; örn. ~16:30 ise 16:30 yazın.")
        delta_min = int(i.time_uncertainty_minutes or 60)
        dt_minus = (utc_dt - timedelta(minutes=delta_min))
        dt_plus  = (utc_dt + timedelta(minutes=delta_min))
        jd_minus = jd_from_dt(dt_minus)
        jd_plus  = jd_from_dt(dt_plus)

        s_minus = asc_sign_for_jd(jd_minus, lat, lon)
        s_plus  = asc_sign_for_jd(jd_plus,  lat, lon)

        asc_probe = {
            "minutes": delta_min,
            "asc_sign_minus": ZODIAC[s_minus],
            "asc_sign_plus":  ZODIAC[s_plus]
        }

        if s_minus == s_plus:
            mode_final = "Placidus"
            auto_reason = "asc_sign_stable"
        else:
            mode_final = "WholeSign"
            auto_reason = "asc_sign_changes_within_window"

    # Seçilecek sistem: manual ise body'deki, auto ise karar
    chosen_system = i.house_system
    if i.mode == "auto" and mode_final:
        chosen_system = mode_final

    # 7) Evler ve ASC/MC
    if chosen_system == "Placidus":
        houses, ascmc = swe.houses(jd_ut, lat, lon, b'P')
        asc_lon = ascmc[0]
        mc_lon  = ascmc[1]
        asc_sign, asc_deg, asc_ecl = sign_deg(asc_lon)
        cusps_out = [round(x % 360, 2) for x in houses]
        asc_payload = {"sign": asc_sign, "degree": asc_deg, "ecliptic_long": asc_ecl}
        mc_payload  = {"ecliptic_long": round(mc_lon % 360, 2)}
        houses_payload = {"system": "Placidus", "cusps_longitudes": cusps_out}
    else:
        # WholeSign
        if i.tob:
            houses_tmp, ascmc_tmp = swe.houses(jd_ut, lat, lon, b'P')
            asc_lon_tmp = ascmc_tmp[0]
            anchor_idx = sign_index_from_lon(asc_lon_tmp)
            asc_sign, asc_deg, asc_ecl = sign_deg(asc_lon_tmp)
            asc_payload = {"sign": asc_sign, "degree": asc_deg, "ecliptic_long": asc_ecl}
            mc_payload  = {"ecliptic_long": round(ascmc_tmp[1] % 360, 2)}
        else:
            anchor_idx = sign_index_from_lon(sun[0])
            asc_sign = ZODIAC[anchor_idx]
            asc_payload = {
                "sign": asc_sign,
                "degree": 0.0,
                "ecliptic_long": float(anchor_idx * 30),
                "approx": True,
                "note": "Solar Whole Sign (no exact birth time)"
            }
            mc_payload = {"ecliptic_long": None}

        cusps_out = build_whole_sign_cusps(anchor_idx)
        houses_payload = {"system": "WholeSign", "cusps_longitudes": cusps_out}

    # 8) Özet
    dst_on = bool(local_dt.dst())
    offset_seconds = int(local_dt.utcoffset().total_seconds())
    sign_pm = "+" if offset_seconds >= 0 else "-"
    hh = abs(offset_seconds)//3600
    mm = (abs(offset_seconds)%3600)//60
    offset_str = f"{sign_pm}{hh:02d}:{mm:02d}"

    return {
        "input": {
            "name": i.name,
            "dob": i.dob, "tob": i.tob,
            "city": i.city, "country": i.country
        },
        "normalized": {
            "datetime_local": local_dt.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "datetime_utc":   utc_dt.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "lat": lat, "lon": lon, "tzid": tzid,
            "zodiac": i.zodiac, "house_system": chosen_system,
            "approx_time": approx_time
        },
        "sun":  {"sign": sun_sign,  "degree": sun_deg,  "ecliptic_long": sun_lon},
        "moon": {"sign": moon_sign, "degree": moon_deg, "ecliptic_long": moon_lon},
        "ascendant": asc_payload,
        "mc": mc_payload,
        "houses": houses_payload,
        "dst": dst_on,
        "utc_offset": offset_str,
        "mode": i.mode,
        "mode_final": (mode_final or "manual"),
        "auto_reason": auto_reason,
        "asc_probe": asc_probe,
        "engine_version": "2.2.0"
    }
