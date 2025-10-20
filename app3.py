import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from chart_utils import draw_chart

app = FastAPI(title="Madam Dudu Astro Core Unified")

# 🌐 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🖼️ STATIC FILE SERVING (charts klasörü)
charts_path = os.path.join(os.path.dirname(__file__), "charts")
os.makedirs(charts_path, exist_ok=True)
app.mount("/charts", StaticFiles(directory=charts_path), name="charts")


@app.get("/health")
async def health():
    return {
        "ok": True,
        "service": "Madam Dudu Astro Core Unified",
        "version": "3.2.0"
    }


@app.post("/compute")
async def compute_chart(request: Request):
    try:
        data = await request.json()
        return JSONResponse(
            content={
                "message": "Compute endpoint aktif (Render test modunda).",
                "input": data
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/render")
async def render_chart(request: Request):
    try:
        data = await request.json()
        planets = data.get("planets")
        if not planets:
            raise ValueError("Missing 'planets' in request body")

        result = draw_chart(planets)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 🔍 DEBUG ENDPOINT: Template kontrol
@app.get("/debug/check-template")
async def check_template():
    import traceback
    try:
        path = os.path.join(os.path.dirname(__file__), "chart_template.png")
        exists = os.path.exists(path)
        size = os.path.getsize(path) if exists else 0
        cwd = os.getcwd()
        files = os.listdir(os.path.dirname(__file__))

        return JSONResponse(
            content={
                "exists": exists,
                "size_bytes": size,
                "path": path,
                "cwd": cwd,
                "files_in_dir": files
            }
        )
    except Exception as e:
        return JSONResponse(
            content={
                "error": str(e),
                "trace": traceback.format_exc()
            },
            status_code=500
        )
