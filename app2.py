# app2.py
from fastapi import FastAPI, Body, Header, HTTPException
from fastapi.responses import StreamingResponse
from chart_utils import draw_chart
from io import BytesIO
import os

# --- Mevcut FastAPI uygulamasını (app.py) içe aktar ---
from app import app as compute_app  # /compute, /health rotalarını getirir

# --- Yeni birleşik üst uygulama ---
app = FastAPI(title="Madam Dudu Unified", version="1.0.2")

# --- Alt uygulamayı dahil et (/compute ve /health) ---
app.include_router(compute_app.router)

# --- Ortak API anahtarı ---
SERVICE_KEY = os.getenv("API_KEY", "")


@app.post("/render")
def render_chart(payload: dict = Body(...), Authorization: str | None = Header(default=None)):
    """
    /render uç noktası:
    - Authorization: Bearer <API_KEY> zorunlu
    - Gövde: {
        "name": "...",
        "dob": "YYYY-MM-DD",
        "tob": "HH:MM",
        "city": "...",
        "country": "...",
        "planets": [{"name":"Sun","ecliptic_long":311.53}, ...]
      }
    """
    # --- Kimlik doğrulama ---
    if not SERVICE_KEY:
        raise HTTPException(status_code=500, detail="API_KEY not set on server.")
    if Authorization is None or not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization: Bearer <API_KEY> header required.")
    if Authorization.split(" ", 1)[1] != SERVICE_KEY:
        raise HTTPException(status_code=403, detail="Invalid API_KEY.")

    # --- Gezegen verisi kontrolü ---
    planets = payload.get("planets")
    if not isinstance(planets, list) or not planets:
        raise HTTPException(status_code=400, detail="'planets' list is required.")

    # --- Çizim ---
    img_io = draw_chart(
        planets=planets,
        name=payload.get("name"),
        dob=payload.get("dob"),
        tob=payload.get("tob"),
        city=payload.get("city"),
        country=payload.get("country"),
    )

    # draw_chart hem BytesIO hem bytes döndürebilir
    if isinstance(img_io, bytes):
        img_io = BytesIO(img_io)
    img_io.seek(0)

    # --- PNG çıktısını StreamingResponse olarak döndür ---
    return StreamingResponse(
        img_io,
        media_type="image/png",
        headers={"Cache-Control": "no-store"}
    )
