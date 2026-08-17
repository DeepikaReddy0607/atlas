from .types import VisualizationLayer


class OverlayRenderer:

    def render(
        self,
        image_path: str,
        segmentation_result,
    ) -> VisualizationLayer:
        """
        Creates a visualization layer from the segmentation result.
        """

        overlay_path = (
            segmentation_result.metadata.get("overlay_path")
        )

        if overlay_path is None:
            return None

        return VisualizationLayer(
            id="segmentation",
            name="Road Segmentation",
            url=overlay_path,
            layer_type="overlay",
        )