from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.health import router as health_router
from app.api.router import api_router


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="ATLAS API",
    version="0.1.0",
    description="Autonomous Terrain Learning & Analysis System",
)


# ============================================================
# PATHS
# ============================================================

# main.py is inside:
# backend/app/main.py
#
# parents[0] -> backend/app
# parents[1] -> backend

BASE_DIR = Path(__file__).resolve().parents[1]

OUTPUTS_DIR = BASE_DIR / "outputs"


# ============================================================
# STATIC OUTPUTS
# ============================================================

# Backend-generated visualizations are exposed through:
#
# http://localhost:8000/outputs/...
#
# Example:
# /outputs/visualizations/overlays/<uuid>_overlay.png

app.mount(
    "/outputs",
    StaticFiles(directory=str(OUTPUTS_DIR)),
    name="outputs",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "project": "ATLAS",
        "status": "online",
        "version": "0.1.0",
    }


# ============================================================
# API ROUTES
# ============================================================

app.include_router(api_router)


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


# ============================================================
# VERSION
# ============================================================

@app.get("/version")
def version():
    return {
        "version": "0.1.0",
    }