from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.upload import router as upload_router
from app.api.uploads import router as uploads_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(upload_router)
api_router.include_router(uploads_router)