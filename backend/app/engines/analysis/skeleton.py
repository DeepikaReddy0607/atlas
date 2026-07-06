import numpy as np
from skimage.morphology import skeletonize


class Skeletonizer:

    @staticmethod
    def build(mask: np.ndarray) -> np.ndarray:
        """
        Convert a binary road mask into a 1-pixel-wide skeleton.
        """

        binary = mask > 0

        skeleton = skeletonize(binary)

        return (skeleton * 255).astype(np.uint8)