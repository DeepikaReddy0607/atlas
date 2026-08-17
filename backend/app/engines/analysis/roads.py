import cv2
import numpy as np


class RoadExtractor:

    # ---------------------------------------------------------
    # Raw road extraction
    # ---------------------------------------------------------

    @staticmethod
    def extract(
        mask: np.ndarray,
        road_classes: list[int],
    ) -> np.ndarray:
        """
        Extract road pixels from a semantic
        segmentation mask.

        Parameters
        ----------
        mask : np.ndarray
            Semantic segmentation class mask.

        road_classes : list[int]
            Class IDs corresponding to roads.

        Returns
        -------
        np.ndarray
            Binary road mask with values 0 or 1.
        """

        road_mask = np.isin(
            mask,
            road_classes,
        )

        return road_mask.astype(
            np.uint8
        )

    # ---------------------------------------------------------
    # Remove small isolated components
    # ---------------------------------------------------------

    @staticmethod
    def remove_small_components(
        road_mask: np.ndarray,
        min_size: int = 50,
    ) -> np.ndarray:
        """
        Remove small isolated regions from
        the road mask.

        Parameters
        ----------
        road_mask : np.ndarray
            Binary road mask.

        min_size : int
            Minimum connected-component size
            to preserve.

        Returns
        -------
        np.ndarray
            Cleaned binary road mask.
        """

        binary = (
            road_mask > 0
        ).astype(np.uint8)

        num_labels, labels, stats, _ = (
            cv2.connectedComponentsWithStats(
                binary,
                connectivity=8,
            )
        )

        cleaned = np.zeros_like(
            binary
        )

        for label in range(
            1,
            num_labels,
        ):
            area = stats[
                label,
                cv2.CC_STAT_AREA,
            ]

            if area >= min_size:
                cleaned[
                    labels == label
                ] = 1

        return cleaned

    # ---------------------------------------------------------
    # Morphological gap closing
    # ---------------------------------------------------------

    @staticmethod
    def close_gaps(
        road_mask: np.ndarray,
        kernel_size: int = 5,
        iterations: int = 1,
    ) -> np.ndarray:
        """
        Close small gaps and holes in the
        predicted road network.

        Parameters
        ----------
        road_mask : np.ndarray
            Binary road mask.

        kernel_size : int
            Morphological kernel size.

        iterations : int
            Number of closing iterations.

        Returns
        -------
        np.ndarray
            Refined binary road mask.
        """

        binary = (
            road_mask > 0
        ).astype(np.uint8)

        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE,
            (
                kernel_size,
                kernel_size,
            ),
        )

        closed = cv2.morphologyEx(
            binary,
            cv2.MORPH_CLOSE,
            kernel,
            iterations=iterations,
        )

        return closed.astype(
            np.uint8
        )

    # ---------------------------------------------------------
    # Complete refinement pipeline
    # ---------------------------------------------------------

    @staticmethod
    def refine(
        road_mask: np.ndarray,
        min_component_size: int = 50,
        kernel_size: int = 5,
        closing_iterations: int = 1,
    ) -> np.ndarray:
        """
        Refine a raw SegFormer road mask.

        Pipeline:

            Raw road mask
                ↓
            Morphological closing
                ↓
            Remove small components

        Parameters
        ----------
        road_mask : np.ndarray
            Raw binary road mask.

        min_component_size : int
            Minimum connected-component size.

        kernel_size : int
            Morphological closing kernel.

        closing_iterations : int
            Number of closing iterations.

        Returns
        -------
        np.ndarray
            Refined binary road mask.
        """

        refined = RoadExtractor.close_gaps(
            road_mask,
            kernel_size=kernel_size,
            iterations=closing_iterations,
        )

        refined = (
            RoadExtractor.remove_small_components(
                refined,
                min_size=min_component_size,
            )
        )

        return refined

    # ---------------------------------------------------------
    # One-step extraction + refinement
    # ---------------------------------------------------------

    @staticmethod
    def extract_refined(
        mask: np.ndarray,
        road_classes: list[int],
        min_component_size: int = 50,
        kernel_size: int = 5,
        closing_iterations: int = 1,
    ) -> np.ndarray:
        """
        Extract road pixels and immediately
        refine the resulting road mask.
        """

        raw_mask = RoadExtractor.extract(
            mask,
            road_classes,
        )

        return RoadExtractor.refine(
            raw_mask,
            min_component_size=min_component_size,
            kernel_size=kernel_size,
            closing_iterations=closing_iterations,
        )