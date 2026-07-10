from pathlib import Path
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File

from app.engines.atlas.engine import AtlasEngine
from app.api.serializers.atlas import serialize_atlas_result

router = APIRouter(
    prefix="/atlas",
    tags=["Atlas"],
)

engine = AtlasEngine()
UPLOAD_DIR = Path("uploads/atlas")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/analyze")
async def analyze(
    image: UploadFile = File(...)
):

    extension = Path(image.filename).suffix

    filename = f"{uuid.uuid4()}{extension}"

    image_path = UPLOAD_DIR / filename

    with image_path.open("wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    result = engine.analyze(
    str(image_path)
    )

    response = serialize_atlas_result(result)

    return response