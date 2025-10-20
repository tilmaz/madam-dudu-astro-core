from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from chart_utils import draw_chart
import os

app = FastAPI(
    title="Madam Dudu Astro Core",
    description="Astrolojik doğum haritası hesaplama ve görselleştirme servisi.",
    version="3.0"
)

# 🟢 'charts' klasörünü oluştur (resimler buraya kaydediliyor)
os.makedirs("charts", exist_ok=True)

# 🟢 Statik dosya servisi (görselleri URL'den göstermek için)
app.mount("/charts", StaticFiles(directory="charts"), name="charts")

# 🧩 Veri modelleri
class Planet(BaseModel):
    name: str
    ecliptic_long: float | None = None


class ChartRequest(BaseModel):
    name: str
    dob: str
    tob: str
    city: str
    country: str
    planets: list[Planet] = []


# 🪐 Hesaplama endpoint’i
@app.post("/compute")
def compute(req: ChartRequest):
    """
    Gelecekte doğum verilerini hesaplayacak.
    Şimdilik test için sadece input'u döndürüyor.
    """
    return {
        "message": "Compute endpoint aktif (Render test modunda).",
        "input": req.model_dump()
    }


# 🖼️ Görsel oluşturma endpoint’i
@app.post("/render")
def render_chart(req: ChartRequest):
    """
    Doğum haritası görselini oluşturur.
    Planets listesi verilmelidir.
    """
    result = draw_chart(
        planets=[p.model_dump() for p in req.planets],
        name=req.name,
        dob=req.dob,
        tob=req.tob,
        city=req.city,
        country=req.country
    )
    return result


# 🔍 Template dosyasını kontrol et (debug amaçlı)
@app.get("/debug/check-template")
def check_template():
    """
    chart_template.png dosyası sistemde var mı diye kontrol eder.
    """
    path = os.path.join(os.getcwd(), "chart_template.png")
    exists = os.path.exists(path)
    size = os.path.getsize(path) if exists else 0
    cwd = os.getcwd()
    files_in_dir = os.listdir(cwd)
    return {
        "exists": exists,
        "size_bytes": size,
        "path": path,
        "cwd": cwd,
        "files_in_dir": files_in_dir
    }


# 🧠 Health check
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "App3 is running!"}
