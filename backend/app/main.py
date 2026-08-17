from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.health import router as health_router
from app.api.router import api_router

app = FastAPI(
    title="ATLAS API",
    version="0.1.0",
    description="Autonomous Terrain Learning & Analysis System"
)

# -----------------------------
# CORS Configuration
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

app.mount(
    "/outputs",
    StaticFiles(directory="outputs"),
    name="outputs",
)