from app.engines.vision.models.ade20k import (
    ADE20KPredictor,
)

from app.engines.vision.models.openearthmap import (
    OpenEarthMapPredictor,
)


class ModelRegistry:

    MODELS = {
        "openearthmap": OpenEarthMapPredictor,
        "ade20k": ADE20KPredictor,
    }

    @classmethod
    def get(cls, model_name):
        if model_name not in cls.MODELS:
            raise ValueError(
                f"Unknown model: {model_name}"
            )

        return cls.MODELS[model_name]()