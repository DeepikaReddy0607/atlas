from app.engines.atlas.engine import AtlasEngine

engine = AtlasEngine()

result = engine.analyze("data/sample/roads_gt.png")

print("=" * 50)
print("ATLAS Engine Test")
print("=" * 50)

print("Pixel Graph Nodes :", result.pixel_graph.number_of_nodes())
print("Pixel Graph Edges :", result.pixel_graph.number_of_edges())

print("Topology Nodes    :", result.topology_graph.number_of_nodes())
print("Topology Edges    :", result.topology_graph.number_of_edges())
print("\nTop 5 Critical Junctions")

node_scores = result.criticality["node"]

for node, score in sorted(
    node_scores.items(),
    key=lambda item: item[1],
    reverse=True,
)[:5]:

    print(f"{node} -> {score:.4f}")

print("\nResilience Analysis")

print(
    "Critical Node      :",
    result.resilience["critical_node"],
)

print(
    "Connected Components:",
    result.resilience["connected_components"],
)

print(
    "Largest Component  :",
    result.resilience["largest_component"],
)
print("\nRisk Assessment")

print(
    "ARI               :",
    f"{result.risk['ari']:.2f}",
)

print(
    "Risk Level        :",
    result.risk["level"],
)

print(
    "Recommendation    :",
    result.risk["recommendation"],
)

print("\nScenario Simulation")

print(
    "Scenario          :",
    result.simulation.scenario,
)

print(
    "Removed Node      :",
    result.simulation.critical_node,
)

print(
    "Remaining Nodes   :",
    result.simulation.remaining_nodes,
)

print(
    "Remaining Edges   :",
    result.simulation.remaining_edges,
)

print(
    "Connected Components:",
    result.simulation.connected_components,
)

print(
    "Largest Component :",
    result.simulation.largest_component,
)