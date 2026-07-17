from fastapi import FastAPI

app = FastAPI(title="SEDAP", version="0.1.0")


@app.get("/")
async def root():
    return {"status": "ok", "service": "sedap", "message": "placeholder endpoint"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
