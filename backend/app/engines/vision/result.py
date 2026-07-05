from dataclasses import dataclass
import numpy as np


@dataclass
class SegmentationResult:
    mask: np.ndarray
    labels: list[str]
    inference_time_ms: float
    model_name: str