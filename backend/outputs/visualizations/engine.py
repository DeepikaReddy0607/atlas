from pathlib import Path

import cv2
import numpy as np

from app.engines.vision.result import SegmentationResult
from outputs.visualizations.result import VisualizationResult
from app.engines.atlas.result import AtlasResult

class VisualizationEngine:
    """
    Responsible for generating visual outputs
    produced by Project ATLAS.
    """

    def __init__(self):

        self.output_dir = Path("outputs/visualizations")
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def generate_segmentation_overlay(
        self,
        image_path: str,
        segmentation: SegmentationResult,
    ) -> Path:

        # Load original image
        image = cv2.imread(image_path)

        if image is None:
            raise FileNotFoundError(
                f"Unable to read image: {image_path}"
            )

        mask = segmentation.mask

        # Convert mask to uint8
        mask = mask.astype(np.uint8)

        # Normalize labels into 0-255 range
        if mask.max() > 0:
            mask = (
                mask.astype(np.float32)
                / mask.max()
                * 255
            ).astype(np.uint8)

        # Apply OpenCV colormap
        colored_mask = cv2.applyColorMap(
            mask,
            cv2.COLORMAP_JET,
        )

        # Blend image and mask
        overlay = cv2.addWeighted(
            image,
            0.6,
            colored_mask,
            0.4,
            0,
        )

        # Create output directory
        overlay_dir = self.output_dir / "overlays"
        overlay_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path = (
            overlay_dir
            / f"{Path(image_path).stem}_overlay.png"
        )

        cv2.imwrite(
            str(output_path),
            overlay,
        )

        return output_path
    def generate(
        self,
        image_path: str,
        atlas_result: AtlasResult,
    ) -> VisualizationResult:
        """
        Generate every visualization for the current
        ATLAS analysis.
        """

        visualizations = VisualizationResult()

        visualizations.segmentation_overlay = str(
            self.generate_segmentation_overlay(
                image_path=image_path,
                segmentation=atlas_result.segmentation,
            )
        )

        # Future visualizations
        #
        # visualizations.road_mask = ...
        # visualizations.skeleton = ...
        # visualizations.graph = ...
        # visualizations.criticality = ...

        return visualizations