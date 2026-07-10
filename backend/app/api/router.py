from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.upload import router as upload_router
from app.api.uploads import router as uploads_router
from app.api.geo import router as geo_router
from app.api.vision import router as vision_router
from app.api.atlas import router as atlas_router   

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(upload_router)
api_router.include_router(uploads_router)
api_router.include_router(geo_router)
api_router.include_router(vision_router)
api_router.include_router(atlas_router)