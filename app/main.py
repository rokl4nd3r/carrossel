from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.models import GenerateRequest, GenerateResponse
from app.services.carousel import CarouselGenerator
from app.services.stable_diffusion import StableDiffusionClient

settings = get_settings()
Path(settings.output_dir).mkdir(parents=True, exist_ok=True)

app = FastAPI(title=settings.app_name)

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.mount("/output", StaticFiles(directory=settings.output_dir), name="output")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/api/health")
def health() -> dict:
    sd = StableDiffusionClient(settings)
    return {
        "ok": True,
        "stable_diffusion": sd.healthcheck(),
        "sd_base_url": settings.sd_base_url,
        "llm_provider": settings.llm_provider,
    }


@app.post("/api/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest) -> GenerateResponse:
    try:
        generator = CarouselGenerator(settings)
        return generator.generate(request)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
