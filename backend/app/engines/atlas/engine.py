from pathlib import Path
from typing import Optional

from PIL import Image

from app.engines.atlas.result import AtlasResult
from app.engines.vision.pipeline import VisionPipeline

from app.engines.analysis.roads import RoadExtractor
from app.engines.analysis.skeleton import Skeletonizer
from app.engines.analysis.graph_builder import GraphBuilder
from app.engines.analysis.topology import TopologyBuilder
from app.engines.analysis.criticality import CriticalityAnalyzer
from app.engines.analysis.resilience import ResilienceAnalyzer
from app.engines.analysis.risk import RiskAssessment
from app.engines.analysis.simulator import ScenarioSimulator

from outputs.visualizations.engine import VisualizationEngine


class AtlasEngine:
    """
    Main orchestration engine for ATLAS.

    Production pipeline:

        Input Image
              ↓
        ATLAS Road Ensemble
              ↓
        Binary Road Mask
              ↓
        Road Mask Refinement
              ↓
        Skeletonization
              ↓
        Pixel Graph
              ↓
        Topology Graph
              ↓
        Criticality Analysis
              ↓
        Resilience Analysis
              ↓
        Risk Assessment
              ↓
        Failure Simulation
              ↓
        Visualization
              ↓
        AtlasResult

    AtlasEngine owns orchestration only. Domain operations remain
    delegated to their respective analysis engines.
    """

    # ---------------------------------------------------------
    # Configuration
    # ---------------------------------------------------------

    DEFAULT_MODEL = "ensemble"

    # These paths are intentionally retained for compatibility
    # with the existing local/development workflow.
    GENERATED_DIR = Path("generated")
    ROAD_MASK_PATH = GENERATED_DIR / "atlas_roads.png"
    SKELETON_PATH = GENERATED_DIR / "atlas_skeleton.png"

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
    ):
        print(
            f"Initializing ATLAS with model: "
            f"{model_name}"
        )

        self.model_name = model_name

        # -----------------------------------------------------
        # Vision Engine
        # -----------------------------------------------------

        self.vision = VisionPipeline(
            model_name
        )

        # -----------------------------------------------------
        # Visualization Engine
        # -----------------------------------------------------

        self.visualization = VisualizationEngine()

        # -----------------------------------------------------
        # Last analysis
        # -----------------------------------------------------

        # Kept for compatibility with the existing simulation API.
        # The API must run with a single application process/worker
        # while simulation state is kept in memory.
        self._last_result: Optional[AtlasResult] = None

        print(
            "ATLAS engine initialized."
        )

    # =========================================================
    # INTERNAL HELPERS
    # =========================================================

    @classmethod
    def _save_binary_mask(
        cls,
        mask,
        path: Path,
    ) -> None:
        """Save a binary NumPy mask using the existing output paths."""

        cls.GENERATED_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        Image.fromarray(
            mask.astype("uint8") * 255
        ).save(path)

    # =========================================================
    # ANALYZE
    # =========================================================

    def analyze(
        self,
        image_path: str,
    ) -> AtlasResult:

        if not image_path:
            raise ValueError(
                "An image path is required for ATLAS analysis."
            )

        image_file = Path(image_path)

        if not image_file.is_file():
            raise ValueError(
                f"Input image does not exist: {image_path}"
            )

        print(
            "\n================================"
        )
        print(
            "ATLAS ANALYSIS STARTED"
        )
        print(
            "================================"
        )

        # =====================================================
        # STEP 1 — Vision
        # =====================================================

        print(
            "\n[1/10] Running vision..."
        )

        segmentation = self.vision.run(
            str(image_file)
        )

        print(
            "Vision model:",
            segmentation.model_name,
        )

        print(
            "Inference time:",
            segmentation.inference_time_ms,
            "ms",
        )

        print(
            "Image size:",
            segmentation.image_size,
        )

        print(
            "Segmentation mask shape:",
            segmentation.mask.shape,
        )

        # =====================================================
        # STEP 2 — Road Extraction
        # =====================================================

        print(
            "\n[2/10] Extracting roads..."
        )

        output_type = segmentation.metadata.get(
            "output_type",
            "semantic",
        )

        # -----------------------------------------------------
        # Semantic segmentation models
        # -----------------------------------------------------

        if output_type == "semantic":

            road_class_id = segmentation.metadata.get(
                "road_class_id"
            )

            if road_class_id is None:
                raise ValueError(
                    f"Model '{segmentation.model_name}' "
                    "does not define road_class_id."
                )

            road_mask = RoadExtractor.extract(
                segmentation.mask,
                [road_class_id],
            )

            print(
                "Segmentation type: semantic"
            )

            print(
                "Road class:",
                road_class_id,
            )

        # -----------------------------------------------------
        # Binary road segmentation models
        # -----------------------------------------------------

        elif output_type == "binary_road":

            road_mask = segmentation.mask > 0

            print(
                "Segmentation type: binary road"
            )

            print(
                "Binary road mask detected."
            )

        # -----------------------------------------------------
        # Unknown output type
        # -----------------------------------------------------

        else:

            raise ValueError(
                f"Unsupported segmentation output type: "
                f"{output_type}"
            )

        print(
            "Raw road pixels:",
            int(road_mask.sum()),
        )

        # =====================================================
        # STEP 3 — Road Mask Refinement
        # =====================================================

        print(
            "\n[3/10] Refining road mask..."
        )

        # These settings are intentionally unchanged from the
        # validated ATLAS production configuration.
        refined_road_mask = RoadExtractor.refine(
            road_mask,
            min_component_size=0,
            kernel_size=1,
            closing_iterations=0,
        )

        print(
            "Refined road pixels:",
            int(refined_road_mask.sum()),
        )

        self._save_binary_mask(
            refined_road_mask,
            self.ROAD_MASK_PATH,
        )

        print(
            "Road mask saved to:",
            str(self.ROAD_MASK_PATH),
        )

        # =====================================================
        # STEP 4 — Skeletonization
        # =====================================================

        print(
            "\n[4/10] Skeletonizing road network..."
        )

        skeleton = Skeletonizer.build(
            refined_road_mask
        )

        print(
            "Skeleton shape:",
            skeleton.shape,
        )

        print(
            "Skeleton dtype:",
            skeleton.dtype,
        )

        print(
            "Skeleton pixels:",
            int(skeleton.sum()),
        )

        self._save_binary_mask(
            skeleton,
            self.SKELETON_PATH,
        )

        print(
            "Skeleton saved to:",
            str(self.SKELETON_PATH),
        )

        # =====================================================
        # STEP 5 — Pixel Graph
        # =====================================================

        print(
            "\n[5/10] Building pixel graph..."
        )

        pixel_graph = GraphBuilder.build(
            skeleton
        )

        print(
            "Pixel graph nodes:",
            pixel_graph.number_of_nodes(),
        )

        print(
            "Pixel graph edges:",
            pixel_graph.number_of_edges(),
        )

        # =====================================================
        # STEP 6 — Topology Graph
        # =====================================================

        print(
            "\n[6/10] Building topology graph..."
        )

        topology_graph = TopologyBuilder.build(
            pixel_graph
        )

        print(
            "Topology nodes:",
            topology_graph.number_of_nodes(),
        )

        print(
            "Topology edges:",
            topology_graph.number_of_edges(),
        )

        # =====================================================
        # STEP 7 — Criticality
        # =====================================================

        print(
            "\n[7/10] Computing criticality..."
        )

        node_scores = CriticalityAnalyzer.node_centrality(
            topology_graph
        )

        edge_scores = CriticalityAnalyzer.edge_centrality(
            topology_graph
        )

        criticality = {
            "node": node_scores,
            "edge": edge_scores,
        }

        if node_scores:

            critical_node = max(
                node_scores,
                key=node_scores.get,
            )

            print(
                "Most critical node:",
                critical_node,
            )

        else:

            critical_node = None

            print(
                "No critical node found."
            )

        # =====================================================
        # STEP 8 — Resilience
        # =====================================================

        print(
            "\n[8/10] Computing resilience..."
        )

        if critical_node is not None:

            failed_graph = ResilienceAnalyzer.remove_node(
                topology_graph,
                critical_node,
            )

            components = (
                ResilienceAnalyzer.connected_components(
                    failed_graph
                )
            )

            largest_component = (
                ResilienceAnalyzer.largest_component_size(
                    failed_graph
                )
            )

        else:

            # No failure is applied when there is no critical node.
            # Use the original topology for baseline measurements.
            components = (
                ResilienceAnalyzer.connected_components(
                    topology_graph
                )
            )

            largest_component = (
                ResilienceAnalyzer.largest_component_size(
                    topology_graph
                )
            )

        # Only public resilience metrics belong in AtlasResult.
        # The temporary failed graph remains an internal object.
        resilience = {
            "critical_node": critical_node,
            "connected_components": len(components),
            "largest_component": largest_component,
        }

        print(
            "Connected components:",
            len(components),
        )

        print(
            "Largest component:",
            largest_component,
        )

        # =====================================================
        # STEP 9 — Risk
        # =====================================================

        print(
            "\n[9/10] Assessing risk..."
        )

        original_size = topology_graph.number_of_nodes()

        ari = (
            largest_component / original_size
            if original_size > 0
            else 0
        )

        risk_level = RiskAssessment.classify(
            ari
        )

        recommendation = RiskAssessment.recommendation(
            risk_level
        )

        risk = {
            "ari": ari,
            "level": risk_level,
            "recommendation": recommendation,
        }

        print(
            "ARI:",
            round(ari, 4),
        )

        print(
            "Risk:",
            risk_level,
        )

        # =====================================================
        # STEP 10 — Simulation
        # =====================================================

        print(
            "\n[10/10] Running simulation..."
        )

        if critical_node is not None:

            simulation = ScenarioSimulator.simulate_node_failure(
                topology_graph,
                critical_node,
            )

        else:

            simulation = None

            print(
                "Simulation skipped: "
                "no critical node."
            )

        # =====================================================
        # Build AtlasResult
        # =====================================================

        atlas_result = AtlasResult(
            segmentation=segmentation,
            skeleton=skeleton,
            pixel_graph=pixel_graph,
            topology_graph=topology_graph,
            criticality=criticality,
            resilience=resilience,
            risk=risk,
            simulation=simulation,
            recommendation=recommendation,
        )

        # =====================================================
        # Visualization
        # =====================================================

        print(
            "\nGenerating visualizations..."
        )

        atlas_result.visualizations = (
            self.visualization.generate(
                image_path=str(image_file),
                atlas_result=atlas_result,
            )
        )

        # =====================================================
        # Store result
        # =====================================================

        self._last_result = atlas_result

        print(
            "\n================================"
        )
        print(
            "ATLAS ANALYSIS COMPLETE"
        )
        print(
            "================================"
        )

        return atlas_result

    # =========================================================
    # SIMULATION
    # =========================================================

    def simulate(
        self,
        scenario: str,
        node=None,
        edge=None,
    ):
        """
        Run a failure simulation on the most
        recently analyzed topology graph.

        Supported scenarios:

            critical
            critical_node
            node
            critical_edge
            edge

        The stored topology graph is never mutated.
        """

        if self._last_result is None:

            raise ValueError(
                "No analyzed network available. "
                "Run /atlas/analyze first."
            )

        topology_graph = (
            self._last_result.topology_graph
        )

        if topology_graph is None:

            raise ValueError(
                "Topology graph is not available."
            )

        normalized = (
            scenario
            .strip()
            .lower()
        )

        # -----------------------------------------------------
        # Critical node
        # -----------------------------------------------------

        if normalized in {
            "critical",
            "critical_node",
            "critical-node",
        }:

            return (
                ScenarioSimulator
                .simulate_most_critical_node(
                    topology_graph
                )
            )

        # -----------------------------------------------------
        # Selected node
        # -----------------------------------------------------

        if normalized in {
            "node",
            "node_failure",
            "node-failure",
        }:

            if node is None:
                raise ValueError(
                    "Node coordinates are required "
                    "for node failure simulation."
                )
            return (
                ScenarioSimulator
                .simulate_node_failure(
                    topology_graph,
                    node,
                )
            )

        # -----------------------------------------------------
        # Critical edge
        # -----------------------------------------------------

        if normalized in {
            "critical_edge",
            "critical-edge",
        }:

            return (
                ScenarioSimulator
                .simulate_most_critical_edge(
                    topology_graph
                )
            )

        # -----------------------------------------------------
        # Selected edge
        # -----------------------------------------------------

        if normalized in {
            "edge",
            "edge_failure",
            "edge-failure",
        }:
            if edge is None:
                raise ValueError(
                    "Edge coordinates are required "
                    "for edge failure simulation."
                )
            return ScenarioSimulator.simulate_edge_failure(
                topology_graph,
                edge,
            )
        raise ValueError(
            f"Unsupported simulation scenario: "
            f"{scenario}"
        )