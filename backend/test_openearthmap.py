import numpy as np
from PIL import Image

from app.engines.vision.pipeline import VisionPipeline
from app.engines.vision.colorizer import MaskColorizer
from app.engines.analysis.roads import RoadExtractor


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

IMAGE_PATH = "generated/tile0.png"

MODEL = "openearthmap"

ROAD_CLASS_ID = 4


# ---------------------------------------------------------
# Run Vision Pipeline
# ---------------------------------------------------------

print(
    f"Using image: {IMAGE_PATH}"
)

print(
    f"Using model: {MODEL}"
)

pipeline = VisionPipeline(MODEL)

segmentation_result = pipeline.run(
    IMAGE_PATH
)


# ---------------------------------------------------------
# Get segmentation mask
# ---------------------------------------------------------

mask = segmentation_result.mask


print("\n--------------------------------")
print("SEGMENTATION RESULT")
print("--------------------------------")

print(
    "Model:",
    segmentation_result.model_name
)

print(
    "Inference time:",
    segmentation_result.inference_time_ms,
    "ms"
)

print(
    "Image size:",
    segmentation_result.image_size
)

print(
    "Mask shape:",
    mask.shape
)


# ---------------------------------------------------------
# Print detected classes
# ---------------------------------------------------------

classes = np.unique(mask)

print(
    "\nDetected classes:",
    classes
)

for c in classes:

    pixels = np.sum(mask == c)

    print(
        f"Class {c}: {pixels} pixels"
    )


# ---------------------------------------------------------
# Road class
# ---------------------------------------------------------

road_pixels = np.sum(
    mask == ROAD_CLASS_ID
)

print(
    "\nRoad class ID:",
    ROAD_CLASS_ID
)

print(
    "Road pixels:",
    road_pixels
)


# ---------------------------------------------------------
# Extract road mask
# ---------------------------------------------------------

road_mask = RoadExtractor.extract(
    mask,
    [ROAD_CLASS_ID],
)


# ---------------------------------------------------------
# Save road mask
# ---------------------------------------------------------

Image.fromarray(
    (
        road_mask.astype(np.uint8)
        * 255
    )
).save(
    "generated/roads.png"
)

print(
    "\nRoad mask saved to:"
)

print(
    "generated/roads.png"
)


# ---------------------------------------------------------
# Save raw segmentation
# ---------------------------------------------------------

np.save(
    "generated/test_mask.npy",
    mask,
)

print(
    "Raw mask saved to:"
)

print(
    "generated/test_mask.npy"
)


# ---------------------------------------------------------
# Save colored segmentation
# ---------------------------------------------------------

colored = MaskColorizer.colorize(
    mask
)

colored.save(
    "generated/test_mask.png"
)

print(
    "Colored segmentation saved to:"
)

print(
    "generated/test_mask.png"
)


# ---------------------------------------------------------
# Final
# ---------------------------------------------------------

print(
    "\nOpenEarthMap segmentation test completed."
)