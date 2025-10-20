import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from chart_utils import draw_chart

app = FastAPI(title="Madam Dudu Astro Core Unified")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {
        "ok": True,
        "service": "Madam Dudu Astro Core Unified",
        "version": "3.2.0-debug"
    }


@app.post("/compute")
async def compute_chart(request: Request):
    try:
        data = await request.json()
        # Dummy simulation (Render test only)
        # Asıl compute işlemi ChatGPT plugin tarafında çalışıyor.
        return JSONResponse(
            content={
                "message": "Compute endpoint aktif fakat bu ortamda harici astro hesaplama yapılmıyor.",
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

        # Görsel oluştur
        result = draw_chart(planets)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 🔍 Debug endpoint: chart_template.png erişimini test eder
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
