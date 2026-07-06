import cv2

from app.engines.analysis.skeleton import Skeletonizer
from app.engines.analysis.graph_builder import GraphBuilder
from app.engines.analysis.topology import TopologyBuilder
from app.engines.analysis.criticality import CriticalityAnalyzer


# Load road mask
mask = cv2.imread(
    "data/sample/roads_gt.png",
    cv2.IMREAD_GRAYSCALE,
)

# Build pixel graph
skeleton = Skeletonizer.build(mask)

pixel_graph = GraphBuilder.build(skeleton)

# Build topology graph
topology = TopologyBuilder.build_topology(pixel_graph)

print("=" * 50)
print("Topology Graph")
print("=" * 50)

print(f"Nodes : {topology.number_of_nodes()}")
print(f"Edges : {topology.number_of_edges()}")

print()

# -----------------------------
# Node Centrality
# -----------------------------

print("=" * 50)
print("Node Betweenness Centrality")
print("=" * 50)

node_scores = CriticalityAnalyzer.node_centrality(topology)

for node, score in sorted(
    node_scores.items(),
    key=lambda x: x[1],
    reverse=True,
):
    print(f"{node} -> {score:.4f}")

print()

# -----------------------------
# Edge Centrality
# -----------------------------

print("=" * 50)
print("Edge Betweenness Centrality")
print("=" * 50)

edge_scores = CriticalityAnalyzer.edge_centrality(topology)

for edge, score in sorted(
    edge_scores.items(),
    key=lambda x: x[1],
    reverse=True,
):
    print(f"{edge} -> {score:.4f}")