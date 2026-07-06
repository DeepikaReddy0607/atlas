import networkx as nx

from app.engines.analysis.node_detector import NodeDetector
from app.engines.analysis.graph_compressor import GraphCompressor


class TopologyBuilder:

    @staticmethod
    def build(pixel_graph: nx.Graph):

        topo = nx.Graph()

        endpoints = set(NodeDetector.endpoints(pixel_graph))

        clusters = GraphCompressor.junction_clusters(pixel_graph)

        representatives = set()

        for cluster in clusters:
            representatives.add(next(iter(cluster)))

        important = endpoints | representatives

        for node in important:
            topo.add_node(node)

        return topo
    @staticmethod
    def trace_path(pixel_graph, start, next_node, important_nodes):
        """
        Trace a road segment from one important node to another.
        """

        path = [start, next_node]

        previous = start
        current = next_node

        while current not in important_nodes:

            neighbors = list(pixel_graph.neighbors(current))

            # Don't go backwards
            neighbors = [
                n
                for n in neighbors
                if n != previous
            ]

            if not neighbors:
                break

            previous = current
            current = neighbors[0]

            path.append(current)

        return path
    
    @staticmethod
    def build_topology(pixel_graph):

        topology = nx.Graph()

        # Important nodes
        endpoints = set(NodeDetector.endpoints(pixel_graph))

        clusters = GraphCompressor.junction_clusters(pixel_graph)

        representatives = {
            next(iter(cluster))
            for cluster in clusters
        }

        important_nodes = endpoints | representatives

        # Add topology nodes
        for node in important_nodes:
            topology.add_node(node)

        visited_edges = set()

        # Trace every road segment
        for start in important_nodes:

            for neighbor in pixel_graph.neighbors(start):

                edge_key = tuple(sorted([start, neighbor]))

                if edge_key in visited_edges:
                    continue

                path = TopologyBuilder.trace_path(
                    pixel_graph,
                    start,
                    neighbor,
                    important_nodes,
                )

                end = path[-1]

                if end == start:
                    continue

                topology.add_edge(
                    start,
                    end,
                    pixels=path,
                    length=len(path),
                )

                visited_edges.add(edge_key)

        return topology