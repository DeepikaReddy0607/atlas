from abc import ABC, abstractmethod


class BaseVisionModel(ABC):

    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def predict(self, image):
        pass

    @abstractmethod
    def postprocess(self, prediction):
        pass