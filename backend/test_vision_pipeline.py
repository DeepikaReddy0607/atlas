import numpy as np
from PIL import Image

from app.engines.vision.pipeline import VisionPipeline
from app.engines.vision.colorizer import MaskColorizer
from app.engines.analysis.roads import RoadExtractor

# -----------------------------
# Configuration
# -----------------------------
IMAGE_PATH = "generated/tile0.png"
ROAD_CLASS_IDS = [6]      # Change only here when switching models

# -----------------------------
# Run Vision Pipeline
# -----------------------------
MODEL = "ade20k"
pipeline = VisionPipeline(MODEL)

mask = pipeline.run(IMAGE_PATH)

# -----------------------------
# Print detected classes
# -----------------------------
classes = np.unique(mask)

print("Detected classes:", classes)

for c in classes:
    pixels = np.sum(mask == c)
    print(f"Class {c}: {pixels} pixels")

# -----------------------------
# Extract roads
# -----------------------------
road_mask = RoadExtractor.extract(
    mask,
    ROAD_CLASS_IDS
)

Image.fromarray(
    road_mask * 255
).save("generated/roads.png")

print("Road mask saved to generated/roads.png")

# -----------------------------
# Save raw prediction
# -----------------------------
np.save(
    "generated/test_mask.npy",
    mask
)

# -----------------------------
# Save colored segmentation
# -----------------------------
colored = MaskColorizer.colorize(mask)

colored.save(
    "generated/test_mask.png"
)

print("Colored segmentation saved.")

print(mask.shape)

print("Done!")