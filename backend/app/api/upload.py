from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil
import uuid
from datetime import datetime
from app.engines.geo.reader import GeoReader
from app.storage.file_registry import uploaded_files

router = APIRouter()

from app.core.config import settings

settings.UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/tiff",
    "image/geotiff"
}

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload JPEG, PNG or TIFF images."
        )
    # Generate unique ID
    unique_id = str(uuid.uuid4())[:8]

    # Create unique filename
    stored_filename = f"{unique_id}_{file.filename}"

    # Full file path
    file_path = settings.UPLOAD_DIR / stored_filename

    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        geo_metadata = {}

        if file.filename.lower().endswith((".tif", ".tiff")):
            geo_metadata = GeoReader.read_metadata(file_path)
        
        from app.engines.geo.preview import GeoPreview

        preview_path = f"previews/{unique_id}.png"

        GeoPreview.generate_preview(
            file_path,
            preview_path
        )
            # Create metadata
    metadata = {
        "id": unique_id,
        "original_filename": file.filename,
        "stored_filename": stored_filename,
        "content_type": file.content_type,
        "size": None,          # We'll improve this later
        "uploaded_at": datetime.now().isoformat(),
        "status": "UPLOADED"
    }

    # Store metadata
    uploaded_files.append(metadata)

    # Return metadata
    return {
    **metadata,
    "geo_metadata": geo_metadata,
    "preview": preview_path
}