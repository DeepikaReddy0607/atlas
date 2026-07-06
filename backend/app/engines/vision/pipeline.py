from PIL import Image

from app.engines.vision.tiler import ImageTiler
from app.engines.vision.stitcher import MaskStitcher


class VisionPipeline:

    def __init__(self, model_name="ade20k"):

        from app.engines.vision.registry import ModelRegistry

        print(f"Using model: {model_name}")

        self.predictor = ModelRegistry.get(model_name)

    def run(self, image_path):

        image = Image.open(image_path).convert("RGB")

        tiles = ImageTiler.split(image)

        predictions = []

        print(f"Processing {len(tiles)} tiles...")

        for i, (tile, x, y) in enumerate(tiles):

            print(f"{i + 1}/{len(tiles)}")

            mask = self.predictor.predict(tile)

            predictions.append((mask, x, y))

        return MaskStitcher.stitch(
            predictions,
            image.width,
            image.height,
        )