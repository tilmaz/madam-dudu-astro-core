# app2.py
from fastapi import FastAPI, Body, Header, HTTPException
from fastapi.responses import StreamingResponse
from io import BytesIO
import os, requests

# Çizim yardımcı fonksiyonu
from chart_utils import draw_chart

# app.py içindeki compute uygulamasını dahil et
from app import compute as compute_fn  # /compute fonksiyonunu doğrudan çağıracağız

app = FastAPI(title="Madam Dudu Unified", version="3.0.0")

SERVICE_KEY = os.getenv("API_KEY", "")
BASE_URL = os.getenv("BASE_URL", "https://madam-dudu-astro-core-1.onrender.com")

@app.get("/health")
def health():
    return {"ok": True, "service": "Madam Dudu Astro Core Unified", "version": "3.0.0"}


@app.post("/render")
def render_chart(payload: dict = Body(...), Authorization: str | None = Header(default=None)):
    """
    Tek endpoint: hem gezegen konumlarını hesaplar (/compute),
    hem de PNG olarak doğum haritası çizer.
    """
    # --- Güvenlik kontrolü ---
    if not SERVICE_KEY:
        raise HTTPException(500, detail="API_KEY not set on server.")
    if Authorization is None or not Authorization.startswith("Bearer "):
        raise HTTPException(401, detail="Authorization: Bearer <API_KEY> header required.")
    if Authorization.split(" ", 1)[1] != SERVICE_KEY:
        raise HTTPException(403, detail="Invalid API_KEY.")

    # --- Giriş verileri kontrolü ---
    name = payload.get("name", "Unknown")
    dob = payload.get("dob")
    tob = payload.get("tob")
    city = payload.get("city")
    country = payload.get("country")

    if not all([dob, tob, city, country]):
        raise HTTPException(400, detail="Missing required fields: dob, tob, city, country.")

    # --- Eğer gezegen verileri yoksa, otomatik hesapla ---
    planets = payload.get("planets")
    if not planets:
        try:
            # Sunucunun kendi içinden /compute fonksiyonunu çağır
            from app import Input
            i = Input(name=name, dob=dob, tob=tob, city=city, country=country)
            compute_result = compute_fn(i, Authorization=f"Bearer {SERVICE_KEY}")
            planets = []
            planets.append({"name": "Sun", "ecliptic_long": compute_result["sun"]["ecliptic_long"]})
            planets.append({"name": "Moon", "ecliptic_long": compute_result["moon"]["ecliptic_long"]})
            for pname, pdata in compute_result["planets"].items():
                planets.append({"name": pname, "ecliptic_long": pdata["ecliptic_long"]})
        except Exception as e:
            raise HTTPException(500, detail=f"Failed to auto-compute planets: {str(e)}")

    # --- Çizimi oluştur ---
    img = draw_chart(
        planets=planets,
        name=name,
        dob=dob,
        tob=tob,
        city=city,
        country=country,
    )
    if isinstance(img, bytes):
        img = BytesIO(img)

    # --- PNG olarak döndür ---
    return StreamingResponse(img, media_type="image/png", headers={"Cache-Control": "no-store"})
