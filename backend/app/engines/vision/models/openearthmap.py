from PIL import Image

from app.engines.vision.models.base import BasePredictor
from app.engines.vision.result import SegmentationResult


class OpenEarthMapPredictor(BasePredictor):
    """
    Placeholder for the future OpenEarthMap implementation.

    This predictor is intentionally not implemented because a stable,
    production-ready OpenEarthMap checkpoint has not yet been selected.

    ATLAS v0.2 officially supports:
        - ADE20KPredictor

    OpenEarthMap support will be introduced in a future release after
    benchmarking and validating an appropriate model.
    """

    MODEL_NAME = "OpenEarthMap"

    def __init__(self):
        raise NotImplementedError(
            "OpenEarthMapPredictor is not implemented yet. "
            "Use ADE20KPredictor for ATLAS v0.2."
        )

    def predict(self, image: Image.Image) -> SegmentationResult:
        raise NotImplementedError(
            "Prediction is unavailable because this model "
            "has not been implemented."
        )