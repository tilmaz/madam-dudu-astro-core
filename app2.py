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
import traceback

# --- Ana Uygulama ---
app = FastAPI(
    title="Madam Dudu Astro Core Unified",
    version="3.1.0-debug",
    description="Unified API: combines computation (/compute) and rendering (/render) for Madam Dudu Astrology engine (debug mode)."
)

# --- compute_app rotalarını ekle (/compute ve /health dahil) ---
app.mount("/compute", compute_app)

# --- API Key doğrulaması ---
SERVICE_KEY = os.getenv("API_KEY", "")
if not SERVICE_KEY:
    print("⚠️ WARNING: API_KEY not set. Set API_KEY in environment variables.")

# --- Geçici klasör oluştur (chart PNG saklama) ---
TEMP_DIR = "/tmp/charts"
try:
    os.makedirs(TEMP_DIR, exist_ok=True)
    os.chmod(TEMP_DIR, 0o777)
    print(f"📁 TEMP_DIR initialized at {TEMP_DIR}")
except Exception as e:
    print(f"❌ Failed to create TEMP_DIR: {e}")

# --- Statik dosyaları servis et ---
app.mount("/charts", StaticFiles(directory=TEMP_DIR), name="charts")

# --- Zaman damgasına göre eski dosyaları temizle ---
def cleanup_old_files():
    now = time.time()
    for fname in os.listdir(TEMP_DIR):
        fpath = os.path.join(TEMP_DIR, fname)
        if os.path.isfile(fpath):
            if now - os.path.getmtime(fpath) > 3600:
                try:
                    os.remove(fpath)
                except Exception as e:
                    print(f"⚠️ Cleanup failed for {fname}: {e}")

# --- Render Endpoint ---
@app.post("/render")
def render_chart(payload: dict = Body(...), Authorization: str | None = Header(default=None)):
    # 🧠 Debug log oluştur
    log_path = os.path.join(TEMP_DIR, "debug_log.txt")
    with open(log_path, "a") as f:
        f.write(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] /render called.\n")

    print("🧠 /render endpoint triggered.")

    try:
        if not SERVICE_KEY:
            raise HTTPException(500, detail="API_KEY not set on server.")
        if Authorization is None or not Authorization.startswith("Bearer "):
            raise HTTPException(401, detail="Authorization: Bearer <API_KEY> header required.")
        if Authorization.split(" ", 1)[1] != SERVICE_KEY:
            raise HTTPException(403, detail="Invalid API_KEY.")

        planets = payload.get("planets")
        if not isinstance(planets, list) or not planets:
            raise HTTPException(400, detail="'planets' list is required.")

        # --- draw_chart() hata yakalama ---
        try:
            img_bytes = draw_chart(
                planets=planets,
                name=payload.get("name"),
                dob=payload.get("dob"),
                tob=payload.get("tob"),
                city=payload.get("city"),
                country=payload.get("country"),
            )
        except Exception as e:
            tb = traceback.format_exc()
            error_log = os.path.join(TEMP_DIR, "errors.log")
            with open(error_log, "a") as f:
                f.write(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] DRAW_CHART ERROR:\n{tb}\n")
            print(f"💥 DRAW_CHART ERROR:\n{tb}")
            raise HTTPException(500, detail=f"Draw chart failed: {e}")

        # Byte kontrolü
        if not isinstance(img_bytes, (bytes, bytearray)):
            raise HTTPException(500, detail="draw_chart() did not return valid bytes.")

        # PNG dosyasını kaydet
        cleanup_old_files()
        file_id = uuid.uuid4().hex
        file_path = os.path.join(TEMP_DIR, f"chart_{file_id}.png")

        try:
            with open(file_path, "wb") as f:
                f.write(img_bytes)
        except Exception as e:
            with open(log_path, "a") as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ❌ Failed to write chart: {e}\n")
            raise HTTPException(500, detail=f"Could not write file to {TEMP_DIR}")

        public_url = f"https://madam-dudu-astro-core-1.onrender.com/charts/chart_{file_id}.png"

        # Sonuç döndür
        if payload.get("as_url", True):
            return JSONResponse({"url": public_url})
        else:
            return StreamingResponse(io.BytesIO(img_bytes), media_type="image/png")

    except HTTPException:
        raise
    except Exception as e:
        tb = traceback.format_exc()
        with open(log_path, "a") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 💥 Internal Server Error:\n{tb}\n")
        print(f"💥 INTERNAL ERROR:\n{tb}")
        raise HTTPException(500, detail=f"Unexpected server error: {str(e)}")

# --- Sağlık kontrolü ---
@app.get("/health")
def unified_health():
    return {"ok": True, "service": "Madam Dudu Astro Core Unified", "version": "3.1.0-debug"}
