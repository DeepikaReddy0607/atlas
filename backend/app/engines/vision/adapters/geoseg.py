from app.engines.vision.adapters.base import VisionAdapter


class GeoSegAdapter(VisionAdapter):

    def load(self):
        print("Loading GeoSeg...")

    def predict(self, image_path):
        print(f"Running GeoSeg on {image_path}")