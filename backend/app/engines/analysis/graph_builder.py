import numpy as np
import networkx as nx


class GraphBuilder:

    @staticmethod
    def build(skeleton: np.ndarray) -> nx.Graph:
        """
        Convert a 1-pixel-wide skeleton into an undirected graph.

        Each white pixel becomes a node.
        Adjacent pixels (8-connectivity) become edges.
        """

        graph = nx.Graph()

        rows, cols = skeleton.shape

        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1),
        ]

        for y in range(rows):
            for x in range(cols):

                if skeleton[y, x] == 0:
                    continue

                graph.add_node((x, y))

                for dx, dy in directions:

                    nx_pos = x + dx
                    ny_pos = y + dy

                    if (
                        0 <= nx_pos < cols
                        and 0 <= ny_pos < rows
                        and skeleton[ny_pos, nx_pos] > 0
                    ):
                        graph.add_edge((x, y), (nx_pos, ny_pos))

        return graph