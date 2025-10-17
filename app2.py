# app2.py
from fastapi import FastAPI, Body, Header, HTTPException
from fastapi.responses import StreamingResponse
from chart_utils import draw_chart
from io import BytesIO
import os

# 1) app.py içindeki mevcut uygulamayı içe al (hiç değiştirmiyoruz)
from app import app as compute_app  # /compute burada tanımlı

# 2) Yeni üst uygulama
app = FastAPI(title="Madam Dudu Unified", version="1.0.0")

# 3) Mevcut compute uygulamasını köke monte et (tüm /compute, /health vs. aynı kalır)
app.mount("/", compute_app)

# 4) Aynı API_KEY ile korunan /render ekle (PNG döndürür)
SERVICE_KEY = os.getenv("API_KEY", "")

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

    img = draw_chart(
        planets=planets,
        name=payload.get("name"),
        dob=payload.get("dob"),
        tob=payload.get("tob"),
        city=payload.get("city"),
        country=payload.get("country"),
    )
    if isinstance(img, bytes):
        img = BytesIO(img)

    return StreamingResponse(img, media_type="image/png", headers={"Cache-Control": "no-store"})
