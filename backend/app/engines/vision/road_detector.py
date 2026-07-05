from app.engines.vision.base import BaseVisionModel


class RoadDetector(BaseVisionModel):

    def load(self):
        print("Road segmentation model loaded.")

    def predict(self, image):
        print(f"Running inference on image: {image.size}")

        return image

    def postprocess(self, prediction):
        print("Generating road mask...")

        return prediction