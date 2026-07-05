import torch
import numpy as np
from PIL import Image

from transformers import (
    SegformerImageProcessor,
    SegformerForSemanticSegmentation,
)

MODEL_NAME = "nvidia/segformer-b0-finetuned-ade-512-512"

print("Loading model...")

processor = SegformerImageProcessor.from_pretrained(MODEL_NAME)

model = SegformerForSemanticSegmentation.from_pretrained(MODEL_NAME)

image = Image.open(
    "generated/hyderabad_clear.png"
).convert("RGB")

inputs = processor(images=image, return_tensors="pt")

with torch.no_grad():
    outputs = model(**inputs)

logits = outputs.logits

prediction = torch.nn.functional.interpolate(
    logits,
    size=image.size[::-1],
    mode="bilinear",
    align_corners=False,
)

mask = prediction.argmax(dim=1)[0].cpu().numpy()

print(mask.shape)

np.save("generated/mask.npy", mask)

print("Mask saved.")