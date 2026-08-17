from pathlib import Path

import numpy as np
from PIL import Image

from app.engines.vision.models.openearthmap import (
    OpenEarthMapPredictor,
)


# =========================================================
# CHANGE THIS
# =========================================================

IMAGE_PATH = "generated/tile0.png"


# =========================================================
# Load image
# =========================================================

image = Image.open(
    IMAGE_PATH
).convert("RGB")

print(
    "Image:",
    IMAGE_PATH,
)

print(
    "Image size:",
    image.size,
)


# =========================================================
# Load model
# =========================================================

predictor = OpenEarthMapPredictor()


# =========================================================
# Direct prediction
# =========================================================

print(
    "\nRunning DIRECT prediction..."
)

result = predictor.predict(image)

mask = result.mask


# =========================================================
# Statistics
# =========================================================

classes, counts = np.unique(
    mask,
    return_counts=True,
)

print(
    "\nPredicted classes:"
)

for c, count in zip(classes, counts):

    percentage = (
        count / mask.size
    ) * 100

    print(
        f"Class {c}: "
        f"{count} pixels "
        f"({percentage:.3f}%)"
    )


# =========================================================
# Road
# =========================================================

road_mask = (
    mask == predictor.ROAD_CLASS_ID
)

road_pixels = int(
    road_mask.sum()
)

road_percentage = (
    road_pixels / mask.size
) * 100


print(
    "\n================================"
)

print(
    "DIRECT ATLAS IMAGE RESULT"
)

print(
    "================================"
)

print(
    "Road class:",
    predictor.ROAD_CLASS_ID,
)

print(
    "Road pixels:",
    road_pixels,
)

print(
    "Road percentage:",
    f"{road_percentage:.3f}%",
)

print(
    "Inference:",
    result.inference_time_ms,
    "ms",
)

print(
    "================================"
)


# =========================================================
# Save mask
# =========================================================

output = (
    road_mask.astype(np.uint8)
    * 255
)

Image.fromarray(
    output
).save(
    "generated/direct_atlas_roads.png"
)

print(
    "\nSaved:"
    " generated/direct_atlas_roads.png"
)