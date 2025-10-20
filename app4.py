from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
from chart_utils_v6 import draw_chart
import math

app = FastAPI(
    title="Madam Dudu Astro Core Unified (v4.0)",
    description="Text + Visual integrated natal chart generator.",
    version="4.0"
)

# Statik dosya dizini
if not os.path.exists("charts"):
    os.makedirs("charts")
app.mount("/charts", StaticFiles(directory="charts"), name="charts")


# MODELLER
class Planet(BaseModel):
    name: str
    ecliptic_long: float
    retrograde: bool = False


class ChartRequest(BaseModel):
    name: str
    dob: str
    tob: str
    city: str
    country: str
    planets: list[Planet]
    houses: list[float] = []
    signs: list[str] = []


# Yardımcı Fonksiyonlar
def format_deg(deg: float) -> str:
    """Dereceyi 00°00′ formatına çevirir."""
    d = int(deg)
    m = int((deg - d) * 60)
    return f"{d:02d}°{m:02d}′"


ZODIAC_SIGNS = [
    "♈ Aries", "♉ Taurus", "♊ Gemini", "♋ Cancer", "♌ Leo", "♍ Virgo",
    "♎ Libra", "♏ Scorpio", "♐ Sagittarius", "♑ Capricorn", "♒ Aquarius", "♓ Pisces"
]


def get_zodiac_position(longitude: float) -> str:
    sign_index = int(longitude // 30)
    deg_in_sign = longitude % 30
    return f"{ZODIAC_SIGNS[sign_index]} {format_deg(deg_in_sign)}"


# ENDPOINTLER
@app.get("/")
async def root():
    return {
        "service": "Madam Dudu Astro Core Unified v4.0",
        "routes": {
            "/compute": "Compute planetary positions",
            "/render": "Generate visual chart",
            "/chart": "Generate full text + image"
        }
    }


@app.post("/compute")
async def compute_chart(data: dict):
    """Test amaçlı veri döndürür"""
    return {
        "message": "Compute endpoint aktif (Render test modunda).",
        "input": data
    }


@app.post("/render")
async def render_chart(request: ChartRequest):
    """PNG olarak doğum haritası çizer."""
    try:
        result = draw_chart(
            planets=[p.dict() for p in request.planets],
            name=request.name,
            dob=request.dob,
            tob=request.tob,
            city=request.city,
            country=request.country
        )
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/chart")
async def full_chart(request: ChartRequest):
    """Metin + Görsel birleşik çıktı"""
    try:
        # 🌞 Core placements (örnek format)
        core = {
            "Sun": get_zodiac_position(request.planets[0].ecliptic_long),
            "Moon": get_zodiac_position(request.planets[1].ecliptic_long),
            "ASC": get_zodiac_position(request.houses[0]) if request.houses else "—",
            "MC": get_zodiac_position(request.houses[9]) if len(request.houses) >= 10 else "—",
        }

        # 🌌 Houses
        houses = []
        for i, cusp in enumerate(request.houses, 1):
            houses.append(f"{i}th: {get_zodiac_position(cusp)}")

        # 🪐 Planets
        planet_lines = []
        for p in request.planets:
            pos = get_zodiac_position(p.ecliptic_long)
            rx = " ℞" if p.retrograde else ""
            planet_lines.append(f"• {p.name}: {pos}{rx}")

        # 🎨 Görsel haritayı oluştur
        chart_data = draw_chart(
            planets=[p.dict() for p in request.planets],
            name=request.name,
            dob=request.dob,
            tob=request.tob,
            city=request.city,
            country=request.country
        )

        # ✨ Nihai metin çıktısı
        text_output = f"""
{request.name}'s Natal Chart
Date: {request.dob}
Time: {request.tob}
Location: {request.city}, {request.country}

Core Placements:
• Sun: {core['Sun']}
• Moon: {core['Moon']}
• Ascendant (ASC): {core['ASC']}
• Midheaven (MC): {core['MC']}

Houses:
{chr(10).join(houses)}

Planets:
{chr(10).join(planet_lines)}

🔗 Doğum Haritasını Görüntüle:
👉 {chart_data['url']}
        """.strip()

        return {"text": text_output, "chart_url": chart_data["url"]}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "message": "Chart oluşturulurken hata oluştu."}
        )
