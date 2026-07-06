import cv2

from app.engines.analysis.skeleton import Skeletonizer
from app.engines.analysis.graph_builder import GraphBuilder
from app.engines.analysis.topology import TopologyBuilder

from app.engines.visualization.renderer import GraphRenderer


mask = cv2.imread(
    "data/sample/roads_gt.png",
    cv2.IMREAD_GRAYSCALE,
)

skeleton = Skeletonizer.build(mask)

pixel_graph = GraphBuilder.build(skeleton)

topology = TopologyBuilder.build_topology(pixel_graph)

canvas = GraphRenderer.blank()

canvas = GraphRenderer.draw_graph(
    canvas,
    topology,
)

cv2.imwrite(
    "generated/topology_graph.png",
    canvas,
)

print("Topology graph rendered.")