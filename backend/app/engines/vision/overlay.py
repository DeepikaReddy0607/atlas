import numpy as np
from PIL import Image


class OverlayGenerator:

    @staticmethod
    def create_overlay(image, mask, alpha=0.5):
        image = np.array(image).astype(np.uint8)

        overlay = image.copy()

        # Red overlay
        overlay[mask == 1] = [255, 0, 0]

        blended = (
            image * (1 - alpha) +
            overlay * alpha
        ).astype(np.uint8)

        return Image.fromarray(blended)