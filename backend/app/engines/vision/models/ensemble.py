import time

import numpy as np
from PIL import Image

from app.engines.vision.result import SegmentationResult
from app.engines.vision.models.dlinknet import (
    DLinkNet34Predictor,
)
from app.engines.vision.models.roadgie import (
    RoadGIEPredictor,
)


class EnsemblePredictor:

    MODEL_NAME = "ATLAS Ensemble"

    DLINKNET_WEIGHT = 0.65
    ROADGIE_WEIGHT = 0.35

    THRESHOLD = 0.275

    def __init__(self):

        print(
            "Loading ATLAS Ensemble..."
        )

        print(
            "Ensemble weights: "
            f"D-LinkNet34={self.DLINKNET_WEIGHT:.2f}, "
            f"RoadGIE={self.ROADGIE_WEIGHT:.2f}"
        )

        print(
            f"Ensemble threshold: "
            f"{self.THRESHOLD:.3f}"
        )

        # ----------------------------------------------------
        # Load component predictors
        # ----------------------------------------------------

        self.dlinknet = (
            DLinkNet34Predictor()
        )

        self.roadgie = (
            RoadGIEPredictor()
        )

        print(
            "ATLAS Ensemble ready."
        )

    # ========================================================
    # Probability prediction
    # ========================================================

    def predict_probabilities(
        self,
        image: Image.Image,
    ):

        image = image.convert(
            "RGB"
        )

        start = time.perf_counter()

        # ----------------------------------------------------
        # D-LinkNet probability
        # ----------------------------------------------------

        dlink_probability = (
            self.dlinknet.predict_probabilities(
                image
            )
        )

        # ----------------------------------------------------
        # RoadGIE probability
        # ----------------------------------------------------

        roadgie_result = (
            self.roadgie.predict_probabilities(
                image
            )
        )

        # RoadGIE returns:
        #
        # probability_map,
        # inference_time_ms

        roadgie_probability = (
            roadgie_result[0]
        )

        # ----------------------------------------------------
        # Safety checks
        # ----------------------------------------------------

        if dlink_probability.shape != (
            image.height,
            image.width,
        ):

            raise RuntimeError(
                "D-LinkNet probability map "
                "has unexpected shape: "
                f"{dlink_probability.shape}"
            )

        if roadgie_probability.shape != (
            image.height,
            image.width,
        ):

            raise RuntimeError(
                "RoadGIE probability map "
                "has unexpected shape: "
                f"{roadgie_probability.shape}"
            )

        # ----------------------------------------------------
        # Weighted probability fusion
        # ----------------------------------------------------

        ensemble_probability = (
            self.DLINKNET_WEIGHT
            * dlink_probability
            +
            self.ROADGIE_WEIGHT
            * roadgie_probability
        )

        # ----------------------------------------------------
        # Safety normalization
        # ----------------------------------------------------

        ensemble_probability = np.clip(
            ensemble_probability,
            0.0,
            1.0,
        )

        total_time_ms = (
            time.perf_counter()
            - start
        ) * 1000.0

        return (
            ensemble_probability,
            total_time_ms,
        )

    # ========================================================
    # ATLAS predictor interface
    # ========================================================

    def predict(
        self,
        image: Image.Image,
    ) -> SegmentationResult:

        probability_map, inference_time_ms = (
            self.predict_probabilities(
                image
            )
        )

        # ----------------------------------------------------
        # Final frozen threshold
        # ----------------------------------------------------

        mask = (
            probability_map
            >= self.THRESHOLD
        ).astype(
            np.uint8
        )

        road_pixels = int(
            mask.sum()
        )

        print(
            "ATLAS Ensemble road pixels: "
            f"{road_pixels}"
        )

        return SegmentationResult(
            mask=mask,

            model_name=self.MODEL_NAME,

            inference_time_ms=round(
                inference_time_ms,
                2,
            ),

            image_size=image.size,

            metadata={
                "output_type": "binary_road",

                "architecture": (
                    "D-LinkNet34 + RoadGIE"
                ),

                "task": (
                    "binary road extraction"
                ),

                "dataset": "DeepGlobe",

                "weights": {
                    "dlinknet34": (
                        self.DLINKNET_WEIGHT
                    ),
                    "roadgie": (
                        self.ROADGIE_WEIGHT
                    ),
                },

                "threshold": (
                    self.THRESHOLD
                ),

                "device": (
                    str(
                        self.dlinknet.device
                    )
                ),

                "road_class_id": 1,

                "probability_min": float(
                    probability_map.min()
                ),

                "probability_max": float(
                    probability_map.max()
                ),

                "probability_mean": float(
                    probability_map.mean()
                ),
            },

            # Preserve the continuous probability
            # map for downstream analysis.
            logits=probability_map,
        )