from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .api.plans import router as plans_router

app = FastAPI(title="DawnTask", version="0.1.0")
app.include_router(plans_router)

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
async def index():
    return FileResponse(str(static_dir / "index.html"))


@app.get("/health")
async def health():
    return {"status": "ok", "app": "DawnTask", "version": "0.1.0"}
