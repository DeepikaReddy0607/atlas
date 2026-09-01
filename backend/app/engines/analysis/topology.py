import networkx as nx

from app.engines.analysis.node_detector import NodeDetector
from app.engines.analysis.graph_compressor import GraphCompressor


class TopologyBuilder:

    @staticmethod
    def build(
        pixel_graph: nx.Graph,
    ) -> nx.Graph:
        """
        Build the compressed road topology graph.

        Pipeline:

            Pixel Graph
                ↓
            Important nodes
                ↓
            Trace road segments
                ↓
            Topology Graph

        Important nodes are:
        - endpoints
        - representatives of junction clusters
        """

        topology = nx.Graph()

        # ----------------------------------------------------
        # Detect important nodes
        # ----------------------------------------------------

        endpoints = set(
            NodeDetector.endpoints(
                pixel_graph
            )
        )

        clusters = (
            GraphCompressor.junction_clusters(
                pixel_graph
            )
        )

        representatives = {
            next(iter(cluster))
            for cluster in clusters
            if cluster
        }

        important_nodes = (
            endpoints
            | representatives
        )

        # ----------------------------------------------------
        # Add topology nodes
        # ----------------------------------------------------

        for node in important_nodes:

            topology.add_node(
                node
            )

        # ----------------------------------------------------
        # Trace road segments
        # ----------------------------------------------------

        visited_edges = set()

        for start in important_nodes:

            for neighbor in pixel_graph.neighbors(
                start
            ):

                edge_key = frozenset(
                    (
                        start,
                        neighbor,
                    )
                )

                if edge_key in visited_edges:
                    continue

                path = (
                    TopologyBuilder.trace_path(
                        pixel_graph,
                        start,
                        neighbor,
                        important_nodes,
                    )
                )

                if len(path) < 2:
                    continue

                end = path[-1]

                # ------------------------------------------------
                # The path must terminate at another important
                # node. Otherwise it is an incomplete trace.
                # ------------------------------------------------

                if end == start:
                    continue

                if end not in important_nodes:
                    continue

                # ------------------------------------------------
                # Add topology edge
                # ------------------------------------------------

                topology.add_edge(
                    start,
                    end,
                    pixels=path,
                    length=len(path),
                )

                # ------------------------------------------------
                # Mark every pixel-graph edge in this segment
                # as visited.
                # ------------------------------------------------

                for i in range(
                    len(path) - 1
                ):

                    visited_edges.add(
                        frozenset(
                            (
                                path[i],
                                path[i + 1],
                            )
                        )
                    )

        return topology

    @staticmethod
    def build_topology(pixel_graph: nx.Graph) -> nx.Graph:
        """
        Backward-compatible alias for build().
        """

        return TopologyBuilder.build(
            pixel_graph
        )
    # ========================================================
    # PATH TRACING
    # ========================================================

    @staticmethod
    def trace_path(
        pixel_graph: nx.Graph,
        start,
        next_node,
        important_nodes,
    ):
        """
        Safely trace a road segment from one important node
        toward another important node.

        The traversal is cycle-safe and bounded.
        """

        path = [
            start,
            next_node,
        ]

        previous = start
        current = next_node

        # ----------------------------------------------------
        # Edges visited during this individual trace.
        # ----------------------------------------------------

        visited_edges = {
            frozenset(
                (
                    start,
                    next_node,
                )
            )
        }

        while current not in important_nodes:

            neighbors = [
                node
                for node in pixel_graph.neighbors(
                    current
                )
                if node != previous
            ]

            if not neighbors:
                break

            # ------------------------------------------------
            # Select an unvisited continuation.
            # ------------------------------------------------

            next_candidate = None

            for candidate in neighbors:

                edge = frozenset(
                    (
                        current,
                        candidate,
                    )
                )

                if edge not in visited_edges:

                    next_candidate = candidate
                    break

            # ------------------------------------------------
            # No unused edge means the path has reached a
            # cycle or exhausted its valid continuation.
            # ------------------------------------------------

            if next_candidate is None:
                break

            edge = frozenset(
                (
                    current,
                    next_candidate,
                )
            )

            visited_edges.add(
                edge
            )

            previous = current
            current = next_candidate

            path.append(
                current
            )

            # ------------------------------------------------
            # Absolute safety guard.
            # A simple path cannot contain more vertices than
            # the pixel graph.
            # ------------------------------------------------

            if len(path) > (
                pixel_graph.number_of_nodes()
                + 1
            ):

                break

        return path