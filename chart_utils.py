from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from chart_utils import draw_chart

import os

app = FastAPI()

# 🟢 charts klasörünü otomatik oluştur
os.makedirs("charts", exist_ok=True)

# 🟢 charts dizinini dışarıdan erişilebilir hale getir
app.mount("/charts", StaticFiles(directory="charts"), name="charts")


# 🧭 Temel model
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


@app.post("/render")
def render_chart(req: ChartRequest):
    result = draw_chart(
        planets=[p.model_dump() for p in req.planets],
        name=req.name,
        dob=req.dob,
        tob=req.tob,
        city=req.city,
        country=req.country
    )
    return result


@app.post("/compute")
def compute(req: ChartRequest):
    # Demo test modu için sadece inputu döndürüyoruz
    return {"message": "Compute endpoint aktif (Render test modunda).", "input": req.model_dump()}


@app.get("/debug/check-template")
def check_template():
    path = os.path.join(os.getcwd(), "chart_template.png")
    exists = os.path.exists(path)
    size = os.path.getsize(path) if exists else 0
    cwd = os.getcwd()
    files_in_dir = os.listdir(cwd)
    return {"exists": exists, "size_bytes": size, "path": path, "cwd": cwd, "files_in_dir": files_in_dir}
