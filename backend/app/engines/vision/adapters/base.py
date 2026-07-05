from abc import ABC, abstractmethod
from ..result import SegmentationResult


class VisionAdapter(ABC):

    @abstractmethod
    def load_model(self):
        pass

    @abstractmethod
    def predict(self, image) -> SegmentationResult:
        pass