from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from chart_utils import draw_chart
import os

app = FastAPI(
    title="Madam Dudu Astro Core Unified",
    description="Unified astrology engine for Madam Dudu GPT.",
    version="3.3.1"
)

# ✅ Statik dosyalar klasörü (chart görüntüleri)
CHARTS_DIR = os.path.join(os.getcwd(), "charts")

if not os.path.exists(CHARTS_DIR):
    os.makedirs(CHARTS_DIR)

# 🔧 Render'da tam yol kullanarak statik dosya bağla
app.mount("/charts", StaticFiles(directory=CHARTS_DIR), name="charts")


# 🔹 Model tanımları
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


# 🔹 Sağlık testi (Render kontrolü)
@app.get("/health")
async def health_check():
    """Render servisinin çalıştığını doğrular."""
    return {
        "status": "ok",
        "service": "Madam Dudu Astro Core",
        "message": "Render servisi aktif ve çalışıyor 🚀"
    }


# 🔹 Debug endpoint (compute testi)
@app.post("/compute")
async def compute_chart(data: dict):
    """Test amaçlı hesaplama endpoint’i."""
    return {
        "message": "Compute endpoint aktif (Render test modunda).",
        "input": data
    }


# 🔹 Doğum haritası oluşturma
@app.post("/render")
async def render_chart(request: ChartRequest):
    """
    Doğum haritasını çizer, PNG olarak kaydeder ve URL döndürür.
    """
    try:
        chart_data = draw_chart(
            planets=[p.dict() for p in request.planets],
            name=request.name,
            dob=request.dob,
            tob=request.tob,
            city=request.city,
            country=request.country
        )
        return chart_data
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "message": "Chart render sırasında hata oluştu."}
        )


# 🔹 Ana sayfa (isteğe bağlı açıklama)
@app.get("/")
async def root():
    return {
        "message": "🌌 Madam Dudu Astro Core API v3.3.1",
        "routes": {
            "/health": "Servis durumu kontrolü",
            "/compute": "Gezegen verisi testi",
            "/render": "Doğum haritası oluşturur"
        }
    }
