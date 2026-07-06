import networkx as nx


class CriticalityAnalyzer:

    @staticmethod
    def node_centrality(graph: nx.Graph):
        """
        Compute betweenness centrality for each node.
        Higher score => more critical junction.
        """

        return nx.betweenness_centrality(
            graph,
            weight="length",
            normalized=True,
        )

    @staticmethod
    def edge_centrality(graph: nx.Graph):
        """
        Compute betweenness centrality for each road segment.
        Higher score => more critical road.
        """

        return nx.edge_betweenness_centrality(
            graph,
            weight="length",
            normalized=True,
        )