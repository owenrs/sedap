from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(title="SEDAP", version="0.1.0")


@app.get("/")
async def root() -> dict[str, object]:
    return {
        "status": "ok",
        "service": "sedap",
        "app_env": settings.APP_ENV.value,
        "message": "placeholder endpoint",
    }


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}
