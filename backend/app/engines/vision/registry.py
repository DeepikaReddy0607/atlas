from app.engines.vision.models.ade20k import (
    ADE20KPredictor,
)

from app.engines.vision.models.openearthmap import (
    OpenEarthMapPredictor,
)

from app.engines.vision.models.dlinknet import (
    DLinkNet34Predictor,
)

from app.engines.vision.models.deeplabv3plus import (
    DeepLabV3PlusPredictor,
)

from app.engines.vision.models.roadgie import (
    RoadGIEPredictor,
)

from app.engines.vision.models.ensemble import (
    EnsemblePredictor,
)

class ModelRegistry:

    MODELS = {
        "openearthmap": OpenEarthMapPredictor,
        "ade20k": ADE20KPredictor,
        "dlinknet34": DLinkNet34Predictor,
        "deeplabv3plus": DeepLabV3PlusPredictor,
        "roadgie": RoadGIEPredictor,
        "ensemble": EnsemblePredictor,
    }

    @classmethod
    def get(cls, model_name):

        if model_name not in cls.MODELS:
            raise ValueError(
                f"Unknown model: {model_name}"
            )

        return cls.MODELS[model_name]()