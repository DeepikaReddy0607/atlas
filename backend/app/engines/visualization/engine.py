from pathlib import Path

from app.engines.atlas.result import AtlasResult

from outputs.visualizations.result import VisualizationResult
from outputs.visualizations.renderers.overlay_renderer import (
    OverlayRenderer,
)
from outputs.visualizations.renderers.road_mask_renderer import (
    RoadMaskRenderer,
)

from outputs.visualizations.renderers.criticality_renderer import (
    CriticalityRenderer,
)

class VisualizationEngine:
    """
    Generates all visual outputs produced by ATLAS.
    """

    def __init__(self):

        self.output_dir = Path("outputs/visualizations")
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.overlay_renderer = OverlayRenderer()
        self.road_mask_renderer = RoadMaskRenderer()
        self.criticality_renderer = CriticalityRenderer()

    def generate(
        self,
        image_path: str,
        atlas_result: AtlasResult,
    ) -> VisualizationResult:

        visualizations = VisualizationResult()

        visualizations.segmentation_overlay = str(
            self.overlay_renderer.render(
                image_path=image_path,
                segmentation=atlas_result.segmentation,
                output_dir=self.output_dir,
            )
        )

        visualizations.road_mask = str(
            self.road_mask_renderer.render(
                image_path=image_path,
                mask=atlas_result.segmentation.mask,
                output_dir=self.output_dir,
            )
        )

        visualizations.criticality = str(
            self.criticality_renderer.render(
                image_path=image_path,
                graph=atlas_result.topology_graph,
                node_scores=atlas_result.criticality["node"],
                output_dir=self.output_dir,
            )
        )
        # Future renderers
        #
        # visualizations.skeleton = ...
        # visualizations.graph = ...
        # visualizations.criticality = ...

        return visualizations