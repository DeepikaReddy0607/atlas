from transformers import (
    AutoImageProcessor,
    SegformerForSemanticSegmentation,
)

import torch
import numpy as np

from PIL import Image

from app.engines.vision.models.base import BasePredictor


MODEL_NAME = "nvidia/segformer-b0-finetuned-ade-512-512"


class ADE20KPredictor(BasePredictor):

    def __init__(self):

        print("Loading SegFormer...")

        self.processor = AutoImageProcessor.from_pretrained(
            MODEL_NAME
        )

        self.model = SegformerForSemanticSegmentation.from_pretrained(
            MODEL_NAME
        )

        self.model.eval()

    def predict(self, image: Image.Image):

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

        return prediction.cpu().numpy()