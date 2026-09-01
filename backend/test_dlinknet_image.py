from pathlib import Path

from PIL import Image

from app.engines.vision.models.dlinknet import (
    DLinkNet34Predictor,
)


IMAGE_PATH = Path(
    "imagery/train/img/10255_sat.jpg"
)

OUTPUT_PATH = Path(
    "generated/dlinknet_roads.png"
)


print("=" * 60)
print("D-LINKNET34 IMAGE TEST")
print("=" * 60)

# ------------------------------------------------------------
# Load image
# ------------------------------------------------------------

if not IMAGE_PATH.exists():
    raise FileNotFoundError(
        f"Image not found: {IMAGE_PATH}"
    )

image = Image.open(
    IMAGE_PATH
).convert("RGB")

print(
    f"Input image: {IMAGE_PATH}"
)

print(
    f"Image size: {image.size}"
)

# ------------------------------------------------------------
# Load model
# ------------------------------------------------------------

predictor = DLinkNet34Predictor()

# ------------------------------------------------------------
# Prediction
# ------------------------------------------------------------

result = predictor.predict(
    image
)

# ------------------------------------------------------------
# Save mask
# ------------------------------------------------------------

mask = result.mask

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)

Image.fromarray(
    mask * 255
).save(
    OUTPUT_PATH
)

# ------------------------------------------------------------
# Statistics
# ------------------------------------------------------------

road_pixels = int(
    mask.sum()
)

total_pixels = (
    mask.shape[0] *
    mask.shape[1]
)

road_percentage = (
    road_pixels /
    total_pixels
) * 100

print()
print("=" * 60)
print("RESULT")
print("=" * 60)

print(
    f"Model: {result.model_name}"
)

print(
    f"Inference time: "
    f"{result.inference_time_ms:.2f} ms"
)

print(
    f"Mask shape: {mask.shape}"
)

print(
    f"Road pixels: {road_pixels}"
)

print(
    f"Road coverage: "
    f"{road_percentage:.2f}%"
)

print(
    f"Saved mask: {OUTPUT_PATH}"
)

print("=" * 60)