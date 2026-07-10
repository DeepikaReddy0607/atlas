import time

import torch
from PIL import Image
from transformers import (
    AutoImageProcessor,
    SegformerForSemanticSegmentation,
)

from app.engines.vision.models.base import BasePredictor
from app.engines.vision.result import SegmentationResult


class ADE20KPredictor(BasePredictor):

    MODEL_NAME = "nvidia/segformer-b0-finetuned-ade-512-512"

    def __init__(self):

        print("Loading SegFormer (ADE20K)...")

        self.processor = AutoImageProcessor.from_pretrained(
            self.MODEL_NAME
        )

        self.model = SegformerForSemanticSegmentation.from_pretrained(
            self.MODEL_NAME
        )

        self.model.eval()

    def predict(
        self,
        image: Image.Image,
    ) -> SegmentationResult:

        start = time.perf_counter()

        inputs = self.processor(
            images=image,
            return_tensors="pt",
        )

        with torch.no_grad():
            outputs = self.model(**inputs)

        logits = outputs.logits

        prediction = torch.nn.functional.interpolate(
            logits,
            size=image.size[::-1],
            mode="bilinear",
            align_corners=False,
        )

        prediction = prediction.argmax(dim=1)[0]

        inference_time = (
            time.perf_counter() - start
        ) * 1000

        return SegmentationResult(
            mask=prediction.cpu().numpy(),
            model_name="ADE20K",
            inference_time_ms=round(inference_time, 2),
            image_size=image.size,
            metadata={
                "model_id": self.MODEL_NAME,
            },
        )