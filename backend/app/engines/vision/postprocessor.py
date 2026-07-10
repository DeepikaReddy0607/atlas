import cv2
import numpy as np


class PostProcessor:
    """
    Utilities for refining semantic segmentation masks before
    graph extraction.
    """

    @staticmethod
    def binary_mask(mask: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        """
        Convert probability/logit mask into a binary mask.
        """
        return (mask > threshold).astype(np.uint8)

    @staticmethod
    def remove_noise(mask: np.ndarray, kernel_size: int = 3) -> np.ndarray:
        """
        Remove isolated pixels using morphological opening.
        """
        kernel = np.ones((kernel_size, kernel_size), np.uint8)

        return cv2.morphologyEx(
            mask,
            cv2.MORPH_OPEN,
            kernel,
        )

    @staticmethod
    def close_gaps(mask: np.ndarray, kernel_size: int = 3) -> np.ndarray:
        """
        Connect nearby road segments.
        """
        kernel = np.ones((kernel_size, kernel_size), np.uint8)

        return cv2.morphologyEx(
            mask,
            cv2.MORPH_CLOSE,
            kernel,
        )

    @staticmethod
    def process(mask: np.ndarray) -> np.ndarray:
        """
        Complete post-processing pipeline.
        """

        mask = PostProcessor.binary_mask(mask)

        mask = PostProcessor.remove_noise(mask)

        mask = PostProcessor.close_gaps(mask)

        return mask