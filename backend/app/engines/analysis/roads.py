import numpy as np


class RoadExtractor:

    @staticmethod
    def extract(mask, road_classes):
        """
        Extract only road pixels from a semantic segmentation mask.

        Parameters
        ----------
        mask : np.ndarray
            Semantic segmentation output.

        road_classes : list[int]
            IDs corresponding to road classes.

        Returns
        -------
        np.ndarray
            Binary road mask.
        """

        road_mask = np.isin(mask, road_classes)

        return road_mask.astype(np.uint8)