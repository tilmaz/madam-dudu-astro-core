from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import logging
import os
from chart_utils import draw_chart

# === Charts klasörünü baştan oluştur (Render deploy hatasını önler) ===
os.makedirs("charts", exist_ok=True)

# === FastAPI uygulaması ===
app = FastAPI()

# === charts klasörünü dışarıya açıyoruz ===
app.mount("/charts", StaticFiles(directory="charts"), name="charts")

# === Logging ayarları ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# === Veri modelleri ===
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

class ComputeRequest(BaseModel):
    name: str
    dob: str
    tob: str
    city: str
    country: str

# === Endpoint: /compute ===
@app.post("/compute")
async def compute_chart(request: ComputeRequest):
    logging.info(f"🧮 Compute endpoint called with data: {request.dict()}")
    return {"input": request.dict()}

# === Endpoint: /render ===
@app.post("/render")
async def render_chart(request: ChartRequest):
    try:
        logging.info(f"🎨 Rendering chart for {request.name} ({request.dob} @ {request.tob}, {request.city}, {request.country})")
        logging.info("=== 🌌 DRAW_CHART STARTED ===")

        output_path = draw_chart(
            name=request.name,
            dob=request.dob,
            tob=request.tob,
            city=request.city,
            country=request.country,
            planets=[p.dict() for p in request.planets]
        )

        chart_url = f"https://madam-dudu-astro-core-1.onrender.com/{output_path}"
        logging.info(f"✅ Chart başarıyla kaydedildi: {output_path}")
        logging.info("=== ✅ DRAW_CHART TAMAMLANDI ===")

        return {
            "text": f"{request.name}'s chart generated successfully.",
            "chart_url": chart_url
        }

    except Exception as e:
        logging.error(f"❌ Error generating chart: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})

# === Health Check ===
@app.get("/")
async def root():
    return {"status": "OK", "message": "Madam Dudu Astro Core is running 🚀"}
