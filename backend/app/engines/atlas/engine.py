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

    Pipeline:

        Input Image
              ↓
        OpenEarthMap SegFormer-B5
              ↓
        Semantic Segmentation
              ↓
        Road Extraction
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
    """

    # ---------------------------------------------------------
    # Configuration
    # ---------------------------------------------------------

    DEFAULT_MODEL = "openearthmap"

    ROAD_CLASS_ID = 4

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

        self.visualization = (
            VisualizationEngine()
        )

        # -----------------------------------------------------
        # Last analysis
        # -----------------------------------------------------

        self._last_result = None

        print(
            "ATLAS engine initialized."
        )

    # =========================================================
    # ANALYZE
    # =========================================================

    def analyze(
        self,
        image_path: str,
    ):

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
            image_path
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

        road_mask = RoadExtractor.extract(
            segmentation.mask,
            [self.ROAD_CLASS_ID],
        )

        import cv2
        import numpy as np

        developed_mask = (
            segmentation.mask == 3
        ).astype(np.uint8) * 255

        cv2.imwrite(
            "generated/developed_space.png",
            developed_mask,
        )
        print(
            "Road class:",
            self.ROAD_CLASS_ID,
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

        refined_road_mask =RoadExtractor.refine(
                                road_mask,
                                min_component_size=50,
                                kernel_size=5,
                                closing_iterations=1,
                                )
        

        print(
            "Refined road pixels:",
            int(
                refined_road_mask.sum()
            ),
        )

        from PIL import Image

        Image.fromarray(
            refined_road_mask.astype("uint8") * 255
        ).save(
            "generated/atlas_roads.png"
        )

        print(
            "Road mask saved to:"
            " generated/atlas_roads.png"
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
        Image.fromarray(
            skeleton.astype("uint8") * 255
        ).save(
            "generated/atlas_skeleton.png"
        )

        print(
            "Skeleton saved to:"
            " generated/atlas_skeleton.png"
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

        topology_graph = (
            TopologyBuilder.build_topology(
                pixel_graph
            )
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

        node_scores = (
            CriticalityAnalyzer.node_centrality(
                topology_graph
            )
        )

        edge_scores = (
            CriticalityAnalyzer.edge_centrality(
                topology_graph
            )
        )

        criticality = {
            "node": node_scores,
            "edge": edge_scores,
        }

        # -----------------------------------------------------
        # Find most critical node
        # -----------------------------------------------------

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

            failed_graph = (
                ResilienceAnalyzer.remove_node(
                    topology_graph,
                    critical_node,
                )
            )

            components = (
                ResilienceAnalyzer.connected_components(
                    failed_graph
                )
            )

            largest_component = (
                ResilienceAnalyzer
                .largest_component_size(
                    failed_graph
                )
            )

        else:

            failed_graph = topology_graph.copy()

            components = (
                ResilienceAnalyzer.connected_components(
                    topology_graph
                )
            )

            largest_component = (
                ResilienceAnalyzer
                .largest_component_size(
                    topology_graph
                )
            )

        resilience = {
            "critical_node": critical_node,
            "failed_graph": failed_graph,
            "connected_components": len(
                components
            ),
            "largest_component": (
                largest_component
            ),
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

        original_size = (
            topology_graph.number_of_nodes()
        )

        ari = (
            largest_component
            / original_size
            if original_size > 0
            else 0
        )

        risk_level = (
            RiskAssessment.classify(
                ari
            )
        )

        recommendation = (
            RiskAssessment.recommendation(
                risk_level
            )
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

            simulation = (
                ScenarioSimulator
                .simulate_node_failure(
                    topology_graph,
                    critical_node,
                )
            )

        else:

            simulation = {}

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
                image_path=image_path,
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
    ):
        """
        Run a failure simulation on the most
        recently analyzed topology graph.
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

        # -----------------------------------------------------
        # Critical-node failure
        # -----------------------------------------------------

        if scenario == "critical":

            return (
                ScenarioSimulator
                .simulate_most_critical_node(
                    topology_graph
                )
            )

        raise ValueError(
            f"Unsupported simulation scenario: "
            f"{scenario}"
        )