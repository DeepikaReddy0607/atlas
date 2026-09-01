from pathlib import Path
import json
import time

import numpy as np
from PIL import Image

from app.engines.vision.registry import ModelRegistry


# ============================================================
# CONFIG — FROZEN BEFORE FINAL TEST
# ============================================================

SPLIT_FILE = Path(
    "generated/deepglobe_split.json"
)

MODELS = [
    "dlinknet34",
    "roadgie",
]

WEIGHTS = np.array(
    [0.65, 0.35],
    dtype=np.float32,
)

THRESHOLD = 0.275

IMAGE_SIZE = 1024


# ============================================================
# DATASET
# ============================================================

def load_split():

    with open(
        SPLIT_FILE,
        "r",
        encoding="utf-8",
    ) as f:

        split = json.load(f)

    test_pairs = split.get(
        "test",
        split.get("final_test", []),
    )

    if not test_pairs:

        raise RuntimeError(
            "No final test split found in "
            f"{SPLIT_FILE}"
        )

    return test_pairs


# ============================================================
# PATH RESOLUTION
# ============================================================

def resolve_path(path):

    path = Path(path)

    if path.exists():
        return path

    # Handle split files containing relative paths.
    candidates = [
        Path(
            r"D:\Projects\atlas"
        ) / path,

        Path(
            r"D:\Projects\atlas\datasets\DeepGlobe"
        ) / path,

        Path(
            r"D:\Projects\atlas\datasets\DeepGlobe\train"
        ) / path,
    ]

    for candidate in candidates:

        if candidate.exists():
            return candidate

    raise FileNotFoundError(
        f"Could not find:\n{path}"
    )


# ============================================================
# PROBABILITY EXTRACTION
# ============================================================

def extract_probability(
    result,
    model_name,
    image_size,
):

    logits = getattr(
        result,
        "logits",
        None,
    )

    if logits is None:

        raise RuntimeError(
            f"{model_name} did not return "
            "probability/logit data."
        )

    probability = np.asarray(
        logits
    )

    # --------------------------------------------------------
    # Remove batch dimension.
    # --------------------------------------------------------

    if probability.ndim == 4:

        probability = probability[0]

    probability = np.squeeze(
        probability
    )

    # --------------------------------------------------------
    # Convert logits to probability if necessary.
    # --------------------------------------------------------

    if (
        probability.min() < 0.0
        or probability.max() > 1.0
    ):

        probability = 1.0 / (
            1.0
            + np.exp(
                -probability
            )
        )

    if probability.ndim != 2:

        raise RuntimeError(
            f"{model_name} produced "
            f"unexpected probability shape "
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
                (
                    width,
                    height,
                ),
                Image.Resampling.BILINEAR,
            ),
            dtype=np.float32,
        )

    return probability

# ============================================================
# METRICS
# ============================================================

