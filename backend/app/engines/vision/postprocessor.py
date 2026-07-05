import numpy as np


class PostProcessor:

    @staticmethod
    def binary_mask(mask, threshold=0.5):

        return (mask > threshold).astype(np.uint8)