import cv2

from app.engines.analysis.skeleton import Skeletonizer
from app.engines.analysis.graph_builder import GraphBuilder
from app.engines.analysis.topology import TopologyBuilder
from app.engines.analysis.simulator import ScenarioSimulator


mask = cv2.imread(
    "data/sample/roads_gt.png",
    cv2.IMREAD_GRAYSCALE,
)

skeleton = Skeletonizer.build(mask)

pixel_graph = GraphBuilder.build(skeleton)

topology = TopologyBuilder.build_topology(pixel_graph)

result = ScenarioSimulator.simulate_most_critical_node(
    topology
)

print("=" * 50)
print("ATLAS Scenario Simulation")
print("=" * 50)

print(result)