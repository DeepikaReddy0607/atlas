import numpy as np
from PIL import Image


class MaskColorizer:

    COLORS = np.random.default_rng(42).integers(
        0,
        255,
        size=(256, 3),
        dtype=np.uint8,
    )

    @staticmethod
    def colorize(mask):

        rgb = MaskColorizer.COLORS[mask]

        return Image.fromarray(rgb)