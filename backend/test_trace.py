import cv2

from app.engines.analysis.skeleton import Skeletonizer
from app.engines.analysis.graph_builder import GraphBuilder
from app.engines.analysis.node_detector import NodeDetector
from app.engines.analysis.graph_compressor import GraphCompressor
from app.engines.analysis.topology import TopologyBuilder

mask = cv2.imread(
    "data/sample/roads_gt.png",
    cv2.IMREAD_GRAYSCALE,
)

skeleton = Skeletonizer.build(mask)

graph = GraphBuilder.build(skeleton)

endpoints = set(NodeDetector.endpoints(graph))

clusters = GraphCompressor.junction_clusters(graph)

representatives = {
    next(iter(cluster))
    for cluster in clusters
}

important_nodes = endpoints | representatives

start = next(iter(endpoints))

print("Starting endpoint:", start)

for neighbor in graph.neighbors(start):

    path = TopologyBuilder.trace_path(
        graph,
        start,
        neighbor,
        important_nodes,
    )

    print("Path length:", len(path))
    print("Ends at:", path[-1])