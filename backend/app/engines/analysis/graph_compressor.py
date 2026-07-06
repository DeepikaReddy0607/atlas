import networkx as nx


class GraphCompressor:

    @staticmethod
    def junction_clusters(graph: nx.Graph):

        # Get all junction nodes
        junctions = {
            node
            for node in graph.nodes
            if graph.degree[node] >= 3
        }

        visited = set()
        clusters = []

        for node in junctions:

            if node in visited:
                continue

            stack = [node]
            cluster = set()

            while stack:

                current = stack.pop()

                if current in visited:
                    continue

                visited.add(current)
                cluster.add(current)

                for neighbor in graph.neighbors(current):

                    if neighbor in junctions and neighbor not in visited:
                        stack.append(neighbor)

            clusters.append(cluster)

        return clusters