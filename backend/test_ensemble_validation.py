from pathlib import Path

import numpy as np
from PIL import Image

from app.engines.vision.registry import ModelRegistry


# ============================================================
# CONFIG
# ============================================================

DATASET_ROOT = Path(
    r"D:\Projects\atlas\datasets\DeepGlobe"
)

TRAIN_DIR = DATASET_ROOT / "train"

# The 20 images used during optimization.
OPTIMIZATION_COUNT = 20

# New images used only for validation.
VALIDATION_COUNT = 500

RANDOM_SEED = 42

ENSEMBLE_DLINK_WEIGHT = 0.65
ENSEMBLE_ROADGIE_WEIGHT = 0.35
ENSEMBLE_THRESHOLD = 0.30

DLINK_THRESHOLD = 0.50


# ============================================================
# DATASET
# ============================================================

def find_pairs():

    images = sorted(
        TRAIN_DIR.glob("*_sat.jpg")
    )

    pairs = []

    for image_path in images:

        image_id = image_path.stem.replace(
            "_sat",
            "",
        )

        mask_path = (
            TRAIN_DIR
            / f"{image_id}_mask.png"
        )

        if mask_path.exists():

            pairs.append(
                (
                    image_path,
                    mask_path,
                )
            )

    return pairs


def get_held_out_pairs(pairs):

    rng = np.random.default_rng(
        RANDOM_SEED
    )

    indices = np.arange(
        len(pairs)
    )

    rng.shuffle(indices)

    # First 20 were used for optimization.
    optimization_indices = (
        indices[:OPTIMIZATION_COUNT]
    )

    optimization_set = set(
        optimization_indices.tolist()
    )

    remaining_indices = [
        i
        for i in indices
        if i not in optimization_set
    ]

    selected = remaining_indices[
        :VALIDATION_COUNT
    ]

    return [
        pairs[i]
        for i in selected
    ]


# ============================================================
# PROBABILITY
# ============================================================

