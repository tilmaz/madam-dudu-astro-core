# app2.py
from fastapi import FastAPI, Body, Header, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from chart_utils import draw_chart
from io import BytesIO
from datetime import datetime, timedelta
from threading import Thread
import os, time

# 1️⃣ app.py (hesaplama motoru) import edilir
from app import app as compute_app

# 2️⃣ Ana birleşik uygulama
app = FastAPI(title="Madam Dudu Unified", version="1.0.4")

# 3️⃣ Alt rotaları (health, compute) dahil et
app.include_router(compute_app.router)

# 4️⃣ Ortak API anahtarı
SERVICE_KEY = os.getenv("API_KEY", "")

# 5️⃣ Statik klasör (render edilmiş PNG'ler)
STATIC_DIR = "./static"
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 6️⃣ Arka planda çalışan temizlik işlevi
def cleanup_old_files():
    """Her saat başı static klasöründeki 1 saatten eski PNG'leri siler."""
    while True:
        now = time.time()
        deleted = 0
        for f in os.listdir(STATIC_DIR):
            if not f.lower().endswith(".png"):
                continue
            path = os.path.join(STATIC_DIR, f)
            try:
                if os.path.isfile(path) and now - os.path.getmtime(path) > 3600:
                    os.remove(path)
                    deleted += 1
            except Exception:
                pass
        if deleted:
            print(f"[CLEANUP] {deleted} eski PNG silindi.")
        time.sleep(3600)  # 1 saatte bir çalışır

Thread(target=cleanup_old_files, daemon=True).start()


# 7️⃣ /render endpoint — PNG üretir ve URL döndürür
@app.post("/render")
def render_chart(payload: dict = Body(...), Authorization: str | None = Header(default=None)):
    """
    /render endpoint:
    - Authorization: Bearer <API_KEY> header zorunlu
    - Body: { name, dob, tob, city, country, planets: [...] }
    - Output: { "url": "https://.../static/chart_YYYYMMDD_HHMMSS.png" }
    """
    # --- Kimlik doğrulama ---
    if not SERVICE_KEY:
        raise HTTPException(500, detail="API_KEY not set on server.")
    if Authorization is None or not Authorization.startswith("Bearer "):
        raise HTTPException(401, detail="Authorization: Bearer <API_KEY> header required.")
    if Authorization.split(" ", 1)[1] != SERVICE_KEY:
        raise HTTPException(403, detail="Invalid API_KEY.")

    # --- Gezegen verisi kontrolü ---
    planets = payload.get("planets")
    if not isinstance(planets, list) or not planets:
        raise HTTPException(400, detail="'planets' list is required.")

    # --- Haritayı çiz ---
    img_io = draw_chart(
        planets=planets,
        name=payload.get("name"),
        dob=payload.get("dob"),
        tob=payload.get("tob"),
        city=payload.get("city"),
        country=payload.get("country"),
    )
    if isinstance(img_io, bytes):
        img_io = BytesIO(img_io)
    img_io.seek(0)

    # --- Dosyayı kaydet ---
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    fname = f"chart_{ts}.png"
    fpath = os.path.join(STATIC_DIR, fname)
    with open(fpath, "wb") as f:
        f.write(img_io.read())

    # --- URL üret ---
    base_url = os.getenv("RENDER_URL", "https://madam-dudu-astro-core-1.onrender.com")
    file_url = f"{base_url}/static/{fname}"

    return JSONResponse(content={"url": file_url})
