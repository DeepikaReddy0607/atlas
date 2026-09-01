import time

import numpy as np
import torch
import torch.nn.functional as F

from PIL import Image

import segmentation_models_pytorch as smp

from app.engines.vision.models.base import BasePredictor
from app.engines.vision.result import SegmentationResult


class DeepLabV3PlusPredictor(BasePredictor):

    MODEL_NAME = "DeepLabV3Plus"

    ROAD_CLASS_ID = 1

    CHECKPOINT_PATH = (
        "models/deeplabv3plus/"
        "deeplabv3plus_road.pth"
    )

    THRESHOLD = 0.5

    def __init__(self):

        print(
            "Loading DeepLabV3+..."
        )

        # ----------------------------------------------------
        # Device
        # ----------------------------------------------------

        self.device = torch.device(
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        print(
            f"DeepLabV3+ device: "
            f"{self.device}"
        )

        # ----------------------------------------------------
        # Model
        # ----------------------------------------------------

        self.model = smp.DeepLabV3Plus(
            encoder_name="resnet50",
            encoder_weights=None,
            in_channels=3,
            classes=1,
        )

        # ----------------------------------------------------
        # Checkpoint
        # ----------------------------------------------------

        print(
            "Loading DeepLabV3+ checkpoint..."
        )

        checkpoint = torch.load(
            self.CHECKPOINT_PATH,
            map_location="cpu",
        )

        # Handle common checkpoint formats.
        if isinstance(checkpoint, dict):

            if "state_dict" in checkpoint:
                state_dict = checkpoint["state_dict"]

            elif "model_state_dict" in checkpoint:
                state_dict = checkpoint[
                    "model_state_dict"
                ]

            elif "model_state" in checkpoint:
                state_dict = checkpoint[
                    "model_state"
                ]

            else:
                state_dict = checkpoint

        else:
            state_dict = checkpoint

        # Remove DataParallel prefix if present.
        cleaned_state_dict = {}

        for key, value in state_dict.items():

            cleaned_key = key

            if cleaned_key.startswith(
                "module."
            ):
                cleaned_key = cleaned_key[
                    len("module.") :
                ]

            cleaned_state_dict[
                cleaned_key
            ] = value

        # ----------------------------------------------------
        # Compatibility check
        # ----------------------------------------------------

        self.model.load_state_dict(
            cleaned_state_dict,
            strict=True,
        )

        print(
            "DeepLabV3+ checkpoint "
            "loaded successfully."
        )

        self.model.to(
            self.device
        )

        self.model.eval()

        print(
            "DeepLabV3+ ready."
        )

    # ========================================================
    # Probability inference
    # ========================================================

    def predict_probabilities(
        self,
        image: Image.Image,
    ) -> np.ndarray:

        image = image.convert(
            "RGB"
        )

        original_size = image.size

        # ----------------------------------------------------
        # Image -> tensor
        # ----------------------------------------------------

        image_array = np.asarray(
            image,
            dtype=np.float32,
        ) / 255.0

        tensor = torch.from_numpy(
            image_array
        ).permute(
            2,
            0,
            1,
        )

        # ----------------------------------------------------
        # ImageNet normalization
        # ----------------------------------------------------

        mean = torch.tensor(
            [
                0.485,
                0.456,
                0.406,
            ],
            dtype=torch.float32,
        ).view(
            3,
            1,
            1,
        )

        std = torch.tensor(
            [
                0.229,
                0.224,
                0.225,
            ],
            dtype=torch.float32,
        ).view(
            3,
            1,
            1,
        )

        tensor = (
            tensor - mean
        ) / std

        tensor = tensor.unsqueeze(
            0
        ).to(
            self.device
        )

        # ----------------------------------------------------
        # Inference
        # ----------------------------------------------------

        with torch.no_grad():

            logits = self.model(
                tensor
            )

        # segmentation_models_pytorch normally returns
        # a tensor directly.

        if isinstance(
            logits,
            dict
        ):
            logits = logits[
                "out"
            ]

        # ----------------------------------------------------
        # Restore original resolution
        # ----------------------------------------------------

        logits = F.interpolate(
            logits,
            size=(
                original_size[1],
                original_size[0],
            ),
            mode="bilinear",
            align_corners=False,
        )

        # ----------------------------------------------------
        # Binary road probability
        # ----------------------------------------------------

        probabilities = torch.sigmoid(
            logits
        )[0, 0]

        return (
            probabilities
            .cpu()
            .numpy()
        )

    # ========================================================
    # ATLAS prediction
    # ========================================================

    def predict(
        self,
        image: Image.Image,
    ) -> SegmentationResult:

        start = time.perf_counter()

        image = image.convert(
            "RGB"
        )

        original_size = image.size

        probabilities = (
            self.predict_probabilities(
                image
            )
        )

        prediction = (
            probabilities
            >= self.THRESHOLD
        ).astype(
            np.uint8
        )

        road_pixels = int(
            prediction.sum()
        )

        inference_time = (
            time.perf_counter()
            - start
        ) * 1000

        print(
            f"DeepLabV3+ road pixels: "
            f"{road_pixels}"
        )

        print(
            f"DeepLabV3+ road coverage: "
            f"{road_pixels / prediction.size * 100:.2f}%"
        )

        return SegmentationResult(
            mask=prediction,

            model_name=self.MODEL_NAME,

            inference_time_ms=round(
                inference_time,
                2,
            ),

            image_size=original_size,

            metadata={
                "architecture": (
                    "DeepLabV3+"
                ),
                "encoder": (
                    "ResNet50"
                ),
                "task": (
                    "binary road extraction"
                ),
                "dataset": (
                    "road-extraction checkpoint"
                ),
                "road_class_id": (
                    self.ROAD_CLASS_ID
                ),
                "threshold": (
                    self.THRESHOLD
                ),
                "device": str(
                    self.device
                ),
                "checkpoint": (
                    self.CHECKPOINT_PATH
                ),
            },
        )