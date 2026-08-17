from dataclasses import dataclass


@dataclass
class VisualizationLayer:
    id: str
    name: str
    url: str
    layer_type: str