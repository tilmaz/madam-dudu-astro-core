from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from chart_utils import draw_chart
import os

app = FastAPI(
    title="Madam Dudu Astro Core Unified",
    description="Unified astrology engine for Madam Dudu GPT — v4.0.1 FINAL",
    version="4.0.1"
)

# ✅ Statik dosyalar klasörü (chart görüntüleri)
charts_dir = os.path.join(os.getcwd(), "charts")
os.makedirs(charts_dir, exist_ok=True)

app.mount("/charts", StaticFiles(directory=charts_dir), name="charts")


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


# 🔹 Sağlık testi
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "Madam Dudu Astro Core",
        "message": "Render servisi aktif ve çalışıyor 🚀"
    }


# 🔹 Compute test endpoint
@app.post("/compute")
async def compute_chart(data: dict):
    return {
        "message": "Compute endpoint aktif (Render test modunda).",
        "input": data
    }


# 🔹 Doğum haritası oluşturma
@app.post("/render")
async def render_chart(request: ChartRequest):
    """
    Doğum haritasını çizer, PNG olarak kaydeder ve erişilebilir URL döndürür.
    """
    try:
        result = draw_chart(
            planets=[p.dict() for p in request.planets],
            name=request.name,
            dob=request.dob,
            tob=request.tob,
            city=request.city,
            country=request.country
        )

        # Eğer draw_chart "charts/" ile başlayan path döndürdüyse
        # onu tam URL haline getirelim:
        file_url = result.get("url")
        if not file_url.startswith("/"):
            file_url = "/" + file_url

        # 🔹 Render URL (tam erişim linki)
        base_url = "https://madam-dudu-astro-core-1.onrender.com"
        full_url = base_url + file_url

        return {"url": full_url}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "message": "Chart render sırasında hata oluştu."
            }
        )


# 🔹 Ana sayfa
@app.get("/")
async def root():
    return {
        "message": "🌌 Madam Dudu Astro Core API v4.0.1",
        "routes": {
            "/health": "Servis durumu kontrolü",
            "/compute": "Gezegen verisi testi",
            "/render": "Doğum haritası oluşturur (chart_utils v4.0-final)"
        }
    }
