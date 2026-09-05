from dataclasses import dataclass

import networkx as nx

from app.engines.analysis.resilience import ResilienceAnalyzer
from app.engines.analysis.criticality import CriticalityAnalyzer


@dataclass
class SimulationResult:
    """
    Result produced by a network failure simulation.
    """

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
    """
    Failure-scenario simulation engine.

    Supported scenarios:

        - Critical Node Failure
        - Selected Node Failure
        - Critical Edge Failure
        - Selected Edge Failure

    All simulations operate on graph copies.
    The original topology graph is never mutated.
    """

    # =========================================================
    # INTERNAL
    # =========================================================

    @staticmethod
    def _validate_graph(
        graph: nx.Graph,
    ) -> None:

        if graph is None:
            raise ValueError(
                "Cannot simulate failure on a null graph."
            )

        if graph.number_of_nodes() == 0:
            raise ValueError(
                "Cannot simulate failure on an empty graph."
            )

    @staticmethod
    def _build_result(
        graph: nx.Graph,
        failed: nx.Graph,
        scenario: str,
        removed_nodes: list,
        removed_edges: list,
        critical_node: tuple | None = None,
    ) -> SimulationResult:

        components = (
            ResilienceAnalyzer.connected_components(
                failed
            )
        )

        largest_component = (
            ResilienceAnalyzer.largest_component_size(
                failed
            )
        )

        return SimulationResult(
            scenario=scenario,

            removed_nodes=removed_nodes,

            removed_edges=removed_edges,

            original_nodes=graph.number_of_nodes(),
            original_edges=graph.number_of_edges(),

            remaining_nodes=failed.number_of_nodes(),
            remaining_edges=failed.number_of_edges(),

            connected_components=len(
                components
            ),

            largest_component=largest_component,

            critical_node=critical_node,
        )

    # =========================================================
    # NODE FAILURE
    # =========================================================

    @staticmethod
    def simulate_node_failure(
        graph: nx.Graph,
        node,
    ) -> SimulationResult:
        """
        Simulate failure of a specific node.
        """

        ScenarioSimulator._validate_graph(
            graph
        )

        if node not in graph:
            raise ValueError(
                f"Node {node} does not exist in the graph."
            )

        removed_edges = list(
            graph.edges(node)
        )

        failed = ResilienceAnalyzer.remove_node(
            graph,
            node,
        )

        return ScenarioSimulator._build_result(
            graph=graph,
            failed=failed,
            scenario="Node Failure",
            removed_nodes=[node],
            removed_edges=removed_edges,
            critical_node=node,
        )

    # =========================================================
    # MOST CRITICAL NODE
    # =========================================================

    @staticmethod
    def simulate_most_critical_node(
        graph: nx.Graph,
    ) -> SimulationResult:
        """
        Identify the highest-centrality node and
        simulate its failure.
        """

        ScenarioSimulator._validate_graph(
            graph
        )

        scores = (
            CriticalityAnalyzer.node_centrality(
                graph
            )
        )

        if not scores:
            raise ValueError(
                "Criticality analysis returned no node scores."
            )

        node = max(
            scores,
            key=scores.get,
        )

        return ScenarioSimulator.simulate_node_failure(
            graph,
            node,
        )

    # =========================================================
    # EDGE FAILURE
    # =========================================================

    @staticmethod
    def simulate_edge_failure(
        graph: nx.Graph,
        edge,
    ) -> SimulationResult:
        """
        Simulate failure of a specific edge.

        Expected edge format:

            ((x1, y1), (x2, y2))
        """

        ScenarioSimulator._validate_graph(
            graph
        )

        if not isinstance(edge, (list, tuple)):
            raise ValueError(
                "Edge must contain source and target nodes."
            )

        if len(edge) != 2:
            raise ValueError(
                "Edge must contain exactly two nodes."
            )

        u, v = edge

        if not graph.has_edge(u, v):
            raise ValueError(
                f"Edge ({u}, {v}) does not exist in the graph."
            )

        failed = ResilienceAnalyzer.remove_edge(
            graph,
            u,
            v,
        )

        return ScenarioSimulator._build_result(
            graph=graph,
            failed=failed,
            scenario="Edge Failure",
            removed_nodes=[],
            removed_edges=[(u, v)],
            critical_node=None,
        )

    # =========================================================
    # MOST CRITICAL EDGE
    # =========================================================

    @staticmethod
    def simulate_most_critical_edge(
        graph: nx.Graph,
    ) -> SimulationResult:
        """
        Identify the highest-centrality edge and
        simulate its failure.
        """

        ScenarioSimulator._validate_graph(
            graph
        )

        if graph.number_of_edges() == 0:
            raise ValueError(
                "Cannot simulate critical-edge failure "
                "on a graph with no edges."
            )

        scores = (
            CriticalityAnalyzer.edge_centrality(
                graph
            )
        )

        if not scores:
            raise ValueError(
                "Criticality analysis returned no edge scores."
            )

        edge = max(
            scores,
            key=scores.get,
        )

        return ScenarioSimulator.simulate_edge_failure(
            graph,
            edge,
        )

