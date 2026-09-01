import time

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
import segmentation_models_pytorch as smp

from app.engines.vision.result import SegmentationResult


class SMPUNetPlusPlusPredictor:

    MODEL_NAME = "SMP-UNet++-ResNet50"

    def __init__(self):

        print("Loading SMP UNet++...")
        
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        print(f"SMP UNet++ device: {self.device}")

        self.model = smp.UnetPlusPlus(
            encoder_name="resnet50",
            encoder_weights="imagenet",
            in_channels=3,
            classes=1,
            activation=None,
        )

        self.model = self.model.to(self.device)
        self.model.eval()

        print("SMP UNet++ ready.")

    def predict(self, image: Image.Image) -> SegmentationResult:

        if not isinstance(image, Image.Image):
            raise TypeError(
                "SMPUNetPlusPlusPredictor expects a PIL Image."
            )

        image = image.convert("RGB")

        original_size = image.size
        original_width, original_height = original_size

        # ---------------------------------------------------------
        # Convert image to tensor
        # ---------------------------------------------------------

        image_np = np.asarray(
            image,
            dtype=np.float32
        ) / 255.0

        tensor = torch.from_numpy(
            image_np
        ).permute(2, 0, 1).unsqueeze(0)

        # ---------------------------------------------------------
        # Resize to model input size
        # ---------------------------------------------------------

        tensor = F.interpolate(
            tensor,
            size=(512, 512),
            mode="bilinear",
            align_corners=False,
        )

        tensor = tensor.to(self.device)

        # ---------------------------------------------------------
        # Inference
        # ---------------------------------------------------------

        start = time.perf_counter()

        with torch.no_grad():

            logits = self.model(tensor)

            probabilities = torch.sigmoid(logits)

        inference_time_ms = (
            time.perf_counter() - start
        ) * 1000.0

        # ---------------------------------------------------------
        # Restore original resolution
        # ---------------------------------------------------------

        probabilities = F.interpolate(
            probabilities,
            size=(original_height, original_width),
            mode="bilinear",
            align_corners=False,
        )

        probability_map = (
            probabilities[0, 0]
            .cpu()
            .numpy()
        )

        # ---------------------------------------------------------
        # Binary road mask
        # ---------------------------------------------------------

        mask = (
            probability_map >= 0.5
        ).astype(np.uint8)

        return SegmentationResult(
            mask=mask,
            model_name=self.MODEL_NAME,
            inference_time_ms=inference_time_ms,
            image_size=(
                original_width,
                original_height,
            ),
            metadata={
                "architecture": "UNet++",
                "library": "segmentation-models-pytorch",
                "smp_version": "0.5.0",
                "encoder": "resnet50",
                "encoder_weights": "imagenet",
                "output_type": "binary_road",
                "threshold": 0.5,
                "probability_map": probability_map,
            },
        )