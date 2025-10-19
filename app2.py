# app2.py
from fastapi import FastAPI, Body, Header, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from chart_utils import draw_chart
from app import app as compute_app
from io import BytesIO
import os
import io
import uuid
import time
import traceback

# --- Ana Uygulama ---
app = FastAPI(
    title="Madam Dudu Astro Core Unified",
    version="3.2.0-debug",
    description="Unified API (deep debug) for Madam Dudu Astrology engine."
)

app.mount("/compute", compute_app)

SERVICE_KEY = os.getenv("API_KEY", "")
if not SERVICE_KEY:
    print("⚠️ WARNING: API_KEY not set. Set API_KEY in environment variables.")

TEMP_DIR = "/tmp/charts"
os.makedirs(TEMP_DIR, exist_ok=True)
os.chmod(TEMP_DIR, 0o777)
print(f"📁 TEMP_DIR initialized at {TEMP_DIR}")

app.mount("/charts", StaticFiles(directory=TEMP_DIR), name="charts")

def log_debug(msg: str):
    path = os.path.join(TEMP_DIR, "debug_log.txt")
    with open(path, "a") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    print(msg)

def cleanup_old_files():
    now = time.time()
    for fname in os.listdir(TEMP_DIR):
        fpath = os.path.join(TEMP_DIR, fname)
        if os.path.isfile(fpath) and now - os.path.getmtime(fpath) > 3600:
            os.remove(fpath)

@app.post("/render")
def render_chart(payload: dict = Body(...), Authorization: str | None = Header(default=None)):
    log_debug("🧠 /render endpoint triggered.")
    try:
        if not SERVICE_KEY:
            raise HTTPException(500, detail="API_KEY not set.")
        if Authorization is None or not Authorization.startswith("Bearer "):
            raise HTTPException(401, detail="Missing Bearer header.")
        if Authorization.split(" ", 1)[1] != SERVICE_KEY:
            raise HTTPException(403, detail="Invalid API_KEY.")

        planets = payload.get("planets")
        if not isinstance(planets, list) or not planets:
            raise HTTPException(400, detail="'planets' list is required.")

        log_debug(f"🪐 Planets received: {len(planets)} items.")

        try:
            log_debug("🎨 Calling draw_chart() ...")
            img_bytes = draw_chart(
                planets=planets,
                name=payload.get("name"),
                dob=payload.get("dob"),
                tob=payload.get("tob"),
                city=payload.get("city"),
                country=payload.get("country"),
            )
            log_debug(f"✅ draw_chart() returned type: {type(img_bytes)}")
        except Exception as e:
            tb = traceback.format_exc()
            error_log = os.path.join(TEMP_DIR, "errors.log")
            with open(error_log, "a") as f:
                f.write(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] DRAW_CHART ERROR:\n{tb}\n")
            log_debug(f"💥 draw_chart() failed: {e}")
            raise HTTPException(500, detail=f"Draw chart failed: {e}")

        if not isinstance(img_bytes, (bytes, bytearray)):
            log_debug("💥 draw_chart() did not return bytes.")
            raise HTTPException(500, detail="draw_chart() did not return valid bytes.")

        cleanup_old_files()
        file_id = uuid.uuid4().hex
        file_path = os.path.join(TEMP_DIR, f"chart_{file_id}.png")

        try:
            with open(file_path, "wb") as f:
                f.write(img_bytes)
            log_debug(f"💾 Chart saved: {file_path}")
        except Exception as e:
            log_debug(f"❌ Failed to save chart: {e}")
            raise HTTPException(500, detail=f"Could not write file.")

        public_url = f"https://madam-dudu-astro-core-1.onrender.com/charts/chart_{file_id}.png"
        log_debug(f"🌐 Returning URL: {public_url}")

        if payload.get("as_url", True):
            return JSONResponse({"url": public_url})
        else:
            return StreamingResponse(io.BytesIO(img_bytes), media_type="image/png")

    except HTTPException as e:
        log_debug(f"⚠️ HTTPException: {e.detail}")
        raise
    except Exception as e:
        tb = traceback.format_exc()
        log_debug(f"💥 Unhandled exception:\n{tb}")
        raise HTTPException(500, detail="Unexpected server error")

@app.get("/health")
def unified_health():
    return {"ok": True, "service": "Madam Dudu Astro Core Unified", "version": "3.2.0-debug"}
