from app.api.schemas.atlas import (
    AtlasResponse,
    GraphSummary,
    SegmentationSummary,
    SimulationSummary,
)

from app.engines.atlas.result import AtlasResult


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

        criticality={
            "node": [
                {
                    "node": list(node),
                    "score": score,
                }
                for node, score in result.criticality["node"].items()
            ],
            "edge": [
                {
                    "edge": [list(p) for p in edge],
                    "score": score,
                }
                for edge, score in result.criticality["edge"].items()
            ],
        },

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

        visualization_path=result.visualization_path,
    )