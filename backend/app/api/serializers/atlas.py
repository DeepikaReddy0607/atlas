from app.api.schemas.atlas import (
    AtlasResponse,
    GraphSummary,
    SegmentationSummary,
    SimulationSummary,
    CriticalitySummary,
    NodeCriticality,
    EdgeCriticality,
    GraphData,
)

from app.engines.atlas.result import AtlasResult
from pathlib import Path

def serialize_graph(graph):
    """
    Convert a NetworkX topology graph into frontend-friendly JSON.

    Node coordinates and edge pixel paths use the same
    (x, y) coordinate system as GraphBuilder.
    """

    node_to_id = {}

    nodes = []

    for index, node in enumerate(graph.nodes()):

        node_to_id[node] = index

        nodes.append(
            {
                "id": index,
                "x": int(node[0]),
                "y": int(node[1]),
            }
        )

    edges = []

    for u, v, data in graph.edges(data=True):

        edges.append(
            {
                "source": node_to_id[u],
                "target": node_to_id[v],

                "pixels": [
                    {
                        "x": int(point[0]),
                        "y": int(point[1]),
                    }
                    for point in data.get("pixels", [])
                ],

                "length": int(
                    data.get("length", 0)
                ),
            }
        )

    return {
        "nodes": nodes,
        "edges": edges,
    }

def to_public_url(path: str | None) -> str | None:
    if path is None:
        return None

    path = Path(path).as_posix()

    if path.startswith("outputs/"):
        return f"/{path}"

    return path

def serialize_atlas_result(
    result: AtlasResult,
) -> AtlasResponse:

    simulation = result.simulation

    return AtlasResponse(

        segmentation=SegmentationSummary(
            model_name=result.segmentation.model_name,
            inference_time_ms=result.segmentation.inference_time_ms,
            image_size=list(result.segmentation.image_size),
            mask_shape=list(result.segmentation.mask.shape),
            metadata=result.segmentation.metadata,
        ),

        pixel_graph=GraphSummary(
            nodes=result.pixel_graph.number_of_nodes(),
            edges=result.pixel_graph.number_of_edges(),
        ),

        topology_graph=GraphSummary(
            nodes=result.topology_graph.number_of_nodes(),
            edges=result.topology_graph.number_of_edges(),
        ),

        topology_graph_data=serialize_graph(
            result.topology_graph
        ),

        criticality=CriticalitySummary(

            node=[
                NodeCriticality(
                    node=list(node),
                    score=score,
                )
                for node, score in result.criticality["node"].items()
            ],

            edge=[
                EdgeCriticality(
                    edge=[list(p) for p in edge],
                    score=score,
                )
                for edge, score in result.criticality["edge"].items()
            ],
        ),

        resilience={
            "critical_node": (
                list(result.resilience["critical_node"])
                if result.resilience["critical_node"] is not None
                else None
            ),
            "connected_components": result.resilience["connected_components"],
            "largest_component": result.resilience["largest_component"],
        },

        risk={
            "ari": result.risk["ari"],
            "level": result.risk["level"],
            "recommendation": result.risk["recommendation"],
        },

        simulation=SimulationSummary(
            scenario=simulation.scenario,
            removed_nodes=simulation.removed_nodes,
            removed_edges=simulation.removed_edges,
            original_nodes=simulation.original_nodes,
            original_edges=simulation.original_edges,
            remaining_nodes=simulation.remaining_nodes,
            remaining_edges=simulation.remaining_edges,
            connected_components=simulation.connected_components,
            largest_component=simulation.largest_component,
            critical_node=list(simulation.critical_node)
            if simulation.critical_node
            else None,
        ),

        recommendation=result.recommendation,

        visualizations={
            "segmentation_overlay": (
                to_public_url(result.visualizations.segmentation_overlay)
                if result.visualizations
                else None
            ),
            "road_mask": (
                to_public_url(result.visualizations.road_mask)
                if result.visualizations
                else None
            ),
            "skeleton": (
                to_public_url(result.visualizations.skeleton)
                if result.visualizations
                else None
            ),
            "graph": (
                to_public_url(result.visualizations.graph)
                if result.visualizations
                else None
            ),
            "criticality": (
                to_public_url(result.visualizations.criticality)
                if result.visualizations
                else None
            ),
        },
    )