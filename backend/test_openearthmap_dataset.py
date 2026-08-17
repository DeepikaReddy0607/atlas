import base64
import io
import json
import zlib

import numpy as np
from PIL import Image

from app.engines.vision.models.openearthmap import (
    OpenEarthMapPredictor,
)


IMAGE_PATH = "imagery/train/img/10255_sat.jpg"
ANNOTATION_PATH = "imagery/train/ann/10255_sat.jpg.json"

ROAD_CLASS_ID = 4


# =========================================================
# Load model
# =========================================================

print("Loading model...")

predictor = OpenEarthMapPredictor()


# =========================================================
# Load image
# =========================================================

print("\nLoading image...")

image = Image.open(
    IMAGE_PATH
).convert("RGB")

print(
    "Image size:",
    image.size,
)


# =========================================================
# Prediction
# =========================================================

print("\nRunning segmentation...")

result = predictor.predict(image)

mask = result.mask

print(
    "Prediction shape:",
    mask.shape,
)


# =========================================================
# Predicted road mask
# =========================================================

predicted_road = (
    mask == ROAD_CLASS_ID
)

print(
    "\nPredicted road pixels:",
    int(predicted_road.sum()),
)

print(
    "Predicted road percentage:",
    f"{predicted_road.mean() * 100:.3f}%"
)


# =========================================================
# Load annotation
# =========================================================

print("\nLoading annotation...")

with open(
    ANNOTATION_PATH,
    "r",
    encoding="utf-8",
) as f:

    annotation = json.load(f)


# =========================================================
# Find road object
# =========================================================

road_objects = [
    obj
    for obj in annotation["objects"]
    if obj["classTitle"].lower() == "road"
]


if not road_objects:

    raise RuntimeError(
        "No road annotation found."
    )


road_object = road_objects[0]

bitmap_data = road_object[
    "bitmap"
]["data"]


# =========================================================
# Decode DatasetNinja bitmap
# =========================================================

print(
    "\nDecoding ground-truth road bitmap..."
)

try:

    compressed = base64.b64decode(
        bitmap_data
    )

    decoded = zlib.decompress(
        compressed
    )

    ground_truth_image = Image.open(
        io.BytesIO(decoded)
    )

except Exception as e:

    raise RuntimeError(
        f"Could not decode road bitmap: {e}"
    )


ground_truth_image = (
    ground_truth_image.convert("L")
)

ground_truth = (
    np.array(ground_truth_image) > 0
)


# =========================================================
# Verify dimensions
# =========================================================

print(
    "Ground-truth shape:",
    ground_truth.shape,
)

print(
    "Prediction shape:",
    predicted_road.shape,
)


if ground_truth.shape != predicted_road.shape:

    raise RuntimeError(
        "Ground-truth and prediction "
        "dimensions do not match."
    )


# =========================================================
# Ground-truth statistics
# =========================================================

gt_pixels = int(
    ground_truth.sum()
)

pred_pixels = int(
    predicted_road.sum()
)

print(
    "\nGround-truth road pixels:",
    gt_pixels,
)

print(
    "Ground-truth road percentage:",
    f"{ground_truth.mean() * 100:.3f}%"
)


# =========================================================
# Confusion values
# =========================================================

intersection = np.logical_and(
    predicted_road,
    ground_truth,
).sum()

union = np.logical_or(
    predicted_road,
    ground_truth,
).sum()

true_positive = intersection

false_positive = np.logical_and(
    predicted_road,
    ~ground_truth,
).sum()

false_negative = np.logical_and(
    ~predicted_road,
    ground_truth,
).sum()


# =========================================================
# Metrics
# =========================================================

iou = (
    intersection / union
    if union > 0
    else 0.0
)

precision = (
    true_positive
    / (true_positive + false_positive)
    if (true_positive + false_positive) > 0
    else 0.0
)

recall = (
    true_positive
    / (true_positive + false_negative)
    if (true_positive + false_negative) > 0
    else 0.0
)

f1 = (
    2 * precision * recall
    / (precision + recall)
    if (precision + recall) > 0
    else 0.0
)


# =========================================================
# Result
# =========================================================

print(
    "\n================================"
)

print(
    "OPENEARTHMAP ROAD VALIDATION"
)

print(
    "================================"
)

print(
    f"Road class:       {ROAD_CLASS_ID}"
)

print(
    f"Ground truth:     {gt_pixels}"
)

print(
    f"Prediction:       {pred_pixels}"
)

print(
    f"Intersection:     {intersection}"
)

print(
    f"False positives:  {false_positive}"
)

print(
    f"False negatives:  {false_negative}"
)

print(
    f"IoU:              {iou:.4f}"
)

print(
    f"Precision:        {precision:.4f}"
)

print(
    f"Recall:           {recall:.4f}"
)

print(
    f"F1:               {f1:.4f}"
)

print(
    "================================"
)