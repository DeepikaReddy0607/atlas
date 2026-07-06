from PIL import Image
import numpy as np

from app.engines.vision.models.base import BasePredictor


class GeoSegPredictor(BasePredictor):

    def __init__(self):

        print("GeoSeg model not integrated yet.")

    def predict(self, image: Image.Image) -> np.ndarray:

        raise NotImplementedError(
            "GeoSeg predictor is not implemented yet."
        )