import torch
from PIL import Image

from app.engines.vision.models.openearthmap import (
    OpenEarthMapPredictor,
)


predictor = OpenEarthMapPredictor()

image = Image.open(
    "generated/tile0.png"
).convert("RGB")

inputs = predictor.processor(
    images=image,
    return_tensors="pt",
)

with torch.no_grad():
    outputs = predictor.model(
        **inputs
    )

probs = torch.softmax(
    outputs.logits,
    dim=1,
)

print(
    "Logits shape:",
    tuple(outputs.logits.shape),
)

print("\nMean probability per class:")

for class_id in range(9):
    value = probs[:, class_id].mean().item()
    print(
        f"Class {class_id}: {value:.6f}"
    )

print("\nMaximum probability per class:")

for class_id in range(9):
    value = probs[:, class_id].max().item()
    print(
        f"Class {class_id}: {value:.6f}"
    )