import numpy as np
from PIL import Image

from app.engines.vision.tiler import ImageTiler
from app.engines.vision.stitcher import MaskStitcher

image = Image.open("generated/hyderabad_clear.png")

tiles = ImageTiler.split(image)

predictions = []

for tile, x, y in tiles:

    # Fake prediction for now
    mask = np.zeros((tile.height, tile.width), dtype=np.uint8)

    mask[150:170, :] = 1

    predictions.append((mask, x, y))

full_mask = MaskStitcher.stitch(
    predictions,
    image.width,
    image.height
)

print(full_mask.shape)