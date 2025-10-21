from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from chart_utils import draw_chart
import logging
import os
from io import BytesIO

# --- LOG AYARLARI ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

app = FastAPI()

# --- CHARTS DİZİNİ GÜVENLİ ŞEKİLDE OLUŞTUR ---
CHART_DIR = "charts"
os.makedirs(CHART_DIR, exist_ok=True)

# --- STATİK DOSYALAR ---
app.mount("/charts", StaticFiles(directory=CHART_DIR), name="charts")


# === MODELLER ===
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


# === ENDPOINTLER ===
@app.post("/compute")
async def compute_chart(request: Request):
    data = await request.json()
    logging.info(f"🧮 Compute endpoint called with data: {data}")
    return {"input": data}


@app.post("/render")
async def render_chart(request: ChartRequest):
    logging.info(f"🎨 Rendering chart for {request.name} ({request.dob} @ {request.tob}, {request.city}, {request.country})")
    logging.info("=== 🌌 DRAW_CHART STARTEDD ===")

    try:
        # --- CHART ÇİZİMİ ---
        buffer = draw_chart(
            planets=[p.dict() for p in request.planets],
            name=request.name,
            dob=request.dob,
            tob=request.tob,
            city=request.city,
            country=request.country,
        )

        if not isinstance(buffer, BytesIO):
            logging.error("❌ draw_chart() BytesIO döndürmedi!")
            return JSONResponse(status_code=500, content={"error": "Invalid chart output type."})

        # --- PNG OLARAK KAYDET ---
        file_path = os.path.join(CHART_DIR, f"chart_{request.name.lower()}_final.png")
        with open(file_path, "wb") as f:
            f.write(buffer.getbuffer())

        logging.info(f"✅ Chart başarıyla kaydedildi: {file_path}")
        logging.info("=== ✅ DRAW_CHART TAMAMLANDI ===")

        # --- BAŞARILI YANIT ---
        return {
            "text": f"{request.name}'s chart generated successfully.",
            "chart_url": f"https://madam-dudu-astro-core-1.onrender.com/{file_path}"
        }

    except Exception as e:
        logging.exception("❌ Error generating chart")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/")
def home():
    return {"status": "ok", "message": "Madam Dudu Astro Core is running 🎨"}
