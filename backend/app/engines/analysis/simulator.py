from dataclasses import dataclass

import networkx as nx

from app.engines.analysis.resilience import ResilienceAnalyzer
from app.engines.analysis.criticality import CriticalityAnalyzer


@dataclass
class SimulationResult:

    scenario: str

    removed_nodes: list

    removed_edges: list

    original_nodes: int
    original_edges: int

    remaining_nodes: int
    remaining_edges: int

    connected_components: int

    largest_component: int

    critical_node: tuple | None


class ScenarioSimulator:

    @staticmethod
    def simulate_node_failure(graph: nx.Graph, node):

        original_nodes = graph.number_of_nodes()
        original_edges = graph.number_of_edges()

        failed = ResilienceAnalyzer.remove_node(
            graph,
            node,
        )

        return SimulationResult(
            scenario="Node Failure",

            removed_nodes=[node],

            removed_edges=[],

            original_nodes=original_nodes,
            original_edges=original_edges,

            remaining_nodes=failed.number_of_nodes(),
            remaining_edges=failed.number_of_edges(),

            connected_components=len(
                ResilienceAnalyzer.connected_components(
                    failed
                )
            ),

            largest_component=
            ResilienceAnalyzer.largest_component_size(
                failed
            ),

            critical_node=node,
        )

    @staticmethod
    def simulate_most_critical_node(graph: nx.Graph):

        scores = CriticalityAnalyzer.node_centrality(
            graph
        )

        node = max(
            scores,
            key=scores.get,
        )

        return ScenarioSimulator.simulate_node_failure(
            graph,
            node,
        )