import cv2

from app.engines.analysis.skeleton import Skeletonizer
from app.engines.analysis.graph_builder import GraphBuilder
from app.engines.analysis.topology import TopologyBuilder

mask = cv2.imread(
    "data/sample/roads_gt.png",
    cv2.IMREAD_GRAYSCALE,
)

skeleton = Skeletonizer.build(mask)

graph = GraphBuilder.build(skeleton)

topology = TopologyBuilder.build(graph)

print("Topology Nodes:", topology.number_of_nodes())
print("Topology Edges:", topology.number_of_edges())

print(list(topology.nodes()))