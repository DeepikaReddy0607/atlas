from abc import ABC, abstractmethod
from PIL import Image

from app.engines.vision.result import SegmentationResult


class BasePredictor(ABC):

    @abstractmethod
    def predict(
        self,
        image: Image.Image,
    ) -> SegmentationResult:
        """
        Perform semantic segmentation on an image.

        Parameters
        ----------
        image : PIL.Image.Image
            Input RGB image.

        Returns
        -------
        SegmentationResult
            Complete segmentation result including mask and metadata.
        """
        pass