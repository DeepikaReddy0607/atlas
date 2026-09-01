from PIL import Image

from app.engines.vision.result import SegmentationResult
from app.engines.vision.tiler import ImageTiler
from app.engines.vision.stitcher import MaskStitcher


class VisionPipeline:

    # Models that operate directly on the complete image.
    FULL_IMAGE_MODELS = {
        "dlinknet34",
        "roadgie",
        "ensemble",
    }

    def __init__(
        self,
        model_name="ensemble",
    ):
        from app.engines.vision.registry import ModelRegistry

        print(
            f"Using model: {model_name}"
        )

        self.model_name = model_name

        self.predictor = ModelRegistry.get(
            model_name
        )

    def run(
        self,
        image_path,
    ):

        image = Image.open(
            image_path
        ).convert("RGB")

        # =====================================================
        # FULL-IMAGE BINARY ROAD MODELS
        # =====================================================
        #
        # These predictors already handle their own internal
        # preprocessing/resizing and return a binary road
        # probability/mask.
        #
        # IMPORTANT:
        # The ATLAS Ensemble MUST be processed as one complete
        # image. Do not send it through the generic tiler.
        # =====================================================

        if self.model_name in self.FULL_IMAGE_MODELS:

            print(
                f"Processing full image with "
                f"{self.model_name}..."
            )

            result = self.predictor.predict(
                image
            )

            return SegmentationResult(
                mask=result.mask,

                model_name=result.model_name,

                inference_time_ms=(
                    result.inference_time_ms
                ),

                image_size=image.size,

                metadata=result.metadata,

                logits=getattr(
                    result,
                    "logits",
                    None,
                ),
            )

        # =====================================================
        # SEMANTIC / TILED MODELS
        # =====================================================

        tiles = ImageTiler.split(
            image
        )

        predictions = []

        print(
            f"Processing {len(tiles)} tiles..."
        )

        last_result = None

        for i, tile in enumerate(tiles):

            print(
                f"Processing tile "
                f"{i + 1}/{len(tiles)}"
            )

            result = self.predictor.predict(
                tile.image
            )

            last_result = result

            predictions.append(
                (
                    result.mask,
                    tile.x,
                    tile.y,
                )
            )

        if last_result is None:
            raise RuntimeError(
                "Vision pipeline produced "
                "no predictions."
            )

        stitched_mask = MaskStitcher.stitch(
            predictions,
            image.width,
            image.height,
        )

        return SegmentationResult(
            mask=stitched_mask,

            model_name=last_result.model_name,

            inference_time_ms=(
                last_result.inference_time_ms
            ),

            image_size=image.size,

            metadata=last_result.metadata,

            logits=getattr(
                last_result,
                "logits",
                None,
            ),
        )