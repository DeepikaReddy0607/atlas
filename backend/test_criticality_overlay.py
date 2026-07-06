import cv2

from app.engines.analysis.skeleton import Skeletonizer
from app.engines.analysis.graph_builder import GraphBuilder
from app.engines.analysis.topology import TopologyBuilder
from app.engines.analysis.criticality import CriticalityAnalyzer

from app.engines.visualization.renderer import GraphRenderer


# Load road mask
mask = cv2.imread(
    "data/sample/roads_gt.png",
    cv2.IMREAD_GRAYSCALE,
)

# Build topology graph
skeleton = Skeletonizer.build(mask)

pixel_graph = GraphBuilder.build(skeleton)

topology = TopologyBuilder.build_topology(pixel_graph)

# Compute centrality
scores = CriticalityAnalyzer.node_centrality(topology)

# Render graph
canvas = GraphRenderer.blank()

canvas = GraphRenderer.draw_graph(
    canvas,
    topology,
)

# Overlay criticality
canvas = GraphRenderer.draw_criticality(
    canvas,
    topology,
    scores,
)

# Save image
cv2.imwrite(
    "generated/criticality_overlay.png",
    canvas,
)

print("Criticality overlay saved.")