def calculate_metrics(
    tp,
    fp,
    fn,
    tn,
):

    union = (
        tp + fp + fn
    )

    iou = (
        tp / union
        if union > 0
        else 1.0
    )

    dice_denominator = (
        2 * tp
        + fp
        + fn
    )

    dice = (
        2 * tp
        / dice_denominator
        if dice_denominator > 0
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

    accuracy = (
        (tp + tn)
        /
        (
            tp
            + tn
            + fp
            + fn
        )
    )

    return (
        iou,
        dice,
        precision,
        recall,
        accuracy,
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)

    print(
        "ATLAS — FINAL DEEPGLOBE ENSEMBLE TEST"
    )

    print("=" * 70)

    print()
    print(
        "FROZEN CONFIGURATION"
    )

    print(
        "-" * 70
    )

    print(
        f"OpenEarthMap : 0.00"
    )

    print(
        f"D-LinkNet34  : {WEIGHTS[0]:.2f}"
    )

    print(
        f"RoadGIE      : {WEIGHTS[1]:.2f}"
    )

    print(
        f"Threshold    : {THRESHOLD:.3f}"
    )

    print(
        "Post-process : NONE"
    )

    print()
    pairs = load_split()

    print(
        f"Final test images : "
        f"{len(pairs)}"
    )

    if len(pairs) != 935:

        raise RuntimeError(
            "Expected exactly 935 final-test "
            f"images, found {len(pairs)}."
        )
    # --------------------------------------------------------
    # Load models ONCE.
    # --------------------------------------------------------

    predictors = {}

    for model_name in MODELS:

        print()
        print(
            f"Loading {model_name}..."
        )

        predictors[
            model_name
        ] = ModelRegistry.get(
            model_name
        )

    print()
    print(
        "Models loaded."
    )

    # --------------------------------------------------------
    # Global confusion counts.
    # --------------------------------------------------------

    ensemble_tp = 0
    ensemble_fp = 0
    ensemble_fn = 0
    ensemble_tn = 0

    # Individual D-LinkNet baseline.
    dlink_tp = 0
    dlink_fp = 0
    dlink_fn = 0
    dlink_tn = 0

    # Original ensemble @ 0.30.
    old_tp = 0
    old_fp = 0
    old_fn = 0
    old_tn = 0

    inference_times = []

    start_total = time.perf_counter()

    # --------------------------------------------------------
    # Evaluate every final-test image.
    # --------------------------------------------------------

    for index, item in enumerate(
        pairs,
        start=1,
    ):

        image_path = resolve_path(
            item["image"]
        )

        mask_path = resolve_path(
            item["mask"]
        )

        print(
            f"[{index}/{len(pairs)}] "
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
            )
            > 127
        )

        # ----------------------------------------------------
        # Model inference.
        # ----------------------------------------------------

        probabilities = []

        inference_start = (
            time.perf_counter()
        )

        for model_name in MODELS:

            result = predictors[
                model_name
            ].predict(
                image
            )

            probability = (
                extract_probability(
                    result,
                    model_name,
                    image.size,
                )
            )

            probabilities.append(
                probability
            )

        inference_times.append(
            (
                time.perf_counter()
                - inference_start
            )
            * 1000
        )

        probabilities = np.stack(
            probabilities,
            axis=0,
        )

        # ----------------------------------------------------
        # FROZEN ensemble.
        # ----------------------------------------------------

        ensemble_probability = (
            WEIGHTS[:, None, None]
            * probabilities
        ).sum(
            axis=0
        )

        ensemble_prediction = (
            ensemble_probability
            >= THRESHOLD
        )

        # ----------------------------------------------------
        # D-LinkNet baseline.
        # ----------------------------------------------------

        dlink_prediction = (
            probabilities[0]
            >= 0.5
        )

        # ----------------------------------------------------
        # Original ensemble.
        # ----------------------------------------------------

        old_probability = (
            0.65 * probabilities[0]
            +
            0.35 * probabilities[1]
        )

        old_prediction = (
            old_probability
            >= 0.30
        )

        # ----------------------------------------------------
        # Update confusion matrices.
        # ----------------------------------------------------

        ensemble_tp += int(
            np.logical_and(
                ensemble_prediction,
                ground_truth,
            ).sum()
        )

        ensemble_fp += int(
            np.logical_and(
                ensemble_prediction,
                ~ground_truth,
            ).sum()
        )

        ensemble_fn += int(
            np.logical_and(
                ~ensemble_prediction,
                ground_truth,
            ).sum()
        )

        ensemble_tn += int(
            np.logical_and(
                ~ensemble_prediction,
                ~ground_truth,
            ).sum()
        )

        dlink_tp += int(
            np.logical_and(
                dlink_prediction,
                ground_truth,
            ).sum()
        )

        dlink_fp += int(
            np.logical_and(
                dlink_prediction,
                ~ground_truth,
            ).sum()
        )

        dlink_fn += int(
            np.logical_and(
                ~dlink_prediction,
                ground_truth,
            ).sum()
        )

        dlink_tn += int(
            np.logical_and(
                ~dlink_prediction,
                ~ground_truth,
            ).sum()
        )

        old_tp += int(
            np.logical_and(
                old_prediction,
                ground_truth,
            ).sum()
        )

        old_fp += int(
            np.logical_and(
                old_prediction,
                ~ground_truth,
            ).sum()
        )

        old_fn += int(
            np.logical_and(
                ~old_prediction,
                ground_truth,
            ).sum()
        )

        old_tn += int(
            np.logical_and(
                ~old_prediction,
                ~ground_truth,
            ).sum()
        )

    # ========================================================
    # FINAL METRICS
    # ========================================================

    (
        ensemble_iou,
        ensemble_dice,
        ensemble_precision,
        ensemble_recall,
        ensemble_accuracy,
    ) = calculate_metrics(
        ensemble_tp,
        ensemble_fp,
        ensemble_fn,
        ensemble_tn,
    )

    (
        dlink_iou,
        dlink_dice,
        dlink_precision,
        dlink_recall,
        dlink_accuracy,
    ) = calculate_metrics(
        dlink_tp,
        dlink_fp,
        dlink_fn,
        dlink_tn,
    )

    (
        old_iou,
        old_dice,
        old_precision,
        old_recall,
        old_accuracy,
    ) = calculate_metrics(
        old_tp,
        old_fp,
        old_fn,
        old_tn,
    )

    total_time = (
        time.perf_counter()
        - start_total
    )

    # ========================================================
    # REPORT
    # ========================================================

    print()
    print("=" * 70)

    print(
        "FINAL DEEPGLOBE HOLDOUT RESULT"
    )

    print("=" * 70)

    print()
    print(
        "D-LINKNET34 BASELINE"
    )

    print(
        f"IoU       : {dlink_iou:.4f}"
    )

    print(
        f"Dice      : {dlink_dice:.4f}"
    )

    print(
        f"Precision : {dlink_precision:.4f}"
    )

    print(
        f"Recall    : {dlink_recall:.4f}"
    )

    print(
        f"Accuracy  : {dlink_accuracy:.4f}"
    )

    print()
    print(
        "ORIGINAL ENSEMBLE"
    )

    print(
        "Weights    : D-LinkNet 0.65 "
        "+ RoadGIE 0.35"
    )

    print(
        "Threshold  : 0.300"
    )

    print(
        f"IoU       : {old_iou:.4f}"
    )

    print(
        f"Dice      : {old_dice:.4f}"
    )

    print(
        f"Precision : {old_precision:.4f}"
    )

    print(
        f"Recall    : {old_recall:.4f}"
    )

    print(
        f"Accuracy  : {old_accuracy:.4f}"
    )

    print()
    print(
        "OPTIMIZED ENSEMBLE"
    )

    print(
        "Weights    : D-LinkNet 0.65 "
        "+ RoadGIE 0.35"
    )

    print(
        "Threshold  : 0.275"
    )

    print(
        f"IoU       : {ensemble_iou:.4f}"
    )

    print(
        f"Dice      : {ensemble_dice:.4f}"
    )

    print(
        f"Precision : {ensemble_precision:.4f}"
    )

    print(
        f"Recall    : {ensemble_recall:.4f}"
    )

    print(
        f"Accuracy  : {ensemble_accuracy:.4f}"
    )

    print()
    print(
        "IMPROVEMENT OVER ORIGINAL ENSEMBLE"
    )

    print(
        f"IoU change : "
        f"{ensemble_iou - old_iou:+.4f}"
    )

    print(
        f"Dice change: "
        f"{ensemble_dice - old_dice:+.4f}"
    )

    print()
    print(
        "IMPROVEMENT OVER D-LINKNET"
    )

    print(
        f"IoU change : "
        f"{ensemble_iou - dlink_iou:+.4f}"
    )

    print(
        f"Dice change: "
        f"{ensemble_dice - dlink_dice:+.4f}"
    )

    print()
    print(
        f"Average model inference: "
        f"{np.mean(inference_times):.2f} ms/image"
    )

    print(
        f"Total evaluation time: "
        f"{total_time / 60:.2f} minutes"
    )

    print()
    print("=" * 70)

    if ensemble_iou > old_iou:

        print(
            "RESULT: OPTIMIZED ENSEMBLE "
            "GENERALIZES BETTER THAN "
            "THE ORIGINAL ENSEMBLE."
        )

    else:

        print(
            "RESULT: THRESHOLD OPTIMIZATION "
            "DID NOT GENERALIZE."
        )

    print("=" * 70)


if __name__ == "__main__":
    main()