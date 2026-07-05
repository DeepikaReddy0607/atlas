import torch
import numpy as np
from PIL import Image

from transformers import (
    SegformerImageProcessor,
    SegformerForSemanticSegmentation,
)

from app.engines.vision.tiler import ImageTiler
from app.engines.vision.stitcher import MaskStitcher

MODEL_NAME = "nvidia/segformer-b0-finetuned-ade-512-512"

print("Loading model...")

processor = SegformerImageProcessor.from_pretrained(MODEL_NAME)
model = SegformerForSemanticSegmentation.from_pretrained(MODEL_NAME)

image = Image.open("generated/hyderabad_clear.png").convert("RGB")

tiles = ImageTiler.split(image, tile_size=512)

predictions = []

print(f"Processing {len(tiles)} tiles...")

# Process only the first 5 tiles for now
for tile, x, y in tiles[:5]:

    inputs = processor(images=tile, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits

    prediction = torch.nn.functional.interpolate(
        logits,
        size=(tile.height, tile.width),
        mode="bilinear",
        align_corners=False,
    )

    mask = prediction.argmax(dim=1)[0].cpu().numpy().astype(np.uint8)

    predictions.append((mask, x, y))

print("First 5 tiles processed successfully.")