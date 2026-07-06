from dataclasses import dataclass
from typing import Dict, List

import numpy as np


@dataclass
class SegmentationResult:

    mask: np.ndarray

    labels: List[str]

    class_ids: List[int]

    model_name: str

    inference_time_ms: float

    metadata: Dict