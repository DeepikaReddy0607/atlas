import numpy as np

from app.engines.vision.pipeline import VisionPipeline
from app.engines.vision.colorizer import MaskColorizer

pipeline = VisionPipeline()

mask = pipeline.run("generated/tile0.png")

import numpy as np

classes = np.unique(mask)

print("Detected classes:", classes)

for c in classes:
    pixels = np.sum(mask == c)
    print(f"Class {c}: {pixels} pixels")

from PIL import Image
from app.engines.analysis.roads import RoadExtractor

road_mask = RoadExtractor.extract(mask, [6])

Image.fromarray(
    road_mask * 255
).save("generated/roads.png")

print("Road mask saved.")

np.save("generated/test_mask.npy", mask)

colored = MaskColorizer.colorize(mask)

colored.save("generated/test_mask.png")

print(mask.shape)
print("Done!")