def extract_probability(
    result,
    model_name,
    image_size,
):

    probability = np.asarray(
        result.logits
    )

    if probability.ndim == 4:
        probability = probability[0]

    if model_name == "openearthmap":

        # Not required for the final ensemble,
        # but kept here for completeness.
        probability = probability[4]

    else:

        probability = np.squeeze(
            probability
        )

    if probability.ndim != 2:

        raise RuntimeError(
            f"{model_name} produced "
            f"unexpected shape: "
            f"{probability.shape}"
        )

    width, height = image_size

    if probability.shape != (
        height,
        width,
    ):

        probability = np.asarray(
            Image.fromarray(
                probability.astype(
                    np.float32
                ),
                mode="F",
            ).resize(
                (width, height),
                Image.Resampling.BILINEAR,
            ),
            dtype=np.float32,
        )

    return probability


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(
    prediction,
    ground_truth,
):

    prediction = prediction.astype(
        bool
    )

    ground_truth = ground_truth.astype(
        bool
    )

    tp = np.logical_and(
        prediction,
        ground_truth,
    ).sum()

    fp = np.logical_and(
        prediction,
        ~ground_truth,
    ).sum()

    fn = np.logical_and(
        ~prediction,
        ground_truth,
    ).sum()

    union = (
        tp + fp + fn
    )

    denominator = (
        2 * tp + fp + fn
    )

    iou = (
        tp / union
        if union > 0
        else 1.0
    )

    dice = (
        2 * tp / denominator
        if denominator > 0
        else 1.0
    )

    precision = (
        tp / (tp + fp)
        if tp + fp > 0
        else 0.0
    )

    recall = (
        tp / (tp + fn)
        if tp + fn > 0
        else 0.0
    )

    return (
        float(iou),
        float(dice),
        float(precision),
        float(recall),
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print(
        "ATLAS — HELD-OUT ENSEMBLE VALIDATION"
    )
    print("=" * 70)

    pairs = find_pairs()

    print(
        f"Total labeled pairs: "
        f"{len(pairs)}"
    )

    validation_pairs = (
        get_held_out_pairs(
            pairs
        )
    )

    print(
        f"Optimization images excluded: "
        f"{OPTIMIZATION_COUNT}"
    )

    print(
        f"Held-out validation images: "
        f"{len(validation_pairs)}"
    )

    # --------------------------------------------------------
    # Load models
    # --------------------------------------------------------

    print()
    print(
        "Loading D-LinkNet34..."
    )

    dlinknet = ModelRegistry.get(
        "dlinknet34"
    )

    print()
    print(
        "Loading RoadGIE..."
    )

    roadgie = ModelRegistry.get(
        "roadgie"
    )

    # --------------------------------------------------------
    # Metrics storage
    # --------------------------------------------------------

    dlink_metrics = []
    ensemble_metrics = []

    # --------------------------------------------------------
    # Evaluation
    # --------------------------------------------------------

    for index, (
        image_path,
        mask_path,
    ) in enumerate(
        validation_pairs,
        start=1,
    ):

        print(
            f"[{index}/{len(validation_pairs)}] "
            f"{image_path.name}"
        )

        image = Image.open(
            image_path
        ).convert("RGB")

        ground_truth = (
            np.asarray(
                Image.open(
                    mask_path
                ).convert("L")
            ) > 127
        )

        # ----------------------------------------------------
        # D-LinkNet
        # ----------------------------------------------------

        dlink_result = (
            dlinknet.predict(
                image
            )
        )

        dlink_probability = (
            extract_probability(
                dlink_result,
                "dlinknet34",
                image.size,
            )
        )

        dlink_prediction = (
            dlink_probability
            >= DLINK_THRESHOLD
        )

        dlink_metrics.append(
            calculate_metrics(
                dlink_prediction,
                ground_truth,
            )
        )

        # ----------------------------------------------------
        # RoadGIE
        # ----------------------------------------------------

        roadgie_result = (
            roadgie.predict(
                image
            )
        )

        roadgie_probability = (
            extract_probability(
                roadgie_result,
                "roadgie",
                image.size,
            )
        )

        # ----------------------------------------------------
        # Ensemble
        # ----------------------------------------------------

        ensemble_probability = (
            ENSEMBLE_DLINK_WEIGHT
            * dlink_probability
            +
            ENSEMBLE_ROADGIE_WEIGHT
            * roadgie_probability
        )

        ensemble_prediction = (
            ensemble_probability
            >= ENSEMBLE_THRESHOLD
        )

        ensemble_metrics.append(
            calculate_metrics(
                ensemble_prediction,
                ground_truth,
            )
        )

    # ========================================================
    # RESULTS
    # ========================================================

    dlink_metrics = np.asarray(
        dlink_metrics
    )

    ensemble_metrics = np.asarray(
        ensemble_metrics
    )

    dlink_mean = (
        dlink_metrics.mean(
            axis=0
        )
    )

    ensemble_mean = (
        ensemble_metrics.mean(
            axis=0
        )
    )

    print()
    print("=" * 70)
    print(
        "HELD-OUT VALIDATION RESULTS"
    )
    print("=" * 70)

    print(
        f"{'MODEL':<25}"
        f"{'IoU':>10}"
        f"{'Dice':>10}"
        f"{'Precision':>12}"
        f"{'Recall':>10}"
    )

    print("-" * 70)

    print(
        f"{'D-LinkNet34':<25}"
        f"{dlink_mean[0]:>10.4f}"
        f"{dlink_mean[1]:>10.4f}"
        f"{dlink_mean[2]:>12.4f}"
        f"{dlink_mean[3]:>10.4f}"
    )

    print(
        f"{'D-LinkNet + RoadGIE':<25}"
        f"{ensemble_mean[0]:>10.4f}"
        f"{ensemble_mean[1]:>10.4f}"
        f"{ensemble_mean[2]:>12.4f}"
        f"{ensemble_mean[3]:>10.4f}"
    )

    print("-" * 70)

    iou_difference = (
        ensemble_mean[0]
        - dlink_mean[0]
    )

    dice_difference = (
        ensemble_mean[1]
        - dlink_mean[1]
    )

    print(
        f"IoU improvement : "
        f"{iou_difference:+.4f}"
    )

    print(
        f"Dice improvement: "
        f"{dice_difference:+.4f}"
    )

    print()

    if iou_difference > 0:

        print(
            "RESULT: ENSEMBLE GENERALIZES "
            "BETTER THAN D-LINKNET."
        )

    else:

        print(
            "RESULT: ENSEMBLE DOES NOT "
            "GENERALIZE BETTER."
        )

    print("=" * 70)


if __name__ == "__main__":
    main()