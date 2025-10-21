from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from chart_utils import draw_chart
import logging
import os

app = FastAPI()
from fastapi.staticfiles import StaticFiles
app.mount("/charts", StaticFiles(directory="charts"), name="charts")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# === MODELS ===
class PlanetData(BaseModel):
    name: str
    ecliptic_long: float

class ChartRequest(BaseModel):
    name: str
    dob: str
    tob: str
    city: str
    country: str
    planets: list[PlanetData]

# === ROUTES ===
@app.get("/")
async def root():
    return {"message": "Madam Dudu Natal Chart API v4 — active and ready 🌙"}

@app.post("/render")
async def render_chart(request: ChartRequest):
    try:
        logging.info(f"🎨 Rendering chart for {request.name} ({request.dob} @ {request.tob}, {request.city}, {request.country})")

        # Görsel dosyasını oluştur
        output_path = draw_chart(
            name=request.name,
            dob=request.dob,
            tob=request.tob,
            city=request.city,
            country=request.country,
            planets=[p.dict() for p in request.planets]
        )

        # 🔁 Tam URL'yi oluştur (Render URL’si dahil)
        full_url = f"https://madam-dudu-astro-core-1.onrender.com/{output_path}"

        logging.info(f"✅ Chart successfully generated and saved at: {full_url}")

        # ✅ Artık JSON formatında döndür (PowerShell için uygun)
        return {
            "text": f"{request.name}'s chart generated successfully.",
            "chart_url": full_url
        }

    except Exception as e:
        logging.exception("❌ Error generating chart")
        return JSONResponse(status_code=500, content={"error": str(e)})

# === OPTIONAL: /compute endpoint sadece test amaçlı ===
@app.post("/compute")
async def compute_chart(request: Request):
    data = await request.json()
    logging.info(f"🧮 Compute endpoint called with data: {data}")
    return {"input": data}
