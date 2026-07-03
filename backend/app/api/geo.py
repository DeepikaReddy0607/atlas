from fastapi import APIRouter
from app.engines.geo.reader import GeoReader

router = APIRouter()


@router.get("/geo/test")
def test_geo():

    metadata = GeoReader.read_metadata("sample.tif")

    return metadata