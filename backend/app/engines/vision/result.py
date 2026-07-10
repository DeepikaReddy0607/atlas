from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class SegmentationResult:
    """
    Output produced by every Vision model in ATLAS.
    """

    mask: np.ndarray

    model_name: str

    inference_time_ms: float

    image_size: tuple[int, int]

    metadata: dict[str, Any]