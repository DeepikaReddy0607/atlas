from PIL import Image
import numpy as np

from app.engines.vision.models.base import BasePredictor


class OpenEarthMapPredictor(BasePredictor):

    def __init__(self):

        print("OpenEarthMap model not integrated yet.")

    def predict(self, image: Image.Image) -> np.ndarray:

        raise NotImplementedError(
            "OpenEarthMap predictor is not implemented yet."
        )