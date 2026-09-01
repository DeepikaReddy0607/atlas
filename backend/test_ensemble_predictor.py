from PIL import Image
from pathlib import Path
from app.engines.vision.models.ensemble import (
    EnsemblePredictor,
)


IMAGE_PATH = (
    Path(__file__).resolve().parent.parent
    / "datasets"
    / "DeepGlobe"
    / "valid"
    / "100794_sat.jpg"
)


def main():

    print("=" * 60)
    print("ATLAS ENSEMBLE PREDICTOR TEST")
    print("=" * 60)

    image = Image.open(
        IMAGE_PATH
    ).convert("RGB")

    predictor = EnsemblePredictor()

    result = predictor.predict(
        image
    )

    print()
    print(
        "MODEL:",
        result.model_name,
    )

    print(
        "MASK SHAPE:",
        result.mask.shape,
    )

    print(
        "ROAD PIXELS:",
        int(result.mask.sum()),
    )

    print(
        "LOGITS SHAPE:",
        result.logits.shape,
    )

    print(
        "INFERENCE:",
        result.inference_time_ms,
        "ms",
    )

    print(
        "THRESHOLD:",
        result.metadata["threshold"],
    )

    print(
        "WEIGHTS:",
        result.metadata["weights"],
    )

    print("=" * 60)
    print("ENSEMBLE TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()