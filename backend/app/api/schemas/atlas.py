from pydantic import BaseModel


class GraphSummary(BaseModel):
    nodes: int
    edges: int


class SegmentationSummary(BaseModel):
    model_name: str
    inference_time_ms: float
    image_size: list[int]
    mask_shape: list[int]
    metadata: dict


class SimulationSummary(BaseModel):
    scenario: str

    removed_nodes: list
    removed_edges: list

    original_nodes: int
    original_edges: int

    remaining_nodes: int
    remaining_edges: int

    connected_components: int

    largest_component: int

    critical_node: list | None


class AtlasResponse(BaseModel):

    segmentation: SegmentationSummary

    pixel_graph: GraphSummary

    topology_graph: GraphSummary

    criticality: dict

    resilience: dict

    risk: dict

    simulation: SimulationSummary

    recommendation: str | None = None

    visualization_path: str | None = None