from abc import ABC, abstractmethod
import numpy as np
from PIL import Image


class BasePredictor(ABC):

    @abstractmethod
    def predict(self, image: Image.Image) -> np.ndarray:
        pass