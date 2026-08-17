import networkx as nx


class ResilienceAnalyzer:

    @staticmethod
    def remove_node(
        graph: nx.Graph,
        node,
    ) -> nx.Graph:

        G = graph.copy()

        if node not in G:
            raise ValueError(
                f"Node {node} does not exist in the graph."
            )

        G.remove_node(node)

        return G

    @staticmethod
    def remove_edge(
        graph: nx.Graph,
        u,
        v,
    ) -> nx.Graph:

        G = graph.copy()

        if not G.has_edge(u, v):
            raise ValueError(
                f"Edge ({u}, {v}) does not exist in the graph."
            )

        G.remove_edge(u, v)

        return G

    @staticmethod
    def connected_components(
        graph: nx.Graph,
    ):

        return list(
            nx.connected_components(graph)
        )

    @staticmethod
    def largest_component_size(
        graph: nx.Graph,
    ) -> int:

        if graph.number_of_nodes() == 0:
            return 0

        return len(
            max(
                nx.connected_components(graph),
                key=len,
            )
        )