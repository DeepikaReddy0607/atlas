from pathlib import Path
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File, UploadFile, HTTPException

from app.engines.atlas.engine import AtlasEngine
from app.api.serializers.atlas import serialize_atlas_result
from fastapi.responses import FileResponse
from app.reporting.report_generator import ReportGenerator
from app.api.schemas.simulation import (
    SimulationRequest,
)
router = APIRouter(
    prefix="/atlas",
    tags=["Atlas"],
)

engine = AtlasEngine()
UPLOAD_DIR = Path("uploads/atlas")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

REPORT_DIR = Path("outputs/reports")
REPORT_DIR.mkdir(parents=True, exist_ok=True)

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

@router.post("/report")
async def generate_report(
    image: UploadFile = File(...)
):
    extension = Path(image.filename).suffix

    filename = f"{uuid.uuid4()}{extension}"

    image_path = UPLOAD_DIR / filename

    with image_path.open("wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    atlas_result = engine.analyze(str(image_path))

    pdf_path = REPORT_DIR / f"{image_path.stem}.pdf"

    ReportGenerator.generate(
        atlas_result=atlas_result,
        output_path=str(pdf_path),
    )

    return FileResponse(
        path=pdf_path,
        filename="atlas_report.pdf",
        media_type="application/pdf",
    )

@router.post("/simulate")
async def simulate(
    request: SimulationRequest,
):
    try:
        result = engine.simulate(
            request.scenario
        )

        return {
            "scenario": result.scenario,

            "removed_nodes": result.removed_nodes,
            "removed_edges": result.removed_edges,

            "original_nodes": result.original_nodes,
            "original_edges": result.original_edges,

            "remaining_nodes": result.remaining_nodes,
            "remaining_edges": result.remaining_edges,

            "connected_components":
                result.connected_components,

            "largest_component":
                result.largest_component,

            "critical_node":
                list(result.critical_node)
                if result.critical_node is not None
                else None,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )