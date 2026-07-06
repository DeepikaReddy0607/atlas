from app.engines.vision.models.base import BasePredictor

class OpenEarthMapPredictor(BasePredictor):

    MODEL_NAME = "OpenEarthMap"

    ROAD_CLASSES = []

    def __init__(self):
        self.model = None
        self.processor = None

    def predict(self, image):
        raise NotImplementedError