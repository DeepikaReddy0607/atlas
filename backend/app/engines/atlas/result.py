from dataclasses import dataclass
from typing import Optional

import networkx as nx

from app.engines.vision.result import SegmentationResult
from app.engines.analysis.simulator import SimulationResult


@dataclass
class AtlasResult:
    """
    Final output produced by the ATLAS Engine.
    """

    segmentation: Optional[SegmentationResult] = None

    pixel_graph: Optional[nx.Graph] = None

    topology_graph: Optional[nx.Graph] = None

    criticality: dict | None = None

    simulation: SimulationResult | None = None

    resilience: dict | None = None

    risk: dict | None = None

    recommendation: Optional[str] = None

    visualization_path: Optional[str] = None