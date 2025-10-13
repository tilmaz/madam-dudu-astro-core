from fastapi import FastAPI

app = FastAPI(title="Madam Dudu Astro Core", version="0.1.0")

@app.get("/health")
def health():
    return {"ok": True, "service": "Madam Dudu Astro Core", "version": "0.1.0"}
