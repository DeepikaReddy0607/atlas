import cv2
import numpy as np


class GraphRenderer:

    @staticmethod
    def blank(width=512, height=512):

        return np.full(
            (height, width, 3),
            255,
            dtype=np.uint8,
        )

    @staticmethod
    def draw_graph(canvas, graph):

        # Draw edges
        for u, v in graph.edges():

            cv2.line(
                canvas,
                u,
                v,
                (0, 180, 0),   # Green
                2,
            )

        # Draw nodes
        for node in graph.nodes():

            cv2.circle(
                canvas,
                node,
                5,
                (255, 0, 0),   # Blue
                -1,
            )

        return canvas

    @staticmethod
    def draw_criticality(
        canvas,
        graph,
        scores,
    ):
        """
        Highlight the most critical node.

        Parameters
        ----------
        canvas : np.ndarray
            Image to draw on.

        graph : nx.Graph
            Topology graph.

        scores : dict
            Output of CriticalityAnalyzer.node_centrality()
        """

        highest_score = max(scores.values())

        for node in graph.nodes():

            score = scores[node]

            if score == highest_score:

                color = (0, 0, 255)      # Red
                radius = 8

            else:

                color = (255, 0, 0)      # Blue
                radius = 5

            cv2.circle(
                canvas,
                node,
                radius,
                color,
                -1,
            )

        return canvas