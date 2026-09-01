import os

import numpy as np
from PIL import Image
from scipy import ndimage

from app.engines.vision.models.dlinknet import (
    DLinkNet34Predictor,
)
from app.engines.analysis.skeleton import (
    Skeletonizer,
)


IMAGE_PATH = (
    "imagery/train/img/10255_sat.jpg"
)

OUTPUT_DIR = "generated/dlinknet_thresholds"

THRESHOLDS = [
    0.30,
    0.35,
    0.40,
    0.45,
    0.50,
    0.55,
    0.60,
    0.65,
    0.70,
]


def analyze_components(mask):

    labeled, count = ndimage.label(
        mask,
        structure=np.ones(
            (3, 3),
            dtype=np.uint8,
        ),
    )

    if count == 0:
        return 0, 0

    sizes = np.bincount(
        labeled.ravel()
    )[1:]

    largest = int(
        sizes.max()
    )

    return count, largest


def main():

    print("=" * 70)
    print("D-LINKNET34 THRESHOLD BENCHMARK")
    print("=" * 70)

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True,
    )

    image = Image.open(
        IMAGE_PATH
    ).convert("RGB")

    print(
        f"Image: {IMAGE_PATH}"
    )

    print(
        f"Image size: {image.size}"
    )

    # --------------------------------------------------------
    # Load model
    # --------------------------------------------------------

    predictor = DLinkNet34Predictor()

    # --------------------------------------------------------
    # ONE inference only
    # --------------------------------------------------------

    print(
        "\nRunning model inference once..."
    )

    probabilities = (
        predictor.predict_probabilities(
            image
        )
    )

    print(
        "Probability statistics:"
    )

    print(
        f"  min : {probabilities.min():.6f}"
    )

    print(
        f"  max : {probabilities.max():.6f}"
    )

    print(
        f"  mean: {probabilities.mean():.6f}"
    )

    print()

    # --------------------------------------------------------
    # Threshold evaluation
    # --------------------------------------------------------

    print(
        "=" * 70
    )

    print(
        "THRESHOLD RESULTS"
    )

    print(
        "=" * 70
    )

    print(
        f"{'Threshold':<12}"
        f"{'Road %':<12}"
        f"{'Road Px':<14}"
        f"{'Components':<14}"
        f"{'Largest':<14}"
        f"{'Skeleton':<14}"
    )

    print(
        "-" * 80
    )

    for threshold in THRESHOLDS:

        mask = (
            probabilities >= threshold
        )

        road_pixels = int(
            mask.sum()
        )

        road_percentage = (
            road_pixels
            / mask.size
            * 100
        )

        components, largest = (
            analyze_components(
                mask
            )
        )

        skeleton = Skeletonizer.build(
            mask
        )

        skeleton_pixels = int(
            skeleton.sum()
        )

        # ----------------------------------------------------
        # Save mask
        # ----------------------------------------------------

        filename = (
            f"roads_t{threshold:.2f}.png"
        )

        output_path = os.path.join(
            OUTPUT_DIR,
            filename,
        )

        Image.fromarray(
            mask.astype(
                np.uint8
            ) * 255
        ).save(
            output_path
        )

        print(
            f"{threshold:<12.2f}"
            f"{road_percentage:<12.2f}"
            f"{road_pixels:<14}"
            f"{components:<14}"
            f"{largest:<14}"
            f"{skeleton_pixels:<14}"
        )

    print()
    print(
        f"Masks saved to: {OUTPUT_DIR}"
    )

    print(
        "=" * 70
    )
    print(
        "BENCHMARK COMPLETE"
    )
    print(
        "=" * 70
    )


if __name__ == "__main__":
    main()