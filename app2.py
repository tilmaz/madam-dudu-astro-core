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
import logging

# --- Logging ayarı ---
logging.basicConfig(level=logging.DEBUG)

# --- Ana Uygulama ---
app = FastAPI(
    title="Madam Dudu Astro Core Unified",
    version="3.1.0",
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
try:
    os.makedirs(TEMP_DIR, exist_ok=True)
    os.chmod(TEMP_DIR, 0o777)  # Herkese yazma izni
    print(f"📁 TEMP_DIR initialized at {TEMP_DIR}")
except Exception as e:
    print(f"❌ Failed to create TEMP_DIR: {e}")

# --- Statik dosyaları servis et (görseli ve logları göstermek için) ---
app.mount("/charts", StaticFiles(directory=TEMP_DIR), name="charts")

# --- Eski dosyaları temizle ---
def cleanup_old_files():
    now = time.time()
    for fname in os.listdir(TEMP_DIR):
        fpath = os.path.join(TEMP_DIR, fname)
        if os.path.isfile(fpath):
            if now - os.path.getmtime(fpath) > 3600:  # 1 saat
                try:
                    os.remove(fpath)
                except Exception as e:
                    print(f"⚠️ Cleanup failed for {fname}: {e}")

# --- Render Endpoint ---
@app.post("/render")
def render_chart(payload: dict = Body(...), Authorization: str | None = Header(default=None)):
    try:
        # --- API key kontrolü ---
        if not SERVICE_KEY:
            raise HTTPException(500, detail="API_KEY not set on server.")
        if Authorization is None or not Authorization.startswith("Bearer "):
            raise HTTPException(401, detail="Authorization: Bearer <API_KEY> header required.")
        if Authorization.split(" ", 1)[1] != SERVICE_KEY:
            raise HTTPException(403, detail="Invalid API_KEY.")

        # --- Planet verisi kontrolü ---
        planets = payload.get("planets")
        if not isinstance(planets, list) or not planets:
            raise HTTPException(400, detail="'planets' list is required.")

        # --- draw_chart() güvenli çağırma ---
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
            print(f"💥 DRAW_CHART ERROR:\n{tb}")
            try:
                log_path = os.path.join(TEMP_DIR, "errors.log")
                with open(log_path, "a") as log_file:
                    log_file.write("\n\n==== DRAW_CHART ERROR ====\n")
                    log_file.write(tb)
                    log_file.write("\n===========================\n")
                print(f"🧾 Error saved to {log_path}")
            except Exception as log_err:
                print(f"⚠️ Could not write error log: {log_err}")
            raise HTTPException(500, detail=f"Draw chart failed: {e}")

        # --- Byte dönüşüm kontrolü ---
        if not isinstance(img_bytes, (bytes, bytearray)):
            raise HTTPException(500, detail="draw_chart() did not return valid bytes.")

        # --- Geçici PNG kaydet ---
        cleanup_old_files()
        file_id = uuid.uuid4().hex
        file_path = os.path.join(TEMP_DIR, f"chart_{file_id}.png")

        try:
            with open(file_path, "wb") as f:
                f.write(img_bytes)
        except Exception as e:
            print(f"❌ Failed to write file: {e}")
            raise HTTPException(500, detail=f"Could not write file to {TEMP_DIR}")

        # --- Public URL oluştur ---
        public_url = f"https://madam-dudu-astro-core-1.onrender.com/charts/chart_{file_id}.png"

        # --- JSON veya direkt görsel döndür ---
        if payload.get("as_url", True):
            return JSONResponse({"url": public_url})
        else:
            return StreamingResponse(io.BytesIO(img_bytes), media_type="image/png")

    except HTTPException:
        raise
    except Exception as e:
        # Genel hata yakalayıcı
        error_detail = traceback.format_exc()
        print(f"💥 Internal Server Error:\n{error_detail}")
        try:
            log_path = os.path.join(TEMP_DIR, "errors.log")
            with open(log_path, "a") as log_file:
                log_file.write("\n\n==== INTERNAL ERROR ====\n")
                log_file.write(error_detail)
                log_file.write("\n=========================\n")
        except Exception as log_err:
            print(f"⚠️ Could not write internal error log: {log_err}")
        raise HTTPException(500, detail=f"Unexpected server error: {str(e)}")

# --- Sağlık kontrolü ---
@app.get("/health")
def unified_health():
    return {"ok": True, "service": "Madam Dudu Astro Core Unified", "version": "3.1.0"}
