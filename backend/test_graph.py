import cv2

from app.engines.analysis.graph_builder import GraphBuilder

# Load skeleton
skeleton = cv2.imread(
    "data/sample/skeleton.png",
    cv2.IMREAD_GRAYSCALE,
)

graph = GraphBuilder.build(skeleton)

print(f"Nodes : {graph.number_of_nodes()}")
print(f"Edges : {graph.number_of_edges()}")

from app.engines.analysis.node_detector import NodeDetector

endpoints = NodeDetector.endpoints(graph)
junctions = NodeDetector.junctions(graph)

print(f"Endpoints : {len(endpoints)}")
print(f"Junctions : {len(junctions)}")

from app.engines.analysis.graph_compressor import GraphCompressor

clusters = GraphCompressor.junction_clusters(graph)

print(f"Junction Clusters : {len(clusters)}")

for i, cluster in enumerate(clusters):
    print(f"Cluster {i+1}: {len(cluster)} pixels")