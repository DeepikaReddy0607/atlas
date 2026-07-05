from fastapi import APIRouter
from pydantic import BaseModel

from app.engines.vision.pipeline import VisionPipeline

router = APIRouter(prefix="/vision", tags=["Vision"])

pipeline = VisionPipeline()


class SegmentRequest(BaseModel):
    image_path: str


@router.get("/health")
def health():
    return {
        "engine": "Vision Engine",
        "status": "ready"
    }


@router.post("/segment")
def segment(request: SegmentRequest):

    mask = pipeline.run(request.image_path)

    return {
        "status": "success",
        "shape": list(mask.shape)
    }