import torch

from transformers import (
    SegformerImageProcessor,
    SegformerForSemanticSegmentation,
)


class SegFormerPredictor:

    def __init__(
        self,
        model_name="nvidia/segformer-b0-finetuned-ade-512-512",
    ):
        print("Loading SegFormer...")

        self.processor = SegformerImageProcessor.from_pretrained(model_name)

        self.model = SegformerForSemanticSegmentation.from_pretrained(
            model_name
        )

        self.model.eval()

    def predict(self, image):

        inputs = self.processor(
            images=image,
            return_tensors="pt"
        )

        with torch.no_grad():
            outputs = self.model(**inputs)

        logits = outputs.logits

        prediction = torch.nn.functional.interpolate(
            logits,
            size=(image.height, image.width),
            mode="bilinear",
            align_corners=False,
        )

        return prediction.argmax(dim=1)[0].cpu().numpy()