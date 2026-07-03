from fastapi import APIRouter
from app.storage.file_registry import uploaded_files

router = APIRouter()

@router.get("/uploads")
def list_uploads():
    return uploaded_files