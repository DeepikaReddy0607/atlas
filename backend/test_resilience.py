import cv2

from app.engines.analysis.skeleton import Skeletonizer
from app.engines.analysis.graph_builder import GraphBuilder
from app.engines.analysis.topology import TopologyBuilder
from app.engines.analysis.criticality import CriticalityAnalyzer
from app.engines.analysis.resilience import ResilienceAnalyzer


mask = cv2.imread(
    "data/sample/roads_gt.png",
    cv2.IMREAD_GRAYSCALE,
)

skeleton = Skeletonizer.build(mask)

pixel_graph = GraphBuilder.build(skeleton)

topology = TopologyBuilder.build_topology(pixel_graph)

print("=" * 50)
print("Original Graph")
print("=" * 50)

print("Nodes:", topology.number_of_nodes())
print("Edges:", topology.number_of_edges())

print(
    "Largest Component:",
    ResilienceAnalyzer.largest_component_size(topology),
)

print()

# Find the most critical junction
scores = CriticalityAnalyzer.node_centrality(topology)

critical_node = max(scores, key=scores.get)

print("Critical Node:", critical_node)
print("Score:", scores[critical_node])

print()

# Simulate failure
failed = ResilienceAnalyzer.remove_node(
    topology,
    critical_node,
)

print("=" * 50)
print("After Failure")
print("=" * 50)

print("Nodes:", failed.number_of_nodes())
print("Edges:", failed.number_of_edges())

components = ResilienceAnalyzer.connected_components(failed)

print("Connected Components:", len(components))

print(
    "Largest Component:",
    ResilienceAnalyzer.largest_component_size(failed),
)

print()

for i, component in enumerate(components, start=1):
    print(f"Component {i}: {len(component)} nodes")