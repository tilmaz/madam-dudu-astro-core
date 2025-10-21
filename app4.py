# app4.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from chart_utils import draw_chart
from io import BytesIO
from PIL import Image
import logging
import os

# --- LOG ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

app = FastAPI()

# --- CHARTS DİZİNİ ---
CHART_DIR = "charts"
os.makedirs(CHART_DIR, exist_ok=True)

# --- STATİK ---
app.mount("/charts", StaticFiles(directory=CHART_DIR), name="charts")

# --- MODELLER ---
class Planet(BaseModel):
    name: str
    ecliptic_long: float

class ChartRequest(BaseModel):
    name: str
    dob: str
    tob: str
    city: str
    country: str
    planets: list[Planet]

# --- Savunmacı tip dönüştürücü ---
def _to_bytes_io(maybe):
    if isinstance(maybe, BytesIO):
        return maybe
    if isinstance(maybe, (bytes, bytearray)):
        return BytesIO(maybe)
    if isinstance(maybe, Image.Image):
        bio = BytesIO()
        maybe.save(bio, format="PNG")
        bio.seek(0)
        return bio
    if maybe is None:
        raise TypeError("draw_chart returned None")
    raise TypeError(f"draw_chart returned unexpected type: {type(maybe)}")

# === ENDPOINTLER ===
@app.post("/compute")
async def compute_chart(request: Request):
    data = await request.json()
    logging.info(f"🧮 Compute endpoint called with data: {data}")
    return {"input": data}

@app.post("/render")
async def render_chart(request: ChartRequest):
    logging.info(f"🎨 Rendering chart for {request.name} ({request.dob} @ {request.tob}, {request.city}, {request.country})")
    logging.info("=== 🌌 DRAW_CHART STARTED ===")
    try:
        # ÇİZİM
        buffer = draw_chart(
            planets=[p.dict() for p in request.planets],
            name=request.name, dob=request.dob, tob=request.tob,
            city=request.city, country=request.country,
        )
        # Tipi normalize et
        try:
            buffer = _to_bytes_io(buffer)
        except Exception as te:
            logging.error(f"❌ draw_chart çıktı tipi hatalı: {te}")
            return JSONResponse(status_code=500, content={"error": "Invalid chart output type."})

        # PNG olarak kaydet
        safe_name = "".join(c for c in request.name.lower() if c.isalnum() or c in ("-", "_"))
        file_path = os.path.join(CHART_DIR, f"chart_{safe_name}_final.png")
        with open(file_path, "wb") as f:
            f.write(buffer.getbuffer())

        logging.info(f"✅ Chart kaydedildi: {file_path}")
        logging.info("=== ✅ DRAW_CHART TAMAMLANDI ===")

        base_url = os.getenv("BASE_URL", "https://madam-dudu-astro-core-1.onrender.com")
        return {"text": f"{request.name}'s chart generated successfully.", "chart_url": f"{base_url}/{file_path}"}

    except Exception as e:
        logging.exception("❌ Error generating chart")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/")
def home():
    return {"status": "ok", "message": "Madam Dudu Astro Core is running 🎨"}

# HEAD / için 200 ver (health-check 405 almasın)
@app.head("/")
def home_head():
    return ""
