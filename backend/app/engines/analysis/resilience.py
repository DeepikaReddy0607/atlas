import networkx as nx


class ResilienceAnalyzer:

    @staticmethod
    def remove_node(graph: nx.Graph, node):

        G = graph.copy()

        if node in G:
            G.remove_node(node)

        return G

    @staticmethod
    def remove_edge(graph: nx.Graph, u, v):

        G = graph.copy()

        if G.has_edge(u, v):
            G.remove_edge(u, v)

        return G

    @staticmethod
    def connected_components(graph: nx.Graph):

        return list(nx.connected_components(graph))

    @staticmethod
    def largest_component_size(graph: nx.Graph):

        if graph.number_of_nodes() == 0:
            return 0

        return len(
            max(
                nx.connected_components(graph),
                key=len,
            )
        )