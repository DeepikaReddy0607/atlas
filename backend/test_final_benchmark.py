from pathlib import Path
import json
import time

import numpy as np
from PIL import Image

from app.engines.vision.registry import ModelRegistry


# ============================================================
# CONFIGURATION
# ============================================================

SPLIT_FILE = Path(
    "generated/deepglobe_split.json"
)

CONFIG_OUTPUT = Path(
    "generated/final_ensemble_config.json"
)

RESULT_OUTPUT = Path(
    "generated/final_benchmark_results.json"
)

# ------------------------------------------------------------
# Optimization search
# ------------------------------------------------------------

WEIGHT_STEP = 0.05

THRESHOLD_START = 0.20
THRESHOLD_END = 0.60
THRESHOLD_STEP = 0.025

# D-LinkNet standalone baseline
DLINK_THRESHOLD = 0.50


# ============================================================
# LOAD FROZEN SPLIT
# ============================================================

def load_split():

    if not SPLIT_FILE.exists():

        raise FileNotFoundError(
            f"Split file not found: "
            f"{SPLIT_FILE}"
        )

    with open(
        SPLIT_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        split = json.load(file)

    required = {
        "train",
        "validation",
        "test",
    }

    if not required.issubset(
        split.keys()
    ):

        raise RuntimeError(
            "Invalid DeepGlobe split file."
        )

    return split


# ============================================================
# PROBABILITY EXTRACTION
# ============================================================

def extract_probability(
    result,
    model_name,
    image_size,
):

    if result.logits is None:

        raise RuntimeError(
            f"{model_name} did not return "
            "probability data in "
            "SegmentationResult.logits."
        )

    probability = np.asarray(
        result.logits
    )

    # --------------------------------------------------------
    # Remove batch dimension
    # --------------------------------------------------------

    if probability.ndim == 4:

        probability = probability[0]

    # --------------------------------------------------------
    # OpenEarthMap
    # --------------------------------------------------------

    if model_name == "openearthmap":

        if probability.ndim != 3:

            raise RuntimeError(
                "OpenEarthMap logits have "
                f"unexpected shape: "
                f"{probability.shape}"
            )

        probability = probability[4]

    # --------------------------------------------------------
    # Binary models
    # --------------------------------------------------------

    else:

        probability = np.squeeze(
            probability
        )

    if probability.ndim != 2:

        raise RuntimeError(
            f"{model_name} probability map "
            f"must be 2D, got "
            f"{probability.shape}"
        )

    width, height = image_size

    # --------------------------------------------------------
    # Resize to original image
    # --------------------------------------------------------

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

    return probability.astype(
        np.float32
    )


# ============================================================
# GROUND TRUTH
# ============================================================

def load_ground_truth(
    mask_path,
):

    mask = np.asarray(
        Image.open(
            mask_path
        ).convert("L")
    )

    return (
        mask > 127
    )


# ============================================================
# COLLECT PROBABILITY MAPS
# ============================================================

def collect_predictions(
    pairs,
    dlinknet,
    roadgie,
    split_name,
):

    dlink_maps = []
    roadgie_maps = []
    ground_truths = []

    print()
    print("=" * 70)
    print(
        f"COLLECTING {split_name.upper()} PREDICTIONS"
    )
    print("=" * 70)

    total = len(pairs)

    start_total = time.perf_counter()

    for index, pair in enumerate(
        pairs,
        start=1,
    ):

        image_path = Path(
            pair["image"]
        )

        mask_path = Path(
            pair["mask"]
        )

        print(
            f"[{index}/{total}] "
            f"{image_path.name}"
        )

        image = Image.open(
            image_path
        ).convert("RGB")

        ground_truth = (
            load_ground_truth(
                mask_path
            )
        )

        # ====================================================
        # D-LINKNET
        # ====================================================

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

        # ====================================================
        # ROADGIE
        # ====================================================

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

        # ====================================================
        # STORE
        # ====================================================

        dlink_maps.append(
            dlink_probability
        )

        roadgie_maps.append(
            roadgie_probability
        )

        ground_truths.append(
            ground_truth
        )

    elapsed = (
        time.perf_counter()
        - start_total
    )

    print()
    print(
        f"{split_name} collection complete."
    )

    print(
        f"Images: {total}"
    )

    print(
        f"Elapsed: {elapsed:.2f} seconds"
    )

    return (
        np.stack(
            dlink_maps
        ),
        np.stack(
            roadgie_maps
        ),
        np.stack(
            ground_truths
        ),
    )


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

    dice_denominator = (
        2 * tp
        + fp
        + fn
    )

    if union > 0:

        iou = (
            tp / union
        )

    else:

        iou = 1.0

    if dice_denominator > 0:

        dice = (
            2 * tp
            / dice_denominator
        )

    else:

        dice = 1.0

    if tp + fp > 0:

        precision = (
            tp
            / (tp + fp)
        )

    else:

        precision = 0.0

    if tp + fn > 0:

        recall = (
            tp
            / (tp + fn)
        )

    else:

        recall = 0.0

    return np.array(
        [
            iou,
            dice,
            precision,
            recall,
        ],
        dtype=np.float64,
    )


# ============================================================
# DATASET METRICS
# ============================================================

def evaluate_configuration(
    dlink_maps,
    roadgie_maps,
    ground_truths,
    dlink_weight,
    roadgie_weight,
    threshold,
):

    fused = (
        dlink_weight
        * dlink_maps
        +
        roadgie_weight
        * roadgie_maps
    )

    prediction = (
        fused >= threshold
    )

    metrics = []

    for index in range(
        len(ground_truths)
    ):

        metrics.append(
            calculate_metrics(
                prediction[index],
                ground_truths[index],
            )
        )

    metrics = np.stack(
        metrics
    )

    return metrics.mean(
        axis=0
    )


# ============================================================
# OPTIMIZATION
# ============================================================

def optimize_ensemble(
    dlink_maps,
    roadgie_maps,
    ground_truths,
):

    print()
    print("=" * 70)
    print(
        "ENSEMBLE OPTIMIZATION"
    )
    print("=" * 70)

    weights = np.arange(
        0.0,
        1.0001,
        WEIGHT_STEP,
    )

    thresholds = np.arange(
        THRESHOLD_START,
        THRESHOLD_END + 0.0001,
        THRESHOLD_STEP,
    )

    total_combinations = (
        len(weights)
        * len(thresholds)
    )

    print(
        f"Weight combinations: "
        f"{len(weights)}"
    )

    print(
        f"Thresholds: "
        f"{len(thresholds)}"
    )

    print(
        f"Total evaluations: "
        f"{total_combinations}"
    )

    best = None

    completed = 0

    for dlink_weight in weights:

        roadgie_weight = (
            1.0
            - dlink_weight
        )

        fused = (
            dlink_weight
            * dlink_maps
            +
            roadgie_weight
            * roadgie_maps
        )

        for threshold in thresholds:

            prediction = (
                fused >= threshold
            )

            intersection = (
                np.logical_and(
                    prediction,
                    ground_truths,
                ).sum(
                    axis=(1, 2)
                )
            )

            union = (
                np.logical_or(
                    prediction,
                    ground_truths,
                ).sum(
                    axis=(1, 2)
                )
            )

            dice_denominator = (
                prediction.sum(
                    axis=(1, 2)
                )
                +
                ground_truths.sum(
                    axis=(1, 2)
                )
            )

            ious = np.divide(
                intersection,
                union,
                out=np.ones_like(
                    intersection,
                    dtype=np.float64,
                ),
                where=union != 0,
            )

            dices = np.divide(
                2.0 * intersection,
                dice_denominator,
                out=np.ones_like(
                    intersection,
                    dtype=np.float64,
                ),
                where=dice_denominator != 0,
            )

            mean_iou = float(
                ious.mean()
            )

            mean_dice = float(
                dices.mean()
            )

            completed += 1

            if (
                best is None
                or mean_iou > best["iou"]
            ):

                best = {
                    "dlinknet_weight":
                        float(
                            dlink_weight
                        ),

                    "roadgie_weight":
                        float(
                            roadgie_weight
                        ),

                    "threshold":
                        float(
                            threshold
                        ),

                    "iou":
                        mean_iou,

                    "dice":
                        mean_dice,
                }

        if (
            completed % 50 == 0
            or completed
            == total_combinations
        ):

            print(
                f"Progress: "
                f"{completed}/"
                f"{total_combinations} "
                f"| Best IoU: "
                f"{best['iou']:.4f}"
            )

    return best


# ============================================================
# PRINT RESULTS
# ============================================================

def print_results(
    dlink_metrics,
    ensemble_metrics,
):

    print()
    print(
        f"{'MODEL':<28}"
        f"{'IoU':>10}"
        f"{'Dice':>10}"
        f"{'Precision':>12}"
        f"{'Recall':>10}"
    )

    print("-" * 70)

    print(
        f"{'D-LinkNet34':<28}"
        f"{dlink_metrics[0]:>10.4f}"
        f"{dlink_metrics[1]:>10.4f}"
        f"{dlink_metrics[2]:>12.4f}"
        f"{dlink_metrics[3]:>10.4f}"
    )

    print(
        f"{'D-LinkNet + RoadGIE':<28}"
        f"{ensemble_metrics[0]:>10.4f}"
        f"{ensemble_metrics[1]:>10.4f}"
        f"{ensemble_metrics[2]:>12.4f}"
        f"{ensemble_metrics[3]:>10.4f}"
    )

    print("-" * 70)

    print(
        f"IoU improvement: "
        f"{ensemble_metrics[0] - dlink_metrics[0]:+.4f}"
    )

    print(
        f"Dice improvement: "
        f"{ensemble_metrics[1] - dlink_metrics[1]:+.4f}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print(
        "ATLAS — FINAL DEEPGLOBE BENCHMARK"
    )
    print("=" * 70)

    # ========================================================
    # LOAD FROZEN SPLIT
    # ========================================================

    split = load_split()

    optimization_pairs = (
        split["train"]
    )

    validation_pairs = (
        split["validation"]
    )

    test_pairs = (
        split["test"]
    )

    print()
    print(
        "FROZEN DATASET SPLIT"
    )

    print(
        f"Optimization : "
        f"{len(optimization_pairs)}"
    )

    print(
        f"Validation   : "
        f"{len(validation_pairs)}"
    )

    print(
        f"Final test   : "
        f"{len(test_pairs)}"
    )

    print(
        f"Seed         : "
        f"{split.get('seed')}"
    )

    # ========================================================
    # LOAD MODELS
    # ========================================================

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

    # ========================================================
    # STEP 1
    # OPTIMIZATION
    # ========================================================

    (
        train_dlink,
        train_roadgie,
        train_gt,
    ) = collect_predictions(
        optimization_pairs,
        dlinknet,
        roadgie,
        "OPTIMIZATION",
    )

    best = optimize_ensemble(
        train_dlink,
        train_roadgie,
        train_gt,
    )

    print()
    print("=" * 70)
    print(
        "BEST OPTIMIZATION CONFIGURATION"
    )
    print("=" * 70)

    print(
        f"D-LinkNet weight : "
        f"{best['dlinknet_weight']:.2f}"
    )

    print(
        f"RoadGIE weight   : "
        f"{best['roadgie_weight']:.2f}"
    )

    print(
        f"Threshold        : "
        f"{best['threshold']:.3f}"
    )

    print(
        f"Optimization IoU : "
        f"{best['iou']:.4f}"
    )

    print(
        f"Optimization Dice: "
        f"{best['dice']:.4f}"
    )

    # ========================================================
    # STEP 2
    # VALIDATION
    # ========================================================

    (
        valid_dlink,
        valid_roadgie,
        valid_gt,
    ) = collect_predictions(
        validation_pairs,
        dlinknet,
        roadgie,
        "VALIDATION",
    )

    dlink_valid = evaluate_configuration(
        valid_dlink,
        valid_roadgie,
        valid_gt,
        1.0,
        0.0,
        DLINK_THRESHOLD,
    )

    ensemble_valid = evaluate_configuration(
        valid_dlink,
        valid_roadgie,
        valid_gt,
        best["dlinknet_weight"],
        best["roadgie_weight"],
        best["threshold"],
    )

    print()
    print("=" * 70)
    print(
        "VALIDATION RESULTS"
    )
    print("=" * 70)

    print_results(
        dlink_valid,
        ensemble_valid,
    )

    # ========================================================
    # LOCK CONFIGURATION
    # ========================================================

    locked_config = {
        "dlinknet_weight":
            best["dlinknet_weight"],

        "roadgie_weight":
            best["roadgie_weight"],

        "threshold":
            best["threshold"],

        "baseline":
            {
                "model":
                    "dlinknet34",

                "threshold":
                    DLINK_THRESHOLD,
            },

        "optimization_images":
            len(optimization_pairs),

        "validation_images":
            len(validation_pairs),

        "test_images":
            len(test_pairs),

        "seed":
            split.get("seed"),

        "status":
            "LOCKED_BEFORE_FINAL_TEST",
    }

    CONFIG_OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        CONFIG_OUTPUT,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            locked_config,
            file,
            indent=4,
        )

    print()
    print(
        f"Locked configuration saved: "
        f"{CONFIG_OUTPUT}"
    )

    # ========================================================
    # STEP 3
    # FINAL TEST
    #
    # IMPORTANT:
    # Nothing above used the test set.
    # ========================================================

    print()
    print("=" * 70)
    print(
        "FINAL TEST — LOCKED CONFIGURATION"
    )
    print("=" * 70)

    (
        test_dlink,
        test_roadgie,
        test_gt,
    ) = collect_predictions(
        test_pairs,
        dlinknet,
        roadgie,
        "FINAL TEST",
    )

    dlink_test = evaluate_configuration(
        test_dlink,
        test_roadgie,
        test_gt,
        1.0,
        0.0,
        DLINK_THRESHOLD,
    )

    ensemble_test = evaluate_configuration(
        test_dlink,
        test_roadgie,
        test_gt,
        best["dlinknet_weight"],
        best["roadgie_weight"],
        best["threshold"],
    )

    # ========================================================
    # FINAL RESULTS
    # ========================================================

    print()
    print("=" * 70)
    print(
        "FINAL TEST RESULTS"
    )
    print("=" * 70)

    print_results(
        dlink_test,
        ensemble_test,
    )

    improvement_iou = (
        ensemble_test[0]
        - dlink_test[0]
    )

    improvement_dice = (
        ensemble_test[1]
        - dlink_test[1]
    )

    print()
    print(
        "FINAL DECISION"
    )

    if improvement_iou > 0:

        print(
            "ENSEMBLE BEATS D-LINKNET"
        )

    else:

        print(
            "D-LINKNET BEATS ENSEMBLE"
        )

    print(
        f"Final IoU improvement : "
        f"{improvement_iou:+.4f}"
    )

    print(
        f"Final Dice improvement: "
        f"{improvement_dice:+.4f}"
    )

    # ========================================================
    # SAVE RESULTS
    # ========================================================

    results = {

        "dataset":
            "DeepGlobe",

        "split_file":
            str(
                SPLIT_FILE.resolve()
            ),

        "optimization_images":
            len(
                optimization_pairs
            ),

        "validation_images":
            len(
                validation_pairs
            ),

        "test_images":
            len(
                test_pairs
            ),

        "seed":
            split.get("seed"),

        "configuration":
            locked_config,

        "validation":
            {
                "dlinknet":
                    dlink_valid.tolist(),

                "ensemble":
                    ensemble_valid.tolist(),
            },

        "final_test":
            {
                "dlinknet":
                    {
                        "iou":
                            float(
                                dlink_test[0]
                            ),
                        "dice":
                            float(
                                dlink_test[1]
                            ),
                        "precision":
                            float(
                                dlink_test[2]
                            ),
                        "recall":
                            float(
                                dlink_test[3]
                            ),
                    },

                "ensemble":
                    {
                        "iou":
                            float(
                                ensemble_test[0]
                            ),
                        "dice":
                            float(
                                ensemble_test[1]
                            ),
                        "precision":
                            float(
                                ensemble_test[2]
                            ),
                        "recall":
                            float(
                                ensemble_test[3]
                            ),
                    },

                "iou_improvement":
                    float(
                        improvement_iou
                    ),

                "dice_improvement":
                    float(
                        improvement_dice
                    ),
            },
    }

    with open(
        RESULT_OUTPUT,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            results,
            file,
            indent=4,
        )

    print()
    print(
        f"Results saved: "
        f"{RESULT_OUTPUT}"
    )

    print()
    print("=" * 70)
    print(
        "FINAL BENCHMARK COMPLETE"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()