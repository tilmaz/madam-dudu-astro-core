# app2.py
from fastapi import FastAPI, Body, Header, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from chart_utils import draw_chart
from app import app as compute_app  # /compute ve /health rotalarını buradan alır
from io import BytesIO
import os
import io
import uuid
import time

# --- Ana Uygulama ---
app = FastAPI(
    title="Madam Dudu Astro Core Unified",
    version="3.0.0",
    description="Unified API: combines computation (/compute) and rendering (/render) for Madam Dudu Astrology engine."
)

# --- compute_app rotalarını ekle (/compute ve /health dahil) ---
app.mount("/compute", compute_app)

# --- API Key doğrulaması ---
SERVICE_KEY = os.getenv("API_KEY", "")
if not SERVICE_KEY:
    print("⚠️ WARNING: API_KEY not set. Set API_KEY in environment variables.")

# --- Geçici klasör oluştur (chart PNG saklama) ---
TEMP_DIR = "/tmp/charts"
os.makedirs(TEMP_DIR, exist_ok=True)

# --- Statik dosyaları servis et (görseli URL olarak gösterebilmek için) ---
app.mount("/charts", StaticFiles(directory=TEMP_DIR), name="charts")

# --- Zaman damgasına göre eski dosyaları temizle ---
def cleanup_old_files():
    now = time.time()
    for fname in os.listdir(TEMP_DIR):
        fpath = os.path.join(TEMP_DIR, fname)
        if os.path.isfile(fpath):
            if now - os.path.getmtime(fpath) > 3600:  # 1 saat
                os.remove(fpath)

# --- Render Endpoint ---
@app.post("/render")
def render_chart(payload: dict = Body(...), Authorization: str | None = Header(default=None)):
    if not SERVICE_KEY:
        raise HTTPException(500, detail="API_KEY not set on server.")
    if Authorization is None or not Authorization.startswith("Bearer "):
        raise HTTPException(401, detail="Authorization: Bearer <API_KEY> header required.")
    if Authorization.split(" ", 1)[1] != SERVICE_KEY:
        raise HTTPException(403, detail="Invalid API_KEY.")

    planets = payload.get("planets")
    if not isinstance(planets, list) or not planets:
        raise HTTPException(400, detail="'planets' list is required.")

    img_bytes = draw_chart(
        planets=planets,
        name=payload.get("name"),
        dob=payload.get("dob"),
        tob=payload.get("tob"),
        city=payload.get("city"),
        country=payload.get("country"),
    )

    # Byte dönüştürme
    if not isinstance(img_bytes, (bytes, bytearray)):
        raise HTTPException(500, detail="draw_chart() did not return valid bytes.")

    # Geçici PNG kaydet
    cleanup_old_files()
    file_id = uuid.uuid4().hex
    file_path = os.path.join(TEMP_DIR, f"chart_{file_id}.png")
    with open(file_path, "wb") as f:
        f.write(img_bytes)

    public_url = f"https://madam-dudu-astro-core-1.onrender.com/charts/chart_{file_id}.png"

    # İki opsiyonlu dönüş:
    # 1️⃣ Görsel direkt (StreamingResponse)
    # 2️⃣ JSON içinde URL (kolay erişim için)
    if payload.get("as_url", True):
        return JSONResponse({"url": public_url})
    else:
        return StreamingResponse(io.BytesIO(img_bytes), media_type="image/png")

# --- Sağlık kontrolü ---
@app.get("/health")
def unified_health():
    return {"ok": True, "service": "Madam Dudu Astro Core Unified", "version": "3.0.0"}

