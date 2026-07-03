from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.router import api_router 
app = FastAPI(
    title="ATLAS API",
    version="0.1.0",
    description="Autonomous Terrain Learning & Analysis System"
)

@app.get("/")
def root():
    return {
        "project": "ATLAS",
        "status": "online",
        "version": "0.1.0"
    }

app.include_router(api_router)

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }

@app.get("/version")
def version():
    return {
        "version": "0.1.0"
    }