from app.engines.atlas.result import AtlasResult
from app.engines.vision.pipeline import VisionPipeline
from app.engines.analysis.topology import TopologyBuilder
from app.engines.analysis.skeleton import Skeletonizer
from app.engines.analysis.graph_builder import GraphBuilder
from app.engines.analysis.criticality import CriticalityAnalyzer
from app.engines.analysis.resilience import ResilienceAnalyzer
from app.engines.analysis.risk import RiskAssessment
from app.engines.analysis.simulator import ScenarioSimulator
from outputs.visualizations.engine import VisualizationEngine

class AtlasEngine:
    """
    Main orchestration engine for ATLAS.

    This class coordinates all major ATLAS subsystems.

    Pipeline:

        Input Image
              ↓
        Vision Engine
              ↓
        Analysis Engine
              ↓
        Simulation Engine
              ↓
        Decision Engine
              ↓
        Visualization Engine
              ↓
        AtlasResult
    """

    def __init__(self, model_name: str = "ade20k"):

        self.vision = VisionPipeline(model_name)

        self.visualization = VisualizationEngine()

    def analyze(self, image_path: str):

        # Step 1 : Vision
        segmentation = self.vision.run(image_path)

        # Step 2 : Skeleton
        skeleton = Skeletonizer.build(segmentation.mask)

        # Step 3 : Pixel Graph
        pixel_graph = GraphBuilder.build(skeleton)

        # Step 4 : Topology Graph
        topology_graph = TopologyBuilder.build_topology(pixel_graph)

        # Step 5 : Criticality
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

        # Step 6 : Most critical junction
        critical_node = max(
            node_scores,
            key=node_scores.get,
        )

        # Step 7 : Simulate failure
        failed_graph = ResilienceAnalyzer.remove_node(
            topology_graph,
            critical_node,
        )

        components = ResilienceAnalyzer.connected_components(
            failed_graph,
        )

        largest_component = (
            ResilienceAnalyzer.largest_component_size(
                failed_graph
            )
        )

        resilience = {
            "critical_node": critical_node,
            "failed_graph": failed_graph,
            "connected_components": len(components),
            "largest_component": largest_component,
        }

        # Step 8 : Risk
        original_size = topology_graph.number_of_nodes()

        ari = (
            largest_component / original_size
            if original_size > 0
            else 0
        )

        risk_level = RiskAssessment.classify(ari)

        recommendation = RiskAssessment.recommendation(
            risk_level
        )

        risk = {
            "ari": ari,
            "level": risk_level,
            "recommendation": recommendation,
        }

        # Step 9 : Simulation
        simulation = ScenarioSimulator.simulate_node_failure(
            topology_graph,
            critical_node,
        )

        atlas_result = AtlasResult(
            segmentation=segmentation,
            pixel_graph=pixel_graph,
            topology_graph=topology_graph,
            criticality=criticality,
            resilience=resilience,
            risk=risk,
            simulation=simulation,
            recommendation=recommendation,
        )
        atlas_result.visualizations = self.visualization.generate(
            image_path=image_path,
            atlas_result=atlas_result,
        )
        return atlas_result