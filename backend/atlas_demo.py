import cv2

from app.engines.analysis.skeleton import Skeletonizer
from app.engines.analysis.graph_builder import GraphBuilder
from app.engines.analysis.topology import TopologyBuilder
from app.engines.analysis.criticality import CriticalityAnalyzer
from app.engines.analysis.simulator import ScenarioSimulator
from app.engines.analysis.risk import RiskAssessment

from app.engines.visualization.renderer import GraphRenderer


def main():

    print("=" * 60)
    print("ATLAS - Infrastructure Resilience Analysis")
    print("=" * 60)

    # ------------------------------------
    # Load Input
    # ------------------------------------

    mask = cv2.imread(
        "data/sample/roads_gt.png",
        cv2.IMREAD_GRAYSCALE,
    )

    # ------------------------------------
    # Build Analysis Pipeline
    # ------------------------------------

    skeleton = Skeletonizer.build(mask)

    pixel_graph = GraphBuilder.build(skeleton)

    topology = TopologyBuilder.build_topology(pixel_graph)

    node_scores = CriticalityAnalyzer.node_centrality(topology)

    simulation = ScenarioSimulator.simulate_most_critical_node(
        topology
    )

    # ------------------------------------
    # Temporary ARI
    # ------------------------------------

    ari = 0.30

    risk = RiskAssessment.classify(ari)

    recommendation = RiskAssessment.recommendation(risk)

    # ------------------------------------
    # Visualization
    # ------------------------------------

    canvas = GraphRenderer.blank()

    canvas = GraphRenderer.draw_graph(
        canvas,
        topology,
    )

    canvas = GraphRenderer.draw_criticality(
        canvas,
        topology,
        node_scores,
    )

    cv2.imwrite(
        "generated/atlas_result.png",
        canvas,
    )

    # ------------------------------------
    # Report
    # ------------------------------------

    critical_node = max(
        node_scores,
        key=node_scores.get,
    )

    print()

    print(f"Road Nodes          : {topology.number_of_nodes()}")
    print(f"Road Segments       : {topology.number_of_edges()}")

    print()

    print(f"Critical Junction   : {critical_node}")
    print(f"Criticality Score   : {node_scores[critical_node]:.4f}")

    print()

    print(f"Connected Components: {simulation.connected_components}")
    print(f"Largest Component   : {simulation.largest_component}")

    print()

    print(f"ATLAS Resilience Index : {ari:.2f}")
    print(f"Risk Level             : {risk}")

    print()

    print("Recommendation:")
    print(recommendation)

    print()

    print("Visualization Saved:")
    print("generated/atlas_result.png")

    print("=" * 60)


if __name__ == "__main__":
    main()