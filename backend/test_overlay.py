from PIL import Image
import numpy as np

from app.engines.vision.overlay import OverlayGenerator

image = Image.open("generated/hyderabad_clear.png")

mask = np.zeros(
    (image.height, image.width),
    dtype=np.uint8
)

# Fake road strip
mask[300:350, 100:900] = 1

overlay = OverlayGenerator.create_overlay(
    image,
    mask
)

overlay.save(
    "generated/hyderabad_overlay.png"
)

print("Overlay created successfully!")