from PIL import Image

from app.engines.vision.tiler import ImageTiler
from app.engines.vision.stitcher import MaskStitcher
from app.engines.vision.result import SegmentationResult


class VisionPipeline:

    def __init__(
        self,
        model_name="openearthmap",
    ):

        from app.engines.vision.registry import ModelRegistry

        print(
            f"Using model: {model_name}"
        )

        self.predictor = (
            ModelRegistry.get(model_name)
        )

    def run(self, image_path):

        from PIL import Image

        image = (
            Image.open(image_path)
            .convert("RGB")
        )

        print(
            "Processing full image with "
            "OpenEarthMap 1000x1000 checkpoint..."
        )

        result = self.predictor.predict(
            image
        )

        return result