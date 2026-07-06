import networkx as nx


class NodeDetector:

    @staticmethod
    def endpoints(graph: nx.Graph):
        """
        Nodes with exactly one connection.
        """
        return [
            node
            for node in graph.nodes
            if graph.degree[node] == 1
        ]

    @staticmethod
    def junctions(graph: nx.Graph):
        """
        Nodes with three or more connections.
        """
        return [
            node
            for node in graph.nodes
            if graph.degree[node] >= 3
        ]