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

        for i, tile in enumerate(tiles):

            print(f"Processing tile {i + 1}/{len(tiles)}")

            result = self.predictor.predict(tile.image)

            predictions.append(
                (
                    result.mask,
                    tile.x,
                    tile.y,
                )
            )

        stitched_mask =  MaskStitcher.stitch(
            predictions,
            image.width,
            image.height,
        )
        from app.engines.vision.result import SegmentationResult

        return SegmentationResult(
            mask=stitched_mask,
            model_name=result.model_name,
            inference_time_ms=result.inference_time_ms,
            image_size=image.size,
            metadata=result.metadata,
        )