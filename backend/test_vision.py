from app.engines.vision.predictor import Predictor
from app.engines.vision.road_detector import RoadDetector

model = RoadDetector()

model.load()

predictor = Predictor(model)

prediction = predictor.predict("generated/hyderabad_clear.png")

model.postprocess(prediction)